#!/usr/bin/env python3
"""
style_check.py — mehanske kontrole za kolumno v Igorjevem slogu.

Uporaba:
    python style_check.py pot/do/kolumne.md

Skripta preverja SAMO stvari, ki se dajo izmeriti deterministično:
dolzino, prepovedane fraze in zargon, emoji, nastevanja, ritem stavkov,
tipografijo, stevilo podnaslovov. Presojo o glasu, "ucbeniku", sarkazmu
in o tem, ali kolumna ponudi resitev, opravi model sam — to ni naloga
skripte. Vsako opozorilo je nasvet, ne absolutna zapora; koncni urednik
je Igor.

Brez zunanjih odvisnosti — tece povsod, kjer je Python 3.
"""

import re
import sys

BANNED_PHRASES = [
    "v današnjem digitalnem svetu", "v današanjem digitalnem svetu",
    "v današnjem hitro spreminjajočem se okolju", "ključno je poudariti",
    "pomembno je omeniti", "ne smemo pozabiti", "vsi se strinjamo, da",
    "ni skrivnost, da", "kot vemo", "brez dvoma", "morda sem starokopiten",
    "če sem iskren", "v zaključku lahko rečemo", "sklepamo lahko",
    "poleg tega je pomembno poudariti", "kot rečeno", "poglejmo še drug primer",
    "tu je trik",
]
# enobesedne prepovedi — preverjamo z mejo besede, da ni laznih zadetkov
BANNED_WORDS = ["seveda"]
# 'razumem' je prepovedan samo kot mašilo (na začetku povedi: "Razumem, ..."),
# ne kot običajen glagol sredi stavka ("razumem trgovca" je legitimno)
FILLER_PATTERNS = [r"(?:^|[.!?…»«])\s*razumem\s*[,.!]"]

BANNED_JARGON = [
    "leverage", "synergy", "paradigm shift", "best practice", "game changer",
    "disruptive", "scalable", "agile", "ecosystem", "stakeholder", "holistic",
]

DISCOURAGED = [
    "bolečinska točka", "aha trenutek", "aha moment", "nizko viseče sadje",
    "na koncu dneva", "proaktiven pristop", "sinergija", "optimizacija procesov",
    "dodana vrednost", "strateški pristop", "holistični pogled",
]

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u2190-\u21FF\u2B00-\u2BFF\uFE0F]"
)


def strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def body_words(text):
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)   # markdown linki -> samo besedilo
    t = re.sub(r"[#>*`_]", " ", t)
    return re.findall(r"\b[\wščžćđ]+\b", t, flags=re.IGNORECASE)



# okrajšave in decimalke ne smejo deliti stavkov — piko zamenjamo z ne-delilnim znakom
_ABBREVS = [
    "npr.", "itd.", "ipd.", "oz.", "tj.", "t. i.", "št.", "mio.", "mrd.",
    "dr.", "prof.", "g.", "ga.", "str.", "gl.", "cca.", "d. o. o.", "d.o.o.",
    "e.g.", "i.e.", "etc.", "vs.", "Mr.", "Mrs.", "Ms.", "Dr.", "approx.",
    "tzv.", "tj.", "sl.", "engl.", "hrv.",
]
def _protect_dots(t):
    for ab in sorted(_ABBREVS, key=len, reverse=True):
        t = re.sub(re.escape(ab), ab.replace(".", "\u2024"), t, flags=re.IGNORECASE)
    t = re.sub(r"(\d)\.(\d)", "\\1\u2024\\2", t)   # decimalke: 4.1
    return t

def sentences(text):
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    t = re.sub(r"^#{1,6}.*$", "", t, flags=re.MULTILINE)   # podnaslovi ven
    t = re.sub(r"[#>*`_]", " ", t)
    parts = re.split(r"[.!?…]+", _protect_dots(t))
    out = []
    for p in parts:
        words = re.findall(r"\b[\wščžćđ]+\b", p, flags=re.IGNORECASE)
        if words:
            out.append(len(words))
    return out


def line(label, status, detail=""):
    mark = {"ok": "  OK  ", "warn": " WARN ", "info": " INFO "}[status]
    print(f"[{mark}] {label}" + (f"  —  {detail}" if detail else ""))


def main():
    if len(sys.argv) < 2:
        print("Uporaba: python style_check.py pot/do/kolumne.md")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        raw = f.read()

    text = strip_frontmatter(raw)
    low = text.lower()
    warns = 0

    print("=" * 64)
    print("STYLE CHECK —", sys.argv[1])
    print("=" * 64)

    # --- dolzina ---
    wc = len(body_words(text))
    if 900 <= wc <= 1300:
        line("Dolžina", "ok", f"{wc} besed (sladka točka 900–1.300)")
    elif 850 <= wc <= 1500:
        line("Dolžina", "info", f"{wc} besed (sprejemljivo; ideal 900–1.300)")
    else:
        line("Dolžina", "warn", f"{wc} besed (izven 850–1.500)")
        warns += 1

    # --- prepovedane fraze ---
    hits = [p for p in BANNED_PHRASES if p in low]
    hits += [w for w in BANNED_WORDS if re.search(rf"\b{re.escape(w)}\b", low)]
    hits += ["razumem (mašilo)" for pat in FILLER_PATTERNS if re.search(pat, low, flags=re.M)]
    if hits:
        line("Prepovedane fraze", "warn", ", ".join(hits))
        warns += 1
    else:
        line("Prepovedane fraze", "ok", "nobene")

    # --- zargon ---
    jhits = [j for j in BANNED_JARGON if re.search(rf"\b{re.escape(j)}\b", low)]
    if jhits:
        line("Prepovedani žargon", "warn", ", ".join(jhits))
        warns += 1
    else:
        line("Prepovedani žargon", "ok", "nobenega")

    # --- odsvetovane fraze ---
    dhits = [d for d in DISCOURAGED if d in low]
    if dhits:
        line("Odsvetovane fraze", "info", ", ".join(dhits) + " (razmisli o zamenjavi)")
    else:
        line("Odsvetovane fraze", "ok", "nobene")

    # --- emoji ---
    em = EMOJI.findall(text)
    if em:
        line("Emoji", "warn", f"{len(em)} najdenih — odstrani")
        warns += 1
    else:
        line("Emoji", "ok", "nobenega")

    # --- nastevanja ---
    bullets = len(re.findall(r"^\s*[-*]\s+", text, flags=re.MULTILINE))
    numbered = len(re.findall(r"^\s*\d+[.)]\s+", text, flags=re.MULTILINE))
    if bullets > 8:
        line("Naštevanja", "warn", f"{bullets} alinej — privzeto piši v prozi")
        warns += 1
    elif bullets or numbered:
        line("Naštevanja", "info", f"{bullets} alinej, {numbered} oštevilčenih — naj bo seznam res seznam")
    else:
        line("Naštevanja", "ok", "čista proza")

    # --- tipografija ---
    straight = text.count('"')
    if straight >= 2:
        line("Narekovaji", "warn", f'{straight}× ravni " — uporabi » «')
        warns += 1
    else:
        line("Narekovaji", "ok", "» « ali brez")

    # --- pomišljaj (—) ---
    # FrodX nikoli ne uporablja U+2014: kolumne/blog rabijo razmaknjen vezaj,
    # newslettri kratki pomišljaj (–). Vsak — je spodrsljaj (pogosto autocorrect).
    emdash = text.count("\u2014")
    if emdash:
        line("Pomišljaj (—)", "warn",
             f"{emdash}× U+2014 — zamenjaj z razmaknjenim vezajem ( - ) za "
             "kolumno; FrodX nikoli ne uporablja —")
        warns += 1
    else:
        line("Pomišljaj (—)", "ok", "nobenega")

    # --- podnaslovi ---
    h2 = len(re.findall(r"^##\s+", text, flags=re.MULTILINE))
    if 4 <= h2 <= 8:
        line("Podnaslovi (##)", "ok", f"{h2}")
    else:
        line("Podnaslovi (##)", "warn", f"{h2} (ciljaj 4–8)")
        warns += 1

    # --- ritem stavkov ---
    s = sentences(text)
    if s:
        avg = sum(s) / len(s)
        short = 100 * sum(1 for x in s if x <= 8) / len(s)
        long = 100 * sum(1 for x in s if x > 20) / len(s)
        detail = f"povpr. {avg:.1f} bes. | kratkih ≤8: {short:.0f}% | dolgih >20: {long:.0f}%"
        ok = (9 <= avg <= 13) and (35 <= short <= 58) and (long <= 22)
        line("Ritem stavkov", "ok" if ok else "info",
             detail + "  (cilj: ~11 bes., ~48% kratkih)")
        if not ok:
            warns += 1
    else:
        line("Ritem stavkov", "warn", "ni zaznanih stavkov")
        warns += 1

    # --- placeholderji ---
    ph = re.findall(r"\[VSTAVI[^\]]*\]", text)
    if ph:
        line("Vrzeli [VSTAVI]", "info", f"{len(ph)} — Igor mora vstaviti resnične podatke")

    # --- zakljucni CTA (igor.pauletic@frodx.com: en sam, sam v vrstici, na koncu) ---
    EMAIL = "igor.pauletic@frodx.com"
    nlines = [l.strip() for l in text.splitlines() if l.strip()]
    n_email = sum(l.lower().count(EMAIL) for l in nlines)
    email_idx = [i for i, l in enumerate(nlines) if EMAIL in l.lower()]
    if n_email == 0:
        line("Zaključni CTA", "warn",
             f"manjka obvezni '{EMAIL}' v svoji vrstici na koncu")
        warns += 1
    elif n_email > 1:
        line("Zaključni CTA", "warn",
             f"{n_email}× '{EMAIL}' — naj bo EN sam (edini CTA)")
        warns += 1
    else:
        idx = email_idx[0]
        # 'sam v vrstici' = vrstica je gol e-mail (dovolimo morebiten obkrožajoč markdown)
        alone = re.fullmatch(rf"[*_>\s]*{re.escape(EMAIL)}[*_\s]*", nlines[idx], flags=re.I) is not None
        near_end = idx >= len(nlines) - 4   # med zadnjimi vrsticami (dovoljen kratek P.S. za njo)
        if alone and near_end:
            line("Zaključni CTA", "ok", f"'{EMAIL}' sam na koncu")
        elif alone and not near_end:
            line("Zaključni CTA", "info",
                 f"'{EMAIL}' je sam, a ne na koncu — naj bo zadnji (pred morebitnim P.S.)")
        else:
            line("Zaključni CTA", "warn",
                 f"'{EMAIL}' naj stoji SAM v svoji vrstici (brez imena/besedila ob njem)")
            warns += 1

    print("-" * 64)
    if warns == 0:
        print("Rezultat: brez opozoril. Mehanske kontrole prestane.")
    else:
        print(f"Rezultat: {warns} opozoril. Preveri zgoraj — vsako je nasvet, ne zapora.")
    print("Opomba: glas, 'učbenik', sarkazem in rešitev oceni model/Igor, ne skripta.")
    print("=" * 64)


if __name__ == "__main__":
    main()
