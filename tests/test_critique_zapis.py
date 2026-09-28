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


PROMPTA = (
    REPO / "plugins" / "content-factory" / "skills" / "frodx-critique-loop" / "references" / "critique-prompt.md",
    REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik"
    / "references" / "critique-prompt.md",
)


def test_poslje_samo_prompt_pod_crto():
    assert "samo besedilo pod prvo vrstico `---`" in SKILL.read_text(encoding="utf-8")


def test_klic_ima_trigger():
    assert '"triggerNodeName": "Trigger"' in SKILL.read_text(encoding="utf-8")


def test_bere_odgovor_webhooka_ne_izvedbe():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "Respond to Webhook" in vsebina
    assert "Preberi izhod prek `get_execution`" not in vsebina
    assert '"openai_error": null, "gemini_error": null}' in vsebina


def test_prazna_sodba_ni_glas():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "**Prazna sodba ni glas.**" in vsebina
    assert "prazna sodba: <dobesedni odgovor>" in vsebina


def test_zavrnjene_pripombe_gredo_v_naslednji_krog():
    vsebina = SKILL.read_text(encoding="utf-8")
    naslov = "## Zavrnjene pripombe iz prejšnjih krogov"
    assert naslov in vsebina
    assert "razdelka ne dodaš" in vsebina
    for prompt in PROMPTA:
        assert naslov.removeprefix("## ") in prompt.read_text(encoding="utf-8"), prompt


def test_prompt_se_med_krogi_ne_razglasa_za_enakega():
    assert "Prompt je v vseh krogih enak" not in SKILL.read_text(encoding="utf-8")


def test_verzija_kritike():
    assert "version: 0.3.0" in SKILL.read_text(encoding="utf-8")
