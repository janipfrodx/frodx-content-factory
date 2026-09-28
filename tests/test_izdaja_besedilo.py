import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTE = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik" / "scripts"
SKRIPTA = SKRIPTE / "izdaja_besedilo.py"
FIXTURE = REPO / "tests" / "fixtures" / "newsletter_draft_body.json"
sys.path.insert(0, str(SKRIPTE))

from izdaja_besedilo import NapakaOznak, besedilo_v_izdajo, izdaja_v_besedilo


def _fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _vsi_tipi():
    izdaja = copy.deepcopy(_fixture()["editions"][0])
    izdaja["blocks"].append({
        "block_id": "block-03",
        "type": "announcement",
        "image": {"url": "", "alt": "", "file": "novica.png"},
        "title": "Nova stranka",
        "body": ["Rezultat: 30 % več odgovorov.", "Drugi odstavek."],
        "bullets": [],
        "event": None,
        "cta": {"label": "Preberite več", "url": "https://www.frodx.com/"},
    })
    izdaja["ps"] = "P.S. Prijave se zaprejo v petek."
    return izdaja


def _zamenjaj(besedilo, staro, novo):
    assert staro in besedilo, staro
    return besedilo.replace(staro, novo, 1)


@pytest.mark.parametrize("indeks", [0, 1, 2])
def test_pretvorba_brez_izgube_na_fixturju(indeks):
    izdaja = _fixture()["editions"][indeks]
    assert besedilo_v_izdajo(izdaja_v_besedilo(izdaja), izdaja) == izdaja


def test_pretvorba_brez_izgube_z_vsemi_tipi_blokov():
    izdaja = _vsi_tipi()
    assert besedilo_v_izdajo(izdaja_v_besedilo(izdaja), izdaja) == izdaja


def test_vhodna_izdaja_ostane_nespremenjena():
    izdaja = _vsi_tipi()
    kopija = copy.deepcopy(izdaja)
    besedilo = _zamenjaj(izdaja_v_besedilo(izdaja), "NASLOV: Nova stranka", "NASLOV: Drugačen")
    besedilo_v_izdajo(besedilo, izdaja)
    assert izdaja == kopija


def test_popravek_spremeni_samo_besedilna_polja():
    izdaja = _vsi_tipi()
    besedilo = izdaja_v_besedilo(izdaja)
    besedilo = _zamenjaj(besedilo, "NASLOV: Testni webinar brez slike", "NASLOV: Popravljen webinar")
    besedilo = _zamenjaj(besedilo, "SUBJECT: TEST: osnutek iz tovarne", "SUBJECT: Nov subject")
    nova = besedilo_v_izdajo(besedilo, izdaja)
    assert nova["blocks"][1]["title"] == "Popravljen webinar"
    assert nova["subject"] == "Nov subject"
    for kljuc in ("delivery", "sender", "package_id", "edition_name", "status", "footer_ref"):
        assert nova[kljuc] == izdaja[kljuc], kljuc
    assert nova["hook"]["archetype"] == izdaja["hook"]["archetype"]
    for star, nov in zip(izdaja["blocks"], nova["blocks"]):
        for kljuc in ("block_id", "type", "event", "image"):
            assert nov[kljuc] == star[kljuc], kljuc
        assert nov["cta"]["url"] == star["cta"]["url"]


def test_odstavek_z_dvopicjem_ni_oznaka():
    izdaja = _vsi_tipi()
    nova = besedilo_v_izdajo(izdaja_v_besedilo(izdaja), izdaja)
    assert nova["blocks"][2]["body"][0] == "Rezultat: 30 % več odgovorov."


def test_prazne_vrstice_se_preskocijo():
    izdaja = _fixture()["editions"][0]
    besedilo = izdaja_v_besedilo(izdaja).replace("\n", "\n\n")
    assert besedilo_v_izdajo(besedilo, izdaja) == izdaja


@pytest.mark.parametrize("staro,novo", [
    ("[block-02 · webinar]\n", ""),
    ("[block-02 · webinar]", "[block-02 · column]"),
    ("[block-01 · column]", "[block-09 · column]"),
    ("SUBJECT: TEST: osnutek iz tovarne\n", "SUBJECT: a\nSUBJECT: b\n"),
    ("CTA: Prijava\n", ""),
    ("ZAKLJUČEK:\n", ""),
    ("TELO:\nOpis webinarja.\n", "TELO:\n"),
    ("ALINEJE:\nPrva alineja\n", "Prva alineja\n"),
    ("PS: \n", ""),
    ("HOOK:\n", ""),
])
def test_pokvarjene_oznake_glasno_padejo(staro, novo):
    izdaja = _fixture()["editions"][0]
    besedilo = _zamenjaj(izdaja_v_besedilo(izdaja), staro, novo)
    with pytest.raises(NapakaOznak):
        besedilo_v_izdajo(besedilo, izdaja)


def test_zamenjan_vrstni_red_blokov_pade():
    izdaja = _fixture()["editions"][0]
    besedilo = izdaja_v_besedilo(izdaja)
    prvi = besedilo[besedilo.index("[block-01"):besedilo.index("[block-02")]
    drugi = besedilo[besedilo.index("[block-02"):besedilo.index("ZAKLJUČEK:")]
    with pytest.raises(NapakaOznak):
        besedilo_v_izdajo(besedilo.replace(prvi + drugi, drugi + prvi), izdaja)


def test_besedilo_pred_prvo_oznako_pade():
    izdaja = _fixture()["editions"][0]
    with pytest.raises(NapakaOznak):
        besedilo_v_izdajo("Tu je popravljena verzija:\n" + izdaja_v_besedilo(izdaja), izdaja)


def test_prelom_v_polju_pade_ze_ob_izpisu():
    izdaja = copy.deepcopy(_fixture()["editions"][0])
    izdaja["blocks"][0]["title"] = "Prva vrstica\nDruga vrstica"
    with pytest.raises(NapakaOznak):
        izdaja_v_besedilo(izdaja)



@pytest.mark.parametrize("lokacija,vrednost", [
    ("hook.paragraphs", "CTA: klikni"),
    ("hook.paragraphs", "PS: še to"),
    ("hook.paragraphs", "TELO:"),
    ("hook.paragraphs", "[block-01 · column]"),
    ("hook.paragraphs", "SUBJECT: x"),
    ("body", "CTA: klikni"),
    ("body", "PS: še to"),
    ("body", "TELO:"),
    ("body", "[block-01 · column]"),
    ("body", "SUBJECT: x"),
    ("bullets", "CTA: klikni"),
    ("bullets", "PS: še to"),
    ("bullets", "TELO:"),
    ("bullets", "[block-01 · column]"),
    ("bullets", "SUBJECT: x"),
    ("closing.paragraphs", "CTA: klikni"),
    ("closing.paragraphs", "PS: še to"),
    ("closing.paragraphs", "TELO:"),
    ("closing.paragraphs", "[block-01 · column]"),
    ("closing.paragraphs", "SUBJECT: x"),
])
def test_odstavek_z_rezervirano_oznako_pade_ob_izpisu(lokacija, vrednost):
    izdaja = copy.deepcopy(_fixture()["editions"][0])
    if lokacija == "hook.paragraphs":
        izdaja["hook"]["paragraphs"][0] = vrednost
    elif lokacija == "body":
        izdaja["blocks"][0]["body"][0] = vrednost
    elif lokacija == "bullets":
        izdaja["blocks"][0]["bullets"] = [vrednost]
    elif lokacija == "closing.paragraphs":
        izdaja["closing"]["paragraphs"][0] = vrednost
    with pytest.raises(NapakaOznak):
        izdaja_v_besedilo(izdaja)


def test_cli_izpis_z_rezervirano_oznako_v_odstavku_vrne_napako(tmp_path):
    pot = _stanje(tmp_path)
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    stanje["editions"][0]["hook"]["paragraphs"][0] = "PS: neka opozorila"
    pot.write_text(json.dumps(stanje, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SKRIPTA), "izpis", str(pot), "si"], capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stdout.startswith("NAPAKA:")

def _stanje(tmp_path):
    stanje = _fixture()
    stanje["_run"] = {"veja": "novicnik", "step": 2}
    pot = tmp_path / "state.json"
    pot.write_text(json.dumps(stanje, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pot


def test_cli_izpis(tmp_path):
    pot = _stanje(tmp_path)
    r = subprocess.run([sys.executable, str(SKRIPTA), "izpis", str(pot), "hr"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("SUBJECT: TEST: nacrt iz tvornice")


def test_cli_vpis_zapise_popravek(tmp_path):
    pot = _stanje(tmp_path)
    izpis = subprocess.run([sys.executable, str(SKRIPTA), "izpis", str(pot), "si"], capture_output=True, text=True).stdout
    popravek = tmp_path / "si.txt"
    popravek.write_text(izpis.replace("NASLOV: Testni blok s sliko", "NASLOV: Popravljen blok"), encoding="utf-8")
    r = subprocess.run([sys.executable, str(SKRIPTA), "vpis", str(pot), "si", str(popravek)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    assert stanje["editions"][0]["blocks"][0]["title"] == "Popravljen blok"
    assert stanje["_run"] == {"veja": "novicnik", "step": 2}


def test_cli_vpis_s_pokvarjenimi_oznakami_ne_spremeni_datoteke(tmp_path):
    pot = _stanje(tmp_path)
    pred = pot.read_bytes()
    popravek = tmp_path / "si.txt"
    popravek.write_text("Popravljeno besedilo brez oznak.\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SKRIPTA), "vpis", str(pot), "si", str(popravek)], capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stdout.startswith("NAPAKA:")
    assert pot.read_bytes() == pred


def test_cli_neznan_jezik(tmp_path):
    pot = _stanje(tmp_path)
    r = subprocess.run([sys.executable, str(SKRIPTA), "izpis", str(pot), "de"], capture_output=True, text=True)
    assert r.returncode == 1
    assert "de" in r.stdout


def test_cli_brez_argumentov():
    r = subprocess.run([sys.executable, str(SKRIPTA)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "uporaba" in r.stdout.lower()
