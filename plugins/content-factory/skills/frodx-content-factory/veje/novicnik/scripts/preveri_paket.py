#!/usr/bin/env python3
"""Preverba paketa novičnika pred oddajo v Newsletter Hub.

Uporaba: python3 preveri_paket.py <state.json> [--telo <pot>]

Iz state.json odstrani _run in preveri telo za POST /api/drafts. Kršitve
izpiše s pristojnim korakom in vrne exit 1. Blok brez slike je opozorilo:
Igor sliko doda v aplikaciji. Z --telo zapiše telo za oddajo, a samo,
kadar kršitev ni. Manjkajočo mapo za --telo ustvari sam; če zapis kljub
temu spodleti (napaka datotečnega sistema), izpiše eno vrstico NAPAKA: in
vrne exit 2, ločeno od kršitev (exit 1). V SI in HR zahteva nedeljivi
presledek pred %, v EN % brez presledka.
"""
import json
import re
import sys
from pathlib import Path

JEZIKI = ("si", "en", "hr")
TIPI = ("column", "webinar", "announcement")
STATUSI = ("ready_to_send", "draft")
RUN_SLUG = re.compile(r"^[a-z0-9-]{3,120}$")
BLOCK_ID = re.compile(r"^block-\d{2}$")
DATUM = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URA = re.compile(r"^\d{2}:\d{2}$")
DOLGI_POMISLJAJ = "\u2014"
ODSTOTEK_BREZ_NBSP = re.compile(r"\d[ \t]*%")
ODSTOTEK_S_PRESLEDKOM = re.compile(r"\d\s%")
# Vrednosti iz predloge EDITIONS v Igorjevem build_newsletter.py. Pisec
# predlogo prepisuje; kar ostane dobesedno, ni vsebina izdaje.
VZORCI = (
    "Tematski naslov izdaje.", "Subject po arhetipu.", "Preheader, ki nadaljuje subject.",
    "Alt besedilo slike.", "Naslov bloka 1.", "Prvi odstavek telesa.",
)


def _prazno(vrednost):
    return not isinstance(vrednost, str) or not vrednost.strip()


def _odstavki(vrednost):
    return isinstance(vrednost, list) and bool(vrednost) and all(not _prazno(x) for x in vrednost)


def _nizi(obj, pot=""):
    if isinstance(obj, str):
        yield pot, obj
    elif isinstance(obj, dict):
        for kljuc, vrednost in obj.items():
            yield from _nizi(vrednost, f"{pot}.{kljuc}" if pot else kljuc)
    elif isinstance(obj, list):
        for i, vrednost in enumerate(obj):
            yield from _nizi(vrednost, f"{pot}[{i}]")


def _kljuci(obj):
    if isinstance(obj, dict):
        for kljuc, vrednost in obj.items():
            yield kljuc
            yield from _kljuci(vrednost)
    elif isinstance(obj, list):
        for vrednost in obj:
            yield from _kljuci(vrednost)


def _struktura(izdaja):
    return [(b.get("block_id"), b.get("type")) for b in izdaja.get("blocks") or [] if isinstance(b, dict)]


def _preveri_blok(blok, p, napaka, opozorilo):
    if not isinstance(blok, dict):
        napaka(p, "blok ni objekt")
        return
    if not isinstance(blok.get("block_id"), str) or not BLOCK_ID.match(blok["block_id"]):
        napaka(f"{p}.block_id", "oblika block-01")
    tip = blok.get("type")
    if tip not in TIPI:
        napaka(f"{p}.type", f"mora biti eden od {', '.join(TIPI)}")
    if _prazno(blok.get("title")):
        napaka(f"{p}.title", "prazno")
    if not _odstavki(blok.get("body")):
        napaka(f"{p}.body", "vsaj en neprazen odstavek")
    cta = blok.get("cta") if isinstance(blok.get("cta"), dict) else {}
    if _prazno(cta.get("label")):
        napaka(f"{p}.cta.label", "prazno")
    if not isinstance(cta.get("url"), str) or not cta["url"].startswith("https://"):
        napaka(f"{p}.cta.url", "mora biti https:// URL")

    dogodek = blok.get("event")
    if tip == "webinar":
        if not isinstance(dogodek, dict):
            napaka(f"{p}.event", "webinar potrebuje date, time in duration_min")
        else:
            if not isinstance(dogodek.get("date"), str) or not DATUM.match(dogodek["date"]):
                napaka(f"{p}.event.date", "oblika 2026-11-12")
            if not isinstance(dogodek.get("time"), str) or not URA.match(dogodek["time"]):
                napaka(f"{p}.event.time", "oblika 10:00")
            trajanje = dogodek.get("duration_min")
            if not isinstance(trajanje, int) or isinstance(trajanje, bool) or trajanje <= 0:
                napaka(f"{p}.event.duration_min", "celo število minut, večje od 0")
    elif dogodek is not None:
        napaka(f"{p}.event", "samo webinar ima event, drugi bloki imajo null")

    slika = blok.get("image")
    if slika is not None and not isinstance(slika, dict):
        napaka(f"{p}.image", "mora biti objekt ali null", 5)
        return
    url = (slika or {}).get("url")
    if url in (None, ""):
        opozorilo(f"{p}: blok {blok.get('block_id')} nima slike - Igor jo doda v aplikaciji (korak 5)")
    elif not isinstance(url, str) or not url.startswith("https://"):
        napaka(f"{p}.image.url", "mora biti https:// URL", 5)


def _preveri_izdajo(izdaja, opozorila):
    jezik = izdaja.get("language")
    korak = 2 if jezik == "si" else 4
    krsitve = []

    def napaka(pot, opis, n=korak):
        krsitve.append(f"{jezik}.{pot}: {opis} (korak {n})")

    def opozorilo(besedilo):
        opozorila.append(f"{jezik}.{besedilo}")

    for polje in ("package_id", "edition_name", "subject", "preheader"):
        if _prazno(izdaja.get(polje)):
            napaka(polje, "prazno")
    if izdaja.get("status") not in STATUSI:
        napaka("status", f"mora biti {' ali '.join(STATUSI)}")
    if _prazno((izdaja.get("delivery") or {}).get("segment_ref")):
        napaka("delivery.segment_ref", "prazno")
    for polje in ("from_name", "from_email"):
        if _prazno((izdaja.get("sender") or {}).get(polje)):
            napaka(f"sender.{polje}", "prazno")
    if not _odstavki((izdaja.get("hook") or {}).get("paragraphs")):
        napaka("hook.paragraphs", "vsaj en neprazen odstavek")
    if not _odstavki((izdaja.get("closing") or {}).get("paragraphs")):
        napaka("closing.paragraphs", "vsaj en neprazen odstavek")
    for polje in ("phrase", "name"):
        if _prazno((izdaja.get("signoff") or {}).get(polje)):
            napaka(f"signoff.{polje}", "prazno")

    bloki = izdaja.get("blocks")
    if not isinstance(bloki, list) or not 1 <= len(bloki) <= 3:
        napaka("blocks", "izdaja ima 1-3 bloke")
        bloki = bloki if isinstance(bloki, list) else []
    for i, blok in enumerate(bloki):
        _preveri_blok(blok, f"blocks[{i}]", napaka, opozorilo)

    for pot, niz in _nizi(izdaja):
        if DOLGI_POMISLJAJ in niz and pot != "delivery.segment_ref":
            napaka(pot, "dolgi pomišljaj (U+2014); v novičniku en dash")
        if niz.strip() in VZORCI or "YYYY" in niz or niz.rstrip().endswith("/..."):
            napaka(pot, "vzorčna vrednost iz Igorjeve predloge EDITIONS")
        if pot.endswith("url"):
            continue
        if jezik in ("si", "hr") and ODSTOTEK_BREZ_NBSP.search(niz):
            napaka(pot, "pred % mora biti nedeljivi presledek (U+00A0), npr. 12\u00a0%")
        elif jezik == "en" and ODSTOTEK_S_PRESLEDKOM.search(niz):
            napaka(pot, "v angleščini je % brez presledka, npr. 12%")
    return krsitve


def preveri(telo: dict):
    krsitve, opozorila = [], []
    if not isinstance(telo, dict):
        return ["paket ni objekt (init_run.py)"], []
    if "_run" in telo:
        krsitve.append("_run: odstrani ga pred oddajo (korak 6)")
    kljuci_telesa = set(_kljuci(telo))
    if "send_datetime" in kljuci_telesa:
        krsitve.append("send_datetime: čas pošiljanja nastavi Igor v aplikaciji (korak 6)")
    if "timezone" in kljuci_telesa:
        krsitve.append("timezone: časovni pas je vedno Europe/Ljubljana, paket ga ne nosi (korak 6)")
    if "toc" in kljuci_telesa:
        krsitve.append("toc: kazalo doda aplikacija, paket ga ne nosi (korak 6)")
    if not isinstance(telo.get("run_slug"), str) or not RUN_SLUG.match(telo["run_slug"]):
        krsitve.append("run_slug: mora ustrezati ^[a-z0-9-]{3,120}$ (init_run.py)")

    izdaje = telo.get("editions")
    if not isinstance(izdaje, list):
        krsitve.append("editions: manjka seznam izdaj (korak 2)")
        izdaje = []
    jeziki = [i.get("language") if isinstance(i, dict) else None for i in izdaje]
    for jezik in JEZIKI:
        stevilo = jeziki.count(jezik)
        if stevilo != 1:
            korak = 2 if jezik == "si" else 4
            krsitve.append(f"editions: jezik {jezik} mora biti natanko enkrat, je {stevilo}-krat (korak {korak})")
    tuji = [j for j in jeziki if j not in JEZIKI]
    if tuji:
        krsitve.append(f"editions: neznan jezik {tuji} (korak 2)")

    si = next((i for i in izdaje if isinstance(i, dict) and i.get("language") == "si"), None)
    for izdaja in izdaje:
        if not isinstance(izdaja, dict):
            continue
        krsitve += _preveri_izdajo(izdaja, opozorila)
        if si is not None and izdaja is not si and _struktura(izdaja) != _struktura(si):
            krsitve.append(
                f"{izdaja.get('language')}.blocks: block_id in type se ne ujemata s si {_struktura(si)} (korak 4)"
            )
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
