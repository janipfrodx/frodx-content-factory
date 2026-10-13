#!/usr/bin/env python3
"""Paket Nikine zgodbe → markdown zavihka v Docu »Nikine zgodbe«.

Uporaba: python3 zavihek.py <state.json> [--celice]

Brez --celice izpiše markdown. Z --celice izpiše JSON vrstic tabele odločitve
in njihovih dovoljenih vrednosti za spustne sezname. Naslovi razdelkov so
fiksni, ker po njih bere iz_zavihka.py.
"""
import json
import sys
from pathlib import Path

RAZDELKI = ("Nikina odločitev", "Odprte oznake PREVERI", "Zgodba za blog", "LinkedIn", "Trditve", "Za Igorja")
SPUSTNI = {
    "Odločitev (Potrdi / Zavrni)": ["Potrdi", "Zavrni"],
    "Bi se tako odločila? (da / ne / drugače)": ["da", "ne", "drugače"],
    "Razlog zavrnitve (presoja / dejstvo / novost / slog)": ["presoja", "dejstvo", "novost", "slog"],
}
KOMENTAR = "Komentar"


def _brez_naslova(blog_md):
    vrstice = blog_md.split("\n")
    if vrstice and vrstice[0].startswith("# "):
        vrstice = vrstice[1:]
    return "\n".join(vrstice).strip("\n")


def _odstavki_vrstic(besedilo):
    """Vsaka neprazna vrstica svoj odstavek: Docs enojni prelom uvozi kot presledek, deli samo na prazno vrstico."""
    return "\n\n".join(v.strip() for v in besedilo.splitlines() if v.strip())


def _celica(niz):
    return str(niz).replace("|", "/").replace("\n", " ")


def zgradi(telo):
    z, v = telo["story"], telo["source"]
    deli = [
        f"# {z['title']}",
        "",
        f"Novost: {v['update_title']} | Status: {v['status']} | Dejavnost: {telo['activity']}",
        f"Vir: {', '.join(v['kb_urls'])}",
        "",
        f"## {RAZDELKI[0]}",
        "",
        "| Vprašanje | Odgovor |",
        "|---|---|",
        *[f"| {vrstica} |  |" for vrstica in (*SPUSTNI, KOMENTAR)],
        "",
        f"## {RAZDELKI[1]}",
        "",
        *([f"- [ ] {p['text']} ({p['where']})" for p in telo["preveri"]] or ["Ni odprtih oznak."]),
        "",
        f"## {RAZDELKI[2]}",
        "",
        _brez_naslova(z["blog_md"]),
        "",
        f"## {RAZDELKI[3]}",
        "",
        _odstavki_vrstic(z["linkedin_text"]),
        "",
        f"## {RAZDELKI[4]}",
        "",
        "| Kategorija | Trditev | Navedek | Povezava |",
        "|---|---|---|---|",
        *[f"| {t['category']} | {_celica(t['text'])} | {_celica(t.get('quote', ''))} | {t.get('url', '')} |" for t in telo["claims"]],
        "",
        f"## {RAZDELKI[5]}",
        "",
        f"- Ocena: {telo['score'].get('total')}",
        f"- Opozorila: {'; '.join(telo['warnings']) or 'ni'}",
        f"- Alternativna naslova: {' / '.join(z['alt_titles'])}",
        f"- Meta opis: {z['meta_description']}",
        "",
    ]
    return "\n".join(deli)


def main(argv):
    if len(argv) not in (2, 3) or (len(argv) == 3 and argv[2] != "--celice"):
        print("Uporaba: zavihek.py <state.json> [--celice]")
        return 1
    if len(argv) == 3:
        print(json.dumps(SPUSTNI, ensure_ascii=False, indent=2))
        return 0
    telo = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    print(zgradi(telo), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
