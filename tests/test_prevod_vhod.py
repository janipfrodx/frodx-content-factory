import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTE = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik" / "scripts"
SKRIPTA = SKRIPTE / "prevod_vhod.py"
VAROVALO = REPO / "plugins" / "content-factory" / "skills" / "frodx-transcreation-check" / "scripts" / "preveri_iznicenje.py"
FIXTURE = REPO / "tests" / "fixtures" / "newsletter_draft_body.json"
sys.path.insert(0, str(SKRIPTE))

from prevod_vhod import ManjkaKorak, sestavi


def _stanje():
    telo = json.loads(FIXTURE.read_text(encoding="utf-8"))
    si = next(e for e in telo["editions"] if e["language"] == "si")
    return {
        "run_slug": telo["run_slug"],
        "editions": [copy.deepcopy(si)],
        "_run": {
            "veja": "novicnik",
            "approvals": {"step1": "2026-10-01T15:01:26Z", "step3": "2026-10-01T16:18:35Z"},
            "gradivo_odlocitve": {
                "jeziki": {
                    "hr": {
                        "block-01": {"nacin": "transkreacija", "url": "https://frodx.com/hr/blog/kolumna"},
                        "block-02": {"nacin": "lokalni_vir", "url": "https://frodx.com/hr/radionica"},
                    },
                    "en": {
                        "block-01": {"nacin": "transkreacija", "url": ""},
                        "block-02": {"nacin": "transkreacija", "url": ""},
                    },
                }
            },
        },
    }


def _mapa(tmp_path, zetev=None, viri=None):
    (tmp_path / "prevod" / "viri").mkdir(parents=True)
    zetev = [] if zetev is None else zetev
    (tmp_path / "prevod" / "zetev.json").write_text(json.dumps(zetev, ensure_ascii=False), encoding="utf-8")
    viri = {"hr-block-01.txt": "Objavljena HR kolumna.", "hr-block-02.txt": "Radionica u Zagrebu."} if viri is None else viri
    for ime, besedilo in viri.items():
        (tmp_path / "prevod" / "viri" / ime).write_text(besedilo, encoding="utf-8")
    return tmp_path


def test_sestavi_loci_referenco_in_vir(tmp_path):
    vhod, _ = sestavi(_stanje(), "hr", _mapa(tmp_path))
    b1, b2 = vhod["bloki"]
    assert b1 == {"block_id": "block-01", "type": "column", "nacin": "transkreacija",
                  "url": "https://frodx.com/hr/blog/kolumna", "referenca": "Objavljena HR kolumna."}
    assert b2 == {"block_id": "block-02", "type": "webinar", "nacin": "lokalni_vir",
                  "url": "https://frodx.com/hr/radionica", "vir": "Radionica u Zagrebu."}
    assert vhod["si"].startswith("SUBJECT: ")
    assert vhod["jezik"] == "hr"
    assert any("playbook.md" in p for p in vhod["pravila"])


def test_transkreacija_brez_url_in_brez_reference_je_v_redu(tmp_path):
    vhod, _ = sestavi(_stanje(), "en", _mapa(tmp_path, viri={}))
    assert [b["referenca"] for b in vhod["bloki"]] == ["", ""]


def test_brez_potrjene_si_manjka_korak_3(tmp_path):
    stanje = _stanje()
    del stanje["_run"]["approvals"]["step3"]
    with pytest.raises(ManjkaKorak, match="korak 3"):
        sestavi(stanje, "hr", _mapa(tmp_path))


def test_brez_nacinov_za_jezik_manjka_korak_1(tmp_path):
    stanje = _stanje()
    del stanje["_run"]["gradivo_odlocitve"]["jeziki"]["hr"]
    with pytest.raises(ManjkaKorak, match="korak 1"):
        sestavi(stanje, "hr", _mapa(tmp_path))


def test_blok_brez_nacina_manjka_korak_1(tmp_path):
    stanje = _stanje()
    del stanje["_run"]["gradivo_odlocitve"]["jeziki"]["hr"]["block-02"]
    with pytest.raises(ManjkaKorak, match="block-02"):
        sestavi(stanje, "hr", _mapa(tmp_path))


def test_neznan_nacin_manjka_korak_1(tmp_path):
    stanje = _stanje()
    stanje["_run"]["gradivo_odlocitve"]["jeziki"]["hr"]["block-01"]["nacin"] = "objavljena"
    with pytest.raises(ManjkaKorak, match="korak 1"):
        sestavi(stanje, "hr", _mapa(tmp_path))


def test_lokalni_vir_brez_datoteke_manjka_korak_4(tmp_path):
    with pytest.raises(ManjkaKorak, match="korak 4.*block-02"):
        sestavi(_stanje(), "hr", _mapa(tmp_path, viri={"hr-block-01.txt": "Kolumna."}))


def test_lokalni_vir_brez_url_z_datoteko_je_v_redu(tmp_path):
    stanje = _stanje()
    stanje["_run"]["gradivo_odlocitve"]["jeziki"]["hr"]["block-02"]["url"] = ""
    vhod, _ = sestavi(stanje, "hr", _mapa(tmp_path))
    assert vhod["bloki"][1]["vir"] == "Radionica u Zagrebu."


def test_referenca_z_url_brez_datoteke_manjka_korak_4(tmp_path):
    with pytest.raises(ManjkaKorak, match="korak 4.*block-01"):
        sestavi(_stanje(), "hr", _mapa(tmp_path, viri={"hr-block-02.txt": "Radionica."}))


def test_brez_datoteke_zetve_manjka_korak_4(tmp_path):
    mapa = _mapa(tmp_path)
    (mapa / "prevod" / "zetev.json").unlink()
    with pytest.raises(ManjkaKorak, match="CF-Zetev"):
        sestavi(_stanje(), "hr", mapa)


def test_zetev_filtrira_jezik_in_odstrani_dvojnike(tmp_path):
    vrstice = [
        {"jezik": "hr", "prej": "udvoje", "potem": "dođu dvije osobe", "razlog": "kalk"},
        {"jezik": "hr", "prej": "udvoje", "potem": "dođu dvije osobe", "razlog": "kalk"},
        {"jezik": "en", "prej": "in two", "potem": "as a pair", "razlog": "x"},
        {"jezik": "hr", "prej": " ", "potem": "prazno", "razlog": ""},
    ]
    vhod, sprejete = sestavi(_stanje(), "hr", _mapa(tmp_path, zetev=vrstice))
    assert vhod["zetev"] == [{"prej": "udvoje", "potem": "dođu dvije osobe", "razlog": "kalk"}]
    assert sprejete == {"round": "zetev",
                        "accepted": [{"navedek": "udvoje", "popravek": "dođu dvije osobe", "razlog": "kalk"}]}


def test_zetev_sprejme_surov_odgovor_orodja(tmp_path):
    odgovor = {"data": [{"id": 7, "createdAt": "2026-10-02", "jezik": "hr", "prej": "Vodimo je",
                         "potem": "Radionicu vodimo", "razlog": "red besed", "veja": "novicnik"}],
               "nextCursor": None}
    vhod, _ = sestavi(_stanje(), "hr", _mapa(tmp_path, zetev=odgovor))
    assert vhod["zetev"] == [{"prej": "Vodimo je", "potem": "Radionicu vodimo", "razlog": "red besed"}]


def _tek(tmp_path):
    mapa = _mapa(tmp_path, zetev=[{"jezik": "hr", "prej": "udvoje", "potem": "dođu dvije osobe", "razlog": "kalk"}])
    pot = mapa / "state.json"
    pot.write_text(json.dumps(_stanje(), ensure_ascii=False), encoding="utf-8")
    return mapa, pot


def test_cli_zapise_vhod_in_sprejete(tmp_path):
    mapa, pot = _tek(tmp_path)
    izid = subprocess.run([sys.executable, str(SKRIPTA), str(pot), "hr"], capture_output=True, text=True)
    assert izid.returncode == 0, izid.stdout
    assert "2 blokov, 1 parov žetve" in izid.stdout
    vhod = json.loads((mapa / "prevod" / "hr-vhod.json").read_text(encoding="utf-8"))
    assert vhod["zetev"][0]["prej"] == "udvoje"
    sprejete = json.loads((mapa / "transcreation-check" / "hr-round-zetev.json").read_text(encoding="utf-8"))
    assert sprejete["accepted"][0]["navedek"] == "udvoje"


def test_cli_manjka_vrne_1_in_nic_ne_zapise(tmp_path):
    mapa, pot = _tek(tmp_path)
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    del stanje["_run"]["approvals"]["step3"]
    pot.write_text(json.dumps(stanje), encoding="utf-8")
    izid = subprocess.run([sys.executable, str(SKRIPTA), str(pot), "hr"], capture_output=True, text=True)
    assert izid.returncode == 1
    assert izid.stdout.startswith("MANJKA: korak 3")
    assert not (mapa / "prevod" / "hr-vhod.json").exists()


def test_cli_napacen_jezik_vrne_2(tmp_path):
    _, pot = _tek(tmp_path)
    izid = subprocess.run([sys.executable, str(SKRIPTA), str(pot), "si"], capture_output=True, text=True)
    assert izid.returncode == 2


def test_varovalo_najde_obliko_iz_zetve_v_prevodu(tmp_path):
    mapa, pot = _tek(tmp_path)
    subprocess.run([sys.executable, str(SKRIPTA), str(pot), "hr"], check=True, capture_output=True)
    prazno = mapa / "prazno.txt"
    prazno.write_text("", encoding="utf-8")
    prevod = mapa / "hr.txt"
    prevod.write_text("Na radionicu dođite udvoje.", encoding="utf-8")
    izid = subprocess.run([sys.executable, str(VAROVALO), str(mapa / "transcreation-check"), "hr",
                           str(prazno), str(prevod)], capture_output=True, text=True)
    assert izid.returncode == 1
    assert 'IZNIČENO: "udvoje"' in izid.stdout
