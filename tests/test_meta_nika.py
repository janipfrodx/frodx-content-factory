import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NIKA = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "nika"
_spec = importlib.util.spec_from_file_location("meta_nika", NIKA / "scripts" / "meta.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

RUB = {"campaign_name": "Interest - Test", "campaign_guid": "00000000-0000-0000-0000-000000000000", "tags": {"sl": "1", "en": "2", "hr": "3"}}
NASL = {j: {"datoteka": f"{j}.png", "url": f"https://f.hubspotusercontent.com/{j}.png", "alt": f"alt {j}"} for j in ("sl", "en", "hr")}


def _stanje():
    return json.loads((REPO / "tests" / "fixtures" / "nika_story_body.json").read_text(encoding="utf-8"))


def test_izpolni_vse():
    s = _stanje()
    assert m.izpolni(s, RUB, NASL) == []
    assert s["meta"]["tags"] == {"sl": "1", "en": "2", "hr": "3"}
    assert s["meta"]["covers"]["hr"] == {"url": "https://f.hubspotusercontent.com/hr.png", "alt": "alt hr"}


def test_prazna_taksonomija_pove_clovekov_korak():
    prazna = {"campaign_name": "", "campaign_guid": "", "tags": {"sl": "", "en": "", "hr": ""}}
    manjka = m.izpolni(_stanje(), prazna, NASL)
    assert any("H2" in x for x in manjka) and any("H3" in x for x in manjka)


def test_prazen_url_naslovnice_pove_h4():
    nasl = {**NASL, "en": {**NASL["en"], "url": ""}}
    assert any("H4" in x and "en" in x for x in m.izpolni(_stanje(), RUB, nasl))


def test_naslovnice_obstajajo_na_disku():
    for j, n in json.loads((NIKA / "assets" / "naslovnice.json").read_text(encoding="utf-8")).items():
        assert (NIKA / "assets" / n["datoteka"]).is_file(), j
        assert n["alt"].strip(), j


def test_kolumna_ne_vidi_nikine_rubrike():
    import sys
    sys.path.insert(0, str(REPO / "plugins" / "content-factory" / "skills" / "frodx-publish-send" / "scripts"))
    from taxonomy import load_campaigns, load_tags
    pot = NIKA.parent / "kolumna" / "publishing-meta" / "references" / "hubspot-taxonomy.md"
    assert len(load_campaigns(pot)) == 10
    assert not any(k[0] == "nika" for k in load_tags(pot))
