#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contract_check.py — deterministična validacija Publishing docx-a
proti pogodbi z Janijevo aplikacijo (references/publishing-contract.md).

Uporaba:
    python contract_check.py <Publishing.docx>
    python contract_check.py --md <combined.md>   # že izvlečen markdown

Izhod: poročilo + exit code 0 (OK) / 1 (kršitev pogodbe).
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANGS = ["Slovenščina", "English", "Hrvatski"]
SOCIAL = "Socialne objave"
URL_RE = re.compile(r"https?://|\[[^\]]*\]\([^)]+\)")
PLACEHOLDER_RE = re.compile(r"\[(povezava|poveznica|link)\]", re.IGNORECASE)


def docx_to_md(path: Path) -> str:
    if shutil.which("extract-text"):
        return subprocess.run(["extract-text", str(path)], capture_output=True,
                              text=True, check=True).stdout
    if shutil.which("pandoc"):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            subprocess.run(["pandoc", str(path), "-t", "gfm", "-o", tmp.name],
                           check=True)
            return Path(tmp.name).read_text(encoding="utf-8")
    sys.exit("Ne najdem extract-text niti pandoc za branje docx.")


def headings(md: str):
    out = []
    for i, line in enumerate(md.splitlines(), 1):
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m:
            out.append((i, len(m.group(1)), m.group(2)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", nargs="?", help="Publishing .docx")
    ap.add_argument("--md", help="Že izvlečen kombiniran markdown")
    args = ap.parse_args()

    if args.md:
        md = Path(args.md).read_text(encoding="utf-8")
    elif args.docx:
        md = docx_to_md(Path(args.docx))
    else:
        ap.error("Podaj .docx ali --md")

    errors, warnings = [], []
    hs = headings(md)
    h2s = [(i, t) for i, lvl, t in hs if lvl == 2]
    h2_titles = [t for _, t in h2s]

    # 1) Jezikovne sekcije: prisotnost in vrstni red
    lang_positions = []
    for lang in LANGS:
        if lang not in h2_titles:
            errors.append(f"Manjka jezikovna sekcija '## {lang}'.")
        else:
            lang_positions.append(h2_titles.index(lang))
    if lang_positions == sorted(lang_positions) and len(lang_positions) == 3:
        pass
    elif len(lang_positions) == 3:
        errors.append(f"Napačen vrstni red jezikov: pričakovano {LANGS}.")

    # 2) Socialne objave: prisotnost, zadnja sekcija
    if SOCIAL not in h2_titles:
        errors.append(f"Manjka sekcija '## {SOCIAL}'.")
    else:
        non_objava_after = [t for t in h2_titles[h2_titles.index(SOCIAL) + 1:]
                            if not re.match(r"^Objava \d+", t)]
        if non_objava_after:
            errors.append(f"Po '## {SOCIAL}' so dovoljene samo '## Objava N', "
                          f"najdeno: {non_objava_after}")

    # 3) Razrez na sekcije po H2
    sections = {}
    bounds = [(i, t) for i, t in h2s] + [(len(md.splitlines()) + 1, "__END__")]
    lines = md.splitlines()
    for (start, title), (end, _) in zip(bounds, bounds[1:]):
        sections.setdefault(title, []).append("\n".join(lines[start:end - 1]))

    # 4) Vsaka jezikovna sekcija: natanko en H1, vsaj en H3
    for lang in LANGS:
        if lang not in sections:
            continue
        body = sections[lang][0]
        h1 = re.findall(r"(?m)^# (?!#)(.+)$", body)
        if len(h1) != 1:
            errors.append(f"'{lang}': pričakovan natanko 1 naslov (H1), "
                          f"najdeno {len(h1)}.")
        if not re.search(r"(?m)^### ", body):
            warnings.append(f"'{lang}': brez podnaslovov (###) — preveri.")
        if PLACEHOLDER_RE.search(body):
            errors.append(f"'{lang}': placeholder [povezava] v kolumni — "
                          f"viri morajo biti žive markdown povezave.")

    # 4b) SEO sekcija (v1.2, obvezna): med Hrvatski in Socialne objave,
    #     natanko ### sl/en/hr, stirje kljuci, slug kebab-case
    SEO_KEYS = ["seo_title", "meta_description", "slug", "image_alt"]
    SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    if "SEO" not in h2_titles:
        errors.append("Manjka sekcija '## SEO' — od v1.2 obvezna na redakcijski strani.")
    else:
        seo_i = h2_titles.index("SEO")
        if "Hrvatski" in h2_titles and seo_i < h2_titles.index("Hrvatski"):
            errors.append("'## SEO' mora stati za '## Hrvatski'.")
        if SOCIAL in h2_titles and seo_i > h2_titles.index(SOCIAL):
            errors.append("'## SEO' mora stati pred '## Socialne objave'.")
        body = sections.get("SEO", [""])[0]
        subs = re.findall(r"(?m)^### (\S+)\s*$", body)
        if subs != ["sl", "en", "hr"]:
            errors.append(f"SEO: pričakovane podsekcije ### sl/en/hr v tem vrstnem redu, najdeno: {subs}")
        chunks = re.split(r"(?m)^### \S+\s*$", body)[1:]
        for lang, chunk in zip(subs, chunks):
            for key in SEO_KEYS:
                m = re.search(rf"(?m)^{key}:\s*(.*)$", chunk)
                if not m:
                    errors.append(f"SEO/{lang}: manjka ključ '{key}:'.")
                elif not m.group(1).strip():
                    errors.append(f"SEO/{lang}: ključ '{key}:' je prazen.")
            for km in re.finditer(r"(?m)^([a-z_]+):", chunk):
                if km.group(1) not in SEO_KEYS:
                    warnings.append(f"SEO/{lang}: neznan ključ '{km.group(1)}:' — importer ga preskoči (tipkarska?).")
            st = re.search(r"(?m)^seo_title:\s*(.*)$", chunk)
            if st and len(st.group(1).strip()) > 70:
                warnings.append(f"SEO/{lang}: seo_title {len(st.group(1).strip())} znakov (cilj do ~60).")
            md_m = re.search(r"(?m)^meta_description:\s*(.*)$", chunk)
            if md_m and md_m.group(1).strip() and not (120 <= len(md_m.group(1).strip()) <= 170):
                warnings.append(f"SEO/{lang}: meta_description {len(md_m.group(1).strip())} znakov (cilj 120-170).")
            sl_m = re.search(r"(?m)^slug:\s*(.*)$", chunk)
            if sl_m and sl_m.group(1).strip() and not SLUG_RE.match(sl_m.group(1).strip()):
                errors.append(f"SEO/{lang}: slug '{sl_m.group(1).strip()}' ni kebab-case (a-z, 0-9, vezaji).")

    # 4c) Key visual (v1.2, obvezen): za SEO, pred Socialne objave,
    #     s podsekcijama ### Prompt Gemini in ### Prompt OpenAI
    if "Key visual" not in h2_titles:
        errors.append("Manjka sekcija '## Key visual' — od v1.2 obvezna (koncept + oba prompta).")
    else:
        kv_i = h2_titles.index("Key visual")
        if "SEO" in h2_titles and kv_i < h2_titles.index("SEO"):
            errors.append("'## Key visual' mora stati za '## SEO'.")
        if SOCIAL in h2_titles and kv_i > h2_titles.index(SOCIAL):
            errors.append("'## Key visual' mora stati pred '## Socialne objave'.")
        kbody = sections.get("Key visual", [""])[0]
        kparts = re.split(r"(?m)^### (.+)$", kbody)
        ksubs = dict(zip(kparts[1::2], kparts[2::2]))
        for need in ("Prompt Gemini", "Prompt OpenAI"):
            if need not in ksubs:
                errors.append(f"Key visual: manjka podsekcija '### {need}'.")
            elif len(ksubs[need].strip()) < 50:
                errors.append(f"Key visual: '### {need}' je prazen ali prekratek.")

    # 4d) featured_image_url je ukinjen — URL nastane v pipelinu
    if re.search(r"(?m)^featured_image_url:", md):
        errors.append("Ključ 'featured_image_url:' je ukinjen — URL naslovne slike nastane v pipelinu (korak 2).")

    # 5) Naslov SL → meta.title
    if "Slovenščina" in sections:
        m = re.search(r"(?m)^# (?!#)(.+)$", sections["Slovenščina"][0])
        if m and len(m.group(1)) > 100:
            warnings.append(f"SL naslov dolg {len(m.group(1))} znakov — "
                            f"preveri smiselnost za meta.title.")

    # 6) Objave: zaporedno oštevilčenje, brez povezav/placeholderjev,
    #    brez newslettra, brez formatiranja
    objave = [(i, t) for i, t in h2s if re.match(r"^Objava \d+", t)]
    nums = [int(re.match(r"^Objava (\d+)", t).group(1)) for _, t in objave]
    if nums and nums != list(range(1, len(nums) + 1)):
        errors.append(f"Objave niso oštevilčene zaporedno od 1: {nums}.")
    if not objave:
        errors.append("Ni nobene '## Objava N'.")
    for _, t in objave:
        body = sections.get(t, [""])[0]
        if URL_RE.search(body):
            errors.append(f"'{t}': vsebuje URL ali markdown povezavo — "
                          f"povezavo doda n8n.")
        if PLACEHOLDER_RE.search(body):
            errors.append(f"'{t}': vsebuje [povezava] placeholder — "
                          f"povezavo doda n8n, placeholder bi šel v objavo.")
        if re.search(r"newsletter|pozdravljeni", body, re.IGNORECASE):
            errors.append(f"'{t}': diši po newslettru — newsletter ni del "
                          f"paketa (pogodba, 11. 6. 2026).")
        if re.search(r"(?m)^#{1,6} ", body):
            errors.append(f"'{t}': vsebuje podnaslove — objava je gol tekst.")
        if "**" in body or re.search(r"(?<!\w)_[^_]+_(?!\w)", body):
            warnings.append(f"'{t}': bold/italic se v JSON splošči — odstrani.")

    print("=" * 60)
    print("CONTRACT CHECK — Publishing docx → Janijeva aplikacija (v1.2)")
    print("=" * 60)
    for e in errors:
        print(f"  NAPAKA   {e}")
    for w in warnings:
        print(f"  opozorilo {w}")
    if not errors and not warnings:
        print("  OK — struktura ustreza pogodbi.")
    elif not errors:
        print(f"\n  OK z {len(warnings)} opozorili.")
    else:
        print(f"\n  USTAVI ODDAJO: {len(errors)} kršitev pogodbe.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
