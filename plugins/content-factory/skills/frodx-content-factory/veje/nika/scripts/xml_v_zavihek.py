#!/usr/bin/env python3
"""Zavihek iz Claude Docsa (XML iz read) → markdown, enak izvozu Docsa.

Uporaba: python3 xml_v_zavihek.py <izhod.md> <kos1.xml> [<kos2.xml> ...]

Kosi so zaporedni odgovori read: prvi in vsak nadaljnji z next. Vsak odstavek
brez spustnega seznama mora imeti h = prvih 8 znakov sha256 svojega besedila.
Ob neujemanju ali odrezanem zavihku izhod ne nastane in exit je 1.
"""
import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PREBERI_ZNOVA = "prepis XML se ne ujema z Docsom; preberi zavihek znova"
ODREZAN = "zavihek ni prebran do konca; nadaljuj z read in next"
# Izvoz Docsa ubeži še * in _ v besedilu; tu namenoma ne, ker bi ubežniki prišli v story in HubSpot.
OZNAKE = {"bold": "**", "italic": "*", "code": "`"}


def _bloki(kosi):
    bloki = []
    for i, kos in enumerate(kosi):
        for otrok in ET.fromstring(kos):
            if otrok.tag == "gap":
                if i == len(kosi) - 1 or otrok.get("cap") != "true":
                    raise ValueError(ODREZAN)
                continue
            if any(True for _ in otrok.iter("gap")):
                raise ValueError(ODREZAN)
            bloki.append(otrok)
    return bloki


def _neujemanja(bloki):
    napacni = []
    for blok in bloki:
        for odstavek in blok.iter("paragraph"):
            if odstavek.find(".//dropdown") is not None:
                continue
            h = hashlib.sha256("".join(odstavek.itertext()).encode("utf-8")).hexdigest()[:8]
            if h != odstavek.get("h"):
                napacni.append(odstavek.get("id", "?"))
    return napacni


def _inline(el):
    deli = [el.text or ""]
    for otrok in el:
        if otrok.tag == "hardBreak":
            deli.append("\\\n")
        elif otrok.tag in OZNAKE:
            deli.append(f"{OZNAKE[otrok.tag]}{_inline(otrok)}{OZNAKE[otrok.tag]}")
        elif otrok.tag == "link":
            deli.append(f"[{''.join(otrok.itertext())}]({otrok.get('href', '')})")
        else:
            deli.append(_inline(otrok))
        deli.append(otrok.tail or "")
    return "".join(deli)


def _odstavki(el):
    return " ".join(_inline(p) for p in el.findall("paragraph"))


def _seznam(el):
    vrstice = []
    for n, alineja in enumerate(el.findall("listItem"), 1):
        if el.get("kind") == "check":
            oznaka = "- [x] " if alineja.get("checked") == "true" else "- [ ] "
        elif el.get("kind") == "ordered":
            oznaka = f"{n}. "
        else:
            oznaka = "- "
        vrstice.append(oznaka + _odstavki(alineja))
        for gnezden in alineja.findall("list"):
            vrstice.extend("  " + v for v in _seznam(gnezden).split("\n"))
    return "\n".join(vrstice)


def _tabela(el):
    vrstice = []
    for i, vrstica in enumerate(el.findall("row")):
        celice = vrstica.findall("cell")
        vrstice.append("| " + " | ".join(_odstavki(c).replace("|", "\\|") for c in celice) + " |")
        if i == 0 and celice and all(c.get("header") == "true" for c in celice):
            vrstice.append("| " + " | ".join("---" for _ in celice) + " |")
    return "\n".join(vrstice)


def _blok(el):
    if el.tag == "paragraph":
        n = int(el.get("heading", 0))
        return f"{'#' * n} {_inline(el)}" if n else _inline(el)
    if el.tag == "list":
        return _seznam(el)
    if el.tag == "table":
        return _tabela(el)
    return "".join(el.itertext())


def pretvori(kosi):
    bloki = _bloki(kosi)
    napacni = _neujemanja(bloki)
    if napacni:
        raise ValueError(f"{PREBERI_ZNOVA} (odstavki: {', '.join(napacni)})")
    return "\n\n".join(b for b in map(_blok, bloki) if b) + "\n"


def main(argv):
    if len(argv) < 3:
        print("Uporaba: xml_v_zavihek.py <izhod.md> <kos1.xml> [<kos2.xml> ...]")
        return 1
    try:
        md = pretvori([Path(p).read_text(encoding="utf-8") for p in argv[2:]])
    except ET.ParseError as napaka:
        print(f"NAPAKA: XML ni berljiv ({napaka}); preberi zavihek znova")
        return 1
    except ValueError as napaka:
        print(f"NAPAKA: {napaka}")
        return 1
    Path(argv[1]).write_bytes(md.encode("utf-8"))
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
