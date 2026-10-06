#!/usr/bin/env python3
"""Deterministična kontrola Nikine zgodbe (nika-update-writer v1.1.1). Python 3, brez odvisnosti.

Uporaba:
  python3 check.py zgodba.md               # golo besedilo zgodbe
  python3 check.py zgodba.md --blog        # blog: en naslov (# ...), do 4 podnaslovi (## ...), vsaj ena povezava, zadnja vrstica e-naslov
  python3 check.py zgodba.md --linkedin    # LinkedIn: brez naslova, podnaslovov, e-naslova in povezav
  python3 check.py zgodba.md --prev MAPA   # mapa prejšnjih zgodb za test ponovljenih formul
Izhodna koda 0 = brez napak (opozorila so dovoljena), 1 = napaka.
"""
import re, sys, os, glob

FORBIDDEN = [
    "tu je trik", "here's the trick", "here is the trick", "ovdje je trik",
    "v današnjem digitalnem svetu", "revolucionar", "game changer", "game-changer",
    "izkoristite polni potencial", "dvignite na višjo raven", "brezhibn", "seamless",
    "leverage", "v enem koraku do", "preprosto in učinkovito", "ni skrivnost, da",
    "kot vsi vemo", "na koncu dneva", "tu bi se marsikdo ustavil", "best practice",
    "touchpoint", "nurturati", "nurturanje",
]
# Nikin my-writing-style, razdelek Blog: retorični vložki so prepovedani
RHETORIC = ["predstavljajte si", "zdaj boste rekli", "zdaj boste morda rekli",
            "ne tako hitro", "ključno vprašanje je"]
# formule, ki so dobre enkrat in se v naslednji zgodbi ne ponovijo
FORMULAS = ["vzemimo", "logično vprašanje je", "drugače bi ravnala", "sama bi",
            "če pri vas", "kljub temu da", "vaše številke bodo"]
TIME_PHRASES = ["ta teden", "ta mesec", "pravkar", "danes je", "včeraj", "te dni", "ravnokar"]
MIN_W, TARGET_W, WARN_W, MAX_W = 300, 400, 430, 450
MAX_SUBS = 4
EMAIL = "nika.bratuz@frodx.com"
LINK_MD = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
URL = re.compile(r"https?://\S+")

def strip_links(text):
    return URL.sub("", LINK_MD.sub(r"\1", text))

def words(text):
    text = re.sub(r"\[PREVERI:[^\]]*\]", "", text)
    return len(re.findall(r"\S+", strip_links(text)))

def story_part(raw):
    return raw.split("\n---\n", 1)[-1] if "\n---\n" in raw else raw

def norm(s):
    return re.sub(r"\s+", " ", strip_links(s).strip().lower())

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)
    path = args[0]
    mode = "blog" if "--blog" in args else "linkedin" if "--linkedin" in args else "plain"
    prev_dir = args[args.index("--prev") + 1] if "--prev" in args else None
    raw = story_part(open(path, encoding="utf-8").read()).strip()
    errors, warns = [], []

    lines = raw.split("\n")
    title = [l for l in lines if l.startswith("# ")]
    subs = [l for l in lines if l.startswith("## ")]
    body_lines = [l for l in lines if not l.startswith("#")]
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    last = body_lines[-1].strip() if body_lines else ""
    if last == EMAIL:
        body_lines = body_lines[:-1]
    body = "\n".join(body_lines).strip()

    if mode == "blog":
        if len(title) != 1: errors.append("blog: potreben natanko en naslov (# ...)")
        if len(subs) > MAX_SUBS: errors.append(f"blog: največ {MAX_SUBS} podnaslovi (## ...)")
        if last != EMAIL: errors.append("blog: zadnja vrstica mora biti " + EMAIL)
        if not (LINK_MD.search(body) or URL.search(body)):
            errors.append("blog: nobene povezave na vir v besedilu")
    elif mode == "linkedin":
        if title or subs: errors.append("linkedin: brez naslova in podnaslovov")
        if EMAIL in raw: errors.append("linkedin: brez e-naslova v objavi")
        if URL.search(body): errors.append("linkedin: povezava gre v prvi komentar, ne v objavo")

    n = words(body)
    if n > MAX_W: errors.append(f"dolžina {n} besed > {MAX_W}")
    elif n > WARN_W: warns.append(f"dolžina {n} besed > {WARN_W}; cilj je okoli {TARGET_W}")
    if n < MIN_W: errors.append(f"dolžina {n} besed < {MIN_W}")

    if "\u2014" in raw: errors.append("dolgi pomišljaj (U+2014)")
    if re.search(r"\s–\s", raw): warns.append("en dash kot vrinek; na blogu razmaknjen vezaj ( - )")
    plain = strip_links(body)
    if "!" in plain: errors.append("klicaj v telesu")
    if re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", plain): errors.append("emoji")
    if re.search(r"\*\*|__", plain): errors.append("krepki tisk v telesu")
    if re.search(r"(?m)^\s*([-*•]|\d+\.)\s", plain): errors.append("seznam v telesu")
    if re.search(r"(?<!\w)#\w", plain): errors.append("ključnik v telesu")
    if re.search(r'(?<![»\w])"', plain): warns.append('ravni narekovaji; uporabi » «')

    low = plain.lower()
    for f in FORBIDDEN:
        if f in low: errors.append(f"prepovedana fraza: »{f}«")
    for r in RHETORIC:
        if r in low: errors.append(f"retorični vložek, ki ga Nika ne uporablja: »{r}«")
    for t in TIME_PHRASES:
        if re.search(r"\b" + re.escape(t) + r"\b", low): errors.append(f"časovna trditev brez datuma: »{t}«")

    paras = [p.strip() for p in re.split(r"\n\s*\n", plain) if p.strip()]
    first = paras[0].lower() if paras else ""
    if first.startswith("kljub"):
        errors.append("uvod začne s »Kljub ...« (Nikin register za strokovne dokumente, ne za blog)")
    if re.match(r"^\s*hubspot\b", first): errors.append("prva poved začne s HubSpotom kot subjektom")
    if paras and not re.search(r"(napišite|sporočite|opišite|povejte|pišite)", paras[-1].lower()):
        errors.append("zadnji odstavek ni vabilo bralcu")
    for p in paras:
        if len(re.findall(r"[.?](\s|$)", p)) > 6: warns.append("odstavek z več kot šestimi povedmi: " + p[:40] + "...")
        for s in re.split(r"(?<=[.?])\s+", p):
            sw = re.findall(r"\w+", s)
            if 0 < len(sw) < 6 and not re.match(r"^\d", s):
                warns.append("aforistična poved do pet besed (Nika misel izpiše): »" + s.strip() + "«")

    scen = re.search(r"(vzemimo|scenarij|recimo|če imate|če ima|denimo)", low)
    MONTHS = r"(jan|feb|mar|apr|maj|jun|jul|avg|sept|okt|nov|dec)"
    nodates = re.sub(r"\b\d{1,2}\.\s?" + MONTHS + r"\w*", "", plain, flags=re.I)
    nodates = re.sub(r"\b(19|20)\d{2}\b", "", nodates)
    first_num = re.search(r"\b\d{2,}\b", nodates)
    if first_num and (not scen or first_num.start() < scen.start()):
        snippet = nodates[max(0, first_num.start()-30):first_num.start()+20].replace("\n", " ")
        warns.append("številka pred oznako scenarija (preveri, ali je iz vira): ..." + snippet + "...")

    # formule in začetki odstavkov proti prejšnjim zgodbam
    here = os.path.dirname(os.path.abspath(__file__))
    prev_files = glob.glob(os.path.join(here, "..", "references", "primeri", "*.md"))
    if prev_dir:
        prev_files += glob.glob(os.path.join(prev_dir, "*.md")) + glob.glob(os.path.join(prev_dir, "*.txt"))
    used, starts = set(), set()
    for pf in prev_files:
        if os.path.abspath(pf) == os.path.abspath(path): continue
        pt = story_part(open(pf, encoding="utf-8").read())
        if norm(pt) == norm(raw): continue
        ptl = strip_links(pt).lower()
        used |= {f for f in FORMULAS if f in ptl}
        for pp in re.split(r"\n\s*\n", ptl):
            w = re.findall(r"\w+", pp)
            if len(w) >= 5 and not pp.lstrip().startswith("#"): starts.add(" ".join(w[:5]))
    for f in FORMULAS:
        if f in low and f in used:
            warns.append(f"formula iz prejšnje zgodbe: »{f}«; zamenjaj ubeseditev")
    for p in paras:
        w = re.findall(r"\w+", p.lower())
        if len(w) >= 5 and " ".join(w[:5]) in starts:
            warns.append("ponovljen začetek odstavka iz prejšnje zgodbe: »" + " ".join(w[:5]) + "«")

    for e in errors: print("NAPAKA:", e)
    for w in warns: print("opozorilo:", w)
    print(f"besed: {n} (cilj ~{TARGET_W}, meja {MAX_W}); način: {mode}")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
