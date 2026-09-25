import json
import re
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "newsletter_draft_body.json"


def _load():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_ima_run_slug_in_tri_jezike():
    body = _load()
    assert re.fullmatch(r"[a-z0-9-]{3,120}", body["run_slug"])
    assert sorted(e["language"] for e in body["editions"]) == ["en", "hr", "si"]


def test_fixture_nima_casa_posiljanja():
    for e in _load()["editions"]:
        assert "send_datetime" not in e.get("delivery", {})


def test_fixture_bloki_ustrezajo_pogodbi():
    for e in _load()["editions"]:
        assert 1 <= len(e["blocks"]) <= 3
        for b in e["blocks"]:
            assert re.fullmatch(r"block-\d{2}", b["block_id"])
            assert b["title"].strip()
            assert any(p.strip() for p in b["body"])
            assert b["cta"]["label"].strip()
            assert b["cta"]["url"].startswith("https://")
            if b["type"] == "webinar":
                assert b["event"] is not None
            if b["image"] is not None and b["image"].get("url"):
                assert b["image"]["url"].startswith("https://")


def test_fixture_pokriva_blok_brez_slike_in_webinar():
    for e in _load()["editions"]:
        tipi = {b["type"] for b in e["blocks"]}
        assert "webinar" in tipi
        assert any(b["image"] is None for b in e["blocks"])


def test_fixture_obvezna_polja_izdaje():
    for e in _load()["editions"]:
        for kljuc in ("package_id", "subject", "preheader"):
            assert e[kljuc].strip(), kljuc
        assert e["delivery"]["segment_ref"].strip()
        assert e["sender"]["from_name"].strip()
        assert e["sender"]["from_email"].strip()
        assert any(p.strip() for p in e["hook"]["paragraphs"])
        assert any(p.strip() for p in e["closing"]["paragraphs"])
        assert e["signoff"]["phrase"].strip()
        assert e["signoff"]["name"].strip()


def test_fixture_brez_dolgega_pomisljaja():
    assert "—" not in FIXTURE.read_text(encoding="utf-8")
