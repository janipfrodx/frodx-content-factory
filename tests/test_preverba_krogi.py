from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "plugins" / "content-factory" / "skills" / "frodx-transcreation-check"
SKILL = SKILL_DIR / "SKILL.md"
PROMPT = SKILL_DIR / "references" / "transcreation-check-prompt.md"


def test_poslje_samo_prompt_pod_crto():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "samo besedilo pod prvo vrstico `---`" in vsebina
    assert "transcreation-check-prompt.md` v celoti" not in vsebina


def test_krog_2_dobi_zavrnjene_najdbe_kroga_1():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "## Zavrnjene najdbe iz kroga 1" in vsebina
    assert "razdelka ne dodaš" in vsebina
    assert "Zavrnjene najdbe iz kroga 1" in PROMPT.read_text(encoding="utf-8")


def test_verzija_preverbe():
    assert "version: 0.3.0" in SKILL.read_text(encoding="utf-8")


def test_brez_dolgega_pomisljaja():
    assert "\u2014" not in SKILL.read_text(encoding="utf-8")
