import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "plugins" / "content-factory" / "skills" / "frodx-transcreation-check"
PROMPT = SKILL_DIR / "references" / "transcreation-check-prompt.md"


def test_prompt_pozna_obe_sodbi():
    """Dvobesedni protokol je isti kot pri kritiki - brez njega se sodba ne da prebrati."""
    vsebina = PROMPT.read_text(encoding="utf-8")
    assert "OBJAVLJIVO" in vsebina
    assert "ZA POPRAVEK" in vsebina


def test_prompt_ima_oznako_za_datum():
    """Brez datuma ocenjevalec pravilne letnice razglasi za halucinacije (15. 8. 2026)."""
    assert "{{DANES}}" in PROMPT.read_text(encoding="utf-8")


def test_prompt_loci_merila_po_jezikih():
    """Hrvaščina in angleščina padeta na različnih stvareh; en sam splošen seznam ju zlije."""
    vsebina = PROMPT.read_text(encoding="utf-8").lower()
    for pojem in ("dvojin", "srbiz", "klijent", "korisnik", "kupac"):
        assert pojem in vsebina, pojem
    for pojem in ("idiom", "phrasal", "cee"):
        assert pojem in vsebina, pojem
