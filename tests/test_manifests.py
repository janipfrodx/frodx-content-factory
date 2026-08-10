import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_marketplace_manifest_je_veljaven():
    data = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert data["name"] == "frodx-content-factory"
    assert isinstance(data["owner"], dict) and data["owner"]["name"]
    assert len(data["plugins"]) == 1
    plugin = data["plugins"][0]
    assert plugin["name"] == "content-factory"
    assert plugin["source"] == "./plugins/content-factory"
    assert plugin["description"]


def test_plugin_manifest_je_veljaven():
    data = json.loads((REPO / "plugins" / "content-factory" / "plugin.json").read_text(encoding="utf-8"))
    assert data["name"] == "content-factory"
    assert data["version"]
    assert data["description"]


def test_verziji_se_ujemata():
    market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    plugin = json.loads((REPO / "plugins" / "content-factory" / "plugin.json").read_text(encoding="utf-8"))
    assert market["plugins"][0]["version"] == plugin["version"]
