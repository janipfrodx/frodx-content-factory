import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKRIPTE = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "nika" / "scripts"
SKRIPTA = SKRIPTE / "xml_v_zavihek.py"
FIKSNE = REPO / "tests" / "fixtures"


def _nalozi(ime):
    spec = importlib.util.spec_from_file_location(f"{ime}_nika", SKRIPTE / f"{ime}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _beri(ime):
    return (FIKSNE / ime).read_text(encoding="utf-8")


def _pozeni(tmp_path, *kosi):
    poti = []
    for i, kos in enumerate(kosi, 1):
        pot = tmp_path / f"zavihek-{i}.xml"
        pot.write_text(kos, encoding="utf-8")
        poti.append(str(pot))
    izhod = tmp_path / "zavihek.md"
    izid = subprocess.run([sys.executable, str(SKRIPTA), str(izhod), *poti], capture_output=True, text=True)
    return izid, izhod


def test_zavihek_zgodbe_je_enak_izvozu(tmp_path):
    izid, izhod = _pozeni(tmp_path, _beri("nika_zavihek_prebran.xml"))
    assert izid.returncode == 0, izid.stdout
    assert izhod.read_bytes() == (FIKSNE / "nika_zavihek_prebran.md").read_bytes()


def test_meritev_je_enaka_izvozu(tmp_path):
    izid, izhod = _pozeni(tmp_path, _beri("docs_meritev.xml"))
    assert izid.returncode == 0, izid.stdout
    assert izhod.read_bytes() == (FIKSNE / "docs_meritev.md").read_bytes()


def test_spremenjena_crka_je_napaka_z_idjem(tmp_path):
    xml = _beri("nika_zavihek_prebran.xml").replace("Pogoj sta snemanje s prepisom in Notetaker.", "Pogoj sta snemanje s prepisom in Notetakar.")
    izid, izhod = _pozeni(tmp_path, xml)
    assert izid.returncode == 1
    assert "NAPAKA" in izid.stdout and ".4895" in izid.stdout
    assert "preberi zavihek znova" in izid.stdout
    assert not izhod.exists()


def test_odrezan_zavihek_je_napaka(tmp_path):
    xml = _beri("nika_zavihek_prebran.xml")
    rez = xml.index("<paragraph id='.5261'")
    izid, izhod = _pozeni(tmp_path, xml[:rez] + "<gap cap='true' from='.5261'/></doc>\n")
    assert izid.returncode == 1
    assert "zavihek ni prebran do konca" in izid.stdout
    assert not izhod.exists()


def test_dva_kosa_dasta_isto_kot_eden(tmp_path):
    xml = _beri("nika_zavihek_prebran.xml")
    rez = xml.index("<paragraph id='.3664'")
    glava = xml[: xml.index(">") + 1]
    prvi = xml[:rez] + "<gap cap='true' from='.3664'/></doc>\n"
    drugi = glava + xml[rez:]
    izid, izhod = _pozeni(tmp_path, prvi, drugi)
    assert izid.returncode == 0, izid.stdout
    assert izhod.read_bytes() == (FIKSNE / "nika_zavihek_prebran.md").read_bytes()


def test_izbran_spustni_seznam_je_vrednost_celice():
    x = _nalozi("xml_v_zavihek")
    assert "| A | Potrdi |" in x.pretvori([_beri("docs_meritev.xml")])
    assert "| C |  |" in x.pretvori([_beri("docs_meritev.xml")])


def test_izbran_potrdi_v_zavihku_je_approve(tmp_path):
    xml = _beri("nika_zavihek_prebran.xml").replace(
        "<dropdown id='.351' enum='832fa5b7-c46c'/>",
        "<dropdown id='.351' enum='832fa5b7-c46c' index='0'>Potrdi</dropdown>",
    )
    izid, izhod = _pozeni(tmp_path, xml)
    assert izid.returncode == 0, izid.stdout
    stanje = tmp_path / "state.json"
    stanje.write_text(_beri("nika_story_body.json"), encoding="utf-8")
    izid = subprocess.run([sys.executable, str(SKRIPTE / "iz_zavihka.py"), str(izhod), str(stanje)], capture_output=True, text=True)
    assert izid.returncode == 0, izid.stdout
    pregled = json.loads(stanje.read_text(encoding="utf-8"))["_run"]["nika_pregled"]
    assert pregled["decision"] == "approve"
    assert pregled["spremenjene_povedi"] == 0


def test_brez_argumentov_izpise_uporabo():
    izid = subprocess.run([sys.executable, str(SKRIPTA)], capture_output=True, text=True)
    assert izid.returncode == 1 and "Uporaba: xml_v_zavihek.py <izhod.md> <kos1.xml>" in izid.stdout


def test_oblike_kot_izvoz_brez_ubezanja_zvezdice_in_podcrtaja(tmp_path):
    izid, izhod = _pozeni(tmp_path, _beri("docs_oblike.xml"))
    assert izid.returncode == 0, izid.stdout
    assert izhod.read_bytes() == (FIKSNE / "docs_oblike.md").read_bytes()
