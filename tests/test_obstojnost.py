from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIRIGENT = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "SKILL.md"
SHEMA = DIRIGENT.parent / "references" / "state-schema.md"


def test_zapis_pred_potrditvijo():
    """Rezultat koraka gre v state.json takoj, ne šele ob Igorjevi potrditvi."""
    for pot in (DIRIGENT, SHEMA):
        vsebina = pot.read_text(encoding="utf-8")
        assert "takoj ob nastanku" in vsebina, pot.name
