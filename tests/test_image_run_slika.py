import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-image-run" / "SKILL.md"
PREIZKUSI = (
    REPO / "plugins" / "content-factory" / "skills" / "frodx-image-run"
    / "docs" / "preizkusi-image-run.md"
)
SHEMA = (
    REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory"
    / "references" / "state-schema.md"
)


def test_skill_zahteva_izmero_in_prag():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "dimenzije.py" in vsebina
    assert "1200" in vsebina


def test_skill_in_shema_poznata_rubriko():
    vsebina = SKILL.read_text(encoding="utf-8")
    for kljuc in ("dimensions", "rubric", "koncept", "anti_slop", "brand_fit"):
        assert kljuc in vsebina, kljuc
    assert "rubric" in SHEMA.read_text(encoding="utf-8")


def test_izbrana_slika_je_ena_sama_datoteka():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "izbrana.<pripona>" in vsebina
    assert "ena sama pripona" in vsebina
    assert "izbrana.png" not in vsebina
    assert "znova prekopiraj izbrano sliko" in vsebina


def test_navodilo_za_preizkus_se_ujema_s_skillom():
    vsebina = PREIZKUSI.read_text(encoding="utf-8")
    assert "get_execution" in vsebina
    assert "ne vrne" in vsebina
    assert "dimenzije.py" in vsebina
    assert "1200x630" in vsebina
    assert "ena sama pripona" in vsebina
    assert "znova prekopira" in vsebina


def test_skill_bere_url_iz_odgovora_workflowa():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "openai" in vsebina and "url" in vsebina
    assert "curl" in vsebina, "skill mora povedati, kako sliko prenese na disk"
    assert "SharePoint" not in vsebina, "SharePoint pot je odstranjena"
    assert "filesystem-v2" not in vsebina, "opis mrtve poti prek get_execution je odstranjen"


def _vrstica_sheme(kljuc: str) -> str:
    """Tabelna vrstica sheme za dani ključ `_run`. Prazen niz, če je ni."""
    for vrstica in SHEMA.read_text(encoding="utf-8").splitlines():
        if vrstica.startswith(f"| `{kljuc}` |"):
            return vrstica
    return ""


def test_shema_pozna_url_izbrane_slike():
    """`assert "url" in SHEMA` bi prehajal zaradi `edit_url` v vrstici `delivery`.

    Zato se trdi o vrstici `image` in o polni poti `_run.image.url`.
    """
    vrstica = _vrstica_sheme("image")
    assert vrstica, "shema nima vrstice za `image`"
    zadetek = re.search(r"\{([^}]+)\}", vrstica)
    assert zadetek, "vrstica `image` ne našteva polj v zavitih oklepajih"
    polja = {p.strip() for p in zadetek.group(1).split(",")}
    assert polja == {"chosen", "url", "attempts", "dimensions", "rubric", "reason"}, polja
    assert "_run.image.url" in SHEMA.read_text(encoding="utf-8")
