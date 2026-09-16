from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-critique-loop" / "SKILL.md"


def test_zapis_kroga_vsebuje_poslani_prompt():
    """Brez zapisa prompta ni mogoče preveriti, ali je bil {{DANES}} zamenjan."""
    vsebina = SKILL.read_text(encoding="utf-8")
    assert '"critique_prompt"' in vsebina
