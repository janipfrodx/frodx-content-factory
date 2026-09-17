import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOSTAVNA_POT = REPO / "docs" / "dostavna-pot.md"
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-publish-send" / "SKILL.md"
SHEMA = (
    REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory"
    / "references" / "state-schema.md"
)


def test_skill_preda_prek_cf_deliver_draft():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "cf-deliver-draft" in vsebina
    assert "execute_workflow" in vsebina


def test_skill_ne_sestavlja_vec_base64():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "kodiran v base64" not in vsebina
    assert "mime_type" not in vsebina
    assert "FRODX_APP_API_KEY" not in vsebina
    assert "/api/ingest" not in vsebina, "stari kontrakt PROD 2 ne sodi v ta skill"
    assert "Idempotency-Key" not in vsebina, "idempotenco nosi run_slug v bazi"


def test_skill_pozna_vse_stiri_izide():
    vsebina = SKILL.read_text(encoding="utf-8")
    for izid in ("created", "duplicate", "rejected", "misconfigured", "retry"):
        assert izid in vsebina, izid


def test_shema_pozna_delivery():
    """Gola beseda `delivery` ne pove nič - trdi se o poljih v njeni vrstici."""
    vrstica = next(
        (v for v in SHEMA.read_text(encoding="utf-8").splitlines() if v.startswith("| `delivery` |")),
        "",
    )
    assert vrstica, "shema nima vrstice za `delivery`"
    for polje in ("status", "draft_id", "edit_url", "delivered_at"):
        assert polje in vrstica, polje


def _id_iz_dostavne_poti() -> str:
    """workflowId iz razdelka `## `cf-deliver-draft`` v docs/dostavna-pot.md."""
    v_razdelku = False
    for vrstica in DOSTAVNA_POT.read_text(encoding="utf-8").splitlines():
        if vrstica.startswith("## "):
            v_razdelku = "cf-deliver-draft" in vrstica
            continue
        if v_razdelku:
            zadetek = re.match(r"- workflowId: `([^`]+)`", vrstica.strip())
            if zadetek:
                return zadetek.group(1)
    return ""


def test_workflow_id_v_skillu_se_ujema_z_dostavno_potjo():
    """Skill nosi ID dobesedno; nič ga doslej ni vezalo na kanonični vir.

    Če se ID v `docs/dostavna-pot.md` spremeni, skill ne sme ostati na starem.
    """
    kanonicni = _id_iz_dostavne_poti()
    assert kanonicni, "docs/dostavna-pot.md nima workflowId v razdelku cf-deliver-draft"
    zadetek = re.search(r'"workflowId":\s*"([^"]+)"', SKILL.read_text(encoding="utf-8"))
    assert zadetek, "SKILL.md ne vsebuje workflowId"
    assert zadetek.group(1) == kanonicni
