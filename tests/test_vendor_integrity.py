import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.vendor_hash import VENDORED, hash_tree

SKILLS = REPO / "plugins" / "content-factory" / "skills"


def test_manifest_obstaja_in_ni_prazen():
    manifest = json.loads((REPO / "vendor-manifest.json").read_text(encoding="utf-8"))
    assert manifest["package_version"] == "2026-08-06"
    assert len(manifest["files"]) > 20


def test_vendorirane_datoteke_niso_spremenjene():
    manifest = json.loads((REPO / "vendor-manifest.json").read_text(encoding="utf-8"))
    dejansko = {}
    for name in VENDORED:
        for rel, digest in hash_tree(SKILLS / name).items():
            dejansko[f"{name}/{rel}"] = digest
    assert dejansko == manifest["files"], "Vendorirani skill je bil spremenjen - spremembe gredo skozi PR na Igorjev vir."


def test_vsak_vendoriran_skill_ima_skill_md():
    for name in VENDORED:
        assert (SKILLS / name / "SKILL.md").is_file()
