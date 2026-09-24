import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLI = REPO / "plugins" / "content-factory" / "skills"
IMAGE_RUN = SKILLI / "frodx-image-run" / "SKILL.md"
DIRIGENT = SKILLI / "frodx-content-factory" / "SKILL.md"
MAPPING = SKILLI / "frodx-content-factory" / "references" / "igor-output-mapping.md"
SHEMA_STANJA = SKILLI / "frodx-content-factory" / "references" / "state-schema.md"
SHEMA = REPO / "schema" / "content-json.schema.json"
APP_DOKUMENT = REPO / "docs" / "social-slike-v-aplikaciji.md"


def _razdelek(vsebina, naslov):
    """Vrne besedilo enega razdelka drugega nivoja, brez naslednjega."""
    zacetek = vsebina.index(naslov)
    ostanek = vsebina[zacetek + len(naslov):]
    konec = ostanek.find("\n## ")
    return ostanek if konec == -1 else ostanek[:konec]


KORAK_2_ZACETEK = "Korak 2 je Igorjev skill"
KORAK_2_KONEC = "Korak 2 in del koraka 4 (Igorjeva vendorirana skilla"


def _korak_2(vsebina):
    """Vrne odsek dirigenta, ki opisuje naročilo socialnih objav v koraku 2.

    Meji sta literalna niza, ne '## ' naslov: znotraj enega razdelka '## Koraki'
    ni ločenega podnaslova za vsak korak, zato _razdelek() tu ne bi ločil
    koraka 2 od koraka 4, ki sledi takoj za njim.
    """
    zacetek = vsebina.index(KORAK_2_ZACETEK)
    konec = vsebina.index(KORAK_2_KONEC, zacetek)
    return vsebina[zacetek:konec]


def test_image_run_ima_fazo_za_socialne_slike():
    vsebina = IMAGE_RUN.read_text(encoding="utf-8")
    assert "## Faza B" in vsebina
    assert "social-image" in vsebina
    assert "1024x1024" in vsebina


def test_image_run_dela_eno_kandidatko_na_objavo():
    """Odločitev 18. 9. 2026: samo OpenAI, ena kandidatka - Gemini para tu ni."""
    faza_b_raw = _razdelek(IMAGE_RUN.read_text(encoding="utf-8"), "## Faza B")
    faza_b = faza_b_raw.lower()
    assert "ZvoLqzl7zBr8X4WR" in faza_b_raw
    assert "lHc3NdejxehMyc9O" not in faza_b_raw
    assert "ena kandidatka" in faza_b


def test_image_run_naslovna_slika_ostane_na_1536():
    """Faza A se ne spremeni - naslovna slika potrebuje crop na 1200x630."""
    vsebina = IMAGE_RUN.read_text(encoding="utf-8")
    assert "1536x1024" in vsebina
    assert "lHc3NdejxehMyc9O" in vsebina


def _faza_b_uvod(vsebina):
    """Uvod faze B - vse pred prvo ostevilceno tocko, z normaliziranim belim prostorom."""
    faza_b = _razdelek(vsebina, "## Faza B")
    return " ".join(faza_b.split("\n12.")[0].split())


def test_image_run_se_ne_ustavi_pri_treh_objavah_ampak_sele_pri_stirih():
    """Spec: meje stevila objav ne zabija stroj - odlocitev je Igorjeva.

    Ustavitev ostane samo pri stirih ali vec (korak 2 ni bil opravljen), in
    Igor mora ob odstopanju izvedeti, koliko placljivih klicev to stane.
    """
    uvod = _faza_b_uvod(IMAGE_RUN.read_text(encoding="utf-8"))
    assert "natanko dve" not in uvod, "stara trda ustavitev pri dveh objavah"
    assert "ne ustavljaj" in uvod
    assert "štirih ali več" in uvod, "ustavitev pri stirih objavah je izpadla"
    assert "plačljiv" in uvod, "uvod mora povedati ceno, ki jo odstopanje pomeni"


def test_image_run_pise_obe_polji_v_social_posts():
    vsebina = IMAGE_RUN.read_text(encoding="utf-8")
    assert "social_posts[i].image_url" in vsebina
    assert "social_posts[i].image_alt" in vsebina


def test_shema_stanja_pozna_social_images():
    vsebina = SHEMA_STANJA.read_text(encoding="utf-8")
    assert "social_images" in vsebina


def test_shema_stanja_pozna_social_candidates():
    """Dirigent ga zapise v koraku 2; brez vrstice v shemi ga bralec sheme ne najde."""
    vrstice = [
        v for v in SHEMA_STANJA.read_text(encoding="utf-8").splitlines()
        if v.startswith("| `social_candidates` |")
    ]
    assert vrstice, "shema `_run` nima vrstice za social_candidates"
    assert "koraka 2" in vrstice[0], "vrstica ne pove, kateri korak ga zapise"


def test_json_shema_zahteva_obe_slikovni_polji():
    shema = json.loads(SHEMA.read_text(encoding="utf-8"))
    objave = shema["properties"]["social_posts"]
    assert set(objave["items"]["required"]) == {"text", "image_url", "image_alt"}
    assert objave["items"]["additionalProperties"] is False


def test_json_shema_stevila_objav_ne_omejuje():
    """Spec: stevila objav gate ne preverja, minItems 1 ostane, maxItems ni."""
    shema = json.loads(SHEMA.read_text(encoding="utf-8"))
    objave = shema["properties"]["social_posts"]
    assert objave["minItems"] == 1
    assert "maxItems" not in objave


def test_image_run_nima_vec_placeholderja_za_id_workflowa():
    """Ce ostane <ID-IZ-TASK-2>, skill poklice neobstojec workflow in tega nihce ne opazi."""
    vsebina = IMAGE_RUN.read_text(encoding="utf-8")
    assert "ID-IZ-TASK-2" not in vsebina


def test_dirigent_zahteva_stiri_objave_in_predlog_dveh():
    korak_2 = _korak_2(DIRIGENT.read_text(encoding="utf-8"))
    assert "igor-column-writer" in korak_2
    assert "štiri objave" in korak_2
    assert "dve najboljši" in korak_2


def test_dirigent_zapise_vse_stiri_pred_vprasanjem():
    """Popravek po teku 14. 9. 2026: rezultat gre v state.json ob nastanku, ne ob potrditvi."""
    korak_2 = _korak_2(DIRIGENT.read_text(encoding="utf-8"))
    assert "_run.social_candidates" in korak_2
    korak_2_brez_prelomov = " ".join(korak_2.split())
    assert "preden Igorja" in korak_2_brez_prelomov


def test_dirigent_pozna_obliko_kandidatk_iz_speca():
    """Spec doloca stiri polja na kandidatko; chosen pove, katero je Igor potrdil."""
    korak_2 = _korak_2(DIRIGENT.read_text(encoding="utf-8"))
    assert "_run.social_candidates" in korak_2
    for polje in ("text", "lever", "score", "chosen"):
        assert f'"{polje}"' in korak_2


def test_mapping_ne_govori_vec_o_batchu_3_5():
    """Standard 3-5 je Igorjev splošni; ta veriga je od 18. 9. 2026 zožena na 4.

    Beli prostor se normalizira: niz je bil nekoč prelomljen čez dve vrstici in
    ga je ta test spregledal.
    """
    vsebina = " ".join(MAPPING.read_text(encoding="utf-8").split())
    assert "batch 3-5" not in vsebina
    assert "štiri" in vsebina


def test_mapping_socialnih_objav_ne_uokvirja_vec_kot_odprto_tocko():
    """Vejo 18. 9. 2026 jo je zaprla - okvir »odprta točka« je zastarel."""
    vsebina = " ".join(MAPPING.read_text(encoding="utf-8").split())
    assert "odprta točka" not in vsebina


def test_mapping_ne_obljublja_vec_da_je_social_posts_koncna_oblika_z_enim_poljem():
    vsebina = MAPPING.read_text(encoding="utf-8")
    assert "image_url" in vsebina


def test_dokument_o_aplikaciji_pojasni_zakaj_sta_polji_neobvezni():
    vsebina = APP_DOKUMENT.read_text(encoding="utf-8")
    assert "dispatchToN8n" in vsebina
    assert 'default("")' in vsebina
    assert "docx" in vsebina
