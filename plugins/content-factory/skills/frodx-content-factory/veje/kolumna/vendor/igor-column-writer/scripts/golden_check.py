#!/usr/bin/env python3
"""
golden_check.py — regresijski test skilla na korpusu objavljenih kolumn.

Uporaba:
    python golden_check.py            # privzeto references/golden/*.md

Namen: vsaka sprememba style_check.py ali pravil skilla se preveri na
resničnem korpusu Igorjevih objavljenih kolumn. Korpus je starejši od
nekaterih današnjih pravil (npr. prepoved "tu je trik", emoji, naštevanja),
zato runner pozna ZGODOVINSKA ODSTOPANJA in jih poroča kot info, ne kot
napako. Napaka je samo:
  - NOVA prepovedana fraza, ki je ni na seznamu znanih zadetkov, ali
  - ritem korpusa izven razumnega pasu (znak, da je merjenje pokvarjeno).

Tier A = nedavne kolumne, merilo današnjega standarda (ritem + glas).
Tier B = starejše kolumne, samo ritmična referenca.
"""

import glob
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "..", "references", "golden")
SC_PATH = os.path.join(HERE, "style_check.py")

spec = importlib.util.spec_from_file_location("style_check", SC_PATH)
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

# Znana zgodovinska odstopanja: fraza/vzorec -> datoteke, kjer je pričakovan.
# Korpus je nastal PRED uvedbo teh pravil; v NOVIH kolumnah so to napake.
KNOWN_HITS = {
    "tu je trik": {"01-", "02-", "04-", "05-"},
    "seveda": {"09-", "12-"},
    "emoji": {"10-", "11-", "12-"},
}

# Razumni pas za ritem korpusa (če merjenje pade ven, je pokvarjen splitter,
# ne korpus): povprečje besed/stavek in delež kratkih stavkov (<=8 besed).
CORPUS_AVG_RANGE = (8.0, 16.0)
CORPUS_SHORT_RANGE = (0.20, 0.60)


def strip_front(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def main():
    files = sorted(glob.glob(os.path.join(GOLDEN, "*.md")))
    if not files:
        print("Ni fikstur v", GOLDEN)
        return 1

    failures = []
    all_lens, a_lens = [], []
    print(f"{'datoteka':38} {'tier':4} {'stavki':>6} {'povp':>6} {'kratki':>7} {'dolgi':>6}")
    for f in files:
        name = os.path.basename(f)
        raw = open(f, encoding="utf-8").read()
        tier = "A" if "tier: A" in raw else "B"
        text = strip_front(raw)
        lens = sc.sentences(text)
        low = text.lower()

        avg = sum(lens) / len(lens)
        short = sum(1 for x in lens if x <= 8) / len(lens)
        long_ = sum(1 for x in lens if x > 20) / len(lens)
        all_lens += lens
        if tier == "A":
            a_lens += lens
        print(f"{name:38} {tier:4} {len(lens):6d} {avg:6.1f} {short:6.0%} {long_:6.0%}")

        # prepovedane fraze: nove = napaka, znane = info
        for ph in sc.BANNED_PHRASES:
            if ph in low:
                pref = name[:3]
                if pref in KNOWN_HITS.get(ph, set()):
                    print(f"    [zgodovinsko] '{ph}' — pričakovano v tem korpusu")
                else:
                    failures.append(f"{name}: NOVA prepovedana fraza '{ph}'")
        for w in sc.BANNED_WORDS:
            if re.search(rf"\b{w}\b", low):
                pref = name[:3]
                if pref in KNOWN_HITS.get(w, set()):
                    print(f"    [zgodovinsko] beseda '{w}'")
                else:
                    failures.append(f"{name}: NOVA prepovedana beseda '{w}'")
        if sc.EMOJI.search(text):
            if name[:3] in KNOWN_HITS["emoji"]:
                print("    [zgodovinsko] emoji")
            else:
                failures.append(f"{name}: NOV emoji")

    def stats(lens):
        avg = sum(lens) / len(lens)
        return avg, sum(1 for x in lens if x <= 8) / len(lens)

    avg_all, short_all = stats(all_lens)
    avg_a, short_a = stats(a_lens) if a_lens else (0, 0)
    print("-" * 72)
    print(f"KORPUS (vse):    povp {avg_all:.1f} bes/stavek, kratkih {short_all:.0%}")
    print(f"KORPUS (tier A): povp {avg_a:.1f} bes/stavek, kratkih {short_a:.0%}  <- merilo glasu")

    if not (CORPUS_AVG_RANGE[0] <= avg_all <= CORPUS_AVG_RANGE[1]):
        failures.append(f"korpusno povprečje {avg_all:.1f} izven pasu {CORPUS_AVG_RANGE}")
    if not (CORPUS_SHORT_RANGE[0] <= short_all <= CORPUS_SHORT_RANGE[1]):
        failures.append(f"delež kratkih {short_all:.0%} izven pasu {CORPUS_SHORT_RANGE}")

    if failures:
        print("\nNAPAKE:")
        for x in failures:
            print(" -", x)
        return 1
    print("\nOK: regresija čista (zgodovinska odstopanja so znana in označena).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
