#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FrodX Newsletter — mehanski preverjalec.

Uporaba:
    python3 scripts/eval_check.py /mnt/user-data/outputs/GameChanger_si.docx   # shema + uredniški ulovi
    python3 scripts/eval_check.py osnutek.md --text                            # samo besedilni ulovi
    python3 scripts/eval_check.py file.docx --lang hr                          # vsili jezik

Vsako opozorilo je NASVET, ne trdi blok. Skripta ujame, kar je strojno
preverljivo: SHEMO (vrstni red/ključi/vdelane slike po Janijevi delujoči shemi)
in besedilna vrata 4/5 (ritem, fraze, žargon, %, em dash, datum). Hook, FrodX
edinstvenost in nativnost (vrata 1/3/6) presodi model — teh skripta ne ocenjuje.
"""
import sys, re, argparse

# ----------------------------- besedilni ulovi (vrata 4/5) -----------------------------
FORBIDDEN_SI = [
    "v današnjem digitalnem svetu", "v današnjem hitro spreminjajočem",
    "ključno je poudariti", "vsi se strinjamo, da", "morda sem starokopiten",
    "ni skrivnost, da", "kot vemo", "brez dvoma", "v zaključku lahko rečemo",
    "sklepamo lahko", "pomembno je omeniti", "ne smemo pozabiti",
    "seveda", "razumem", "če sem iskren",
]
BANNED_JARGON = [
    "leverage", "synergy", "paradigm shift", "best practice", "game changer",
    "disruptive", "scalable", "agile", "ecosystem", "stakeholder",
]
IDIOM_AVOID = {
    "bolečinska točka": "izziv", "aha trenutek": "preobrat",
    "nizko viseče sadje": "hitre zmage", "na koncu dneva": "skratka",
    "proaktiven pristop": "aktivno ukrepanje", "sinergija": "povezovanje",
    "dodana vrednost": "konkretna korist", "holistični pogled": "celovit pregled",
}
HR_KALKI = {"budite dobro": "Sve najbolje", "cjenik check": "provjera cjenika"}
EN_MONTHS = ("january","february","march","april","may","june","july",
             "august","september","october","november","december")
WARN, OK = "⚠", "✓"

def split_sentences(text):
    text = re.sub(r"\s+", " ", text)
    return [p for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]

def word_count(s):
    return len(re.findall(r"\b[\wčšžćđČŠŽĆĐ]+\b", s))

def check_text(text, lang="si"):
    out = []; low = text.lower()
    hits = [p for p in FORBIDDEN_SI if p in low]
    out.append((not hits, f"Prepovedane fraze: {hits if hits else 'nobenih'}"))
    jhits = [j for j in BANNED_JARGON if re.search(r"\b"+re.escape(j)+r"\b", low)]
    out.append((not jhits, f"Angleški žargon: {jhits if jhits else 'nobenega'}"))
    ihits = [f'{k}→{v}' for k, v in IDIOM_AVOID.items() if k in low]
    out.append((not ihits, f"Idiomi za zamenjavo: {ihits if ihits else 'nobenih'}"))
    sents = split_sentences(text)
    if sents:
        lens = [word_count(s) for s in sents]
        avg = sum(lens)/len(lens)
        short_ratio = sum(1 for l in lens if l <= 8)/len(lens)
        longs = [s for s, l in zip(sents, lens) if l > 20]
        out.append((avg <= 16, f"Povprečje stavka: {avg:.1f} besed (cilj ~11, sekano)"))
        out.append((short_ratio >= 0.30, f"Delež stavkov ≤8 besed: {short_ratio*100:.0f}% (cilj ~48%)"))
        out.append((len(longs) <= max(1, len(sents)*0.15), f"Predolgih stavkov (>20 besed): {len(longs)}"))
    if lang in ("si", "hr"):
        bad_pct = len(re.findall(r"\d%", text))
        out.append((bad_pct == 0, f"Manjkajoč NBSP pred %: {bad_pct}x"))
    else:
        sp_pct = len(re.findall(r"\d\s%", text))
        out.append((sp_pct == 0, f"EN: presledek pred % (naj ga ne bo): {sp_pct}x"))
    em = text.count("\u2014")
    out.append((em == 0, f"Em dash (—) namesto en dash (–): {em}x" + (" → zamenjaj z –" if em else "")))
    us_month = re.findall(r"\b(?:"+"|".join(EN_MONTHS)+r")\s+\d{1,2},\s*\d{4}\b", low)
    us_slash = re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", text)
    n_us = len(us_month)+len(us_slash)
    out.append((n_us == 0, f"Ameriški datum: {n_us}x" + (" → ISO ali day-first" if n_us else "")))
    oneliners = len(re.findall(r"\b\w+\s+ni\s+\w+\.\s+Je\s+\w+", text))
    out.append((oneliners <= 2, f"Definicijski one-linerji: {oneliners} (max 2)"))
    if lang == "hr":
        khits = [f'{k}→{v}' for k, v in HR_KALKI.items() if k in low]
        out.append((not khits, f"HR kalki: {khits if khits else 'nobenih'}"))
        out.append((True, "HR dvojina/množina: preveri ročno (skripta ne lovi)"))
    return out

# ----------------------------- shema docx (vrata 2) -----------------------------
REQ_META = ["PACKAGE_ID","EDITION_NAME","LANGUAGE","STATUS","SEGMENT_REF","SEND_DATETIME",
            "TIMEZONE","FROM_NAME","FROM_EMAIL","REPLY_TO","FOOTER_REF","SUBJECT","PREHEADER","GREETING"]
REQ_BLOCK = ["BLOCK_ID","BLOCK_TYPE","IMAGE_FILE","IMAGE_ALT","IMAGE","BLOCK_TITLE","CTA_LABEL","CTA_URL"]

def cell_has_image(cell):
    x = cell._tc.xml
    return ("<a:blip" in x) or ("<w:drawing" in x)

def check_docx(path):
    from docx import Document
    doc = Document(path); out = []
    tables = doc.tables
    def kv(t):  # 2-col tabela -> dict ključ->(vrednost, cell)
        d = {}
        for r in t.rows:
            if len(r.cells) >= 2:
                d[r.cells[0].text.strip()] = (r.cells[1].text.strip(), r.cells[1])
        return d

    # razvrsti tabele po tipu (po prvem ključu)
    meta = hook = toc = closing = signoff = ps = None
    blocks = []
    for t in tables:
        first = t.rows[0].cells[0].text.strip()
        if first == "PACKAGE_ID": meta = kv(t)
        elif first == "HOOK_ARCHETYPE": hook = kv(t)
        elif first == "TOC_LABEL": toc = t
        elif first == "BLOCK_ID": blocks.append((t, kv(t)))
        elif first == "CLOSING_TYPE": closing = kv(t)
        elif first == "SIGNOFF_PHRASE": signoff = kv(t)
        elif first == "PS_TEXT": ps = kv(t)

    lang = (meta.get("LANGUAGE", ("si",))[0] if meta else "si") or "si"

    # META
    if meta is None:
        out.append((False, "META tabela (PACKAGE_ID…) MANJKA"))
    else:
        miss = [k for k in REQ_META if k not in meta or not meta[k][0]]
        out.append((not miss, f"META ključi: {'vsi prisotni' if not miss else 'MANJKA '+str(miss)}"))
        # lokalizacija (mehko opozorilo)
        if lang == "hr":
            out.append((meta.get("TIMEZONE",("",))[0]=="Europe/Zagreb", "HR TIMEZONE == Europe/Zagreb"))
            out.append(("ć" in meta.get("FROM_NAME",("",))[0], "HR FROM_NAME = Igor Pauletić (ć)"))

    # HOOK
    if hook is None:
        out.append((False, "HOOK tabela MANJKA (mora biti tabela, ne proza)"))
    else:
        out.append(("HOOK_ARCHETYPE" in hook and "HOOK_P1" in hook, "HOOK: arhetip + HOOK_P1 prisotna"))

    # bloki
    out.append((1 <= len(blocks) <= 3, f"Število blokov: {len(blocks)} (1–3)"))
    block_ids = []
    for t, d in blocks:
        bid = d.get("BLOCK_ID", ("?",))[0]; block_ids.append(bid)
        miss = [k for k in REQ_BLOCK if k not in d]
        out.append((not miss, f"[{bid}] ključi: {'ok' if not miss else 'MANJKA '+str(miss)}"))
        out.append((bool(re.match(r"block-\d{2}$", bid)), f"[{bid}] BLOCK_ID oblika block-0N"))
        # vdelana slika v IMAGE celici
        img_ok = False
        for r in t.rows:
            if r.cells[0].text.strip() == "IMAGE" and len(r.cells) >= 2:
                img_ok = cell_has_image(r.cells[1]); break
        out.append((img_ok, f"[{bid}] IMAGE = vdelana slika (ne ime datoteke)"))
        # vsaj en BODY_P
        out.append((any(k.startswith("BODY_P") for k in d), f"[{bid}] vsaj en BODY_P"))
        # webinar => EVENT_*
        if d.get("BLOCK_TYPE", ("",))[0] == "webinar":
            out.append((all(k in d for k in ("EVENT_DATE","EVENT_TIME","EVENT_DURATION_MIN")),
                        f"[{bid}] webinar: EVENT_DATE/TIME/DURATION_MIN"))

    # TOC
    if toc is None:
        out.append((False, "TOC tabela MANJKA"))
    else:
        rows = toc.rows[1:]  # brez glave
        out.append((len(rows) == len(blocks), f"TOC vrstic == blokov: {len(rows)}=={len(blocks)}"))
        toc_ids = [r.cells[2].text.strip() for r in rows if len(r.cells) >= 3]
        out.append((set(toc_ids) == set(block_ids), f"TOC BLOCK_ID-ji ustrezajo blokom"))

    # CLOSING / SIGNOFF / PS
    out.append((closing is not None and "CLOSING_P1" in closing, "CLOSING tabela (CLOSING_TYPE + CLOSING_P1)"))
    out.append((signoff is not None and "SIGNOFF_PHRASE" in signoff and "SIGNOFF_NAME" in signoff, "SIGNOFF tabela (PHRASE + NAME)"))
    out.append((ps is not None and "PS_TEXT" in ps, "PS tabela (PS_TEXT)"))

    # brez inline povezav v telesu (samo CTA_URL sme biti povezava)
    body_cells = []
    for _, d in blocks:
        for k, (v, _c) in d.items():
            if k.startswith(("BODY_P","BULLET_")): body_cells.append(v)
    md_links = sum(len(re.findall(r"\]\(http", v)) for v in body_cells)
    out.append((md_links == 0, f"Inline markdown povezave v telesu: {md_links} (naj jih ne bo)"))

    # pain link (nasvet): natanko ena CTA naj cilja problem, ne branosti
    READING = ("/blog", "youtube.", "youtu.be", "spotify.", "podcast", "rastezanja")
    cta_urls = [d.get("CTA_URL", ("",))[0] for _, d in blocks]
    pain = [u for u in cta_urls if u and not any(p in u.lower() for p in READING)]
    out.append((len(pain) == 1,
                f"Pain link (CTA, ki izkazuje problem): {len(pain)} (cilj: 1; pri 0 mora pain signal nositi zaključek/PS – označi)"))

    # em dash povsod razen v SEGMENT_REF (tam je dopusten, ker je v vzorcu)
    seg = meta.get("SEGMENT_REF", ("",))[0] if meta else ""
    all_text = []
    for t in tables:
        for r in t.rows:
            for c in r.cells:
                all_text.append(c.text)
    em_total = sum(s.count("\u2014") for s in all_text)
    em_in_seg = seg.count("\u2014")
    out.append((em_total - em_in_seg == 0,
                f"Em dash zunaj SEGMENT_REF: {em_total - em_in_seg} (v SEGMENT_REF dopusten: {em_in_seg})"))

    # besedilni ulovi na hook + telo + closing + ps
    blob = []
    if hook: blob += [v for k, (v, _c) in hook.items() if k.startswith("HOOK_P")]
    blob += body_cells
    if closing: blob += [v for k, (v, _c) in closing.items() if k.startswith("CLOSING_P")]
    if ps: blob += [ps["PS_TEXT"][0]]
    out += check_text(" ".join(blob), lang)
    return out, lang

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--text", action="store_true", help="vhod je besedilo (.md/.txt), ne docx")
    args = ap.parse_args()

    if args.text or not args.path.lower().endswith(".docx"):
        text = open(args.path, encoding="utf8").read()
        results = check_text(text, args.lang or "si"); lang = args.lang or "si"
    else:
        results, lang = check_docx(args.path)
        if args.lang: lang = args.lang

    fails = sum(1 for ok, _ in results if not ok)
    print(f"\n=== eval_check ({lang}) — {args.path} ===")
    for ok, msg in results:
        print(f"  {OK if ok else WARN} {msg}")
    print(f"\n  Opozoril: {fails}. Vsako je nasvet, ne trdi blok — končni urednik je Igor.\n")

if __name__ == "__main__":
    main()
