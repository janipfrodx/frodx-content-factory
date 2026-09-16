from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-image-run" / "SKILL.md"
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
