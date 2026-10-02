#!/usr/bin/env python3
"""Sestavi vhod prevajalca za en jezik novičnika in žetev zapiše kot sprejete popravke.

Uporaba: python3 prevod_vhod.py <state.json> <hr|en>

Bere iz mape teka (mapa state.json):
  prevod/zetev.json                     odgovor get_data_table_rows nad CF-Zetev ({"rows": [...], "count": N})
  prevod/viri/<jezik>-<block_id>.txt    referenca (transkreacija) ali vir (lokalni_vir) bloka
Piše:
  prevod/<jezik>-vhod.json
  transcreation-check/<jezik>-round-zetev.json   oblika, ki jo bere preveri_iznicenje.py

Exit 0 = zapisano. Exit 1 = manjka korak (izpis ga imenuje). Exit 2 = napaka vhoda.
"""
import json
import sys
from pathlib import Path

from izdaja_besedilo import izdaja_v_besedilo

JEZIKI = ("hr", "en")
NACINI = ("transkreacija", "lokalni_vir")
PRAVILA = [
    "vendor/frodx-newsletter/SKILL.md, koraka 4 in 5",
    "vendor/frodx-newsletter/references/playbook.md, razdelek Transkreacija",
    "vendor/frodx-newsletter/references/self-eval-rubric.md, vrata 6",
]


class ManjkaKorak(ValueError):
    pass


def _si(stanje):
    for izdaja in stanje.get("editions") or []:
        if izdaja.get("language") == "si":
            return izdaja
    raise ManjkaKorak("korak 2: v state.json ni SI izdaje")


def _zetev(mapa, jezik):
    pot = mapa / "prevod" / "zetev.json"
    if not pot.is_file():
        raise ManjkaKorak("korak 4: prevod/zetev.json manjka - preberi CF-Zetev z get_data_table_rows")
    vrstice = json.loads(pot.read_text(encoding="utf-8"))
    stevilo = None
    if isinstance(vrstice, dict):
        stevilo = vrstice.get("count")
        vrstice = vrstice["rows"] if "rows" in vrstice else vrstice.get("data")
    if not isinstance(vrstice, list):
        raise ValueError("prevod/zetev.json: ni seznam vrstic ne objekt s poljem rows")
    if isinstance(stevilo, int) and not isinstance(stevilo, bool) and stevilo > len(vrstice):
        raise ManjkaKorak(
            f"korak 4: prevod/zetev.json ima {len(vrstice)} od {stevilo} vrstic CF-Zetev - preberi vse strani (limit 100, skip)"
        )
    izid, videno = [], set()
    for v in vrstice:
        if not isinstance(v, dict) or v.get("jezik") != jezik:
            continue
        prej, potem = str(v.get("prej") or "").strip(), str(v.get("potem") or "").strip()
        if not prej or not potem or (prej, potem) in videno:
            continue
        videno.add((prej, potem))
        izid.append({"prej": prej, "potem": potem, "razlog": str(v.get("razlog") or "").strip()})
    return izid


def _blok(blok, odlocitev, jezik, mapa):
    bid = blok["block_id"]
    if not isinstance(odlocitev, dict) or odlocitev.get("nacin") not in NACINI:
        raise ManjkaKorak(f"korak 1: za {bid} ({jezik}) ni načina transkreacija ali lokalni_vir")
    url = str(odlocitev.get("url") or "").strip()
    pot = mapa / "prevod" / "viri" / f"{jezik}-{bid}.txt"
    besedilo = pot.read_text(encoding="utf-8").strip() if pot.is_file() else ""
    if odlocitev["nacin"] == "lokalni_vir" and not besedilo:
        raise ManjkaKorak(f"korak 4: {bid} ({jezik}) je lokalni_vir, vir {pot.name} manjka ali je prazen")
    if url and not besedilo:
        raise ManjkaKorak(f"korak 4: {bid} ({jezik}) ima referenco {url}, datoteka {pot.name} manjka ali je prazna")
    kljuc = "vir" if odlocitev["nacin"] == "lokalni_vir" else "referenca"
    return {"block_id": bid, "type": blok["type"], "nacin": odlocitev["nacin"], "url": url, kljuc: besedilo}


def sestavi(stanje: dict, jezik: str, mapa: Path) -> tuple:
    run = stanje.get("_run") or {}
    if not (run.get("approvals") or {}).get("step3"):
        raise ManjkaKorak("korak 3: Igor še ni potrdil SI izdaje (_run.approvals.step3)")
    si = _si(stanje)
    nacini = ((run.get("gradivo_odlocitve") or {}).get("jeziki") or {}).get(jezik)
    if not isinstance(nacini, dict):
        raise ManjkaKorak(f"korak 1: _run.gradivo_odlocitve.jeziki.{jezik} manjka")
    bloki = [_blok(b, nacini.get(b["block_id"]), jezik, mapa) for b in si["blocks"]]
    zetev = _zetev(mapa, jezik)
    vhod = {"jezik": jezik, "si": izdaja_v_besedilo(si), "bloki": bloki, "zetev": zetev, "pravila": PRAVILA}
    sprejete = {
        "round": "zetev",
        "accepted": [{"navedek": z["prej"], "popravek": z["potem"], "razlog": z["razlog"]} for z in zetev],
    }
    return vhod, sprejete


def _zapisi(pot, podatki):
    pot.parent.mkdir(parents=True, exist_ok=True)
    pot.write_text(json.dumps(podatki, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv) -> int:
    if len(argv) != 3 or argv[2] not in JEZIKI:
        print("Uporaba: prevod_vhod.py <state.json> <hr|en>")
        return 2
    pot, jezik = Path(argv[1]), argv[2]
    try:
        stanje = json.loads(pot.read_text(encoding="utf-8"))
        vhod, sprejete = sestavi(stanje, jezik, pot.parent)
    except ManjkaKorak as napaka:
        print(f"MANJKA: {napaka}")
        return 1
    except (OSError, ValueError, KeyError) as napaka:
        print(f"NAPAKA: {napaka}")
        return 2
    _zapisi(pot.parent / "prevod" / f"{jezik}-vhod.json", vhod)
    _zapisi(pot.parent / "transcreation-check" / f"{jezik}-round-zetev.json", sprejete)
    print(f"Zapisano: prevod/{jezik}-vhod.json ({len(vhod['bloki'])} blokov, {len(vhod['zetev'])} parov žetve)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
