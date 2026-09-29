#!/usr/bin/env python3
"""Preveri, ali je audit transkreacije izničil sprejet popravek preverbe GPT + Gemini.

Popravek je izničen, če navedka sprejete najdbe v besedilu pred auditom ni, v besedilu po
auditu pa je. Primerja se brez razlike med velikimi in malimi črkami in s strnjenimi presledki.

Exit 0 = noben popravek ni izničen. Exit 1 = vsaj eden je. Exit 2 = napaka vhoda.

Uporaba: python3 preveri_iznicenje.py <mapa transcreation-check> <hr|en> <pred.txt> <po.txt>
"""
import json
import re
import sys
from pathlib import Path

JEZIKI = ("hr", "en")
_PRESLEDKI = re.compile(r"\s+")


def _normaliziraj(besedilo: str) -> str:
    return _PRESLEDKI.sub(" ", besedilo).strip().casefold()


def nalozi_sprejete(mapa: Path, jezik: str) -> list:
    mapa = Path(mapa)
    if not mapa.is_dir():
        raise OSError(f"mapa {mapa} ne obstaja")
    sprejete = []
    for pot in sorted(mapa.glob(f"{jezik}-round-*.json")):
        podatki = json.loads(pot.read_text(encoding="utf-8"))
        accepted = podatki.get("accepted", [])
        if not isinstance(accepted, list):
            raise ValueError(f"{pot.name}: accepted ni seznam")
        for najdba in accepted:
            if isinstance(najdba, dict) and str(najdba.get("navedek", "")).strip():
                sprejete.append(najdba)
    return sprejete


def iznicene(sprejete: list, pred: str, po: str) -> list:
    pred_n, po_n = _normaliziraj(pred), _normaliziraj(po)
    izid = []
    for najdba in sprejete:
        navedek = _normaliziraj(str(najdba["navedek"]))
        if navedek not in pred_n and navedek in po_n:
            izid.append(najdba)
    return izid


def main(argv) -> int:
    if len(argv) != 5 or argv[2] not in JEZIKI:
        print("Uporaba: preveri_iznicenje.py <mapa transcreation-check> <hr|en> <pred.txt> <po.txt>")
        return 2
    try:
        sprejete = nalozi_sprejete(Path(argv[1]), argv[2])
        pred = Path(argv[3]).read_text(encoding="utf-8")
        po = Path(argv[4]).read_text(encoding="utf-8")
    except (OSError, ValueError) as napaka:
        print(f"NAPAKA: {napaka}")
        return 2
    izid = iznicene(sprejete, pred, po)
    for najdba in izid:
        print(f'IZNIČENO: "{najdba["navedek"]}" -> "{najdba.get("popravek", "")}" ({najdba.get("razlog", "")})')
    if izid:
        return 1
    print(f"OK: {len(sprejete)} sprejetih popravkov, noben ni izničen.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
