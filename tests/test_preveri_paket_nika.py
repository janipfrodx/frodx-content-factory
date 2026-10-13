import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

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
    telo["version"] = "1.0"
    assert _ima(_krsitve(telo), "type/version", "nika_story 1.1")


def test_manjka_polje_zgodbe():
    telo = _telo()
    telo["story"]["meta_description"] = ""
    assert _ima(_krsitve(telo), "story.meta_description: manjka")


def test_en_alternativni_naslov():
    telo = _telo()
    telo["story"]["alt_titles"] = telo["story"]["alt_titles"][:1]
    assert _ima(_krsitve(telo), "story.alt_titles", "korak 3")


def test_meta_opis_prekratek():
    telo = _telo()
    telo["story"]["meta_description"] = "x" * 120
    assert _ima(_krsitve(telo), "story.meta_description", "120 znakov", "korak 3")


def test_check_py_napaka_bloga_je_krsitev():
    telo = _telo()
    telo["story"]["blog_md"] = telo["story"]["blog_md"].rsplit("\n", 1)[0]
    assert _ima(_krsitve(telo), "story.blog_md", "check.py --blog", "zadnja vrstica", "korak 3")


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
    assert _ima(_krsitve(telo), "preveri", "[PREVERI", "korak 3", "oddaja Niki")
    assert not _ima(_krsitve(telo), "aplikacija")


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


def _objava():
    telo = _telo()
    telo["languages"] = {
        "en": {"title": "Who updates the deal after the call?", "blog_md": "# Who updates the deal after the call?\n\nText.",
               "meta_description": "Deal Progression in HubSpot suggests deal updates after a call.", "linkedin_text": "Short post.\n\nSecond line."},
        "hr": {"title": "Tko ažurira posao nakon poziva?", "blog_md": "# Tko ažurira posao nakon poziva?\n\nTekst.",
               "meta_description": "Deal Progression u HubSpotu predlaže ažuriranja posla nakon poziva."},
    }
    telo["meta"] = {
        "campaign_name": "Interest - Test", "campaign_guid": "00000000-0000-0000-0000-000000000000",
        "tags": {"sl": "1", "en": "2", "hr": "3"},
        "covers": {j: {"url": f"https://f.hubspotusercontent.com/{j}.png", "alt": "Nika"} for j in ("sl", "en", "hr")},
    }
    telo["schedule"] = {"publish_at": "2099-10-20T07:00:00+02:00", "linkedin_date": "2099-10-20"}
    telo["story"]["slug"] = "deal-progression-posodobitve-poslov"
    telo["languages"]["en"]["slug"] = "deal-progression-deal-updates"
    telo["languages"]["hr"]["slug"] = "deal-progression-azuriranje-poslova"
    return telo


def test_faza_niki_ne_zahteva_prevodov():
    assert pp.preveri(_telo(), "niki")[0] == []


def test_faza_objava_zahteva_prevode():
    assert _ima(pp.preveri(_telo(), "objava")[0], "languages.en.blog_md", "korak 7")


def test_faza_objava_gre_skozi():
    assert pp.preveri(_objava(), "objava", rubrika=lambda: {"campaign_name": "Interest - Test",
        "campaign_guid": "00000000-0000-0000-0000-000000000000", "tags": {"sl": "1", "en": "2", "hr": "3"}})[0] == []


def test_kratka_objava_s_povezavo():
    assert _ima(pp.kratka_objava("Vrstica.\n\nhttps://frodx.com"), "povezava")


def test_kratka_objava_predolga():
    assert _ima(pp.kratka_objava("\n".join(["vrstica"] * 5)), "4 vrstice")


def test_kratka_objava_ok():
    assert pp.kratka_objava("Ena.\n\nDve.\n\nTri.") == []


def test_preveri_v_prevodu():
    telo = _objava()
    telo["languages"]["hr"]["blog_md"] += " [PREVERI: datum]"
    assert _ima(pp.preveri(telo, "objava")[0], "languages.hr.blog_md", "[PREVERI")


def test_linkedin_pred_blogom():
    telo = _objava()
    telo["schedule"] = {"publish_at": "2099-10-20T09:00:00+02:00", "linkedin_date": "2099-10-20"}
    assert _ima(pp.preveri(telo, "objava")[0], "schedule", "7.30")
    telo["schedule"]["linkedin_date"] = "2099-10-19"
    assert _ima(pp.preveri(telo, "objava")[0], "schedule", "pred blogom")


def test_publish_at_v_preteklosti_ali_brez_zamika():
    telo = _objava()
    telo["schedule"]["publish_at"] = "2020-01-01T07:00:00+01:00"
    assert _ima(pp.preveri(telo, "objava")[0], "schedule.publish_at", "prihodnosti")
    telo["schedule"]["publish_at"] = "2099-10-20T07:00:00"
    assert _ima(pp.preveri(telo, "objava")[0], "schedule.publish_at", "zamik")


def test_rubrika_se_ne_ujema():
    telo = _objava()
    telo["meta"]["tags"]["hr"] = "999"
    rub = lambda: {"campaign_name": "Interest - Test", "campaign_guid": "00000000-0000-0000-0000-000000000000",
                   "tags": {"sl": "1", "en": "2", "hr": "3"}}
    assert _ima(pp.preveri(telo, "objava", rubrika=rub)[0], "meta.tags.hr", "korak 8")


def test_rubrika_se_ni_v_taksonomiji():
    rub = lambda: {"campaign_name": "", "campaign_guid": "", "tags": {"sl": "", "en": "", "hr": ""}}
    assert _ima(pp.preveri(_objava(), "objava", rubrika=rub)[0], "hubspot-taxonomy.md", "H2")


def test_cli_faza(tmp_path):
    stanje = tmp_path / "state.json"
    stanje.write_text(json.dumps(_telo(), ensure_ascii=False), encoding="utf-8")
    izid = subprocess.run([sys.executable, str(SKRIPTA), str(stanje), "--faza", "objava"], capture_output=True, text=True)
    assert izid.returncode == 1 and "languages.en" in izid.stdout


def test_zamik_ustreza_ljubljani():
    assert pp.zamik_ljubljane_ok("2026-10-20T07:00:00+02:00")
    assert pp.zamik_ljubljane_ok("2026-11-05T07:00:00+01:00")
    assert not pp.zamik_ljubljane_ok("2026-11-05T07:00:00+02:00")
    assert not pp.zamik_ljubljane_ok("2026-07-01T07:00:00+01:00")
    assert not pp.zamik_ljubljane_ok("2026-07-01T07:00:00+00:00")


def test_publish_at_z_napacnim_zamikom():
    telo = _objava()
    telo["schedule"] = {"publish_at": "2099-11-05T07:00:00+02:00", "linkedin_date": "2099-11-05"}
    assert _ima(pp.preveri(telo, "objava")[0], "schedule.publish_at", "Europe/Ljubljana", "korak 9")
    telo["schedule"]["publish_at"] = "2099-11-05T07:00:00+01:00"
    assert not _ima(pp.preveri(telo, "objava")[0], "Europe/Ljubljana")
    telo["schedule"] = {"publish_at": "2099-10-20T07:00:00+02:00", "linkedin_date": "2099-10-20"}
    assert not _ima(pp.preveri(telo, "objava")[0], "Europe/Ljubljana")


def _slug_krsitve(telo, faza="objava"):
    rub = lambda: {"campaign_name": "Interest - Test", "campaign_guid": "00000000-0000-0000-0000-000000000000",
                   "tags": {"sl": "1", "en": "2", "hr": "3"}}
    return pp.preveri(telo, faza, rubrika=rub)[0]


def _nastavi_slug(telo, jezik, vrednost):
    rezina = telo["story"] if jezik == "sl" else telo["languages"][jezik]
    if vrednost is None:
        rezina.pop("slug", None)
    else:
        rezina["slug"] = vrednost


POT_SLUGA = {"sl": "story.slug", "en": "languages.en.slug", "hr": "languages.hr.slug"}


@pytest.mark.parametrize("jezik", ["sl", "en", "hr"])
def test_slug_manjka(jezik):
    telo = _objava()
    _nastavi_slug(telo, jezik, None)
    assert _ima(_slug_krsitve(telo), f"{POT_SLUGA[jezik]}: manjka", "korak 8")


@pytest.mark.parametrize("jezik", ["sl", "en", "hr"])
@pytest.mark.parametrize("slug", [
    "Deal-Progression-Posodobitve",
    "deal-progression-posodobitve-poslov-čas",
    "deal--progression-posodobitve",
    "deal-progression",
    "a-b-c-d-e-f-g",
    "deal-progression-posodobitve-poslov-po-pogovoru-v-hubspotu-zdaj",
    "-deal-progression-posodobitve",
    "deal-progression-posodobitve-",
])
def test_slug_napacen(jezik, slug):
    telo = _objava()
    _nastavi_slug(telo, jezik, slug)
    assert _ima(_slug_krsitve(telo), POT_SLUGA[jezik], "korak 8")


def test_slug_dolzina_60_je_ok_61_ni():
    telo = _objava()
    _nastavi_slug(telo, "sl", "a" * 12 + "-" + "b" * 12 + "-" + "c" * 34)
    assert len(telo["story"]["slug"]) == 60
    assert not _ima(_slug_krsitve(telo), "story.slug")
    _nastavi_slug(telo, "sl", "a" * 12 + "-" + "b" * 12 + "-" + "c" * 35)
    assert _ima(_slug_krsitve(telo), "story.slug", "61 znakov", "največ 60", "korak 8")


@pytest.mark.parametrize("slug", ["topics-razvrscanje-tiketov", "a1-b2-c3", "a-b-c-d-e-f"])
def test_slug_veljaven(slug):
    telo = _objava()
    for j in ("sl", "en", "hr"):
        _nastavi_slug(telo, j, slug)
    assert not _ima(_slug_krsitve(telo), "slug")


def test_slug_ni_niz():
    telo = _objava()
    telo["story"]["slug"] = 5
    assert _ima(_slug_krsitve(telo), "story.slug: manjka", "korak 8")


def test_faza_niki_ne_zahteva_sluga():
    telo = _telo()
    telo["story"].pop("slug", None)
    assert pp.preveri(telo, "niki")[0] == []
    assert not _ima(pp.preveri(_telo(), "niki")[0], "slug")
