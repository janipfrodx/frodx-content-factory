#!/usr/bin/env python3
"""HR izdaja novičnika prek n8n cf-transkreacija-hr (GPT-6.1 Sol: pisec in ločen pregled).

Uporaba:
  python3 hr_sol.py vhod <state.json>
  python3 hr_sol.py izdaja <state.json> <izid.json> <execution_id>

vhod    bere prevod/hr-vhod.json (izhod prevod_vhod.py) in SI izdajo, piše prevod/hr-sol-vhod.json.
izdaja  preveri izid workflowa, iz njega, SI strukture in prevod/hr-meta.json sestavi HR izdajo,
        jo vpiše v state.json, zapiše prevod/hr-editions.json in _run.prevod_hr.

Exit 0 = zapisano. Exit 1 = manjka korak (izpis ga imenuje). Exit 2 = napaka vhoda ali izida.
"""
import json
import os
import re
import sys
from pathlib import Path

from iz_editions import NapakaPreslikave, izdaja_iz_editions, vpisi
from izdaja_besedilo import NapakaOznak, izdaja_v_besedilo
from preveri_paket import ODSTOTEK_BREZ_NBSP
from prevod_vhod import ManjkaKorak
from tipografija import nbsp_pred_odstotkom

AUDIENCE = (
    "Vodje marketinga, prodaje, kontaktnih centrov in uporabniške izkušnje na Hrvaškem; "
    "prejemniki novičnika FrodX GameChanger."
)
NAVODILO_LOKALNI = (
    "Blok je za hrvaški trg vsebinsko drug. Napiši ga iz priloženega vira v tonu izdaje; "
    "SI blok z istimi id-ji je samo vzorec dolžine in tona."
)
NAVODILO_OKVIR = "Napovej vsebino hrvaških blokov. Ponudb, ki jih HR izdaja nima, ne omenjaj."
NAVODILO_REFERENCA = (
    "Objavljena hrvaška stran, na katero vodi CTA bloka. Je vir že potrjenih izrazov, naslovov "
    "in terminologije, ne vir besedila: zgodba, dolžina in struktura bloka pridejo iz izvirnika."
)
NAVODILO_ZETEV = (
    "Urednikovi potrjeni popravki iz prejšnjih izdaj. Oblika iz prej se v besedilu ne sme pojaviti; "
    "uporabi obliko iz potem. To velja pred splošnimi pravili."
)

VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "igor-hr-sol"
DOCX_PIPELINE = Path(__file__).resolve().parents[1] / "vendor" / "frodx-newsletter" / "references" / "docx-pipeline.md"
POZDRAV_HR = re.compile(r"^\|\s*`GREETING`\s*\|.*?HR = `([^`]+)`", re.MULTILINE)
NAVODILO_POZDRAV = (
    "Izdaja se začne s stalnim pozdravom »{}«, ki ga ne pišeš. "
    "HOOK mu neposredno sledi, zato se začne z malo začetnico."
)
PROMPTI = {"pisec": "01-transkreacija-system.txt", "pregled": "02-pregled-system.txt"}
URL = re.compile(r"https?://[^\s<>\"»”)]+")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
STEVKE = re.compile(r"\d+")


class NapakaIzida(ValueError):
    pass


def fnv1a(besedilo: str) -> str:
    h = 0x811C9DC5
    enote = besedilo.encode("utf-16-le")
    for i in range(0, len(enote), 2):
        h ^= enote[i] | (enote[i + 1] << 8)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"


def _iz_izvedbe(surovo: dict):
    try:
        return surovo["data"]["resultData"]["runData"]["Respond to Webhook"][0]["data"]["main"][0][0]["json"]
    except (KeyError, IndexError, TypeError):
        return surovo


def razpakiraj(surovo) -> dict:
    if isinstance(surovo, list):
        if not surovo:
            raise NapakaIzida("izid je prazen seznam")
        surovo = surovo[0]
    if isinstance(surovo, dict):
        surovo = _iz_izvedbe(surovo)
    if isinstance(surovo, dict) and isinstance(surovo.get("json"), dict):
        surovo = surovo["json"]
    if not isinstance(surovo, dict):
        raise NapakaIzida("izid ni objekt")
    if "izid" not in surovo:
        izvedba = surovo.get("execution") if isinstance(surovo.get("execution"), dict) else {}
        stanje = f" (izvedba {izvedba.get('id')}, status {izvedba.get('status')})" if izvedba else ""
        raise NapakaIzida(
            f"izid.json nima ključa izid{stanje} - zapiši odgovor get_workflow_execution "
            "z nodeNames [\"Respond to Webhook\"], ko je status izvedbe success"
        )
    return surovo


def _nizi(vzorec, besedilo):
    return [n.rstrip(".,;:!?") for n in vzorec.findall(besedilo)]


def _lokalni_bloki(vhod: dict) -> set:
    return {i for a in vhod.get("approved_adaptations") or []
            if isinstance(a, dict) and a.get("vir") for i in a.get("block_ids") or []}


def preveri_izid(izid: dict, vhod: dict) -> list:
    if izid.get("izid") not in ("PASS", "UREDNIK"):
        raise NapakaIzida(f"izid workflowa je {izid.get('izid')!r}: {izid.get('napaka') or 'brez pojasnila'}")
    pricakovano = {k: fnv1a((VENDOR / ime).read_text(encoding="utf-8")) for k, ime in PROMPTI.items()}
    if izid.get("prompt_fnv") != pricakovano:
        raise NapakaIzida(
            f"prompt v n8n se razlikuje od vendor/igor-hr-sol: {izid.get('prompt_fnv')} namesto {pricakovano}"
        )
    vir = [(b["id"], b["text"]) for b in vhod["source_blocks"]]
    bloki = izid.get("blocks")
    if isinstance(bloki, list) and not all(isinstance(b, dict) for b in bloki):
        raise NapakaIzida("bloki izida niso seznam objektov {id, text}")
    if not isinstance(bloki, list) or [b.get("id") for b in bloki] != [i for i, _ in vir]:
        dobljeno = [b.get("id") for b in bloki] if isinstance(bloki, list) else bloki
        raise NapakaIzida(f"id-ji blokov se ne ujemajo z izvirnikom: {dobljeno}")
    lokalni = _lokalni_bloki(vhod)
    opozorila = []
    for (bid, si_besedilo), blok in zip(vir, bloki):
        besedilo = blok.get("text")
        if not isinstance(besedilo, str) or not besedilo.strip():
            raise NapakaIzida(f"{bid}: prazno besedilo")
        if "\u2014" in besedilo:
            raise NapakaIzida(f"{bid}: dolgi pomišljaj U+2014")
        if "Pauletić" in besedilo:
            raise NapakaIzida(f"{bid}: Pauletić namesto Pauletič")
        if ODSTOTEK_BREZ_NBSP.search(nbsp_pred_odstotkom(URL.sub("", besedilo), "hr")):
            opozorila.append(f"{bid}: pred % manjka nedeljivi presledek (U+00A0), npr. 12\u00a0%")
        if bid in lokalni:
            continue
        for niz in _nizi(URL, si_besedilo) + _nizi(EMAIL, si_besedilo):
            if niz not in besedilo:
                raise NapakaIzida(f"{bid}: manjka {niz}")
        stevke = set(STEVKE.findall(besedilo))
        for st in dict.fromkeys(STEVKE.findall(si_besedilo)):
            if st not in stevke:
                opozorila.append(f"{bid}: številka {st} iz izvirnika ni v prevodu")
    return opozorila


def _si(stanje):
    for izdaja in stanje.get("editions") or []:
        if izdaja.get("language") == "si":
            return izdaja
    raise ManjkaKorak("korak 2: v state.json ni SI izdaje")


def _odstavki(seznam):
    return "\n".join(seznam or [])


def polja_si(si: dict) -> list:
    polja = [("SUBJECT", si["subject"]), ("PREHEADER", si["preheader"]),
             ("HOOK", _odstavki(si["hook"]["paragraphs"]))]
    for n, blok in enumerate(si["blocks"], 1):
        polja.append((f"B{n}_TITLE", blok["title"]))
        polja.append((f"B{n}_BODY", _odstavki(blok["body"])))
        if blok.get("bullets"):
            polja.append((f"B{n}_BULLETS", _odstavki(blok["bullets"])))
        polja.append((f"B{n}_CTA", blok["cta"]["label"]))
    polja.append(("CLOSING", _odstavki(si["closing"]["paragraphs"])))
    if si.get("ps"):
        polja.append(("PS", si["ps"]))
    return polja


def pozdrav_hr() -> str:
    najdba = POZDRAV_HR.search(DOCX_PIPELINE.read_text(encoding="utf-8"))
    if not najdba:
        raise ValueError("vendor/frodx-newsletter/references/docx-pipeline.md nima HR pozdrava v vrstici GREETING")
    return najdba.group(1)


def sestavi_vhod(stanje: dict, hr_vhod: dict) -> dict:
    si = _si(stanje)
    bloki = hr_vhod.get("bloki")
    if hr_vhod.get("jezik") != "hr" or not isinstance(bloki, list):
        raise ValueError("prevod/hr-vhod.json ni vhod prevajalca za hr")
    if [b.get("block_id") for b in bloki] != [b["block_id"] for b in si["blocks"]]:
        raise ManjkaKorak("korak 4: prevod/hr-vhod.json ne ustreza blokom SI izdaje - poženi prevod_vhod.py znova")
    polja = polja_si(si)
    prilagoditve, referenca = [], []
    for n, b in enumerate(bloki, 1):
        if b["nacin"] == "lokalni_vir":
            ids = [i for i, _ in polja if i.startswith(f"B{n}_")]
            prilagoditve.append({"block_ids": ids, "navodilo": NAVODILO_LOKALNI, "vir": b["vir"]})
        elif b.get("referenca"):
            referenca.append({"block_id": f"B{n}", "url": b["url"], "besedilo": b["referenca"]})
    if prilagoditve:
        prilagoditve.append({"block_ids": ["PREHEADER", "HOOK", "CLOSING"], "navodilo": NAVODILO_OKVIR})
    pozdrav = pozdrav_hr()
    return {
        "content_type": "newsletter",
        "audience": AUDIENCE,
        "source_blocks": [{"id": i, "text": t} for i, t in polja],
        "candidate_blocks": [],
        "glossary": [],
        "approved_examples": [],
        "approved_adaptations": prilagoditve,
        "constraints": {
            "referenca": {"navodilo": NAVODILO_REFERENCA, "bloki": referenca},
            "zetev": {"navodilo": NAVODILO_ZETEV, "pari": list(hr_vhod.get("zetev") or [])},
            "pozdrav": {"besedilo": pozdrav, "navodilo": NAVODILO_POZDRAV.format(pozdrav)},
        },
        "audit_feedback": [],
    }


def _beri(pot, korak):
    if not pot.is_file():
        raise ManjkaKorak(f"{korak}: {pot.parent.name}/{pot.name} manjka")
    return json.loads(pot.read_text(encoding="utf-8"))


def _zapisi(pot, podatki):
    pot.parent.mkdir(parents=True, exist_ok=True)
    zacasna = pot.with_name(pot.name + ".tmp")
    zacasna.write_text(json.dumps(podatki, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(zacasna, pot)


def _vhod(pot):
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    hr_vhod = _beri(pot.parent / "prevod" / "hr-vhod.json", "korak 4 (poženi prevod_vhod.py <state.json> hr)")
    vhod = sestavi_vhod(stanje, hr_vhod)
    _zapisi(pot.parent / "prevod" / "hr-sol-vhod.json", vhod)
    print(f"Zapisano: prevod/hr-sol-vhod.json ({len(vhod['source_blocks'])} polj, "
          f"{len(vhod['approved_adaptations'])} prilagoditev, {len(vhod['constraints']['zetev']['pari'])} parov žetve)")


META_HR = (
    "PACKAGE_ID", "EDITION_NAME", "STATUS", "SEGMENT_REF", "FROM_NAME", "FROM_EMAIL",
    "REPLY_TO", "FOOTER_REF", "GREETING", "SIGNOFF_PHRASE", "SIGNOFF_NAME",
)


def _razdeli(besedilo):
    return [p.strip() for p in (besedilo or "").split("\n") if p.strip()]


def _vrstica(besedilo):
    return " ".join(_razdeli(besedilo))


def _meta_hr(meta):
    if not isinstance(meta, dict):
        raise ValueError("prevod/hr-meta.json ni objekt s ključi META za HR")
    manjka = [k for k in META_HR if k not in meta or (k != "FOOTER_REF" and not str(meta[k] or "").strip())]
    if manjka:
        raise ManjkaKorak(f"korak 4: prevod/hr-meta.json nima {', '.join(manjka)}")


def sestavi_editions(stanje: dict, bloki: list, meta: dict) -> dict:
    _meta_hr(meta)
    si = _si(stanje)
    besedila = {b["id"]: b["text"] for b in bloki}
    nacini = ((stanje.get("_run") or {}).get("gradivo_odlocitve") or {}).get("jeziki", {}).get("hr") or {}
    dogodki = meta.get("dogodki") or {}
    ed_bloki = []
    for n, blok in enumerate(si["blocks"], 1):
        bid = blok["block_id"]
        url = str((nacini.get(bid) or {}).get("url") or "").strip() or blok["cta"]["url"]
        b = {
            "id": bid, "type": blok["type"], "img_file": "", "img_alt": "",
            "title": _vrstica(besedila[f"B{n}_TITLE"]),
            "body": _razdeli(besedila[f"B{n}_BODY"]),
            "bullets": _razdeli(besedila.get(f"B{n}_BULLETS", "")),
            "cta_label": _vrstica(besedila[f"B{n}_CTA"]),
            "cta_url": url,
        }
        if blok.get("event"):
            ura = str((dogodki.get(bid) or {}).get("EVENT_TIME") or "").strip()
            if not ura:
                raise ManjkaKorak(f"korak 4: prevod/hr-meta.json nima dogodki.{bid}.EVENT_TIME")
            b["event"] = [["EVENT_DATE", blok["event"]["date"]], ["EVENT_TIME", ura],
                          ["EVENT_DURATION_MIN", str(blok["event"]["duration_min"])]]
        ed_bloki.append(b)
    glava = [["LANGUAGE", "hr"], ["SUBJECT", _vrstica(besedila["SUBJECT"])],
             ["PREHEADER", _vrstica(besedila["PREHEADER"])]]
    glava += [[k, str(meta[k] or "")] for k in META_HR if k not in ("SIGNOFF_PHRASE", "SIGNOFF_NAME")]
    return {"hr": {
        "meta": glava,
        "hook_archetype": si["hook"]["archetype"],
        "hook": _razdeli(besedila["HOOK"]),
        "blocks": ed_bloki,
        "closing_type": si["closing"]["type"],
        "closing": _razdeli(besedila["CLOSING"]),
        "signoff_phrase": meta["SIGNOFF_PHRASE"],
        "signoff_name": meta["SIGNOFF_NAME"],
        "ps": _vrstica(besedila.get("PS", "")),
    }}


def _izdaja(pot, pot_izida, execution_id):
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    vhod = _beri(pot.parent / "prevod" / "hr-sol-vhod.json", "korak 4 (poženi hr_sol.py vhod)")
    izid = razpakiraj(json.loads(Path(pot_izida).read_text(encoding="utf-8")))
    opozorila = preveri_izid(izid, vhod)
    meta = _beri(pot.parent / "prevod" / "hr-meta.json", "korak 4 (zapiši prevod/hr-meta.json)")
    editions = sestavi_editions(stanje, izid["blocks"], meta)
    try:
        izdaja_v_besedilo(izdaja_iz_editions("hr", editions["hr"]))
    except NapakaOznak as napaka:
        raise NapakaIzida(f"HR besedilo: {napaka}")
    nova = vpisi(stanje, editions)
    pregled = izid.get("pregled") or {}
    nova.setdefault("_run", {})["prevod_hr"] = {
        "izid": izid["izid"],
        "krogi": izid.get("krogi"),
        "score": pregled.get("score"),
        "verdict": pregled.get("verdict"),
        "review_reasons": izid.get("review_reasons") or [],
        "nereseno": [i for i in pregled.get("issues") or [] if i.get("blocking") is True],
        "execution_id": str(execution_id),
    }
    _zapisi(pot.parent / "prevod" / "hr-editions.json", editions)
    _zapisi(pot, nova)
    for o in opozorila:
        print(f"OPOZORILO: {o}")
    print(f"Zapisana HR izdaja (izid {izid['izid']}, krogi {izid.get('krogi')}, ocena {pregled.get('score')})")


def main(argv) -> int:
    try:
        if len(argv) == 3 and argv[1] == "vhod":
            _vhod(Path(argv[2]))
        elif len(argv) == 5 and argv[1] == "izdaja":
            _izdaja(Path(argv[2]), argv[3], argv[4])
        else:
            print(__doc__)
            return 2
    except ManjkaKorak as napaka:
        print(f"MANJKA: {napaka}")
        return 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError, NapakaPreslikave) as napaka:
        print(f"NAPAKA: {napaka}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
