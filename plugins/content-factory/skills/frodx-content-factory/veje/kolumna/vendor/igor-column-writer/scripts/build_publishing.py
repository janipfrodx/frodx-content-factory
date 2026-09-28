#!/usr/bin/env python3
"""
build_publishing.py — sestavi FrodX publishing .docx iz gotovih kolumn.

Vzame slovensko kolumno (obvezno) ter neobvezno angleško, hrvaško in blok
socialnih objav, jih zloži v hišno strukturo publishing agenta in pretvori v
.docx prek pandoc-a.

Struktura izhoda:
    ## Slovenščina
    # <naslov>
    <telo, podnaslovi kot ###>
    ## English  (če podan)
    ## Hrvatski (če podan)
    ## Socialne objave (če podan --social)
        ## Objava 1 / 2 / 3

Pravila:
- jezik = '## ', naslov kolumne = '# ', notranji podnaslovi = '### '
- vrstice, ki se v kolumni začnejo s '## ', se demotirajo v '### '
- pandoc doda <w:zoom .../>, ki ga nekateri validatorji zavrnejo — odstranimo ga

Uporaba:
    python build_publishing.py --sl SL.md [--en EN.md] [--hr HR.md] \
        [--social socialne.md] --out Publishing_tema.docx

Zahteva: pandoc v PATH.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile


def demote(md_text: str) -> str:
    """Demote internal '## ' subheads to '### '; keep '# ' title unchanged."""
    out = []
    for line in md_text.splitlines():
        if line.startswith("## "):
            out.append("###" + line[2:])
        else:
            out.append(line)
    return "\n".join(out).strip()


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def assemble(sl: str, en: str | None, hr: str | None, social: str | None) -> str:
    parts = [f"## Slovenščina\n\n{demote(sl)}"]
    if en:
        parts.append(f"## English\n\n{demote(en)}")
    if hr:
        parts.append(f"## Hrvatski\n\n{demote(hr)}")
    if social:
        # Each post becomes its own H2 so downstream parsers that split by
        # H2 detect them as separate items ('### Objava' under one H2 merges).
        social_h2 = re.sub(r"(?m)^### (Objava\b)", r"## \1", social.strip())
        parts.append(f"## Socialne objave\n\n{social_h2}")
    return "\n\n".join(parts) + "\n"


def strip_zoom(docx_path: str) -> None:
    """Remove the <w:zoom .../> element from word/settings.xml in place."""
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".docx")
    os.close(tmp_fd)
    with zipfile.ZipFile(docx_path, "r") as zin, \
            zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/settings.xml":
                text = data.decode("utf-8")
                text = re.sub(r"<w:zoom\b[^>]*/>", "", text)
                text = re.sub(r"<w:zoom\b[^>]*>.*?</w:zoom>", "", text, flags=re.S)
                data = text.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp_path, docx_path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sestavi FrodX publishing .docx.")
    ap.add_argument("--sl", required=True, help="Slovenska kolumna (.md) — obvezno")
    ap.add_argument("--en", help="Angleška kolumna (.md) — neobvezno")
    ap.add_argument("--hr", help="Hrvaška kolumna (.md) — neobvezno")
    ap.add_argument("--social", help="Blok socialnih objav (.md) z '### Objava N' — neobvezno")
    ap.add_argument("--out", required=True, help="Izhodna .docx datoteka")
    args = ap.parse_args()

    if shutil.which("pandoc") is None:
        print("NAPAKA: pandoc ni v PATH. Namesti pandoc ali sestavi ročno.", file=sys.stderr)
        return 2

    for label, path in [("--sl", args.sl), ("--en", args.en), ("--hr", args.hr),
                        ("--social", args.social)]:
        if path and not os.path.exists(path):
            print(f"NAPAKA: datoteka za {label} ne obstaja: {path}", file=sys.stderr)
            return 2

    sl = read(args.sl)
    en = read(args.en) if args.en else None
    hr = read(args.hr) if args.hr else None
    social = read(args.social) if args.social else None

    combined = assemble(sl, en, hr, social)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tf:
        tf.write(combined)
        md_path = tf.name

    try:
        subprocess.run(["pandoc", md_path, "-o", args.out], check=True)
    except subprocess.CalledProcessError as exc:
        print(f"NAPAKA pri pandoc pretvorbi: {exc}", file=sys.stderr)
        return 1
    finally:
        os.unlink(md_path)

    strip_zoom(args.out)

    langs = ["SL"] + (["EN"] if en else []) + (["HR"] if hr else [])
    print(f"OK: {args.out}")
    print(f"  jeziki: {', '.join(langs)}" + ("  + socialne objave" if social else ""))
    print("  Preveri naslove (#/##/###) in žive povezave.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
