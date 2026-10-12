import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTA = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "nika" / "scripts" / "besedilo.py"
_spec = importlib.util.spec_from_file_location("besedilo_nika", SKRIPTA)
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)


def _stanje():
    return json.loads((REPO / "tests" / "fixtures" / "nika_story_body.json").read_text(encoding="utf-8"))


def test_izpis_sl_je_blog_md():
    s = _stanje()
    assert b.izpis(s, "sl") == s["story"]["blog_md"]


def test_vpis_sl_posodobi_tudi_naslov():
    s = _stanje()
    b.vpis(s, "sl", "# Nov naslov\n\nBesedilo.")
    assert s["story"]["title"] == "Nov naslov" and s["story"]["blog_md"].startswith("# Nov naslov")


def test_vpis_en_v_languages():
    s = _stanje()
    b.vpis(s, "en", "# Title\n\nText.")
    assert s["languages"]["en"]["title"] == "Title" and s["languages"]["en"]["blog_md"] == "# Title\n\nText."


def test_brez_naslova_je_napaka():
    with pytest.raises(ValueError, match="# "):
        b.vpis(_stanje(), "hr", "Tekst brez naslova.")


def test_neznan_jezik():
    with pytest.raises(ValueError, match="sl, en, hr"):
        b.izpis(_stanje(), "de")


def test_brez_argumentov_izpise_celo_uporabo():
    import subprocess, sys
    izid = subprocess.run([sys.executable, str(SKRIPTA)], capture_output=True, text=True)
    assert izid.returncode == 1
    assert "besedilo.py izpis <state.json> <sl|en|hr>" in izid.stdout
    assert "besedilo.py vpis <state.json> <sl|en|hr> <datoteka>" in izid.stdout
