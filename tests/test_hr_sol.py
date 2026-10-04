import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTE = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik" / "scripts"
SKRIPTA = SKRIPTE / "hr_sol.py"
FIXTURE = REPO / "tests" / "fixtures" / "newsletter_draft_body.json"
sys.path.insert(0, str(SKRIPTE))

from hr_sol import NapakaIzida, PROMPTI, VENDOR, fnv1a, polja_si, preveri_izid, razpakiraj, sestavi_vhod
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
            "gradivo_odlocitve": {"jeziki": {"hr": {
                "block-01": {"nacin": "transkreacija", "url": "https://frodx.com/hr/blog/kolumna"},
                "block-02": {"nacin": "lokalni_vir", "url": "https://frodx.com/hr/radionica"},
            }}},
        },
    }


def _mapa(tmp_path, zetev=None):
    (tmp_path / "prevod" / "viri").mkdir(parents=True)
    vrstice = zetev if zetev is not None else [
        {"jezik": "hr", "prej": "Zvonilo je u prazno", "potem": "Nitko se nije javio", "razlog": "kalk"},
        {"jezik": "en", "prej": "x", "potem": "y", "razlog": "ni za hr"},
    ]
    (tmp_path / "prevod" / "zetev.json").write_text(
        json.dumps({"rows": vrstice, "count": len(vrstice)}, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "prevod" / "viri" / "hr-block-01.txt").write_text("Objavljena HR kolumna.", encoding="utf-8")
    (tmp_path / "prevod" / "viri" / "hr-block-02.txt").write_text("Radionica u Zagrebu.", encoding="utf-8")
    return tmp_path


def _hr_vhod(stanje, mapa):
    vhod, _ = sestavi(stanje, "hr", mapa)
    return vhod


def test_polja_si_brez_pozdrava_in_podpisa():
    si = _stanje()["editions"][0]
    ids = [i for i, _ in polja_si(si)]
    assert ids == ["SUBJECT", "PREHEADER", "HOOK", "B1_TITLE", "B1_BODY", "B1_BULLETS", "B1_CTA",
                   "B2_TITLE", "B2_BODY", "B2_CTA", "CLOSING"]
    assert "GREETING" not in ids


def test_polja_si_odstavki_z_novo_vrstico_in_ps_samo_neprazen():
    si = _stanje()["editions"][0]
    si["ps"] = "PS vrstica"
    polja = dict(polja_si(si))
    assert polja["B1_BODY"] == "\n".join(si["blocks"][0]["body"])
    assert polja["HOOK"] == "\n".join(si["hook"]["paragraphs"])
    assert polja["PS"] == "PS vrstica"


def test_sestavi_vhod_oblika_igorjevega_primera(tmp_path):
    stanje = _stanje()
    vhod = sestavi_vhod(stanje, _hr_vhod(stanje, _mapa(tmp_path)))
    assert set(vhod) == {"content_type", "audience", "source_blocks", "candidate_blocks", "glossary",
                         "approved_examples", "approved_adaptations", "constraints", "audit_feedback"}
    assert vhod["content_type"] == "newsletter"
    assert vhod["candidate_blocks"] == vhod["glossary"] == vhod["approved_examples"] == vhod["audit_feedback"] == []
    assert vhod["source_blocks"][0] == {"id": "SUBJECT", "text": stanje["editions"][0]["subject"]}


def test_lokalni_vir_postane_prilagoditev_z_okvirjem(tmp_path):
    stanje = _stanje()
    prilagoditve = sestavi_vhod(stanje, _hr_vhod(stanje, _mapa(tmp_path)))["approved_adaptations"]
    assert prilagoditve[0]["block_ids"] == ["B2_TITLE", "B2_BODY", "B2_CTA"]
    assert prilagoditve[0]["vir"] == "Radionica u Zagrebu."
    assert prilagoditve[1]["block_ids"] == ["PREHEADER", "HOOK", "CLOSING"]
    assert "ne omenjaj" in prilagoditve[1]["navodilo"]


def test_brez_lokalnega_vira_ni_prilagoditev(tmp_path):
    stanje = _stanje()
    stanje["_run"]["gradivo_odlocitve"]["jeziki"]["hr"]["block-02"] = {"nacin": "transkreacija", "url": ""}
    vhod = sestavi_vhod(stanje, _hr_vhod(stanje, _mapa(tmp_path)))
    assert vhod["approved_adaptations"] == []


def test_referenca_in_zetev_v_constraints(tmp_path):
    stanje = _stanje()
    c = sestavi_vhod(stanje, _hr_vhod(stanje, _mapa(tmp_path)))["constraints"]
    assert c["referenca"]["bloki"] == [{"block_id": "B1", "url": "https://frodx.com/hr/blog/kolumna",
                                        "besedilo": "Objavljena HR kolumna."}]
    assert c["zetev"]["pari"] == [{"prej": "Zvonilo je u prazno", "potem": "Nitko se nije javio", "razlog": "kalk"}]
    assert "pred splošnimi pravili" in c["zetev"]["navodilo"]


def test_hr_vhod_za_druge_bloke_manjka_korak(tmp_path):
    stanje = _stanje()
    hr_vhod = _hr_vhod(stanje, _mapa(tmp_path))
    hr_vhod["bloki"] = hr_vhod["bloki"][:1]
    with pytest.raises(ManjkaKorak, match="prevod_vhod.py"):
        sestavi_vhod(stanje, hr_vhod)


def test_cli_vhod_zapise_datoteko(tmp_path):
    stanje = _stanje()
    mapa = _mapa(tmp_path)
    vhod, _ = sestavi(stanje, "hr", mapa)
    (mapa / "prevod" / "hr-vhod.json").write_text(json.dumps(vhod, ensure_ascii=False), encoding="utf-8")
    (mapa / "state.json").write_text(json.dumps(stanje, ensure_ascii=False), encoding="utf-8")
    izid = subprocess.run([sys.executable, str(SKRIPTA), "vhod", str(mapa / "state.json")],
                          capture_output=True, text=True)
    assert izid.returncode == 0, izid.stdout
    assert "Zapisano: prevod/hr-sol-vhod.json (11 polj, 2 prilagoditev, 1 parov žetve)" in izid.stdout
    assert json.loads((mapa / "prevod" / "hr-sol-vhod.json").read_text(encoding="utf-8"))["content_type"] == "newsletter"


def test_cli_vhod_brez_hr_vhoda_manjka(tmp_path):
    (tmp_path / "state.json").write_text(json.dumps(_stanje()), encoding="utf-8")
    izid = subprocess.run([sys.executable, str(SKRIPTA), "vhod", str(tmp_path / "state.json")],
                          capture_output=True, text=True)
    assert izid.returncode == 1
    assert "MANJKA:" in izid.stdout and "prevod_vhod.py" in izid.stdout


def test_fnv1a_vektorji_enaki_kot_v_js():
    assert fnv1a("") == "811c9dc5"
    assert fnv1a("a") == "e40c292c"
    assert fnv1a("č") == "080aced8"
    assert fnv1a("Pauletič – „x”") == "3fe7ae8c"


def test_fnv1a_vendoriranih_promptov():
    assert fnv1a((VENDOR / PROMPTI["pisec"]).read_text(encoding="utf-8")) == "e0b4683d"
    assert fnv1a((VENDOR / PROMPTI["pregled"]).read_text(encoding="utf-8")) == "8553ec9f"


def _vhod_mini():
    return {"source_blocks": [
        {"id": "SUBJECT", "text": "Zakaj 12 milijonov klicev?"},
        {"id": "B1_BODY", "text": "Piši na igor.pauletic@frodx.com ali https://frodx.com/si/x. Ob 17.12 pelje."},
    ]}


def _izid_mini(**spremembe):
    izid = {
        "izid": "PASS", "krogi": 1,
        "blocks": [{"id": "SUBJECT", "text": "Zašto 12 milijuna poziva?"},
                   {"id": "B1_BODY", "text": "Pišite na igor.pauletic@frodx.com ili https://frodx.com/si/x. U 17:12 vozi."}],
        "review_reasons": [], "pregled": {"verdict": "PASS", "score": 96, "summary": "", "checks": {}, "issues": []},
        "prompt_fnv": {"pisec": "e0b4683d", "pregled": "8553ec9f"},
    }
    izid.update(spremembe)
    return izid


def test_veljaven_izid_brez_opozoril():
    assert preveri_izid(_izid_mini(), _vhod_mini()) == []


def test_url_s_piko_na_koncu():
    assert preveri_izid(_izid_mini(), _vhod_mini()) == []


def test_urednik_je_sprejemljiv_izid():
    assert preveri_izid(_izid_mini(izid="UREDNIK"), _vhod_mini()) == []


def test_napaka_workflowa_se_prenese():
    with pytest.raises(NapakaIzida, match="NAPAKA.*pisec ni vrnil JSON"):
        preveri_izid(_izid_mini(izid="NAPAKA", blocks=[], napaka="pisec ni vrnil JSON"), _vhod_mini())


def test_razhod_prompta_v_n8n():
    with pytest.raises(NapakaIzida, match="vendor/igor-hr-sol"):
        preveri_izid(_izid_mini(prompt_fnv={"pisec": "00000000", "pregled": "8553ec9f"}), _vhod_mini())


def test_napacen_vrstni_red_id():
    izid = _izid_mini()
    izid["blocks"].reverse()
    with pytest.raises(NapakaIzida, match="id-ji"):
        preveri_izid(izid, _vhod_mini())


@pytest.mark.parametrize("besedilo, sporocilo", [
    ("Zašto \u2014 12 milijuna poziva?", "U\\+2014"),
    ("Igor Pauletić, 12 milijuna", "Pauletić"),
    ("   ", "prazno"),
])
def test_krsitve_v_besedilu(besedilo, sporocilo):
    izid = _izid_mini()
    izid["blocks"][0]["text"] = besedilo
    with pytest.raises(NapakaIzida, match=sporocilo):
        preveri_izid(izid, _vhod_mini())


def test_manjkajoc_url_ali_naslov():
    izid = _izid_mini()
    izid["blocks"][1]["text"] = "Pišite na igor.pauletic@frodx.com. U 17:12 vozi."
    with pytest.raises(NapakaIzida, match="https://frodx.com/si/x"):
        preveri_izid(izid, _vhod_mini())


def test_manjkajoca_stevilka_je_opozorilo():
    izid = _izid_mini()
    izid["blocks"][0]["text"] = "Zašto dvanaest milijuna poziva?"
    assert preveri_izid(izid, _vhod_mini()) == ["SUBJECT: številka 12 iz izvirnika ni v prevodu"]


def test_razpakiraj_sprejme_tri_oblike():
    jedro = _izid_mini()
    assert razpakiraj(jedro) == jedro
    assert razpakiraj({"json": jedro}) == jedro
    assert razpakiraj([{"json": jedro}]) == jedro
    with pytest.raises(NapakaIzida):
        razpakiraj([])
