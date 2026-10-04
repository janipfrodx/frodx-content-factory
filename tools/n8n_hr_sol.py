#!/usr/bin/env python3
"""Generira JS kodo Code vozlišč n8n workflowa cf-transkreacija-hr.

Uporaba: python3 tools/n8n_hr_sol.py <izhodna mapa>

Prompta se vzameta dobesedno iz veje/novicnik/vendor/igor-hr-sol/ in se v JS zapišeta
kot JSON niza; Prompti vrne njuni kontrolni vsoti FNV-1a (enako kot hr_sol.fnv1a).
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENDOR = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik" / "vendor" / "igor-hr-sol"

FNV = ("const fnv = (s) => { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) "
       "{ h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16).padStart(8, '0'); };")

IZVLECI = """const izvleci = (o) => {
  if (typeof o?.message?.content === 'string') return o.message.content;
  if (typeof o?.content === 'string') return o.content;
  if (typeof o?.text === 'string') return o.text;
  if (Array.isArray(o?.output)) {
    return o.output
      .filter((m) => m?.type === 'message' && Array.isArray(m.content))
      .flatMap((m) => m.content)
      .filter((c) => c?.type === 'output_text' && typeof c.text === 'string')
      .map((c) => c.text)
      .join('');
  }
  if (typeof o?.output === 'string') return o.output;
  return '';
};
const razcleni = (o, kdo) => {
  if (o?.error) return { napaka: kdo + ': ' + (typeof o.error === 'string' ? o.error : (o.error.message ?? JSON.stringify(o.error))) };
  const t = izvleci(o).trim().replace(/^```(?:json)?\\s*/, '').replace(/\\s*```$/, '');
  try { return { podatki: JSON.parse(t) }; } catch (e) { return { napaka: kdo + ' ni vrnil JSON: ' + e.message }; }
};
const brez = (v, kljuc) => { const k = { ...v }; delete k[kljuc]; return k; };"""


def _prompti():
    pisec = (VENDOR / "01-transkreacija-system.txt").read_text(encoding="utf-8")
    pregled = (VENDOR / "02-pregled-system.txt").read_text(encoding="utf-8")
    return f"""const PISEC = {json.dumps(pisec, ensure_ascii=False)};
const PREGLED = {json.dumps(pregled, ensure_ascii=False)};
{FNV}
const prompt_fnv = {{ pisec: fnv(PISEC), pregled: fnv(PREGLED) }};
const vhod = $input.first().json.body ?? {{}};
if (!Array.isArray(vhod.source_blocks) || vhod.source_blocks.length === 0) {{
  return [{{ json: {{ izid: 'NAPAKA', napaka: 'vhod brez source_blocks', naprej: false, krogi: 0, kandidat: [], review_reasons: [], pregled: null, prompt_fnv }} }}];
}}
const v = {{ ...vhod, candidate_blocks: [], audit_feedback: [] }};
return [{{ json: {{ vhod: v, prompt_fnv, pisec_system: PISEC, pregled_system: PREGLED, pisec_user: JSON.stringify(v), kandidat: [], audit_feedback: [], krogi: 0, naprej: true, napaka: null }} }}];
"""


def _razcleni_pisca(krog):
    stanje = "Prompti" if krog == 0 else f"Odloci {krog - 1}"
    return f"""{IZVLECI}
const s = $('{stanje}').first().json;
const r = razcleni($input.first().json ?? {{}}, 'pisec');
let napaka = r.napaka ?? null;
const p = r.podatki;
if (!napaka && (!p || typeof p.needs_review !== 'boolean' || !Array.isArray(p.blocks) || !Array.isArray(p.review_reasons))) {{
  napaka = 'pisec: izhod ne ustreza shemi 04';
}}
const kandidat = napaka ? s.kandidat : p.blocks;
const pregled_user = JSON.stringify({{ ...brez(s.vhod, 'audit_feedback'), candidate_blocks: kandidat }});
return [{{ json: {{ ...s, kandidat, needs_review: napaka ? null : p.needs_review, review_reasons: napaka ? [] : p.review_reasons, pregled_user, napaka }} }}];
"""


def _odloci(krog):
    return f"""const KROG = {krog};
{IZVLECI}
const s = $('Razcleni pisec {krog}').first().json;
if (s.napaka) return [{{ json: {{ ...s, krogi: KROG, izid: 'NAPAKA', naprej: false }} }}];
const r = razcleni($input.first().json ?? {{}}, 'pregled');
const p = r.podatki;
const CHECKS = ['meaning_preserved', 'names_numbers_links_preserved', 'structure_and_constraints_preserved', 'source_ambiguities_resolved'];
let napaka = r.napaka ?? null;
if (!napaka && (!p || !['PASS', 'PASS_WITH_MINOR_EDITS', 'FAIL'].includes(p.verdict) || typeof p.score !== 'number' || typeof p.checks !== 'object' || !Array.isArray(p.issues))) {{
  napaka = 'pregled: izhod ne ustreza shemi 05';
}}
if (napaka) return [{{ json: {{ ...s, krogi: KROG, izid: 'NAPAKA', naprej: false, napaka }} }}];
const blokirajoce = p.issues.filter((i) => i?.blocking === true);
const pass = s.needs_review === false && p.verdict === 'PASS' && p.score >= 95
  && CHECKS.every((k) => p.checks?.[k] === true) && blokirajoce.length === 0;
const naprej = !pass && blokirajoce.length > 0 && KROG < 2;
const pisec_user = JSON.stringify({{ ...s.vhod, candidate_blocks: s.kandidat, audit_feedback: p.issues }});
return [{{ json: {{ ...s, pregled: p, krogi: KROG, izid: pass ? 'PASS' : 'UREDNIK', naprej, audit_feedback: p.issues, pisec_user, napaka: null }} }}];
"""


ODGOVOR = """const s = $input.first().json;
const izid = s.izid ?? 'NAPAKA';
return [{ json: { izid, krogi: s.krogi ?? 0, blocks: izid === 'NAPAKA' ? [] : (s.kandidat ?? []), review_reasons: s.review_reasons ?? [], pregled: s.pregled ?? null, prompt_fnv: s.prompt_fnv, napaka: s.napaka ?? null } }];
"""


def vozlisca() -> dict:
    v = {"Prompti": _prompti()}
    for k in range(3):
        v[f"Razcleni pisec {k}"] = _razcleni_pisca(k)
    for k in range(3):
        v[f"Odloci {k}"] = _odloci(k)
    v["Odgovor"] = ODGOVOR
    return v


def main(argv) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    mapa = Path(argv[1])
    mapa.mkdir(parents=True, exist_ok=True)
    for ime, js in vozlisca().items():
        (mapa / f"{ime}.js").write_text(js, encoding="utf-8")
    print(f"Zapisanih {len(vozlisca())} vozlišč v {mapa}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
