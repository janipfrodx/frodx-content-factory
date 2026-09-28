#!/usr/bin/env python3
"""Izdaja novičnika v berljivo besedilo z oznakami in nazaj.

Uporaba:
  python3 izdaja_besedilo.py izpis <state.json> <jezik>
  python3 izdaja_besedilo.py vpis <state.json> <jezik> <besedilo.txt>

Vpis spremeni samo besedilna polja izdaje: subject, preheader, greeting,
hook.paragraphs, blocks[].title/body/bullets/cta.label, closing.paragraphs,
signoff.phrase in ps. Ob pokvarjenih oznakah vrne exit 1 in state.json
pusti nedotaknjen. Rezervirane oznake se preverjajo samo pri odstavkih
znotraj seznamov (hook.paragraphs, blocks[].body, blocks[].bullets,
closing.paragraphs): vsak tak odstavek se mora začeti z besedilom, ki se
ne ujema z rezervirano oznako.
"""
import copy
import json
import os
import re
import sys
from pathlib import Path

GLAVA_BLOKA = re.compile(r"^\[(block-\d{2}) · ([a-z_]+)\]$")
GLAVNE = ("SUBJECT", "PREHEADER", "GREETING")
BLOKOVNE = ("NASLOV", "CTA")
ZAKLJUCNE = ("PODPIS", "PS")
IME_OZNAKE = {"NASLOV": "NASLOV", "CTA": "CTA", "body": "TELO", "bullets": "ALINEJE"}


class NapakaOznak(ValueError):
    pass


def _ena_vrstica(vrednost, polje):
    if not isinstance(vrednost, str):
        raise NapakaOznak(f"{polje} ni besedilo")
    if "\n" in vrednost:
        raise NapakaOznak(f"{polje} vsebuje prelom vrstice; odstavek mora biti ena vrstica")
    return vrednost


def _odstavek(vrednost, polje):
    vrednost = _ena_vrstica(vrednost, polje)
    s = vrednost.strip()
    if GLAVA_BLOKA.match(s):
        raise NapakaOznak(f"{polje} se začne z rezervirano oznako: {vrednost[:40]}")
    if s in ("HOOK:", "ZAKLJUČEK:", "TELO:", "ALINEJE:"):
        raise NapakaOznak(f"{polje} se začne z rezervirano oznako: {vrednost[:40]}")
    label, dvopicje, _ = s.partition(":")
    if dvopicje and label in GLAVNE + BLOKOVNE + ZAKLJUCNE:
        raise NapakaOznak(f"{polje} se začne z rezervirano oznako: {vrednost[:40]}")
    return vrednost


def izdaja_v_besedilo(izdaja: dict) -> str:
    v = [
        f"SUBJECT: {_ena_vrstica(izdaja['subject'], 'subject')}",
        f"PREHEADER: {_ena_vrstica(izdaja['preheader'], 'preheader')}",
        f"GREETING: {_ena_vrstica(izdaja['greeting'], 'greeting')}",
        "",
        "HOOK:",
    ]
    v += [_odstavek(p, "hook.paragraphs") for p in izdaja["hook"]["paragraphs"]]
    for blok in izdaja["blocks"]:
        bid = blok["block_id"]
        v += ["", f"[{bid} · {blok['type']}]", f"NASLOV: {_ena_vrstica(blok['title'], bid + '.title')}", "TELO:"]
        v += [_odstavek(p, bid + ".body") for p in blok["body"]]
        v.append("ALINEJE:")
        v += [_odstavek(a, bid + ".bullets") for a in blok.get("bullets") or []]
        v.append(f"CTA: {_ena_vrstica(blok['cta']['label'], bid + '.cta.label')}")
    v += ["", "ZAKLJUČEK:"]
    v += [_odstavek(p, "closing.paragraphs") for p in izdaja["closing"]["paragraphs"]]
    v.append(f"PODPIS: {_ena_vrstica(izdaja['signoff']['phrase'], 'signoff.phrase')}")
    v.append(f"PS: {_ena_vrstica(izdaja.get('ps') or '', 'ps')}")
    return "\n".join(v) + "\n"


def _nastavi(cilj, oznaka, vrednost, st):
    if oznaka in cilj:
        raise NapakaOznak(f"vrstica {st}: oznaka {oznaka} se ponovi")
    cilj[oznaka] = vrednost


def besedilo_v_izdajo(besedilo: str, izdaja: dict) -> dict:
    glava, konec = {}, {}
    hook, zakljucek = None, None
    bloki, blok, seznam = [], None, None
    po_zakljucku = False

    for st, surova in enumerate(besedilo.splitlines(), 1):
        vrstica = surova.strip()
        if not vrstica:
            continue
        glava_bloka = GLAVA_BLOKA.match(vrstica)
        oznaka, dvopicje, vrednost = vrstica.partition(":")
        vrednost = vrednost.strip()
        if glava_bloka:
            if po_zakljucku:
                raise NapakaOznak(f"vrstica {st}: blok stoji za ZAKLJUČKOM")
            blok = {"block_id": glava_bloka.group(1), "type": glava_bloka.group(2)}
            bloki.append(blok)
            seznam = None
        elif vrstica == "HOOK:":
            if blok is not None or po_zakljucku or hook is not None:
                raise NapakaOznak(f"vrstica {st}: HOOK mora stati enkrat, pred bloki")
            hook = seznam = []
        elif vrstica == "ZAKLJUČEK:":
            if po_zakljucku:
                raise NapakaOznak(f"vrstica {st}: ZAKLJUČEK se ponovi")
            po_zakljucku, blok = True, None
            zakljucek = seznam = []
        elif vrstica in ("TELO:", "ALINEJE:"):
            kljuc = "body" if vrstica == "TELO:" else "bullets"
            if blok is None or kljuc in blok:
                raise NapakaOznak(f"vrstica {st}: {vrstica} stoji izven bloka ali se ponovi")
            blok[kljuc] = seznam = []
        elif dvopicje and oznaka in GLAVNE and blok is None and not po_zakljucku:
            _nastavi(glava, oznaka, vrednost, st)
            seznam = None
        elif dvopicje and oznaka in BLOKOVNE and blok is not None:
            _nastavi(blok, oznaka, vrednost, st)
            seznam = None
        elif dvopicje and oznaka in ZAKLJUCNE and po_zakljucku:
            _nastavi(konec, oznaka, vrednost, st)
            seznam = None
        elif seznam is not None:
            seznam.append(vrstica)
        else:
            raise NapakaOznak(f"vrstica {st}: besedilo izven razdelka: {vrstica[:60]}")

    for oznaka in GLAVNE:
        if oznaka not in glava:
            raise NapakaOznak(f"manjka oznaka {oznaka}")
    if not hook:
        raise NapakaOznak("HOOK manjka ali je prazen")
    if not zakljucek:
        raise NapakaOznak("ZAKLJUČEK manjka ali je prazen")
    for oznaka in ZAKLJUCNE:
        if oznaka not in konec:
            raise NapakaOznak(f"manjka oznaka {oznaka}")
    pricakovano = [(b["block_id"], b["type"]) for b in izdaja["blocks"]]
    dobljeno = [(b["block_id"], b["type"]) for b in bloki]
    if dobljeno != pricakovano:
        raise NapakaOznak(f"bloki v besedilu {dobljeno} se ne ujemajo z izdajo {pricakovano}")
    for b in bloki:
        for kljuc, ime in IME_OZNAKE.items():
            if kljuc not in b:
                raise NapakaOznak(f"{b['block_id']}: manjka oznaka {ime}")
        if not b["body"]:
            raise NapakaOznak(f"{b['block_id']}: TELO je prazno")

    nova = copy.deepcopy(izdaja)
    nova["subject"] = glava["SUBJECT"]
    nova["preheader"] = glava["PREHEADER"]
    nova["greeting"] = glava["GREETING"]
    nova["hook"]["paragraphs"] = hook
    for cilj, b in zip(nova["blocks"], bloki):
        cilj["title"] = b["NASLOV"]
        cilj["body"] = b["body"]
        cilj["bullets"] = b["bullets"]
        cilj["cta"]["label"] = b["CTA"]
    nova["closing"]["paragraphs"] = zakljucek
    nova["signoff"]["phrase"] = konec["PODPIS"]
    nova["ps"] = konec["PS"] or None
    return nova


def _indeks(stanje, jezik):
    for i, izdaja in enumerate(stanje.get("editions") or []):
        if isinstance(izdaja, dict) and izdaja.get("language") == jezik:
            return i
    raise NapakaOznak(f"v state.json ni izdaje {jezik}")


def main(argv) -> int:
    if not ((len(argv) == 4 and argv[1] == "izpis") or (len(argv) == 5 and argv[1] == "vpis")):
        print("Uporaba: izdaja_besedilo.py izpis <state.json> <jezik> | vpis <state.json> <jezik> <besedilo.txt>")
        return 1
    pot = Path(argv[2])
    try:
        stanje = json.loads(pot.read_text(encoding="utf-8"))
        i = _indeks(stanje, argv[3])
        if argv[1] == "izpis":
            sys.stdout.write(izdaja_v_besedilo(stanje["editions"][i]))
            return 0
        besedilo = Path(argv[4]).read_text(encoding="utf-8")
        stanje["editions"][i] = besedilo_v_izdajo(besedilo, stanje["editions"][i])
    except NapakaOznak as napaka:
        print(f"NAPAKA: {napaka}")
        return 1
    except (KeyError, TypeError) as napaka:
        print(f"NAPAKA: izdaja ni popolna: {napaka}")
        return 1
    except (OSError, json.JSONDecodeError) as napaka:
        print(f"NAPAKA: {napaka}")
        return 1
    zacasna = pot.with_name(pot.name + ".tmp")
    zacasna.write_text(json.dumps(stanje, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(zacasna, pot)
    print(f"Vpisano: {argv[3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
