#!/usr/bin/env python3
"""Zavihek Nikine zgodbe (markdown iz Claude Docsa) → paket.

Uporaba: python3 iz_zavihka.py <zavihek.md> <state.json>

Prebere naslov, zgodbo za blog, LinkedIn in Nikino odločitev. Besedila
vpiše v story, odločitev in število spremenjenih povedi v _run.nika_pregled.
Exit 1, če manjka fiksni razdelek ali je odločitev neznana vrednost.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zavihek import KOMENTAR, RAZDELKI, SPUSTNI  # noqa: E402

VREDNOSTI = {
    "decision": {"potrdi": "approve", "zavrni": "reject"},
    "judgment_answer": {"da": "da", "ne": "ne", "drugače": "drugače", "drugace": "drugače"},
    "reason": {"presoja": "presoja", "dejstvo": "dejstvo", "novost": "novost", "slog": "slog"},
}
POLJE = dict(zip(SPUSTNI, VREDNOSTI))
POVED = re.compile(r"(?<=[.!?«])\s+")


def _razdelki(md):
    besedilo = md.replace("\r\n", "\n")
    mesta = []
    for ime in RAZDELKI:
        m = re.search(rf"^##\s+{re.escape(ime)}\s*$", besedilo, re.M)
        if not m:
            raise ValueError(f"manjka razdelek »{ime}«; Nika ga je morda preimenovala ali zbrisala")
        mesta.append((ime, m.start(), m.end()))
    if [m[1] for m in mesta] != sorted(m[1] for m in mesta):
        raise ValueError(f"razdelki niso v vrstnem redu {', '.join(RAZDELKI)}")
    izid = {}
    for i, (ime, _, konec) in enumerate(mesta):
        naslednji = mesta[i + 1][1] if i + 1 < len(mesta) else len(besedilo)
        izid[ime] = besedilo[konec:naslednji].strip("\n")
    glava = besedilo[: mesta[0][1]]
    naslov = re.search(r"^#\s+(.+?)\s*$", glava, re.M)
    if not naslov:
        raise ValueError("manjka naslov zgodbe v prvi vrstici (# ...)")
    return naslov.group(1), izid


def _vrednost(celica):
    return re.sub(r"[*_`\[\]]", "", celica).strip()


def _odlocitev(tabela):
    izid = {"decision": None, "judgment_answer": "", "reason": "", "comment": ""}
    for vrstica in tabela.splitlines():
        celice = [c.strip() for c in vrstica.strip().strip("|").split("|")]
        if len(celice) < 2:
            continue
        kljuc, odgovor = celice[0], _vrednost("|".join(celice[1:]))
        if kljuc == KOMENTAR:
            izid["comment"] = odgovor
            continue
        if kljuc not in POLJE or not odgovor:
            continue
        polje = POLJE[kljuc]
        normalno = VREDNOSTI[polje].get(odgovor.lower())
        if normalno is None:
            raise ValueError(f"»{odgovor}« ni dovoljena vrednost za »{kljuc}«; dovoljeno: {' / '.join(SPUSTNI[kljuc])}")
        izid[polje] = normalno
    return izid


def _povedi(besedilo):
    return [p.strip() for p in POVED.split(re.sub(r"\s+", " ", besedilo)) if p.strip()]


def spremenjene_povedi(staro, novo):
    """Zamenjana poved šteje enkrat; dodane in zbrisane štejejo vsaka zase."""
    stare, nove = set(_povedi(staro)), set(_povedi(novo))
    return max(len(nove - stare), len(stare - nove))


def preberi(md):
    naslov, r = _razdelki(md)
    return {
        "title": naslov,
        "blog_md": f"# {naslov}\n\n{r['Zgodba za blog']}",
        "linkedin_text": r["LinkedIn"],
        "odlocitev": _odlocitev(r["Nikina odločitev"]),
        "odprte": [v[6:] for v in r["Odprte oznake PREVERI"].splitlines() if v.startswith("- [ ] ")],
    }


def main(argv):
    if len(argv) != 3:
        print("Uporaba: iz_zavihka.py <zavihek.md> <state.json>")
        return 1
    pot = Path(argv[2])
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    try:
        izid = preberi(Path(argv[1]).read_text(encoding="utf-8"))
    except ValueError as napaka:
        print(f"NAPAKA: {napaka}")
        return 1
    if izid["odlocitev"]["decision"] is None:
        # Nika še ni končala: state.json ostane izvirnik, sicer bi naslednje branje štelo 0 sprememb.
        print(json.dumps({"decision": None, "odprte": izid["odprte"]}, ensure_ascii=False))
        return 0
    zgodba = stanje["story"]
    spremembe = spremenjene_povedi(zgodba["blog_md"], izid["blog_md"]) + spremenjene_povedi(zgodba["linkedin_text"], izid["linkedin_text"])
    zgodba.update(title=izid["title"], blog_md=izid["blog_md"], linkedin_text=izid["linkedin_text"])
    stanje.setdefault("_run", {})["nika_pregled"] = {**izid["odlocitev"], "spremenjene_povedi": spremembe, "odprte": izid["odprte"]}
    pot.write_text(json.dumps(stanje, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stanje["_run"]["nika_pregled"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
