#!/usr/bin/env python3
"""Preverba paketa Nikine zgodbe (nika_story v1.0) pred oddajo.

Uporaba: python3 preveri_paket.py <state.json> [--telo <pot>]

Iz state.json odstrani _run in preveri telo. Kršitve izpiše s pristojnim
korakom in vrne exit 1. Na blog_md in linkedin_text požene vendorirani
check.py: njegove napake so kršitve, opozorila ostanejo opozorila. Ocena pod
9,0 je opozorilo, ker je Igor zgodbo z njo že potrdil na gate-u koraka 3.
Z --telo zapiše telo za oddajo, a samo, kadar kršitev ni; če zapis spodleti,
vrne exit 2.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

PISEC = Path(__file__).resolve().parents[1] / "vendor" / "nika-update-writer"
CHECK = PISEC / "scripts" / "check.py"
VERTIKALE = PISEC / "references" / "vertikale.md"

TIP = "nika_story"
VERZIJA = "1.0"
POLJA_ZGODBE = ("title", "blog_md", "linkedin_text", "first_comment", "meta_description")
STATUSI = ("beta", "scheduled", "live")
IZVORI = ("nacelo", "igor", "skill")
KATEGORIJE = ("nova", "obstojeci", "priporocilo")
VIRI = ("knowledge.hubspot.com", "hubspot.com", "www.hubspot.com")
RUN_SLUG = re.compile(r"^[a-z0-9-]{3,120}$")
DATUM = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL = re.compile(r"https?://[^\s)\]]+")
OZNAKA = re.compile(r"\[PREVERI")
LOCILO = "\n---\n"
DOLGI_POMISLJAJ = "\u2014"
PRAG = 9.0


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
    prvi = zgodba.get("first_comment")
    if not _prazno(prvi) and not any(_vir_ok(u) for u in URL.findall(prvi)):
        krsitve.append("story.first_comment: nima povezave na knowledge.hubspot.com ali hubspot.com (korak 3)")
    for polje, nacin in (("blog_md", "blog"), ("linkedin_text", "linkedin")):
        besedilo = zgodba.get(polje)
        if _prazno(besedilo):
            continue
        if LOCILO in besedilo:
            krsitve.append(f"story.{polje}: vrstica --- prereče besedilo, check.py bi preveril samo del za njo (korak 3)")
            continue
        napake, opoz = _check(besedilo, nacin)
        krsitve += [f"story.{polje}: check.py --{nacin}: {n} (korak 3)" for n in napake]
        opozorila += [f"story.{polje}: {o}" for o in opoz]


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


def preveri(telo):
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
    if not isinstance(seznam, list) or any(not isinstance(p, dict) or _prazno(p.get("text")) for p in seznam):
        krsitve.append("preveri: seznam objektov s text in where (korak 3)")
        seznam = []
    oznake = sum(len(OZNAKA.findall(zgodba.get(p) or "")) for p in ("blog_md", "linkedin_text") if isinstance(zgodba.get(p), str))
    if oznake > len(seznam):
        krsitve.append(f"preveri: v besedilu je {oznake} oznak [PREVERI, v seznamu {len(seznam)}; aplikacija zaklene Potrdi po seznamu (korak 3)")

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
    return krsitve, opozorila


def main(argv) -> int:
    if len(argv) not in (2, 4) or (len(argv) == 4 and argv[2] != "--telo"):
        print("Uporaba: preveri_paket.py <state.json> [--telo <pot>]")
        return 1
    try:
        stanje = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as napaka:
        print(f"state.json ni mogoče prebrati: {napaka}")
        return 1
    if not isinstance(stanje, dict):
        print("state.json ni objekt")
        return 1
    telo = {k: v for k, v in stanje.items() if k != "_run"}
    krsitve, opozorila = preveri(telo)
    for besedilo in opozorila:
        print(f"Opozorilo: {besedilo}")
    if krsitve:
        for besedilo in krsitve:
            print(f"KRŠITEV: {besedilo}")
        return 1
    if len(argv) == 4:
        cilj = Path(argv[3])
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
