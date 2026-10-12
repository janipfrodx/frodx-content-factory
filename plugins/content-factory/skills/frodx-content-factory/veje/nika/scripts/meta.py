#!/usr/bin/env python3
"""Vpiše kampanjo, oznake rubrike in naslovnice v paket Nikine zgodbe.

Uporaba: python3 meta.py <state.json>

Vir je hubspot-taxonomy.md (razdelek Rubrika HubSpot z Niko) in
assets/naslovnice.json. Česar tam ni, ne izmišlja: izpiše človekov korak
in vrne exit 1.
"""
import json
import sys
from pathlib import Path

NIKA = Path(__file__).resolve().parents[1]
import importlib.util  # noqa: E402

# Po poti, ne z `import preveri_paket`: novičnik ima modul z istim imenom (tests padejo ob zbiranju).
_spec = importlib.util.spec_from_file_location("preveri_paket_nika_meta", NIKA / "scripts" / "preveri_paket.py")
_pp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pp)
rubrika_iz_taksonomije = _pp.rubrika_iz_taksonomije

NASLOVNICE = NIKA / "assets" / "naslovnice.json"


def izpolni(stanje, rubrika, naslovnice):
    manjka = []
    if not rubrika["campaign_guid"]:
        manjka.append("kampanja rubrike ni v hubspot-taxonomy.md (H3)")
    for j, tag_id in rubrika["tags"].items():
        if not tag_id:
            manjka.append(f"oznaka rubrike za {j} ni v hubspot-taxonomy.md (H2)")
    for j, n in naslovnice.items():
        if not n.get("url"):
            manjka.append(f"naslovnica {j} nima URL-ja v HubSpot Files (H4)")
    stanje["meta"] = {
        "campaign_name": rubrika["campaign_name"],
        "campaign_guid": rubrika["campaign_guid"],
        "tags": dict(rubrika["tags"]),
        "covers": {j: {"url": n.get("url", ""), "alt": n["alt"]} for j, n in naslovnice.items()},
    }
    return manjka


def main(argv):
    if len(argv) != 2:
        print("Uporaba: meta.py <state.json>")
        return 1
    pot = Path(argv[1])
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    manjka = izpolni(stanje, rubrika_iz_taksonomije(), json.loads(NASLOVNICE.read_text(encoding="utf-8")))
    pot.write_text(json.dumps(stanje, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for m in manjka:
        print(f"MANJKA: {m}")
    print("OK" if not manjka else "")
    return 1 if manjka else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
