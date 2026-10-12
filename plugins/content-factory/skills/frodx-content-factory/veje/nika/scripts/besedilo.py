#!/usr/bin/env python3
"""Izpis in vpis blog besedila Nikine zgodbe po jeziku.

Uporaba:
  python3 besedilo.py izpis <state.json> <sl|en|hr>
  python3 besedilo.py vpis <state.json> <sl|en|hr> <datoteka>

sl je story.blog_md, en in hr sta languages.<jezik>.blog_md. Prva vrstica
besedila je `# <naslov>`; vpis jo prepiše tudi v naslov.
"""
import json
import sys
from pathlib import Path

JEZIKI = ("sl", "en", "hr")


def _rezina(stanje, jezik):
    if jezik not in JEZIKI:
        raise ValueError(f"jezik mora biti eden od {', '.join(JEZIKI)}")
    if jezik == "sl":
        return stanje.setdefault("story", {})
    return stanje.setdefault("languages", {}).setdefault(jezik, {})


def izpis(stanje, jezik):
    return _rezina(stanje, jezik).get("blog_md", "")


def vpis(stanje, jezik, besedilo):
    rezina = _rezina(stanje, jezik)
    prva = besedilo.lstrip().splitlines()[0] if besedilo.strip() else ""
    if not prva.startswith("# "):
        raise ValueError("prva vrstica mora biti `# <naslov>`")
    rezina["title"] = prva[2:].strip()
    rezina["blog_md"] = besedilo.strip()


def main(argv):
    if len(argv) < 4 or argv[1] not in ("izpis", "vpis") or (argv[1] == "vpis" and len(argv) != 5):
        print(__doc__.strip().splitlines()[2])
        return 1
    pot = Path(argv[2])
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    try:
        if argv[1] == "izpis":
            print(izpis(stanje, argv[3]))
            return 0
        vpis(stanje, argv[3], Path(argv[4]).read_text(encoding="utf-8"))
    except ValueError as napaka:
        print(f"NAPAKA: {napaka}")
        return 1
    pot.write_text(json.dumps(stanje, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
