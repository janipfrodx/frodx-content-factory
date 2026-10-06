import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKRIPTA = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "nika" / "scripts" / "preveri_paket.py"
FIXTURE = REPO / "tests" / "fixtures" / "nika_story_body.json"

_spec = importlib.util.spec_from_file_location("preveri_paket_nika", SKRIPTA)
pp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pp)


def _telo():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _krsitve(telo):
    return pp.preveri(telo)[0]


def _ima(krsitve, *nizi):
    return any(all(n in k for n in nizi) for k in krsitve)


def test_fixture_gre_skozi():
    krsitve, opozorila = pp.preveri(_telo())
    assert krsitve == []
    assert any("dolžina 450" in o for o in opozorila)


def test_dejavnosti_iz_vertikal():
    imena = pp.dejavnosti()
    assert len(imena) == 10
    assert "B2B proizvodnja in distribucija" in imena
    assert "Dejavnost" not in imena


def test_napacna_verzija():
    telo = _telo()
    telo["version"] = "1.1"
    assert _ima(_krsitve(telo), "type/version", "init_run.py")


def test_manjka_polje_zgodbe():
    telo = _telo()
    telo["story"]["first_comment"] = ""
    assert _ima(_krsitve(telo), "story.first_comment", "korak 3")


def test_en_alternativni_naslov():
    telo = _telo()
    telo["story"]["alt_titles"] = telo["story"]["alt_titles"][:1]
    assert _ima(_krsitve(telo), "story.alt_titles", "korak 3")


def test_meta_opis_prekratek():
    telo = _telo()
    telo["story"]["meta_description"] = "x" * 120
    assert _ima(_krsitve(telo), "story.meta_description", "120 znakov", "korak 3")


def test_prvi_komentar_brez_vira():
    telo = _telo()
    telo["story"]["first_comment"] = "Več na https://app.hubspot.com/product-updates/123"
    assert _ima(_krsitve(telo), "story.first_comment", "korak 3")


def test_check_py_napaka_bloga_je_krsitev():
    telo = _telo()
    telo["story"]["blog_md"] = telo["story"]["blog_md"].rsplit("\n", 1)[0]
    assert _ima(_krsitve(telo), "story.blog_md", "check.py --blog", "zadnja vrstica", "korak 3")


def test_povezava_v_linkedin_je_krsitev():
    telo = _telo()
    telo["story"]["linkedin_text"] += " https://knowledge.hubspot.com/x"
    assert _ima(_krsitve(telo), "story.linkedin_text", "check.py --linkedin", "korak 3")


def test_vrstica_s_tremi_vezaji_v_blogu():
    telo = _telo()
    telo["story"]["blog_md"] = "# Naslov\n\nUvod.\n---\n" + telo["story"]["blog_md"]
    assert _ima(_krsitve(telo), "story.blog_md", "---", "korak 3")


def test_dolgi_pomisljaj_kjerkoli():
    telo = _telo()
    telo["dilemma"] = "Ena stvar \u2014 druga stvar."
    assert _ima(_krsitve(telo), "dilemma", "U+2014", "korak")


def test_neznana_dejavnost():
    telo = _telo()
    telo["activity"] = "proizvodnja"
    assert _ima(_krsitve(telo), "activity", "vertikale.md", "korak 2")


def test_kb_urls_prazen():
    telo = _telo()
    telo["source"]["kb_urls"] = []
    assert _ima(_krsitve(telo), "source.kb_urls", "korak 2")


def test_status_in_datum_maila():
    telo = _telo()
    telo["source"]["status"] = "Trending Betas"
    telo["source"]["mail_date"] = "14. 9. 2026"
    krsitve = _krsitve(telo)
    assert _ima(krsitve, "source.status", "korak 1")
    assert _ima(krsitve, "source.mail_date", "korak 1")


def test_nova_trditev_z_app_hubspot():
    telo = _telo()
    telo["claims"][0]["url"] = "https://app.hubspot.com/product-updates/123"
    assert _ima(_krsitve(telo), "claims[0]", "korak 2")


def test_nova_trditev_brez_navedka():
    telo = _telo()
    telo["claims"][0]["quote"] = ""
    assert _ima(_krsitve(telo), "claims[0]", "navedka", "korak 2")


def test_nerazvrscena_trditev():
    telo = _telo()
    telo["claims"][4]["category"] = "mnenje"
    assert _ima(_krsitve(telo), "claims[4]", "korak 3")


def test_nacelo_brez_navedenega_nacela():
    telo = _telo()
    telo["judgment"]["principle"] = ""
    assert _ima(_krsitve(telo), "judgment.principle", "korak 3")


def test_neznan_izvor_presoje():
    telo = _telo()
    telo["judgment"]["origin"] = "nika"
    assert _ima(_krsitve(telo), "judgment.origin", "korak 3")


def test_oznaka_preveri_brez_vrstice():
    telo = _telo()
    telo["preveri"] = []
    telo["story"]["blog_md"] = telo["story"]["blog_md"].replace(
        "Pogoj sta snemanje s prepisom in Notetaker.",
        "Pogoj sta snemanje s prepisom in Notetaker [PREVERI: ali velja za Teams].",
    )
    assert _ima(_krsitve(telo), "preveri", "[PREVERI", "korak 3")


def test_run_v_telesu():
    telo = _telo()
    telo["_run"] = {}
    assert _ima(_krsitve(telo), "_run", "korak 4")


def test_ocena_pod_pragom_je_opozorilo():
    telo = _telo()
    telo["score"]["total"] = 8.5
    krsitve, opozorila = pp.preveri(telo)
    assert krsitve == []
    assert any("8.5" in o and "9,0" in o for o in opozorila)


def test_ocena_manjka():
    telo = _telo()
    telo["score"] = {"total": None, "items": {}}
    assert _ima(_krsitve(telo), "score.total", "korak 3")


def test_vsaka_krsitev_pove_korak():
    krsitve = _krsitve({"type": "x", "story": {"blog_md": "a\n---\nb"}, "claims": [{"text": "t", "category": "?"}], "_run": {}})
    assert len(krsitve) >= 10
    for k in krsitve:
        assert re.search(r"\((korak \d|init_run\.py)\)$", k), k


def test_cli_zapise_telo_brez_run(tmp_path):
    stanje = _telo()
    stanje["_run"] = {"veja": "nika", "step": 4}
    vhod = tmp_path / "state.json"
    vhod.write_text(json.dumps(stanje, ensure_ascii=False), encoding="utf-8")
    cilj = tmp_path / "outbox" / "2026-10-06-deal-progression.json"
    r = subprocess.run([sys.executable, str(SKRIPTA), str(vhod), "--telo", str(cilj)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
    assert "OK" in r.stdout
    telo = json.loads(cilj.read_text(encoding="utf-8"))
    assert "_run" not in telo
    assert telo["type"] == "nika_story"


def test_cli_ob_krsitvi_ne_zapise(tmp_path):
    stanje = _telo()
    stanje["version"] = "2.0"
    vhod = tmp_path / "state.json"
    vhod.write_text(json.dumps(stanje, ensure_ascii=False), encoding="utf-8")
    cilj = tmp_path / "outbox" / "x.json"
    r = subprocess.run([sys.executable, str(SKRIPTA), str(vhod), "--telo", str(cilj)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "KRŠITEV:" in r.stdout
    assert not cilj.exists()


def test_ista_oznaka_v_blogu_in_linkedinu_se_steje_enkrat():
    telo = _telo()
    telo["preveri"] = [{"text": "ali velja za Teams", "where": "uvod"}]
    oznaka = " [PREVERI: ali velja za Teams]"
    telo["story"]["blog_md"] = telo["story"]["blog_md"].replace(
        "Pogoj sta snemanje s prepisom in Notetaker.",
        "Pogoj sta snemanje s prepisom in Notetaker." + oznaka,
    )
    telo["story"]["linkedin_text"] += oznaka
    assert not _ima(_krsitve(telo), "preveri", "[PREVERI")


def test_oznaka_samo_v_naslovu_brez_vrstice():
    telo = _telo()
    telo["preveri"] = []
    telo["story"]["title"] += " [PREVERI: naslov]"
    assert _ima(_krsitve(telo), "preveri", "[PREVERI", "korak 3")


def test_preveri_vrstica_brez_where():
    telo = _telo()
    telo["preveri"] = [{"text": "a"}]
    assert _ima(_krsitve(telo), "preveri", "korak 3")
