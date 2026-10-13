import datetime as dt
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTE = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "nika" / "scripts"
URNIK = SKRIPTE / "urnik.py"

LJ = ZoneInfo("Europe/Ljubljana")


def _nalozi(ime):
    spec = importlib.util.spec_from_file_location(f"{ime}_nika_urnik", SKRIPTE / f"{ime}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


urnik = _nalozi("urnik")
pp = _nalozi("preveri_paket")


def _lj(*cas):
    return dt.datetime(*cas, tzinfo=LJ)


@pytest.mark.parametrize("zdaj, pricakovano", [
    (_lj(2026, 10, 13, 10, 45), _lj(2026, 10, 13, 11, 0)),
    (_lj(2026, 10, 13, 10, 47), _lj(2026, 10, 13, 11, 15)),
    (_lj(2026, 10, 13, 10, 30), _lj(2026, 10, 13, 10, 45)),
    (_lj(2026, 10, 13, 10, 30, 20), _lj(2026, 10, 13, 11, 0)),
    (_lj(2026, 10, 13, 10, 30, 0, 500), _lj(2026, 10, 13, 11, 0)),
    (_lj(2026, 10, 13, 10, 0), _lj(2026, 10, 13, 10, 15)),
    (_lj(2026, 10, 13, 23, 50), _lj(2026, 10, 14, 0, 15)),
])
def test_najzgodnejsi(zdaj, pricakovano):
    izid = urnik.najzgodnejsi(zdaj)
    assert izid == pricakovano
    assert izid.second == 0 and izid.microsecond == 0 and izid.minute % 15 == 0


def test_najzgodnejsi_pretvori_v_ljubljano():
    izid = urnik.najzgodnejsi(dt.datetime(2026, 10, 13, 8, 47, tzinfo=dt.timezone.utc))
    assert izid.isoformat() == "2026-10-13T11:15:00+02:00"


def test_najzgodnejsi_jesenski_prehod():
    pred = urnik.najzgodnejsi(dt.datetime.fromisoformat("2026-10-25T02:50:00+02:00"))
    assert pred.isoformat() == "2026-10-25T02:15:00+01:00"
    po = urnik.najzgodnejsi(dt.datetime.fromisoformat("2026-10-25T02:50:00+01:00"))
    assert po.isoformat() == "2026-10-25T03:15:00+01:00"


def test_najzgodnejsi_spomladanski_prehod():
    izid = urnik.najzgodnejsi(dt.datetime.fromisoformat("2026-03-29T01:50:00+01:00"))
    assert izid.isoformat() == "2026-03-29T03:15:00+02:00"
    zgodaj = urnik.najzgodnejsi(dt.datetime.fromisoformat("2026-03-29T01:30:00+01:00"))
    assert zgodaj.isoformat() == "2026-03-29T01:45:00+01:00"


@pytest.mark.parametrize("blog, dan", [
    (_lj(2026, 10, 14, 7, 15), dt.date(2026, 10, 14)),
    (_lj(2026, 10, 14, 7, 30), dt.date(2026, 10, 14)),
    (_lj(2026, 10, 14, 7, 45), dt.date(2026, 10, 15)),
    (_lj(2026, 10, 14, 23, 45), dt.date(2026, 10, 15)),
])
def test_predlog_linkedin(blog, dan):
    assert urnik.predlog_linkedin(blog) == dan


def _cli(*args):
    return subprocess.run([sys.executable, str(URNIK), *args], capture_output=True, text=True)


def test_cli_z_zdaj_vrne_veljaven_json():
    izid = _cli("--zdaj", "2026-10-13T10:47:00+02:00")
    assert izid.returncode == 0, izid.stderr
    assert len(izid.stdout.strip().splitlines()) == 1
    podatki = json.loads(izid.stdout)
    assert podatki == {"publish_at": "2026-10-13T11:15:00+02:00", "linkedin_date": "2026-10-14"}
    assert pp.zamik_ljubljane_ok(podatki["publish_at"])


def test_cli_pozimi_zamik_plus_ena():
    podatki = json.loads(_cli("--zdaj", "2026-12-01T07:10:00+01:00").stdout)
    assert podatki == {"publish_at": "2026-12-01T07:30:00+01:00", "linkedin_date": "2026-12-01"}
    assert pp.zamik_ljubljane_ok(podatki["publish_at"])


def test_cli_brez_argumentov_uporabi_trenutni_cas():
    podatki = json.loads(_cli().stdout)
    cas = dt.datetime.fromisoformat(podatki["publish_at"])
    razlika = cas - dt.datetime.now(dt.timezone.utc)
    assert dt.timedelta(minutes=15) <= razlika <= dt.timedelta(minutes=30)
    assert pp.zamik_ljubljane_ok(podatki["publish_at"])


def test_cli_zdaj_brez_zamika_je_napaka():
    izid = _cli("--zdaj", "2026-10-13T10:47:00")
    assert izid.returncode != 0
