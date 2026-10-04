import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik" / "scripts"))

from n8n_hr_sol import vozlisca

IMENA = ["Prompti", "Razcleni pisec 0", "Razcleni pisec 1", "Razcleni pisec 2",
         "Odloci 0", "Odloci 1", "Odloci 2", "Odgovor"]


def test_vsa_vozlisca():
    assert list(vozlisca()) == IMENA


def test_prompti_vsebujejo_vendorirana_prompta_dobesedno():
    js = vozlisca()["Prompti"]
    from hr_sol import PROMPTI, VENDOR
    for ime in PROMPTI.values():
        assert json.dumps((VENDOR / ime).read_text(encoding="utf-8"), ensure_ascii=False) in js


def test_odloci_ima_krog_in_pravo_predhodno_vozlisce():
    v = vozlisca()
    assert "const KROG = 1;" in v["Odloci 1"]
    assert "$('Razcleni pisec 1')" in v["Odloci 1"]
    assert "$('Prompti')" in v["Razcleni pisec 0"]
    assert "$('Odloci 0')" in v["Razcleni pisec 1"]


def test_brez_dolgega_pomisljaja_v_generatorju():
    vir = (REPO / "tools" / "n8n_hr_sol.py").read_text(encoding="utf-8")
    assert "\u2014" not in vir


NODE = shutil.which("node")


def _pozeni(js, vhodi):
    """Code vozlišče izvede v node z lažnima $input in $()."""
    ovoj = (
        "const VHODI = " + json.dumps(vhodi, ensure_ascii=False) + ";\n"
        "const $input = { first: () => ({ json: VHODI.__input }) };\n"
        "const $ = (ime) => ({ first: () => ({ json: VHODI[ime] }) });\n"
        "const izid = (() => {\n" + js + "\n})();\n"
        "console.log(JSON.stringify(izid[0].json));\n"
    )
    out = subprocess.run([NODE, "-e", ovoj], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


@pytest.mark.skipif(NODE is None, reason="node ni nameščen")
def test_prompti_fnv_enak_kot_v_pythonu():
    from hr_sol import PROMPTI, VENDOR, fnv1a
    s = _pozeni(vozlisca()["Prompti"], {"__input": {"body": {"source_blocks": [{"id": "SUBJECT", "text": "x"}]}}})
    assert s["prompt_fnv"] == {k: fnv1a((VENDOR / i).read_text(encoding="utf-8")) for k, i in PROMPTI.items()}
    assert s["naprej"] is True
    assert json.loads(s["pisec_user"])["source_blocks"] == [{"id": "SUBJECT", "text": "x"}]


@pytest.mark.skipif(NODE is None, reason="node ni nameščen")
def test_prompti_brez_izvirnika_je_napaka():
    s = _pozeni(vozlisca()["Prompti"], {"__input": {"body": {}}})
    assert s["izid"] == "NAPAKA" and s["naprej"] is False


def _stanje_po_piscu(needs_review=False):
    vhod = {"content_type": "newsletter", "source_blocks": [{"id": "SUBJECT", "text": "x"}], "audit_feedback": []}
    return {"vhod": vhod, "kandidat": [{"id": "SUBJECT", "text": "y"}], "needs_review": needs_review,
            "review_reasons": [], "napaka": None, "prompt_fnv": {}}


def _pregled(verdict="PASS", score=96, blocking=False):
    return {"verdict": verdict, "score": score, "summary": "",
            "checks": {"meaning_preserved": True, "names_numbers_links_preserved": True,
                       "structure_and_constraints_preserved": True, "source_ambiguities_resolved": True},
            "issues": [{"block_id": "SUBJECT", "category": "error" if blocking else "style", "blocking": blocking,
                        "quote": "y", "reason": "r", "replacement": None}]}


@pytest.mark.skipif(NODE is None, reason="node ni nameščen")
@pytest.mark.parametrize("krog, pregled, needs_review, izid, naprej", [
    (0, _pregled(), False, "PASS", False),
    (0, _pregled("FAIL", 84, True), False, "UREDNIK", True),
    (2, _pregled("FAIL", 84, True), False, "UREDNIK", False),
    (0, _pregled(), True, "UREDNIK", False),
    (1, _pregled("PASS_WITH_MINOR_EDITS", 90, False), False, "UREDNIK", False),
])
def test_odloci_pogoj_pass_in_zanka(krog, pregled, needs_review, izid, naprej):
    s = _pozeni(vozlisca()[f"Odloci {krog}"], {
        "__input": {"output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(pregled)}]}]},
        f"Razcleni pisec {krog}": _stanje_po_piscu(needs_review),
    })
    assert (s["izid"], s["naprej"], s["krogi"]) == (izid, naprej, krog)
    if naprej:
        assert json.loads(s["pisec_user"])["audit_feedback"] == pregled["issues"]
        assert json.loads(s["pisec_user"])["candidate_blocks"] == [{"id": "SUBJECT", "text": "y"}]


@pytest.mark.skipif(NODE is None, reason="node ni nameščen")
def test_razcleni_pisca_brez_jsona_je_napaka():
    s = _pozeni(vozlisca()["Razcleni pisec 0"], {
        "__input": {"output": [{"type": "message", "content": [{"type": "output_text", "text": "ni json"}]}]},
        "Prompti": {"vhod": {"source_blocks": []}, "kandidat": [], "napaka": None},
    })
    assert s["napaka"].startswith("pisec ni vrnil JSON")


@pytest.mark.skipif(NODE is None, reason="node ni nameščen")
def test_razcleni_pisca_pregled_ne_dobi_samoocene():
    izhod = {"needs_review": True, "blocks": [{"id": "SUBJECT", "text": "y"}],
             "review_reasons": [{"block_id": "SUBJECT", "source_quote": "x", "question": "?"}]}
    s = _pozeni(vozlisca()["Razcleni pisec 0"], {
        "__input": {"output": [{"type": "message", "content": [{"type": "output_text", "text": "```json\n" + json.dumps(izhod) + "\n```"}]}]},
        "Prompti": {"vhod": {"source_blocks": [{"id": "SUBJECT", "text": "x"}], "audit_feedback": []}, "kandidat": [], "napaka": None},
    })
    pregled_user = json.loads(s["pregled_user"])
    assert pregled_user["candidate_blocks"] == [{"id": "SUBJECT", "text": "y"}]
    assert "audit_feedback" not in pregled_user and "review_reasons" not in pregled_user
    assert s["needs_review"] is True


@pytest.mark.skipif(NODE is None, reason="node ni nameščen")
def test_odgovor_pri_napaki_brez_besedila():
    s = _pozeni(vozlisca()["Odgovor"], {"__input": {"izid": "NAPAKA", "napaka": "x", "kandidat": [{"id": "A", "text": "b"}],
                                                    "krogi": 1, "prompt_fnv": {"pisec": "1", "pregled": "2"}}})
    assert s == {"izid": "NAPAKA", "krogi": 1, "blocks": [], "review_reasons": [], "pregled": None,
                 "prompt_fnv": {"pisec": "1", "pregled": "2"}, "napaka": "x"}
