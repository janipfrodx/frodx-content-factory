from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
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
    assert "delivery" in SHEMA.read_text(encoding="utf-8")
