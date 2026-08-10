#!/usr/bin/env python3
"""
transcreation_check.py — mechanical checks for a FrodX transcreation.

Usage:
    python transcreation_check.py --lang en path/to/draft.md
    python transcreation_check.py --lang hr path/to/draft.md
    python transcreation_check.py --lang sl path/to/draft.md   (source / reference)

Checks ONLY what is deterministic: forbidden phrases (per language),
percent spacing, straight quotes, em dash, emoji, bullet overload, sentence
rhythm, and (for Croatian) a few Serbian-form traps. Voice, "does it read
native", and whether it still sounds like Igor are judged by the model and
Igor — not by this script. Every line is advice, not a hard block; final
editor is Igor.

No external dependencies. Runs anywhere with Python 3.
"""

import argparse
import re
import sys

FORBIDDEN = {
    "en": [
        "in today's digital world", "in today’s digital world",
        "it is important to emphasize", "added value", "pain point",
        "strategic approach", "proactive approach", "process optimization",
        "holistic view", "synergy", "stakeholder", "paradigm shift",
        "best practice", "game changer", "at the end of the day",
        "low-hanging fruit", "in conclusion", "as we all know", "to be honest",
        "not only", "cutting-edge", "seamless", "robust", "transformative",
    ],
    "hr": [
        "u današnjem digitalnom svijetu", "važno je naglasiti",
        "dodana vrijednost", "bolna točka", "strateški pristup",
        "proaktivan pristup", "optimizacija procesa", "holistički pogled",
        "sinergija", "promjena paradigme", "najbolja praksa", "game changer",
        "na kraju dana", "nisko viseće voće", "zaključno možemo reći",
        "kao što znamo",
    ],
    "sl": [
        "v današnjem digitalnem svetu", "ključno je poudariti",
        "dodana vrednost", "bolečinska točka", "strateški pristop",
        "proaktiven pristop", "optimizacija procesov", "holistični pogled",
        "sinergija", "na koncu dneva", "nizko viseče sadje",
        "v zaključku lahko rečemo", "kot vemo", "če sem iskren",
        "morda sem starokopiten",
    ],
}
# single words checked with word boundaries to avoid false hits
BANNED_WORDS = {
    "en": ["leverage", "scalable", "agile", "disruptive", "ecosystem"],
    "hr": ["leverage", "leveraging"],
    "sl": ["seveda", "razumem", "leverage", "stakeholder", "holistic"],
}
# Cold-tell calques (info only): high-signal literal-transfer artifacts.
# Conservative list — the full Cold tell-sweep is a model-run gate (quality-gates.md).
COLD_TELLS = {
    "en": [
        "it is about", "this is about",            # SL "gre za"
        "on the other side",                       # -> "on the other hand"
        "in the frame of", "in the framework of",  # SL "v okviru"
        "from the side of",                        # SL "s strani"
    ],
    "hr": [],
    "sl": [],
}
# Serbian forms that betray non-native Croatian (info only)
SERBIAN_TRAPS = [
    "saradnja", "hiljada", "hiljade", "uslov", "uslovi", "tačno", "tačan",
    "vesti", "mleko", "vreme", "nedelja", "uopšteno", "decembar", "januar",
    "februar", "kompanija", "hleb",
]

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u2B00-\u2BFF\uFE0F]"
)


def strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def body_words(text):
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    t = re.sub(r"[#>*`_]", " ", t)
    return re.findall(r"\b[\w\u0100-\u024fščžćđ]+\b", t, flags=re.IGNORECASE)



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
    t = re.sub(r"^#{1,6}.*$", "", t, flags=re.MULTILINE)
    t = re.sub(r"[#>*`_]", " ", t)
    out = []
    for p in re.split(r"[.!?…]+", _protect_dots(t)):
        w = re.findall(r"\b[\w\u0100-\u024fščžćđ]+\b", p, flags=re.IGNORECASE)
        if w:
            out.append(len(w))
    return out


def line(label, status, detail=""):
    mark = {"ok": "  OK  ", "warn": " WARN ", "info": " INFO "}[status]
    print(f"[{mark}] {label}" + (f"  —  {detail}" if detail else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, choices=["en", "hr", "sl"])
    ap.add_argument("path")
    args = ap.parse_args()

    with open(args.path, encoding="utf-8") as f:
        raw = f.read()
    text = strip_frontmatter(raw)
    low = text.lower()
    lang = args.lang
    warns = 0

    print("=" * 64)
    print(f"TRANSCREATION CHECK [{lang}] —", args.path)
    print("=" * 64)

    # length — informational (transcreation length tracks source/medium)
    wc = len(body_words(text))
    line("Length", "info", f"{wc} words (no fixed target; follows source/medium)")

    # forbidden phrases
    hits = [p for p in FORBIDDEN[lang] if p in low]
    hits += [w for w in BANNED_WORDS[lang]
             if re.search(rf"\b{re.escape(w)}\b", low)]
    if hits:
        line("Forbidden phrases/jargon", "warn", ", ".join(sorted(set(hits))))
        warns += 1
    else:
        line("Forbidden phrases/jargon", "ok", "none")

    # cold-tell calques (info only; full sweep is a model-run gate)
    ct = [p for p in COLD_TELLS.get(lang, []) if p in low]
    if ct:
        line("Cold tells (kalk?)", "info",
             ", ".join(sorted(set(ct))) + " — preveri, ali ni dobesedni prenos iz SL")

    # percent spacing
    if lang == "en":
        bad = re.findall(r"\d\s+%", text)
        if bad:
            line("Percent spacing", "warn",
                 f"{len(bad)}× space before % — English uses 70%, not 70 %")
            warns += 1
        else:
            line("Percent spacing", "ok", "no space (70%)")
    else:
        bad = re.findall(r"\d%", text)
        if bad:
            line("Percent spacing", "warn",
                 f"{len(bad)}× missing space before % — {lang} uses 70 %")
            warns += 1
        else:
            line("Percent spacing", "ok", "space before % (70 %)")

    # straight quotes
    straight = text.count('"')
    if straight >= 2:
        want = {"en": "“ ”", "hr": "„ ”", "sl": "» «"}[lang]
        line("Quotation marks", "warn",
             f'{straight}× straight " — use {want}')
        warns += 1
    else:
        line("Quotation marks", "ok", "typographic or none")

    # em dash — FrodX never uses U+2014: newsletters use en dash (–),
    # blog/columns use a spaced hyphen. So any — is a slip (often autocorrect).
    emdash = text.count("\u2014")
    if emdash:
        line("Em dash (—)", "warn",
             f"{emdash}× U+2014 — swap to en dash (–) for newsletters, "
             "spaced hyphen for blog; FrodX never uses —")
        warns += 1
    else:
        line("Em dash (—)", "ok", "none")

    # emoji
    em = EMOJI.findall(text)
    if em:
        line("Emoji", "warn", f"{len(em)} found — remove")
        warns += 1
    else:
        line("Emoji", "ok", "none")

    # bullets
    bullets = len(re.findall(r"^\s*[-*]\s+", text, flags=re.MULTILINE))
    if bullets > 8:
        line("Bullets", "warn", f"{bullets} — default to prose")
        warns += 1
    elif bullets:
        line("Bullets", "info", f"{bullets} — make sure a list is really a list")
    else:
        line("Bullets", "ok", "clean prose")

    # Serbian traps (Croatian only)
    if lang == "hr":
        st = [w for w in SERBIAN_TRAPS
              if re.search(rf"\b{re.escape(w)}\b", low)]
        if st:
            line("Serbian-form traps", "info",
                 ", ".join(sorted(set(st))) + " (use Croatian form unless a quote)")

    # Croatian-specific review flags (info; high-value lexical/grammar slips)
    if lang == "hr":
        if re.search(r"\bštedionic", low):
            line("HR: 'štedionica'", "info",
                 "za 'building society' rabi 'građevinsko društvo' (ali ostavi izvorni 'building society')")
        if re.search(r"\bpult", low):
            line("HR: 'pult'", "info",
                 "u poslovnom kontekstu vjerojatno 'tvrtke'/'brendovi', ne 'pult'")
        aux = r"(?:je|su|sam|si|smo|ste|bih|bi|bismo|biste)"
        miss = []
        for m in re.finditer(r"\b(me|te|ga|nas|vas|ih|se)\s+(\w{4,}(?:la|lo))\b",
                             text, flags=re.IGNORECASE):
            before = text[max(0, m.start()-14):m.start()].lower()
            after = text[m.end():m.end()+8].lower()
            if re.search(r"\b"+aux+r"\s*$", before) or re.search(r"^\s*"+aux+r"\b", after):
                continue
            miss.append(m.group(0))
        if miss:
            line("HR: perfekt brez pomožnika?", "info",
                 ", ".join(miss[:4]) + " — preveri 'je/su' (npr. 'me je dovela', ne 'me dovela')")

    # rhythm — advisory; meaningful for editorial registers
    s = sentences(text)
    if s:
        avg = sum(s) / len(s)
        short = 100 * sum(1 for x in s if x <= 8) / len(s)
        lng = 100 * sum(1 for x in s if x > 20) / len(s)
        detail = (f"avg {avg:.1f} w | short ≤8: {short:.0f}% | long >20: {lng:.0f}%"
                  "  (editorial target: ~11 w, ~48% short — NOT 15–18)")
        ok = (8.5 <= avg <= 13) and (35 <= short <= 60) and (lng <= 22)
        line("Rhythm (editorial)", "ok" if ok else "info", detail)

    # placeholders
    ph = re.findall(r"\[VSTAVI[^\]]*\]", text)
    if ph:
        line("Gaps [VSTAVI]", "info", f"{len(ph)} — Igor must fill real data")

    print("-" * 64)
    if warns == 0:
        print("Result: no warnings. Mechanical checks pass.")
    else:
        print(f"Result: {warns} warning(s). Each is advice, not a block.")
    print("Note: voice, 'reads native', and Igor-fidelity are judged by the model/Igor.")
    print("=" * 64)


if __name__ == "__main__":
    main()
