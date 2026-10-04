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

from hr_sol import (META_HR, NapakaIzida, PROMPTI, VENDOR, fnv1a, polja_si, preveri_izid, razpakiraj,
                    sestavi_editions, sestavi_vhod)
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


def test_pozdrav_v_constraints_iz_docx_pipeline(tmp_path):
    stanje = _stanje()
    c = sestavi_vhod(stanje, _hr_vhod(stanje, _mapa(tmp_path)))["constraints"]
    assert set(c) == {"referenca", "zetev", "pozdrav"}
    assert c["pozdrav"] == {
        "besedilo": "Pozdrav,",
        "navodilo": "Izdaja se začne s stalnim pozdravom »Pozdrav,«, ki ga ne pišeš. "
                    "HOOK mu neposredno sledi, zato se začne z malo začetnico.",
    }


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
    izid = _izid_mini()
    izid["blocks"][1]["text"] = "Pišite na igor.pauletic@frodx.com ili https://frodx.com/si/x, u 17:12 vozi."
    assert preveri_izid(izid, _vhod_mini()) == []


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


IZVEDBA_217299 = REPO / "tests" / "fixtures" / "hr_sol_izvedba_217299.json"
VHOD_217299 = REPO / "tests" / "fixtures" / "hr_sol_vhod_217299.json"


def test_razpakiraj_odgovor_get_workflow_execution():
    odgovor = json.loads(IZVEDBA_217299.read_text(encoding="utf-8"))
    izid = razpakiraj(odgovor)
    assert izid["izid"] == "UREDNIK" and izid["krogi"] == 2
    assert izid == odgovor["data"]["resultData"]["runData"]["Respond to Webhook"][0]["data"]["main"][0][0]["json"]


def test_preveri_izid_na_resnicnem_odgovoru():
    odgovor = json.loads(IZVEDBA_217299.read_text(encoding="utf-8"))
    vhod = json.loads(VHOD_217299.read_text(encoding="utf-8"))
    assert preveri_izid(razpakiraj(odgovor), vhod) == []


@pytest.mark.parametrize("surovo", [
    {"execution": {"id": "1", "status": "error"}, "data": {"resultData": {"runData": {}}}},
    {"blocks": []},
    [{"json": {"krogi": 1}}],
])
def test_razpakiraj_brez_izida_jasna_napaka(surovo):
    with pytest.raises(NapakaIzida, match="nima ključa izid.*Respond to Webhook"):
        razpakiraj(surovo)


def _meta():
    return {"PACKAGE_ID": "nl-2026-10-test-hr", "EDITION_NAME": "TEST", "STATUS": "draft",
            "SEGMENT_REF": "SEG-HR", "FROM_NAME": "Igor Pauletič", "FROM_EMAIL": "igor.pauletic@frodx.com",
            "REPLY_TO": "igor.pauletic@frodx.com", "FOOTER_REF": "", "GREETING": "Pozdrav,",
            "SIGNOFF_PHRASE": "Sve najbolje,", "SIGNOFF_NAME": "Igor",
            "dogodki": {"block-02": {"EVENT_TIME": "13:00"}}}


def _bloki_hr(stanje):
    return [{"id": i, "text": f"HR {i}\n\n  drugi odstavek  \n"} for i, _ in polja_si(stanje["editions"][0])]


def test_izdaja_struktura_iz_si_besedila_iz_izida():
    stanje = _stanje()
    ed = sestavi_editions(stanje, _bloki_hr(stanje), _meta())["hr"]
    meta = dict(ed["meta"])
    assert meta["LANGUAGE"] == "hr" and meta["GREETING"] == "Pozdrav,"
    assert meta["SUBJECT"] == "HR SUBJECT drugi odstavek"
    assert ed["blocks"][0]["title"] == "HR B1_TITLE drugi odstavek"
    assert [b["id"] for b in ed["blocks"]] == ["block-01", "block-02"]
    assert ed["blocks"][0]["cta_url"] == "https://frodx.com/hr/blog/kolumna"
    assert ed["blocks"][0]["img_file"] == "" and ed["blocks"][0]["img_alt"] == ""
    assert ed["signoff_phrase"] == "Sve najbolje,"
    assert ed["hook_archetype"] == stanje["editions"][0]["hook"]["archetype"]


def test_izdaja_razdeli_odstavke_brez_praznih():
    stanje = _stanje()
    ed = sestavi_editions(stanje, _bloki_hr(stanje), _meta())["hr"]
    assert ed["hook"] == ["HR HOOK", "drugi odstavek"]
    assert ed["blocks"][0]["bullets"] == ["HR B1_BULLETS", "drugi odstavek"]
    assert ed["blocks"][1]["bullets"] == []


def test_izdaja_cta_brez_hr_url_ostane_si():
    stanje = _stanje()
    stanje["_run"]["gradivo_odlocitve"]["jeziki"]["hr"]["block-02"]["url"] = ""
    ed = sestavi_editions(stanje, _bloki_hr(stanje), _meta())["hr"]
    assert ed["blocks"][1]["cta_url"] == stanje["editions"][0]["blocks"][1]["cta"]["url"]


def test_izdaja_webinar_z_hr_uro():
    stanje = _stanje()
    dogodek = dict(sestavi_editions(stanje, _bloki_hr(stanje), _meta())["hr"]["blocks"][1]["event"])
    assert dogodek == {"EVENT_DATE": "2026-11-12", "EVENT_TIME": "13:00", "EVENT_DURATION_MIN": "45"}


def test_izdaja_webinar_brez_hr_ure_manjka():
    stanje = _stanje()
    meta = _meta()
    meta["dogodki"] = {}
    with pytest.raises(ManjkaKorak, match="dogodki.block-02.EVENT_TIME"):
        sestavi_editions(stanje, _bloki_hr(stanje), meta)


def test_izdaja_prazen_pozdrav_manjka():
    stanje = _stanje()
    meta = _meta()
    meta["GREETING"] = " "
    with pytest.raises(ManjkaKorak, match="GREETING"):
        sestavi_editions(stanje, _bloki_hr(stanje), meta)


def _pripravi_tek(tmp_path, bloki=None, izid="PASS"):
    stanje = _stanje()
    mapa = _mapa(tmp_path)
    hr_vhod, _ = sestavi(stanje, "hr", mapa)
    vhod = sestavi_vhod(stanje, hr_vhod)
    (mapa / "prevod" / "hr-sol-vhod.json").write_text(json.dumps(vhod, ensure_ascii=False), encoding="utf-8")
    (mapa / "prevod" / "hr-meta.json").write_text(json.dumps(_meta(), ensure_ascii=False), encoding="utf-8")
    (mapa / "state.json").write_text(json.dumps(stanje, ensure_ascii=False), encoding="utf-8")
    bloki = bloki or [{"id": b["id"], "text": f"HR {b['id']}"} for b in vhod["source_blocks"]]
    zadeva = {"izid": izid, "krogi": 1, "blocks": bloki, "review_reasons": [],
              "pregled": {"verdict": "PASS", "score": 96, "summary": "", "checks": {},
                          "issues": [{"block_id": "HOOK", "category": "style", "blocking": False,
                                      "quote": "x", "reason": "y", "replacement": None}]},
              "prompt_fnv": {"pisec": "e0b4683d", "pregled": "8553ec9f"}}
    (mapa / "izid.json").write_text(json.dumps([{"json": zadeva}], ensure_ascii=False), encoding="utf-8")
    return mapa


def _izdaja(mapa):
    return subprocess.run([sys.executable, str(SKRIPTA), "izdaja", str(mapa / "state.json"),
                           str(mapa / "izid.json"), "216761"], capture_output=True, text=True)


def test_cli_izdaja_vpise_hr_in_prevod_hr(tmp_path):
    mapa = _pripravi_tek(tmp_path)
    izid = _izdaja(mapa)
    assert izid.returncode == 0, izid.stdout
    assert "Zapisana HR izdaja (izid PASS, krogi 1, ocena 96)" in izid.stdout
    stanje = json.loads((mapa / "state.json").read_text(encoding="utf-8"))
    hr = next(e for e in stanje["editions"] if e["language"] == "hr")
    assert hr["subject"] == "HR SUBJECT"
    assert hr["greeting"] == "Pozdrav,"
    assert stanje["_run"]["prevod_hr"] == {"izid": "PASS", "krogi": 1, "score": 96, "verdict": "PASS",
                                          "review_reasons": [], "nereseno": [], "execution_id": "216761"}
    assert (mapa / "prevod" / "hr-editions.json").is_file()


def test_izdaja_zavrne_rezervirano_oznako(tmp_path):
    mapa = _pripravi_tek(tmp_path)
    vhod = json.loads((mapa / "prevod" / "hr-sol-vhod.json").read_text(encoding="utf-8"))
    bloki = [{"id": b["id"], "text": f"HR {b['id']}"} for b in vhod["source_blocks"]]
    bloki[2]["text"] = "Prvi odstavek\nCTA: kliknite"
    mapa = _pripravi_tek(tmp_path / "drugi", bloki=bloki)
    pred = (mapa / "state.json").read_text(encoding="utf-8")
    izid = _izdaja(mapa)
    assert izid.returncode == 2
    assert "NAPAKA:" in izid.stdout and "rezervirano oznako" in izid.stdout
    assert (mapa / "state.json").read_text(encoding="utf-8") == pred


def test_cli_izdaja_brez_meta_manjka(tmp_path):
    mapa = _pripravi_tek(tmp_path)
    (mapa / "prevod" / "hr-meta.json").unlink()
    izid = _izdaja(mapa)
    assert izid.returncode == 1
    assert "MANJKA:" in izid.stdout and "hr-meta.json" in izid.stdout


def test_cli_izdaja_napaka_workflowa_ne_pise(tmp_path):
    mapa = _pripravi_tek(tmp_path, izid="NAPAKA")
    pred = (mapa / "state.json").read_text(encoding="utf-8")
    izid = _izdaja(mapa)
    assert izid.returncode == 2
    assert "NAPAKA:" in izid.stdout
    assert (mapa / "state.json").read_text(encoding="utf-8") == pred


def test_cli_izdaja_na_celem_odgovoru_217299(tmp_path):
    stanje = _stanje()
    stanje["editions"][0]["blocks"] = stanje["editions"][0]["blocks"][:1]
    vhod = json.loads(VHOD_217299.read_text(encoding="utf-8"))
    (tmp_path / "prevod").mkdir()
    (tmp_path / "prevod" / "hr-sol-vhod.json").write_text(json.dumps(vhod, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "prevod" / "hr-meta.json").write_text(json.dumps(_meta(), ensure_ascii=False), encoding="utf-8")
    (tmp_path / "state.json").write_text(json.dumps(stanje, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "izid.json").write_text(IZVEDBA_217299.read_text(encoding="utf-8"), encoding="utf-8")
    izid = subprocess.run([sys.executable, str(SKRIPTA), "izdaja", str(tmp_path / "state.json"),
                           str(tmp_path / "izid.json"), "217299"], capture_output=True, text=True)
    assert izid.returncode == 0, izid.stdout + izid.stderr
    assert "Zapisana HR izdaja (izid UREDNIK, krogi 2, ocena 96)" in izid.stdout
    nova = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    hr = next(e for e in nova["editions"] if e["language"] == "hr")
    assert hr["subject"].startswith("Zašto Britanci 12 milijuna puta")
    assert nova["_run"]["prevod_hr"]["execution_id"] == "217299"


@pytest.mark.parametrize("meta", [[], ["PACKAGE_ID"], 5, "PACKAGE_ID"])
def test_cli_izdaja_meta_ni_objekt_napaka(tmp_path, meta):
    mapa = _pripravi_tek(tmp_path)
    (mapa / "prevod" / "hr-meta.json").write_text(json.dumps(meta), encoding="utf-8")
    pred = (mapa / "state.json").read_text(encoding="utf-8")
    izid = _izdaja(mapa)
    assert izid.returncode == 2, izid.stdout + izid.stderr
    assert "NAPAKA:" in izid.stdout and "hr-meta.json" in izid.stdout
    assert "Traceback" not in izid.stderr
    assert (mapa / "state.json").read_text(encoding="utf-8") == pred


@pytest.mark.parametrize("blok", ["HR besedilo", None, ["SUBJECT"]])
def test_blok_izida_ni_objekt(blok):
    izid = _izid_mini()
    izid["blocks"][0] = blok
    with pytest.raises(NapakaIzida, match="objekt"):
        preveri_izid(izid, _vhod_mini())


def test_cli_izdaja_blok_ni_objekt_brez_tracebacka(tmp_path):
    mapa = _pripravi_tek(tmp_path, bloki=["SUBJECT"])
    izid = _izdaja(mapa)
    assert izid.returncode == 2, izid.stdout + izid.stderr
    assert "NAPAKA:" in izid.stdout
    assert "Traceback" not in izid.stderr


def _vhod_lokalni(okvir_na_b1=False):
    vhod = _vhod_mini()
    vhod["source_blocks"].append({"id": "B2_BODY", "text": "Delavnica 14. 10. v Ljubljani, https://frodx.com/si/delavnica, info@frodx.si"})
    vhod["approved_adaptations"] = [
        {"block_ids": ["B2_BODY"], "navodilo": "lokalni", "vir": "Radionica u Zagrebu 21. 10."},
        {"block_ids": ["PREHEADER", "HOOK", "CLOSING"] + (["B1_BODY"] if okvir_na_b1 else []), "navodilo": "okvir"},
    ]
    return vhod


def _izid_lokalni(b2="Radionica u Zagrebu 21. 10., prijave na stranici."):
    izid = _izid_mini()
    izid["blocks"].append({"id": "B2_BODY", "text": b2})
    return izid


def test_lokalni_vir_brez_preverbe_url_naslova_in_stevilk():
    assert preveri_izid(_izid_lokalni(), _vhod_lokalni()) == []


def test_lokalni_vir_se_vedno_brez_dolgega_pomisljaja():
    with pytest.raises(NapakaIzida, match="B2_BODY: dolgi"):
        preveri_izid(_izid_lokalni("Radionica — Zagreb 21. 10."), _vhod_lokalni())


def test_okvirni_vnos_ne_izklopi_preverbe():
    izid = _izid_lokalni()
    izid["blocks"][1]["text"] = "Pišite na igor.pauletic@frodx.com. U 17:12 vozi."
    with pytest.raises(NapakaIzida, match="B1_BODY: manjka https://frodx.com/si/x"):
        preveri_izid(izid, _vhod_lokalni(okvir_na_b1=True))


@pytest.mark.parametrize("besedilo, opozorilo", [
    ("Zašto 12 milijuna poziva? 27,7%", True),
    ("Zašto 12 milijuna poziva? 27,7 %", False),
    ("Zašto 12 milijuna poziva? 27,7 %", False),
    ("Zašto 12 milijuna poziva? https://frodx.com/hr/a1%20b", False),
])
def test_odstotek_brez_nbsp_je_opozorilo(besedilo, opozorilo):
    izid = _izid_mini()
    izid["blocks"][0]["text"] = besedilo
    pricakovano = ["SUBJECT: pred % manjka nedeljivi presledek (U+00A0), npr. 12 %"] if opozorilo else []
    assert preveri_izid(izid, _vhod_mini()) == pricakovano


def test_odstotek_brez_nbsp_tudi_v_lokalnem_bloku():
    opozorila = preveri_izid(_izid_lokalni("Radionica u Zagrebu, 30% popusta."), _vhod_lokalni())
    assert opozorila == ["B2_BODY: pred % manjka nedeljivi presledek (U+00A0), npr. 12 %"]


def test_brez_hr_pozdrava_v_docx_pipeline_napaka(tmp_path, monkeypatch):
    import hr_sol

    pot = tmp_path / "docx-pipeline.md"
    pot.write_text("| `GREETING` | `Pozdravljeni,` | EN = `Hello,` |\n", encoding="utf-8")
    monkeypatch.setattr(hr_sol, "DOCX_PIPELINE", pot)
    stanje = _stanje()
    with pytest.raises(ValueError, match="GREETING"):
        sestavi_vhod(stanje, _hr_vhod(stanje, _mapa(tmp_path)))
