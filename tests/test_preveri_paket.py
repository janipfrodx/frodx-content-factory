import ast
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
NOVICNIK = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik"
SKRIPTE = NOVICNIK / "scripts"
SKRIPTA = SKRIPTE / "preveri_paket.py"
FIXTURE = REPO / "tests" / "fixtures" / "newsletter_draft_body.json"
BUILD = NOVICNIK / "vendor" / "frodx-newsletter" / "scripts" / "build_newsletter.py"
sys.path.insert(0, str(SKRIPTE))

from preveri_paket import preveri

DOLGI = "\u2014"


def _telo():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _krsitve(telo):
    return preveri(telo)[0]


def _ima(krsitve, *nizi):
    return any(all(n in k for n in nizi) for k in krsitve)


def test_fixture_gre_skozi_z_opozorili_za_bloke_brez_slike():
    krsitve, opozorila = preveri(_telo())
    assert krsitve == []
    assert len(opozorila) == 3
    assert all("block-02" in o for o in opozorila)


def test_razlicna_ura_webinarja_po_jezikih_ni_krsitev():
    telo = _telo()
    assert telo["editions"][0]["blocks"][1]["event"]["time"] != telo["editions"][2]["blocks"][1]["event"]["time"]
    assert _krsitve(telo) == []


def test_status_draft_je_dovoljen():
    telo = _telo()
    for izdaja in telo["editions"]:
        izdaja["status"] = "draft"
    assert _krsitve(telo) == []


def test_manjka_hr():
    telo = _telo()
    telo["editions"] = telo["editions"][:2]
    assert _ima(_krsitve(telo), "hr", "natanko enkrat", "korak 4")


def test_si_dvakrat():
    telo = _telo()
    telo["editions"][1] = copy.deepcopy(telo["editions"][0])
    assert _ima(_krsitve(telo), "si", "natanko enkrat")


@pytest.mark.parametrize("stevilo", [0, 4])
def test_stevilo_blokov(stevilo):
    telo = _telo()
    izdaja = telo["editions"][0]
    izdaja["blocks"] = [copy.deepcopy(izdaja["blocks"][0]) for _ in range(stevilo)]
    assert _ima(_krsitve(telo), "si.blocks", "1-3")


def test_block_id_se_ne_ujema_med_jeziki():
    telo = _telo()
    telo["editions"][1]["blocks"][1]["block_id"] = "block-03"
    assert _ima(_krsitve(telo), "en.blocks", "se ne ujemata")


def test_tip_se_ne_ujema_med_jeziki():
    telo = _telo()
    telo["editions"][2]["blocks"][0]["type"] = "announcement"
    assert _ima(_krsitve(telo), "hr.blocks", "se ne ujemata")


def test_webinar_brez_event():
    telo = _telo()
    telo["editions"][0]["blocks"][1]["event"] = None
    assert _ima(_krsitve(telo), "si.blocks[1].event", "webinar")


def test_column_z_event():
    telo = _telo()
    telo["editions"][0]["blocks"][0]["event"] = {"date": "2026-11-12", "time": "10:00", "duration_min": 45}
    assert _ima(_krsitve(telo), "si.blocks[0].event", "null")


@pytest.mark.parametrize("polje,vrednost", [
    ("date", "12. 11. 2026"),
    ("time", "10h"),
    ("duration_min", "45"),
    ("duration_min", 0),
])
def test_napacen_event(polje, vrednost):
    telo = _telo()
    telo["editions"][0]["blocks"][1]["event"][polje] = vrednost
    assert _ima(_krsitve(telo), f"si.blocks[1].event.{polje}")


@pytest.mark.parametrize("pot,vrednost", [
    (("blocks", 0, "title"), ""),
    (("blocks", 0, "body"), []),
    (("blocks", 0, "cta", "label"), ""),
    (("blocks", 0, "cta", "url"), "http://www.frodx.com/"),
    (("subject",), ""),
    (("preheader",), "  "),
    (("delivery", "segment_ref"), ""),
    (("sender", "from_email"), ""),
    (("hook", "paragraphs"), []),
    (("closing", "paragraphs"), [""]),
    (("signoff", "name"), ""),
    (("status",), "sent"),
])
def test_obvezna_polja(pot, vrednost):
    telo = _telo()
    cilj = telo["editions"][1]
    for kljuc in pot[:-1]:
        cilj = cilj[kljuc]
    cilj[pot[-1]] = vrednost
    ime = ".".join(str(k) for k in pot).replace(".0.", "[0].")
    assert _ima(_krsitve(telo), "en.", "korak 4"), _krsitve(telo)
    assert _ima(_krsitve(telo), ime.split(".")[-1]), ime


def test_dolgi_pomisljaj_v_besedilu():
    telo = _telo()
    telo["editions"][2]["blocks"][0]["body"][1] = f"Drugi {DOLGI} odlomak."
    assert _ima(_krsitve(telo), "hr.blocks[0].body[1]", "pomišljaj", "korak 4")


def test_dolgi_pomisljaj_v_segment_ref_je_dovoljen():
    telo = _telo()
    telo["editions"][0]["delivery"]["segment_ref"] = f"SI_ALL {DOLGI} celotna baza"
    assert _krsitve(telo) == []


def test_send_datetime_je_krsitev():
    telo = _telo()
    telo["editions"][0]["delivery"]["send_datetime"] = "2026-11-12T08:00:00"
    assert _ima(_krsitve(telo), "send_datetime", "korak 6")


def test_run_v_telesu_je_krsitev():
    telo = _telo()
    telo["_run"] = {"veja": "novicnik"}
    assert _ima(_krsitve(telo), "_run", "korak 6")


def test_napacen_run_slug():
    telo = _telo()
    telo["run_slug"] = "Test Strojni Vhod"
    assert _ima(_krsitve(telo), "run_slug", "init_run.py")


def test_prazen_url_slike_je_samo_opozorilo():
    telo = _telo()
    telo["editions"][0]["blocks"][0]["image"] = {"url": "", "alt": "", "file": "x.png"}
    krsitve, opozorila = preveri(telo)
    assert krsitve == []
    assert any("si.blocks[0]" in o and "korak 5" in o for o in opozorila)


@pytest.mark.parametrize("url", ["http://www.frodx.com/a.png", "//cdn.frodx.com/a.png"])
def test_slika_brez_https_je_krsitev(url):
    telo = _telo()
    telo["editions"][0]["blocks"][0]["image"]["url"] = url
    assert _ima(_krsitve(telo), "si.blocks[0].image.url", "korak 5")


def _vzorec_si():
    from iz_editions import izdaja_iz_editions
    drevo = ast.parse(BUILD.read_text(encoding="utf-8"))
    for vozlisce in drevo.body:
        if isinstance(vozlisce, ast.Assign) and any(getattr(t, "id", None) == "EDITIONS" for t in vozlisce.targets):
            return izdaja_iz_editions("si", ast.literal_eval(vozlisce.value)["si"])
    raise AssertionError("EDITIONS ni v build_newsletter.py")


def test_vzorec_iz_igorjeve_predloge_je_krsitev():
    telo = _telo()
    telo["editions"][0] = _vzorec_si()
    krsitve = _krsitve(telo)
    assert _ima(krsitve, "si.package_id", "vzorčna vrednost")
    assert _ima(krsitve, "si.blocks[0].cta.url", "vzorčna vrednost")


def _stanje(tmp_path, telo):
    stanje = dict(telo)
    stanje["_run"] = {"veja": "novicnik", "step": 5}
    pot = tmp_path / "state.json"
    pot.write_text(json.dumps(stanje, ensure_ascii=False), encoding="utf-8")
    return pot


def test_cli_odstrani_run_in_zapise_telo(tmp_path):
    pot = _stanje(tmp_path, _telo())
    izhod = tmp_path / "telo.json"
    r = subprocess.run([sys.executable, str(SKRIPTA), str(pot), "--telo", str(izhod)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip().endswith("OK")
    assert "Opozorilo:" in r.stdout
    assert json.loads(izhod.read_text(encoding="utf-8")) == _telo()


def test_cli_krsitev_brez_telesa(tmp_path):
    telo = _telo()
    telo["editions"] = telo["editions"][:1]
    pot = _stanje(tmp_path, telo)
    izhod = tmp_path / "telo.json"
    r = subprocess.run([sys.executable, str(SKRIPTA), str(pot), "--telo", str(izhod)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "KRŠITEV:" in r.stdout
    assert "korak" in r.stdout
    assert not izhod.exists()


def test_cli_napacni_argumenti(tmp_path):
    r = subprocess.run([sys.executable, str(SKRIPTA)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "uporaba" in r.stdout.lower()
