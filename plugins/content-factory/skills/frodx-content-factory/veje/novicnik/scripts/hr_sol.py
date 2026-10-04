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
import sys
from pathlib import Path

from prevod_vhod import ManjkaKorak

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


def main(argv) -> int:
    if len(argv) != 3 or argv[1] != "vhod":
        print(__doc__)
        return 2
    try:
        _vhod(Path(argv[2]))
    except ManjkaKorak as napaka:
        print(f"MANJKA: {napaka}")
        return 1
    except (OSError, ValueError, KeyError) as napaka:
        print(f"NAPAKA: {napaka}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
