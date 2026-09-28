#!/usr/bin/env python3
"""Ustvari mapo teka in začetni state.json.

Uporaba: python3 init_run.py [--veja kolumna|novicnik] "<naslov teme>" <ciljna-mapa>
Brez --veja nastane tek kolumne. Izpiše pot do ustvarjenega state.json.
Exit 1, če tek že obstaja.
"""
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

JEZIKI = ("sl", "en", "hr")
SLUG_MAX = 80
VEJE = ("kolumna", "novicnik")


def slugify(naslov: str) -> str:
    razstavljeno = unicodedata.normalize("NFKD", naslov)
    brez_naglasov = "".join(z for z in razstavljeno if not unicodedata.combining(z))
    brez_naglasov = brez_naglasov.replace("đ", "d").replace("Đ", "D")
    nizko = brez_naglasov.lower()
    z_vezaji = re.sub(r"[^a-z0-9]+", "-", nizko)
    return z_vezaji.strip("-")


def _okrajsaj_slug(slug: str, najvecja_dolzina: int = SLUG_MAX) -> str:
    """Okrajša slug na mejo besede, če je daljši od najvecja_dolzina.

    Reže na zadnjem vezaju znotraj meje, da beseda ostane cela. Če znotraj
    meje ni nobenega vezaja, reže trdo na najvecja_dolzina.
    """
    if len(slug) <= najvecja_dolzina:
        return slug
    odrezan = slug[:najvecja_dolzina]
    zadnji_vezaj = odrezan.rfind("-")
    if zadnji_vezaj != -1:
        odrezan = odrezan[:zadnji_vezaj]
    return odrezan.strip("-")


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
        "meta": {"title": tema, "exported_at": cas, "version": "1.2"},
        "universal": {"slug": slug},
        "social_posts": [],
        "languages": {koda: _prazen_jezik(koda) for koda in JEZIKI},
        "_run": {
            "veja": "kolumna",
            # Tek nosi datum, ker je run_slug v aplikaciji unique in nosi
            # idempotenco. Brez datuma bi ista tema drugi dan dobila 409
            # in Igor povezavo na star osnutek.
            "slug": f"{cas[:10]}-{slug}",
            "step": 1,
            "status": "awaiting_topic",
            "topic_source": {},
            "brief": {},
            "approvals": {},
            "critique_rounds": 0,
            "open_tasks": [],
            "skill_versions": {},
        },
    }


def zgradi_stanje_novicnik(tema: str, slug: str, cas: str) -> dict:
    # Oblika telesa POST /api/drafts (tests/fixtures/newsletter_draft_body.json).
    # run_slug nosi datum iz istega razloga kot pri kolumni: v aplikaciji je unique.
    tek = f"{cas[:10]}-{slug}"
    return {
        "run_slug": tek,
        "editions": [],
        "_run": {
            "veja": "novicnik",
            "slug": tek,
            "tema": tema,
            "step": 0,
            "status": "awaiting_material",
            "gradivo": [],
            "tip_izdaje": "",
            "approvals": {},
            "critique_rounds": 0,
            "transcreation_check": {},
            "block_images": [],
            "open_tasks": [],
            "skill_versions": {},
        },
    }


def main() -> int:
    argumenti = sys.argv[1:]
    veja = "kolumna"
    if argumenti[:1] == ["--veja"]:
        if len(argumenti) < 2 or argumenti[1] not in VEJE:
            print(f"Neznana veja. Dovoljene: {', '.join(VEJE)}")
            return 1
        veja, argumenti = argumenti[1], argumenti[2:]

    if len(argumenti) != 2:
        print('Uporaba: init_run.py [--veja kolumna|novicnik] "<naslov teme>" <ciljna-mapa>')
        return 1

    tema = argumenti[0].strip()
    if not tema:
        print("Naslov teme je prazen.")
        return 1

    slug = slugify(tema)
    if not slug:
        print(f"Iz naslova '{tema}' ni bilo mogoce sestaviti sluga.")
        return 1
    slug = _okrajsaj_slug(slug)

    zdaj = datetime.now(timezone.utc)
    danes = zdaj.strftime("%Y-%m-%d")
    mapa = Path(argumenti[1]) / f"{danes}-{slug}"

    # mapa.mkdir() brez exist_ok je atomaren zahtevek: hkrati preverba IN
    # ustvarjanje, brez razmika med njima. FileExistsError (podrazred
    # OSError) mora stati pred splosnim OSError, sicer ga ta pogoltne.
    try:
        mapa.mkdir(parents=True)
    except FileExistsError:
        print(f"Tek {mapa} ze obstaja. Nadaljuj ta tek ali izberi drugo temo.")
        return 1
    except OSError as napaka:
        print(f"Ni bilo mogoce ustvariti mape teka {mapa}: {napaka}")
        return 1

    # Od tu naprej je mapa zagotovo nasa - ta zagon jo je pravkar ustvaril.
    # Ciscenje ob napaki je zato varno.
    try:
        (mapa / "critique").mkdir()
        (mapa / "images").mkdir()

        cas = zdaj.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        pot = mapa / "state.json"
        zgradi = zgradi_stanje if veja == "kolumna" else zgradi_stanje_novicnik
        pot.write_text(
            json.dumps(zgradi(tema, slug, cas), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as napaka:
        print(f"Priprava teka v {mapa} ni uspela: {napaka}")
        shutil.rmtree(mapa, ignore_errors=True)
        return 1

    print(pot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
