import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTE = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik" / "scripts"
FIXTURE = REPO / "tests" / "fixtures" / "newsletter_draft_body.json"
sys.path.insert(0, str(SKRIPTE))

from preveri_paket import preveri
from tipografija import nbsp_pred_odstotkom

NBSP = "\u00a0"


@pytest.mark.parametrize("jezik", ["si", "hr"])
def test_presledek_pred_odstotkom_postane_nbsp(jezik):
    assert nbsp_pred_odstotkom("Rast 12 % in 3\t% ter 40%.", jezik) == f"Rast 12{NBSP}% in 3{NBSP}% ter 40%."


def test_anglescina_ostane():
    assert nbsp_pred_odstotkom("Growth 12 %", "en") == "Growth 12 %"


def test_idempotentno():
    enkrat = nbsp_pred_odstotkom("12 %", "si")
    assert nbsp_pred_odstotkom(enkrat, "si") == enkrat == f"12{NBSP}%"


def test_rekurzivno_in_url_ostane():
    izdaja = {"hook": {"paragraphs": ["za 30 % več"]}, "cta": {"url": "https://x.si/a%20b"}, "n": 3}
    nova = nbsp_pred_odstotkom(izdaja, "hr")
    assert nova["hook"]["paragraphs"] == [f"za 30{NBSP}% več"]
    assert nova["cta"]["url"] == "https://x.si/a%20b"
    assert nova["n"] == 3
    assert izdaja["hook"]["paragraphs"] == ["za 30 % več"], "vhod se ne sme spremeniti"


def _telo():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _hook(telo, jezik, besedilo):
    izdaja = next(i for i in telo["editions"] if i["language"] == jezik)
    izdaja["hook"]["paragraphs"] = [besedilo]


@pytest.mark.parametrize("besedilo", ["rast 12 % letno", "rast 12% letno"])
def test_preverba_zavrne_manjkajoc_nbsp_v_si(besedilo):
    telo = _telo()
    _hook(telo, "si", besedilo)
    krsitve = preveri(telo)[0]
    assert any("si.hook.paragraphs[0]" in k and "U+00A0" in k and "korak 2" in k for k in krsitve), krsitve


def test_preverba_zavrne_manjkajoc_nbsp_v_hr_s_korakom_4():
    telo = _telo()
    _hook(telo, "hr", "rast 12 % godišnje")
    assert any("hr.hook.paragraphs[0]" in k and "korak 4" in k for k in preveri(telo)[0])


def test_preverba_sprejme_nbsp_v_si():
    telo = _telo()
    _hook(telo, "si", f"rast 12{NBSP}% letno")
    assert preveri(telo)[0] == []


def test_preverba_zavrne_presledek_v_en():
    telo = _telo()
    _hook(telo, "en", f"growth 12{NBSP}% yearly")
    assert any("en.hook.paragraphs[0]" in k and "brez presledka" in k for k in preveri(telo)[0])


def test_preverba_ne_gleda_url_jev():
    telo = _telo()
    telo["editions"][0]["blocks"][0]["cta"]["url"] = "https://www.frodx.com/a2%20b"
    assert preveri(telo)[0] == []


def test_preverba_odstotka_v_alt_slike_kaze_korak_5():
    telo = _telo()
    si = next(i for i in telo["editions"] if i["language"] == "si")
    si["blocks"][0]["image"]["alt"] = "rast 12 % letno"
    krsitve = preveri(telo)[0]
    assert any("image.alt" in k and "korak 5" in k for k in krsitve), krsitve


def _stanje_iz_fixture(tmp_path):
    telo = _telo()
    stanje = dict(telo, _run={"veja": "novicnik", "approvals": {"step3": "2026-09-28T10:00:00"}})
    pot = tmp_path / "state.json"
    pot.write_text(json.dumps(stanje, ensure_ascii=False), encoding="utf-8")
    return pot


def test_vpis_normalizira_si(tmp_path):
    pot = _stanje_iz_fixture(tmp_path)
    izpis = subprocess.run(
        [sys.executable, str(SKRIPTE / "izdaja_besedilo.py"), "izpis", str(pot), "si"],
        capture_output=True, text=True, check=True,
    ).stdout
    vrstice = izpis.splitlines()
    i = vrstice.index("HOOK:") + 1
    vrstice[i] = "rast 12 % letno"
    besedilo = tmp_path / "si.txt"
    besedilo.write_text("\n".join(vrstice) + "\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(SKRIPTE / "izdaja_besedilo.py"), "vpis", str(pot), "si", str(besedilo)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout
    si = next(i for i in json.loads(pot.read_text(encoding="utf-8"))["editions"] if i["language"] == "si")
    assert si["hook"]["paragraphs"][0] == f"rast 12{NBSP}% letno"


def test_iz_editions_normalizira_hr():
    from iz_editions import izdaja_iz_editions
    ed = {
        "meta": [[k, v] for k, v in {
            "PACKAGE_ID": "nl-2026-10-test-hr", "EDITION_NAME": "Test", "LANGUAGE": "hr", "STATUS": "draft",
            "SEGMENT_REF": "HR_ALL", "FROM_NAME": "Igor Pauletić", "FROM_EMAIL": "igor.pauletic@frodx.com",
            "REPLY_TO": "igor.pauletic@frodx.com", "FOOTER_REF": "FRODX_HR", "SUBJECT": "Rast 12 %",
            "PREHEADER": "P", "GREETING": "Pozdrav,",
        }.items()],
        "hook_archetype": "B_prizor", "hook": ["za 30 % več"],
        "blocks": [{"id": "block-01", "type": "column", "img_file": "", "img_alt": "", "title": "T",
                    "body": ["B"], "bullets": [], "cta_label": "C", "cta_url": "https://www.frodx.com/"}],
        "closing_type": "bookend", "closing": ["K"], "signoff_phrase": "Lijep pozdrav,", "signoff_name": "Igor",
        "ps": "",
    }
    izdaja = izdaja_iz_editions("hr", ed)
    assert izdaja["subject"] == f"Rast 12{NBSP}%"
    assert izdaja["hook"]["paragraphs"] == [f"za 30{NBSP}% več"]
