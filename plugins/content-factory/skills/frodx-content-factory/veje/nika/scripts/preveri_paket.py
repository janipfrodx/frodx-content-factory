#!/usr/bin/env python3
"""Preverba paketa Nikine zgodbe (nika_story v1.1) pred oddajo.

Uporaba: python3 preveri_paket.py <state.json> [--faza niki|objava] [--telo <pot>]

Iz state.json odstrani _run in preveri telo. Kršitve izpiše s pristojnim
korakom in vrne exit 1. Na blog_md požene vendorirani check.py: njegove
napake so kršitve, opozorila ostanejo opozorila. linkedin_text je kratka
objava (1-4 vrstice, brez povezave in naslova), preverja jo kratka_objava.
Ocena pod 9,0 je opozorilo, ker je Igor zgodbo z njo že potrdil na gate-u
koraka 3.

Faza niki (privzeta) preveri slovensko zgodbo za Nikin pregled. Faza objava
doda prevode (EN, HR), sluge vseh treh jezikov, meta podatke (kampanja, oznake,
naslovnice) proti hubspot-taxonomy.md in urnik objave.
Z --telo zapiše telo za oddajo, a samo, kadar kršitev ni; če zapis spodleti,
vrne exit 2.
"""
import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

PISEC = Path(__file__).resolve().parents[1] / "vendor" / "nika-update-writer"
CHECK = PISEC / "scripts" / "check.py"
VERTIKALE = PISEC / "references" / "vertikale.md"

TIP = "nika_story"
VERZIJA = "1.1"
POLJA_ZGODBE = ("title", "blog_md", "linkedin_text", "meta_description")
STATUSI = ("beta", "scheduled", "live")
IZVORI = ("nacelo", "igor", "skill")
KATEGORIJE = ("nova", "obstojeci", "priporocilo")
VIRI = ("knowledge.hubspot.com", "hubspot.com", "www.hubspot.com")
RUN_SLUG = re.compile(r"^[a-z0-9-]{3,120}$")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+){2,5}$")
SLUG_MAX = 60
DATUM = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL = re.compile(r"https?://[^\s)\]]+")
OZNAKA = re.compile(r"\[PREVERI[^\]]*\]")
# check.py vzame samo del za to ločilo (story_part); del pred njim ostane nepreverjen.
LOCILO = "\n---\n"
DOLGI_POMISLJAJ = "\u2014"
PRAG = 9.0
FAZE = ("niki", "objava")
TAKSONOMIJA = Path(__file__).resolve().parents[2] / "kolumna" / "publishing-meta" / "references" / "hubspot-taxonomy.md"
JEZIKI_PREVODA = ("en", "hr")
ISO_Z_ZAMIKOM = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?[+-]\d{2}:\d{2}$")
LINKEDIN_URA = "07:30"
CASOVNI_PAS = "Europe/Ljubljana"


def _prazno(vrednost):
    return not isinstance(vrednost, str) or not vrednost.strip()


def _vir_ok(url):
    if not isinstance(url, str):
        return False
    deli = urlparse(url)
    return deli.scheme == "https" and deli.netloc in VIRI


def _nizi(obj, pot=""):
    if isinstance(obj, str):
        yield pot, obj
    elif isinstance(obj, dict):
        for kljuc, vrednost in obj.items():
            yield from _nizi(vrednost, f"{pot}.{kljuc}" if pot else kljuc)
    elif isinstance(obj, list):
        for i, vrednost in enumerate(obj):
            yield from _nizi(vrednost, f"{pot}[{i}]")


def dejavnosti():
    prvi_razdelek = VERTIKALE.read_text(encoding="utf-8").split("\n## ")[0]
    imena = [v.split("|")[1].strip() for v in prvi_razdelek.splitlines() if v.startswith("| ")]
    return [ime for ime in imena if ime != "Dejavnost"]


def _check(besedilo, nacin):
    with tempfile.TemporaryDirectory() as mapa:
        pot = Path(mapa) / "zgodba.md"
        pot.write_text(besedilo, encoding="utf-8")
        izid = subprocess.run(
            [sys.executable, str(CHECK), str(pot), f"--{nacin}"],
            capture_output=True, text=True, encoding="utf-8",
        )
    vrstice = izid.stdout.splitlines()
    napake = [v[len("NAPAKA: "):] for v in vrstice if v.startswith("NAPAKA: ")]
    opozorila = [v[len("opozorilo: "):] for v in vrstice if v.startswith("opozorilo: ")]
    if izid.returncode != 0 and not napake:
        napake.append(f"check.py ni tekel (exit {izid.returncode}): {izid.stderr.strip()[:200]}")
    return napake, opozorila


def kratka_objava(besedilo):
    krsitve = []
    vrstice = [v for v in besedilo.splitlines() if v.strip()]
    if not 1 <= len(vrstice) <= 4:
        krsitve.append(f"kratka objava ima {len(vrstice)} vrstic, dovoljeno 1-4 vrstice")
    if URL.search(besedilo):
        krsitve.append("povezava gre v prvi komentar, ne v objavo")
    if any(v.lstrip().startswith("#") for v in vrstice):
        krsitve.append("brez naslova v objavi")
    return krsitve


def zamik_ljubljane_ok(iso):
    """Ali je zamik v ISO času tisti, ki ga ima Europe/Ljubljana v tistem trenutku."""
    cas = dt.datetime.fromisoformat(iso)
    return cas.utcoffset() == cas.astimezone(ZoneInfo(CASOVNI_PAS)).utcoffset()


def rubrika_iz_taksonomije(pot=TAKSONOMIJA):
    """Vrstice, ki se začnejo z `| nika |`: kampanja (4 stolpci) in oznake (5 stolpcev)."""
    izid = {"campaign_name": "", "campaign_guid": "", "tags": {"sl": "", "en": "", "hr": ""}}
    for vrstica in Path(pot).read_text(encoding="utf-8").splitlines():
        celice = [c.strip() for c in vrstica.strip().strip("|").split("|")]
        if not vrstica.startswith("|") or celice[0] != "nika":
            continue
        if len(celice) == 4 and celice[1] == "kampanja":
            izid["campaign_name"], izid["campaign_guid"] = celice[2], celice[3]
        elif len(celice) == 5 and celice[1] in izid["tags"]:
            izid["tags"][celice[1]] = celice[2]
    return izid


def _preveri_slug(slug, pot, krsitve):
    if _prazno(slug):
        krsitve.append(f"{pot}: manjka (korak 8)")
        return
    if not SLUG.match(slug):
        krsitve.append(f"{pot}: 3-6 besed iz malih črk a-z in števk, ločenih z enim vezajem, brez šumnikov (korak 8)")
    if len(slug) > SLUG_MAX:
        krsitve.append(f"{pot}: {len(slug)} znakov, največ {SLUG_MAX} (korak 8)")


def _preveri_objavo(telo, krsitve, rubrika):
    zgodba = telo.get("story") if isinstance(telo.get("story"), dict) else {}
    _preveri_slug(zgodba.get("slug"), "story.slug", krsitve)
    jeziki = telo.get("languages") if isinstance(telo.get("languages"), dict) else {}
    for j in JEZIKI_PREVODA:
        jezik = jeziki.get(j) if isinstance(jeziki.get(j), dict) else {}
        polja = ("title", "blog_md", "meta_description") + (("linkedin_text",) if j == "en" else ())
        for polje in polja:
            vrednost = jezik.get(polje)
            if _prazno(vrednost):
                krsitve.append(f"languages.{j}.{polje}: manjka (korak 7)")
            elif OZNAKA.search(vrednost):
                krsitve.append(f"languages.{j}.{polje}: odprta oznaka [PREVERI (korak 7)")
        _preveri_slug(jezik.get("slug"), f"languages.{j}.slug", krsitve)
        meta_opis = jezik.get("meta_description")
        if not _prazno(meta_opis) and len(meta_opis) > 160:
            krsitve.append(f"languages.{j}.meta_description: {len(meta_opis)} znakov, največ 160 (korak 7)")
        if j == "en" and not _prazno(jezik.get("linkedin_text")):
            krsitve += [f"languages.en.linkedin_text: {k} (korak 7)" for k in kratka_objava(jezik["linkedin_text"])]

    meta = telo.get("meta") if isinstance(telo.get("meta"), dict) else {}
    pricakovano = rubrika()
    if not pricakovano["campaign_guid"] or not all(pricakovano["tags"].values()):
        krsitve.append("meta: kampanja ali oznake rubrike še niso v hubspot-taxonomy.md (H2, H3)")
    else:
        for polje in ("campaign_name", "campaign_guid"):
            if meta.get(polje) != pricakovano[polje]:
                krsitve.append(f"meta.{polje}: ne ustreza hubspot-taxonomy.md (korak 8)")
        oznake = meta.get("tags") if isinstance(meta.get("tags"), dict) else {}
        for j, tag_id in pricakovano["tags"].items():
            if oznake.get(j) != tag_id:
                krsitve.append(f"meta.tags.{j}: ne ustreza hubspot-taxonomy.md (korak 8)")
    naslovnice = meta.get("covers") if isinstance(meta.get("covers"), dict) else {}
    for j in ("sl", "en", "hr"):
        n = naslovnice.get(j) if isinstance(naslovnice.get(j), dict) else {}
        if not isinstance(n.get("url"), str) or not n["url"].startswith("https://") or _prazno(n.get("alt")):
            krsitve.append(f"meta.covers.{j}: manjka https URL ali alt opis (korak 8)")

    urnik = telo.get("schedule") if isinstance(telo.get("schedule"), dict) else {}
    objava, li = urnik.get("publish_at"), urnik.get("linkedin_date")
    if not isinstance(objava, str) or not ISO_Z_ZAMIKOM.match(objava):
        krsitve.append("schedule.publish_at: ISO čas z zamikom, npr. 2026-10-20T07:00:00+02:00 (korak 9)")
        return
    try:
        cas = dt.datetime.fromisoformat(objava)
    except ValueError:
        krsitve.append("schedule.publish_at: neveljaven datum ali čas (korak 9)")
        return
    if not zamik_ljubljane_ok(objava):
        krsitve.append(f"schedule.publish_at: zamik ne ustreza {CASOVNI_PAS} (poleti +02:00, pozimi +01:00) (korak 9)")
    if cas <= dt.datetime.now(dt.timezone.utc):
        krsitve.append("schedule.publish_at: mora biti v prihodnosti (korak 9)")
    if not isinstance(li, str) or not DATUM.match(li):
        krsitve.append("schedule.linkedin_date: YYYY-MM-DD (korak 9)")
    elif li < objava[:10]:
        krsitve.append("schedule: LinkedIn ne sme iti pred blogom (korak 9)")
    elif li == objava[:10] and objava[11:16] > LINKEDIN_URA:
        krsitve.append("schedule: LinkedIn teče ob 7.30; na dan bloga mora biti blog objavljen do 7.30 (korak 9)")


def _preveri_zgodbo(zgodba, krsitve, opozorila):
    for polje in POLJA_ZGODBE:
        if _prazno(zgodba.get(polje)):
            krsitve.append(f"story.{polje}: manjka (korak 3)")
    alt = zgodba.get("alt_titles")
    if not isinstance(alt, list) or len(alt) != 2 or any(_prazno(x) for x in alt):
        krsitve.append("story.alt_titles: natanko dva neprazna alternativna naslova (korak 3)")
    meta = zgodba.get("meta_description")
    if not _prazno(meta) and not 140 <= len(meta) <= 160:
        krsitve.append(f"story.meta_description: {len(meta)} znakov, dovoljeno 140-160 (korak 3)")
    for polje, nacin in (("blog_md", "blog"),):
        besedilo = zgodba.get(polje)
        if _prazno(besedilo):
            continue
        if LOCILO in besedilo:
            krsitve.append(f"story.{polje}: vrstica --- prereže besedilo, check.py bi preveril samo del za njo (korak 3)")
            continue
        napake, opoz = _check(besedilo, nacin)
        krsitve += [f"story.{polje}: check.py --{nacin}: {n} (korak 3)" for n in napake]
        opozorila += [f"story.{polje}: {o}" for o in opoz]
    objava = zgodba.get("linkedin_text")
    if not _prazno(objava):
        krsitve += [f"story.linkedin_text: {k} (korak 3)" for k in kratka_objava(objava)]


def _preveri_vir(vir, krsitve):
    if _prazno(vir.get("update_title")):
        krsitve.append("source.update_title: manjka naslov novosti iz maila (korak 1)")
    if vir.get("status") not in STATUSI:
        krsitve.append(f"source.status: mora biti eden od {', '.join(STATUSI)} (korak 1)")
    datum = vir.get("mail_date")
    if not (datum == "" or (isinstance(datum, str) and DATUM.match(datum))):
        krsitve.append("source.mail_date: YYYY-MM-DD ali prazno, če je mail prilepljen brez datuma (korak 1)")
    kb = vir.get("kb_urls")
    if not isinstance(kb, list) or not kb or not all(_vir_ok(u) for u in kb):
        krsitve.append("source.kb_urls: brez članka na knowledge.hubspot.com ali hubspot.com ni zgodbe (korak 2)")


def _preveri_trditve(trditve, krsitve):
    if not isinstance(trditve, list) or not trditve:
        krsitve.append("claims: manjka seznam trditev (korak 3)")
        return
    for i, t in enumerate(trditve):
        p = f"claims[{i}]"
        if not isinstance(t, dict) or _prazno(t.get("text")):
            krsitve.append(f"{p}: trditev brez besedila (korak 3)")
            continue
        if t.get("category") not in KATEGORIJE:
            krsitve.append(f"{p}: nerazvrščena trditev ustavi paket, kategorija mora biti {', '.join(KATEGORIJE)} (korak 3)")
            continue
        if t["category"] == "nova":
            if not _vir_ok(t.get("url")):
                krsitve.append(f"{p}: nova zmožnost brez povezave na knowledge.hubspot.com ali hubspot.com (korak 2)")
            if _prazno(t.get("quote")):
                krsitve.append(f"{p}: nova zmožnost brez navedka iz vira (korak 2)")


def preveri(telo, faza="niki", rubrika=rubrika_iz_taksonomije):
    krsitve, opozorila = [], []
    if "_run" in telo:
        krsitve.append("_run: telo za oddajo ne nosi _run (korak 4)")
    if telo.get("type") != TIP or telo.get("version") != VERZIJA:
        krsitve.append(f"type/version: mora biti {TIP} {VERZIJA} (init_run.py)")
    if not isinstance(telo.get("run_slug"), str) or not RUN_SLUG.match(telo["run_slug"]):
        krsitve.append("run_slug: mora ustrezati ^[a-z0-9-]{3,120}$ (init_run.py)")

    zgodba = telo.get("story") if isinstance(telo.get("story"), dict) else {}
    _preveri_zgodbo(zgodba, krsitve, opozorila)
    _preveri_vir(telo.get("source") if isinstance(telo.get("source"), dict) else {}, krsitve)

    if telo.get("activity") not in dejavnosti():
        krsitve.append("activity: ime dejavnosti dobesedno iz prvega stolpca vertikale.md (korak 2)")
    if _prazno(telo.get("dilemma")):
        krsitve.append("dilemma: manjka (korak 2)")

    presoja = telo.get("judgment") if isinstance(telo.get("judgment"), dict) else {}
    if presoja.get("origin") not in IZVORI:
        krsitve.append(f"judgment.origin: mora biti eden od {', '.join(IZVORI)} (korak 3)")
    elif presoja["origin"] == "nacelo" and _prazno(presoja.get("principle")):
        krsitve.append("judgment.principle: presoja iz načela mora navesti načelo iz nacela.md (korak 3)")
    if _prazno(presoja.get("question")):
        krsitve.append("judgment.question: manjka vprašanje za Niko (korak 3)")

    _preveri_trditve(telo.get("claims"), krsitve)

    seznam = telo.get("preveri")
    if not isinstance(seznam, list) or any(not isinstance(p, dict) or _prazno(p.get("text")) or _prazno(p.get("where")) for p in seznam):
        krsitve.append("preveri: seznam objektov s text in where (korak 3)")
        seznam = []
    oznake = len({o for _, niz in _nizi(zgodba) for o in OZNAKA.findall(niz)})
    if oznake > len(seznam):
        krsitve.append(f"preveri: v besedilu je {oznake} oznak [PREVERI, v seznamu {len(seznam)}; brez vrstice v seznamu se oddaja Niki ustavi (korak 3)")

    for kljuc in ("warnings", "formulas"):
        if not isinstance(telo.get(kljuc), list):
            krsitve.append(f"{kljuc}: mora biti seznam (korak 3)")

    ocena = telo.get("score") if isinstance(telo.get("score"), dict) else {}
    skupaj = ocena.get("total")
    if isinstance(skupaj, bool) or not isinstance(skupaj, (int, float)):
        krsitve.append("score.total: manjka ocena po rubriki (korak 3)")
    elif skupaj < PRAG:
        opozorila.append(f"ocena {skupaj} je pod pragom 9,0")

    for pot, niz in _nizi(telo):
        if DOLGI_POMISLJAJ in niz:
            krsitve.append(f"{pot}: dolgi pomišljaj (U+2014), uporabi razmaknjen vezaj (korak 3)")
    if faza == "objava":
        _preveri_objavo(telo, krsitve, rubrika)
    return krsitve, opozorila


UPORABA = "Uporaba: preveri_paket.py <state.json> [--faza niki|objava] [--telo <pot>]"


def _argumenti(argv):
    if len(argv) < 2 or argv[1].startswith("--"):
        return None
    faza, telo, i = "niki", None, 2
    while i < len(argv):
        if argv[i] not in ("--faza", "--telo") or i + 1 >= len(argv):
            return None
        if argv[i] == "--faza":
            faza = argv[i + 1]
        else:
            telo = argv[i + 1]
        i += 2
    if faza not in FAZE:
        return None
    return argv[1], faza, telo


def main(argv) -> int:
    razclenjeno = _argumenti(argv)
    if razclenjeno is None:
        print(UPORABA)
        return 1
    vhod, faza, cilj_pot = razclenjeno
    try:
        stanje = json.loads(Path(vhod).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as napaka:
        print(f"state.json ni mogoče prebrati: {napaka}")
        return 1
    if not isinstance(stanje, dict):
        print("state.json ni objekt")
        return 1
    telo = {k: v for k, v in stanje.items() if k != "_run"}
    krsitve, opozorila = preveri(telo, faza)
    for besedilo in opozorila:
        print(f"Opozorilo: {besedilo}")
    if krsitve:
        for besedilo in krsitve:
            print(f"KRŠITEV: {besedilo}")
        return 1
    if cilj_pot:
        cilj = Path(cilj_pot)
        try:
            cilj.parent.mkdir(parents=True, exist_ok=True)
            cilj.write_text(json.dumps(telo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as napaka:
            print(f"NAPAKA: telo ni bilo mogoče zapisati: {napaka}")
            return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
