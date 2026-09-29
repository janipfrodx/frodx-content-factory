import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.vendor_hash import POTI, VENDORED, hash_tree, pot_skilla

SKILLS = REPO / "plugins" / "content-factory" / "skills"


def test_manifest_obstaja_in_ni_prazen():
    manifest = json.loads((REPO / "vendor-manifest.json").read_text(encoding="utf-8"))
    assert manifest["package_version"] == "2026-09-29"
    assert len(manifest["files"]) > 20


def test_vendorirane_datoteke_niso_spremenjene():
    manifest = json.loads((REPO / "vendor-manifest.json").read_text(encoding="utf-8"))
    dejansko = {}
    for name in VENDORED:
        for rel, digest in hash_tree(pot_skilla(SKILLS, name)).items():
            dejansko[f"{name}/{rel}"] = digest
    assert dejansko == manifest["files"], "Vendorirani skill je bil spremenjen - spremembe gredo skozi PR na Igorjev vir."


def test_vsak_vendoriran_skill_ima_skill_md():
    for name in VENDORED:
        assert (pot_skilla(SKILLS, name) / "SKILL.md").is_file(), name


def test_preseljeni_pisci_niso_vec_na_vrhu_skills():
    """Cowork vidi kot skill samo SK/<ime>/SKILL.md. Pisec v vendor/ ne tekmuje z deblom."""
    assert "frodx-newsletter" in POTI
    for name in POTI:
        assert not (SKILLS / name).exists(), f"{name} je še vedno samostojen skill"
        assert "/vendor/" in POTI[name], POTI[name]


def test_audit_je_vendoriran_pod_preverbo_ne_na_vrhu():
    """Audit ima allow_implicit_invocation - kot samostojen skill bi ga Cowork sprožil še sam."""
    assert "frodx-transcreation-audit" in VENDORED
    assert POTI["frodx-transcreation-audit"] == "frodx-transcreation-check/vendor/frodx-transcreation-audit"
    assert not (SKILLS / "frodx-transcreation-audit").exists()
    koren = pot_skilla(SKILLS, "frodx-transcreation-audit")
    for rel in ("SKILL.md", "references/croatian.md", "references/english.md",
                "dist/transcreation-audit-hr.md", "dist/transcreation-audit-en.md"):
        assert (koren / rel).is_file(), rel


def test_pisec_kolumne_je_1_5_0():
    vsebina = (pot_skilla(SKILLS, "igor-column-writer") / "SKILL.md").read_text(encoding="utf-8")
    assert "version: 1.5.0" in vsebina


def test_transkreacija_zahteva_audit():
    vsebina = (pot_skilla(SKILLS, "frodx-transcreation") / "SKILL.md").read_text(encoding="utf-8")
    assert "version: 1.0.0" in vsebina
    assert "frodx-transcreation-audit" in vsebina
