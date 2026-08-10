#!/usr/bin/env python3
"""Ustvari mapo teka in začetni state.json.

Uporaba: python3 init_run.py "<naslov teme>" <ciljna-mapa>
Izpiše pot do ustvarjenega state.json. Exit 1, če tek že obstaja.
"""
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

JEZIKI = ("sl", "en", "hr")


def slugify(naslov: str) -> str:
    razstavljeno = unicodedata.normalize("NFKD", naslov)
    brez_naglasov = "".join(z for z in razstavljeno if not unicodedata.combining(z))
    brez_naglasov = brez_naglasov.replace("đ", "d").replace("Đ", "D")
    nizko = brez_naglasov.lower()
    z_vezaji = re.sub(r"[^a-z0-9]+", "-", nizko)
    return z_vezaji.strip("-")


def _prazen_jezik(koda: str) -> dict:
    return {
        "language_code": koda,
        "content": "",
        "slug": "",
        "seo_title": "",
        "meta_description": "",
        "topic_cluster": "",
        "campaign_name": "",
        "tag_id": "",
        "tag_name": "",
        "tag_slug": "",
        "featured_image_alt": "",
    }


def zgradi_stanje(tema: str, slug: str, cas: str) -> dict:
    return {
        "meta": {"title": tema, "exported_at": cas, "version": "1.1"},
        "universal": {"slug": slug},
        "social_posts": [],
        "languages": {koda: _prazen_jezik(koda) for koda in JEZIKI},
        "_run": {
            "slug": slug,
            "step": 1,
            "status": "awaiting_topic",
            "topic_source": {},
            "brief": {},
            "approvals": {},
            "critique_rounds": 0,
            "skill_versions": {},
        },
    }


def main() -> int:
    if len(sys.argv) != 3:
        print('Uporaba: init_run.py "<naslov teme>" <ciljna-mapa>')
        return 1

    tema = sys.argv[1].strip()
    if not tema:
        print("Naslov teme je prazen.")
        return 1

    slug = slugify(tema)
    if not slug:
        print(f"Iz naslova '{tema}' ni bilo mogoce sestaviti sluga.")
        return 1

    danes = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mapa = Path(sys.argv[2]) / f"{danes}-{slug}"
    if mapa.exists():
        print(f"Tek {mapa} ze obstaja. Nadaljuj ta tek ali izberi drugo temo.")
        return 1

    (mapa / "critique").mkdir(parents=True)
    (mapa / "images").mkdir()

    cas = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    pot = mapa / "state.json"
    pot.write_text(
        json.dumps(zgradi_stanje(tema, slug, cas), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(pot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
