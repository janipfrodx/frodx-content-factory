from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-critique-loop" / "SKILL.md"


def test_zapis_kroga_vsebuje_poslani_prompt():
    """Brez zapisa prompta ni mogoče preveriti, ali je bil {{DANES}} zamenjan."""
    vsebina = SKILL.read_text(encoding="utf-8")
    assert '"critique_prompt"' in vsebina
import re

DOSTAVNA_POT = REPO / "docs" / "dostavna-pot.md"


def _razdelek_dostavne_poti(ime):
    vsebina = DOSTAVNA_POT.read_text(encoding="utf-8")
    zacetek = vsebina.index(f"## `{ime}`")
    ostanek = vsebina[zacetek + 4:]
    konec = ostanek.find("\n## ")
    return ostanek if konec == -1 else ostanek[:konec]


def test_dostavna_pot_opisuje_odgovor_critique_text():
    razdelek = _razdelek_dostavne_poti("critique-text")
    assert "- workflowId: `GZmnPGOcVANH2sfy`" in razdelek
    for polje in ("openai", "gemini", "openai_error", "gemini_error"):
        assert f"`{polje}`" in razdelek, polje
    assert "Respond to Webhook" in razdelek
    assert "responseNode" in razdelek
    zadetek = re.search(r'"workflowId":\s*"([^"]+)"', SKILL.read_text(encoding="utf-8"))
    assert zadetek and zadetek.group(1) == "GZmnPGOcVANH2sfy"
