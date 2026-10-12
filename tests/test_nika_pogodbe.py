import hashlib
import hmac
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIX = REPO / "tests" / "fixtures"
ORODJE = REPO / "tools" / "podpisi_hmac.py"

ODLOCITEV_POLJA = {"draft_id", "run_slug", "title", "draft_url", "decision", "judgment_answer", "judgment_text", "reason", "comment"}
OBJAVA_POLJA = {"draft_id", "run_slug", "publish_at", "title", "blog_md", "meta_description", "linkedin_text", "first_comment"}


def _json(ime):
    return json.loads((FIX / ime).read_text(encoding="utf-8"))


def _podpisi(pot, secret, *dodatno):
    okolje = {**os.environ, "NIKA_HMAC_SECRET": secret}
    izhod = subprocess.run(
        [sys.executable, str(ORODJE), str(pot), *dodatno],
        capture_output=True, text=True, encoding="utf-8", env=okolje, check=True,
    )
    telo, podpis = izhod.stdout.rstrip("\n").split("\n")
    return telo, podpis


def test_odlocitev_ima_polja_iz_speca():
    assert set(_json("nika_decision_body.json")) == ODLOCITEV_POLJA


def test_odlocitev_uporablja_dovoljene_vrednosti():
    telo = _json("nika_decision_body.json")
    assert telo["decision"] in {"approve", "reject"}
    assert telo["judgment_answer"] in {"da", "ne", "drugace"}
    assert telo["reason"] in {"presoja", "dejstvo", "novost", "slog"}
    assert telo["draft_url"].startswith("https://")


def test_objava_ima_polja_iz_speca():
    assert set(_json("nika_publish_body.json")) == OBJAVA_POLJA


def test_objava_brez_oznak_in_s_casovnim_zamikom():
    objava = _json("nika_publish_body.json")
    for polje in ("title", "blog_md", "linkedin_text", "first_comment"):
        assert "[PREVERI" not in objava[polje], polje
    assert objava["publish_at"].endswith(("+01:00", "+02:00"))


def test_podpis_je_hmac_kompaktnega_jsona(tmp_path):
    pot = tmp_path / "telo.json"
    pot.write_text('{"b": 1, "a": "x"}', encoding="utf-8")
    telo, podpis = _podpisi(pot, "key")
    assert telo == '{"b":1,"a":"x"}'
    assert podpis == hmac.new(b"key", telo.encode("utf-8"), hashlib.sha256).hexdigest()


def test_podpis_ohrani_sumnike_in_upostevi_set(tmp_path):
    pot = tmp_path / "telo.json"
    pot.write_text('{"title": "Čas za »šolo«\\nnaprej", "run_slug": "a"}', encoding="utf-8")
    telo, podpis = _podpisi(pot, "key", "--set", "run_slug=preizkus-1")
    assert telo == '{"title":"Čas za »šolo«\\nnaprej","run_slug":"preizkus-1"}'
    assert podpis == hmac.new(b"key", telo.encode("utf-8"), hashlib.sha256).hexdigest()
