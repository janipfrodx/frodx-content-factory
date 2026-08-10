#!/usr/bin/env python3
"""Binarni gate pred pošiljanjem paketa v aplikacijo.

Exit 0 = paket je pripravljen. Exit 1 = kršitev, napake na stdout.
Vzorec je namenoma enak Igorjevemu contract_check.py.

Uporaba: python3 validate_package.py <pot-do-state.json>
"""
import json
import re
import sys
from pathlib import Path

JEZIKI = ("sl", "en", "hr")
SEO_TITLE_MAX = 65
META_MIN = 140
META_MAX = 160
ALT_MAX = 160
EM_DASH = "\u2014"
PODPIS = "igor.pauletic@frodx.com"
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PREPOVEDANE = ("tu je trik", "here's the trick", "ovdje je trik")

_TU = Path(__file__).resolve()
_REPO = _TU.parents[5]
TAXONOMY = _REPO / "plugins" / "content-factory" / "skills" / "frodx-publishing-meta" / "references" / "hubspot-taxonomy.md"


def validate(pkg: dict, campaigns: dict, tags: dict) -> list:
    napake = []

    meta = pkg.get("meta") or {}
    if not str(meta.get("title", "")).strip():
        napake.append("meta.title je prazen")
    if meta.get("version") != "1.1":
        napake.append(f"meta.version mora biti '1.1', je '{meta.get('version')}'")
    if not str(meta.get("exported_at", "")).strip():
        napake.append("meta.exported_at je prazen")

    slug = str((pkg.get("universal") or {}).get("slug", "")).strip()
    if not SLUG.fullmatch(slug):
        napake.append(f"universal.slug ni veljaven slug: '{slug}'")

    objave = pkg.get("social_posts") or []
    if not objave:
        napake.append("social_posts je prazen - potrebna je vsaj ena objava")
    for i, objava in enumerate(objave):
        if not str(objava.get("text", "")).strip():
            napake.append(f"social_posts[{i}].text je prazen")

    kampanje_v_paketu = set()

    for jezik in JEZIKI:
        podatki = (pkg.get("languages") or {}).get(jezik)
        if not podatki:
            napake.append(f"languages.{jezik} manjka")
            continue

        vsebina = str(podatki.get("content", ""))
        if not vsebina.strip():
            napake.append(f"languages.{jezik}.content je prazen")
        else:
            if EM_DASH in vsebina:
                napake.append(f"languages.{jezik}.content vsebuje dolgi pomišljaj (U+2014)")
            nizka = vsebina.lower()
            for fraza in PREPOVEDANE:
                if fraza in nizka:
                    napake.append(f"languages.{jezik}.content vsebuje prepovedano frazo '{fraza}'")
            if PODPIS not in vsebina:
                napake.append(f"languages.{jezik}.content se ne zapre s podpisom {PODPIS}")

        naslov = str(podatki.get("seo_title", "")).strip()
        if not naslov:
            napake.append(f"languages.{jezik}.seo_title je prazen")
        elif len(naslov) > SEO_TITLE_MAX:
            napake.append(f"languages.{jezik}.seo_title ima {len(naslov)} znakov, dovoljenih {SEO_TITLE_MAX}")

        opis = str(podatki.get("meta_description", "")).strip()
        if not opis:
            napake.append(f"languages.{jezik}.meta_description je prazen")
        elif not (META_MIN <= len(opis) <= META_MAX):
            napake.append(f"languages.{jezik}.meta_description ima {len(opis)} znakov, dovoljeno {META_MIN}-{META_MAX}")

        jezikovni_slug = str(podatki.get("slug", "")).strip()
        if not SLUG.fullmatch(jezikovni_slug):
            napake.append(f"languages.{jezik}.slug ni veljaven slug: '{jezikovni_slug}'")

        if not str(podatki.get("topic_cluster", "")).strip():
            napake.append(f"languages.{jezik}.topic_cluster je prazen")

        alt = str(podatki.get("featured_image_alt", "")).strip()
        if not alt:
            napake.append(f"languages.{jezik}.featured_image_alt je prazen")
        elif len(alt) > ALT_MAX:
            napake.append(f"languages.{jezik}.featured_image_alt ima {len(alt)} znakov, dovoljenih {ALT_MAX}")

        kampanja = str(podatki.get("campaign_name", "")).strip()
        kampanje_v_paketu.add(kampanja)
        if kampanja not in campaigns:
            napake.append(f"languages.{jezik}.campaign_name '{kampanja}' ni na seznamu desetih kampanj")
        else:
            pricakovan = tags.get((kampanja, jezik))
            dejanski_id = str(podatki.get("tag_id", "")).strip()
            if pricakovan is None:
                if dejanski_id:
                    napake.append(
                        f"languages.{jezik}.tag_id je '{dejanski_id}', a taksonomija za ({kampanja}, {jezik}) taga nima - tagov se ne izmišlja"
                    )
            else:
                if dejanski_id != pricakovan["id"]:
                    napake.append(
                        f"languages.{jezik}.tag_id je '{dejanski_id}', pričakovan '{pricakovan['id']}'"
                    )
                if str(podatki.get("tag_name", "")).strip() != pricakovan["name"]:
                    napake.append(f"languages.{jezik}.tag_name se ne ujema s taksonomijo")
                if str(podatki.get("tag_slug", "")).strip() != pricakovan["slug"]:
                    napake.append(f"languages.{jezik}.tag_slug se ne ujema s taksonomijo")

    if len(kampanje_v_paketu) > 1:
        napake.append(f"campaign_name mora biti enak v vseh jezikih, najdene: {sorted(kampanje_v_paketu)}")

    return napake


def main() -> int:
    if len(sys.argv) != 2:
        print("Uporaba: validate_package.py <pot-do-state.json>")
        return 1

    sys.path.insert(0, str(_REPO))
    from tools.taxonomy import load_campaigns, load_tags

    pkg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    pkg.pop("_run", None)
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))

    if napake:
        print(f"Paket ni pripravljen. {len(napake)} kršitev:")
        for napaka in napake:
            print(f"  - {napaka}")
        return 1

    print("Paket je pripravljen za pošiljanje.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
