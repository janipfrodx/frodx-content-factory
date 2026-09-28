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
SKRIPTA = SKRIPTE / "iz_editions.py"
BUILD = NOVICNIK / "vendor" / "frodx-newsletter" / "scripts" / "build_newsletter.py"
sys.path.insert(0, str(SKRIPTE))

from iz_editions import NapakaPreslikave, izdaja_iz_editions, vpisi
from izdaja_besedilo import besedilo_v_izdajo, izdaja_v_besedilo


def _vzorec():
    """EDITIONS iz Igorjevega build_newsletter.py, prebran z ast.

    Skripte ne uvažamo: uvoz bi ustvaril __pycache__ v vendor mapi in podrl
    test_vendor_integrity.
    """
    drevo = ast.parse(BUILD.read_text(encoding="utf-8"))
    for vozlisce in drevo.body:
        if isinstance(vozlisce, ast.Assign) and any(getattr(t, "id", None) == "EDITIONS" for t in vozlisce.targets):
            return ast.literal_eval(vozlisce.value)
    raise AssertionError("EDITIONS ni v build_newsletter.py")


def _webinar_ed():
    ed = copy.deepcopy(_vzorec()["si"])
    ed["blocks"].append({
        "id": "block-02", "type": "webinar", "img": "block-02.png", "img_file": "block-02.png",
        "img_alt": "Napoved webinarja.", "title": "Naslov webinarja.", "body": ["Opis webinarja."],
        "bullets": ["Točka 1"],
        "event": [("EVENT_DATE", "2026-06-18"), ("EVENT_TIME", "10:00"), ("EVENT_DURATION_MIN", "45")],
        "cta_label": "Prijavite se", "cta_url": "https://frodx.com/webinar",
    })
    return ed


def test_vzorec_je_berljiv():
    assert "si" in _vzorec()


def test_preslikava_vzorca_si():
    izdaja = izdaja_iz_editions("si", _vzorec()["si"])
    assert izdaja["language"] == "si"
    assert izdaja["package_id"] == "nl-YYYY-MM-slug"
    assert izdaja["status"] == "ready_to_send"
    assert "SI_ALL" in izdaja["delivery"]["segment_ref"]
    assert izdaja["sender"] == {
        "from_name": "Igor Pauletič",
        "from_email": "igor.pauletic@frodx.com",
        "reply_to": "igor.pauletic@frodx.com",
    }
    assert izdaja["greeting"] == "Pozdravljeni,"
    assert izdaja["footer_ref"] == "FRODX_SI"
    assert izdaja["hook"]["archetype"] == "B_prizor"
    assert len(izdaja["hook"]["paragraphs"]) == 3
    blok = izdaja["blocks"][0]
    assert blok["block_id"] == "block-01"
    assert blok["type"] == "column"
    assert blok["image"] == {"alt": "Alt besedilo slike.", "file": "block-01.png"}
    assert len(blok["bullets"]) == 3
    assert blok["event"] is None
    assert blok["cta"] == {"label": "Preberi kolumno", "url": "https://frodx.com/sl/blog/..."}
    assert izdaja["closing"]["type"] == "bookend"
    assert izdaja["signoff"] == {"phrase": "Bodite dobro,", "name": "Igor"}
    assert izdaja["ps"].startswith("P.S.")


def test_toc_cas_in_casovni_pas_se_ne_preneseta():
    izdaja = izdaja_iz_editions("si", _vzorec()["si"])
    besedilo = json.dumps(izdaja, ensure_ascii=False)
    for prepovedano in ("toc", "send_datetime", "SEND_DATETIME", "timezone", "TIMEZONE", "Europe/"):
        assert prepovedano not in besedilo, prepovedano


def test_webinar_dobi_event_s_celim_stevilom_minut():
    izdaja = izdaja_iz_editions("si", _webinar_ed())
    assert izdaja["blocks"][1]["event"] == {"date": "2026-06-18", "time": "10:00", "duration_min": 45}


def test_json_seznami_parov_delujejo_kot_tuple():
    ed = json.loads(json.dumps(_webinar_ed()))
    assert izdaja_iz_editions("si", ed) == izdaja_iz_editions("si", _webinar_ed())


def test_trajanje_ki_ni_stevilo_pade():
    ed = _webinar_ed()
    ed["blocks"][1]["event"][2] = ("EVENT_DURATION_MIN", "45 min")
    with pytest.raises(NapakaPreslikave):
        izdaja_iz_editions("si", ed)


def test_blok_brez_slike_dobi_null():
    ed = copy.deepcopy(_vzorec()["si"])
    for kljuc in ("img", "img_file", "img_alt"):
        ed["blocks"][0].pop(kljuc)
    assert izdaja_iz_editions("si", ed)["blocks"][0]["image"] is None


def test_napacen_jezik_v_meta_pade():
    with pytest.raises(NapakaPreslikave):
        izdaja_iz_editions("hr", _vzorec()["si"])


def test_manjkajoce_meta_polje_pade():
    ed = copy.deepcopy(_vzorec()["si"])
    ed["meta"] = [p for p in ed["meta"] if p[0] != "SEGMENT_REF"]
    with pytest.raises(NapakaPreslikave, match="SEGMENT_REF"):
        izdaja_iz_editions("si", ed)


def test_preslikana_izdaja_gre_skozi_pretvorbo_brez_izgube():
    izdaja = izdaja_iz_editions("si", _webinar_ed())
    assert besedilo_v_izdajo(izdaja_v_besedilo(izdaja), izdaja) == izdaja


def _hr_ed():
    ed = copy.deepcopy(_vzorec()["si"])
    ed["meta"] = [("LANGUAGE", "hr") if k == "LANGUAGE" else (k, v) for k, v in ed["meta"]]
    return ed


def test_hr_pred_potrjeno_kritiko_se_zavrne():
    stanje = {"run_slug": "2026-09-28-x", "editions": [], "_run": {"approvals": {"step2": "t"}}}
    with pytest.raises(NapakaPreslikave, match="step3"):
        vpisi(stanje, {"hr": _hr_ed()})


def test_hr_po_potrjeni_kritiki_se_zapise_za_si():
    stanje = {"run_slug": "2026-09-28-x", "editions": [], "_run": {"approvals": {"step3": "t"}}}
    stanje = vpisi(stanje, {"si": _vzorec()["si"]})
    stanje = vpisi(stanje, {"hr": _hr_ed()})
    assert [i["language"] for i in stanje["editions"]] == ["si", "hr"]


def test_si_pred_kritiko_se_zapise():
    stanje = {"run_slug": "2026-09-28-x", "editions": [], "_run": {"approvals": {}}}
    assert vpisi(stanje, {"si": _vzorec()["si"]})["editions"][0]["language"] == "si"


def test_cli(tmp_path):
    stanje = tmp_path / "state.json"
    stanje.write_text(json.dumps({"run_slug": "2026-09-28-x", "editions": [], "_run": {"approvals": {}}}), encoding="utf-8")
    editions = tmp_path / "editions.json"
    editions.write_text(json.dumps({"si": _vzorec()["si"]}, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, str(SKRIPTA), str(stanje), str(editions)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "si" in r.stdout
    assert json.loads(stanje.read_text(encoding="utf-8"))["editions"][0]["language"] == "si"


def test_cli_napaka_ne_spremeni_datoteke(tmp_path):
    stanje = tmp_path / "state.json"
    stanje.write_text(json.dumps({"run_slug": "2026-09-28-x", "editions": [], "_run": {"approvals": {}}}), encoding="utf-8")
    pred = stanje.read_bytes()
    editions = tmp_path / "editions.json"
    editions.write_text(json.dumps({"hr": _hr_ed()}, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, str(SKRIPTA), str(stanje), str(editions)], capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stdout.startswith("NAPAKA:")
    assert stanje.read_bytes() == pred
