import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SKRIPTA = REPO / "plugins" / "content-factory" / "skills" / "frodx-publish-send" / "scripts" / "validate_package.py"
TAXONOMY = REPO / "plugins" / "content-factory" / "skills" / "frodx-publishing-meta" / "references" / "hubspot-taxonomy.md"
FIXTURES = REPO / "tests" / "fixtures"

sys.path.insert(0, str(SKRIPTA.parent))

from taxonomy import load_campaigns, load_tags


def _validate(ime):
    from validate_package import validate
    pkg = json.loads((FIXTURES / ime).read_text(encoding="utf-8"))
    return validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))


def test_veljaven_paket_nima_napak():
    assert _validate("package_valid.json") == []


def test_prazna_hrvascina_pade():
    napake = _validate("package_missing_hr.json")
    assert any("languages.hr.content" in n for n in napake)
    assert any("languages.hr.seo_title" in n for n in napake)
    assert not [n for n in napake if "social_posts" in n], (
        "vzorec meri samo manjkajoco hrvascino - slikovna polja objav morajo biti veljavna"
    )


def test_izmisljena_kampanja_pade():
    napake = _validate("package_bad_campaign.json")
    assert any("campaign_name" in n and "Zvestoba in nagrade" in n for n in napake)
    assert not [n for n in napake if "social_posts" in n], (
        "vzorec meri samo izmisljeno kampanjo - slikovna polja objav morajo biti veljavna"
    )


def test_predolg_seo_title_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["seo_title"] = "x" * 66
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("seo_title" in n and "65" in n for n in napake)


def test_prekratek_meta_description_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["en"]["meta_description"] = "Prekratko."
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("meta_description" in n and "140" in n for n in napake)


def test_dolgi_pomisljaj_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = "Stavek — in nadaljevanje.\n\nigor.pauletic@frodx.com"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("pomi" in n.lower() for n in napake)


def test_manjkajoc_podpis_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = "Kolumna brez podpisa."
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("igor.pauletic@frodx.com" in n for n in napake)


def test_manjkajoc_tag_kjer_obstaja_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["tag_id"] = ""
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("tag_id" in n and "sl" in n for n in napake)


def test_prazen_tag_kjer_ga_taksonomija_nima_je_v_redu():
    """EN in HR za Programi zvestobe nimata taga. Prazno je pravilno, ne napaka."""
    from validate_package import validate
    tags = load_tags(TAXONOMY)
    kampanja = "Interest - Programi zvestobe"
    assert (kampanja, "en") not in tags, "predpogoj: taksonomija za EN taga nima"
    assert (kampanja, "hr") not in tags, "predpogoj: taksonomija za HR taga nima"
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    assert pkg["languages"]["en"]["tag_id"] == ""
    assert pkg["languages"]["hr"]["tag_id"] == ""
    napake = validate(pkg, load_campaigns(TAXONOMY), tags)
    assert [n for n in napake if "tag_" in n] == []


def test_izmisljen_tag_kjer_ga_taksonomija_nima_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["en"]["tag_id"] = "999999999"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("tag_id" in n and "en" in n for n in napake)


def test_brez_socialnih_objav_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["social_posts"] = []
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("social_posts" in n for n in napake)


def test_run_blok_se_ignorira():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["_run"] = {"step": 7}
    assert validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY)) == []


def test_cli_vrne_0_za_veljaven_paket():
    r = subprocess.run([sys.executable, str(SKRIPTA), str(FIXTURES / "package_valid.json")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_cli_vrne_1_za_neveljaven_paket():
    r = subprocess.run([sys.executable, str(SKRIPTA), str(FIXTURES / "package_bad_campaign.json")], capture_output=True, text=True)
    assert r.returncode == 1
    assert "campaign_name" in r.stdout


# --- Popravni krog 1: campaign_name enakost med jeziki ---

def test_campaign_name_razlicna_med_jeziki_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["en"]["campaign_name"] = "Interest - CX Customer Experience"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("campaign_name" in n and "enak" in n for n in napake)


# --- Popravni krog 1: prepovedane fraze ---

def test_prepovedana_fraza_sl_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = "Tu je trik, ki deluje.\n\nigor.pauletic@frodx.com"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("tu je trik" in n for n in napake)


def test_prepovedana_fraza_en_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["en"]["content"] = "Here's the trick that works.\n\nigor.pauletic@frodx.com"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("here's the trick" in n for n in napake)


def test_prepovedana_fraza_hr_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["hr"]["content"] = "Ovdje je trik koji djeluje.\n\nigor.pauletic@frodx.com"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("ovdje je trik" in n for n in napake)


def test_prepovedana_fraza_neobcutljiva_na_velikost_crk_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = "Tu Je Trik, ki deluje.\n\nigor.pauletic@frodx.com"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("tu je trik" in n for n in napake)


# --- Popravni krog 1: featured_image_alt ---

def test_featured_image_alt_prazen_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["featured_image_alt"] = ""
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("featured_image_alt" in n and "prazen" in n for n in napake)


def test_featured_image_alt_predolg_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["featured_image_alt"] = "x" * 161
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("featured_image_alt" in n and "160" in n for n in napake)


# --- Popravni krog 1: meta.version ---

def test_meta_version_napacna_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["meta"]["version"] = "1.0"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("meta.version" in n for n in napake)


# --- Popravni krog 1: tag_name/tag_slug neujemanje s taksonomijo ---

def test_tag_name_se_ne_ujema_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["tag_name"] = "Napačno ime"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("tag_name" in n and "sl" in n for n in napake)


def test_tag_slug_se_ne_ujema_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["tag_slug"] = "napacen-slug"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("tag_slug" in n and "sl" in n for n in napake)


# --- Popravni krog 1: podpis - ponovljen, ni sam v vrstici, ni na koncu, hiperpovezava ---

def test_podpis_ponovljen_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = (
        "Prvi odstavek.\n\nigor.pauletic@frodx.com\n\nigor.pauletic@frodx.com"
    )
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("krat" in n and "igor.pauletic@frodx.com" in n for n in napake)


def test_podpis_ni_sam_v_vrstici_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = "Prvi odstavek.\n\nIgor Pauletic igor.pauletic@frodx.com"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("ne stoji sam" in n for n in napake)


def test_podpis_ni_na_koncu_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = (
        "Prvi odstavek.\n\nigor.pauletic@frodx.com\n\n"
        "Vrstica 1.\nVrstica 2.\nVrstica 3.\nVrstica 4.\nVrstica 5."
    )
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("ni na koncu" in n for n in napake)


def test_podpis_hiperpovezava_markdown_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = "Prvi odstavek.\n\n[pišite mi](mailto:igor.pauletic@frodx.com)"
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("hiperpovezava" in n for n in napake)


def test_podpis_hiperpovezava_html_pade():
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["content"] = (
        'Prvi odstavek.\n\n<a href="mailto:igor.pauletic@frodx.com">pišite mi</a>'
    )
    napake = validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))
    assert any("hiperpovezava" in n for n in napake)


# --- Popravni krog 2: gate ne rabi ničesar izven plugins/content-factory ---

def test_gate_dela_iz_samostojno_kopiranega_plugina(tmp_path):
    """Cowork namesti samo plugins/content-factory/ (glej marketplace.json).

    Gate ne sme uvažati ničesar izven te mape - ne sme pasti z
    ModuleNotFoundError, ko poganjamo skripto iz kopije, ki vsebuje
    samo to mapo, brez repo korena in brez tools/.
    """
    plugin_kopija = tmp_path / "content-factory"
    shutil.copytree(REPO / "plugins" / "content-factory", plugin_kopija)
    skripta_kopija = plugin_kopija / "skills" / "frodx-publish-send" / "scripts" / "validate_package.py"

    r = subprocess.run(
        [sys.executable, str(skripta_kopija), str(FIXTURES / "package_valid.json")],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr


# --- Popravki po teku 14.-15. 8. 2026: _run.open_tasks opozori, ne blokira ---

ZADOLZITEV = {
    "what": "hrvaška različica ni šla skozi native pregled",
    "who": "native govorec hrvaščine",
    "created_at": "2026-08-15T12:00:00.000Z",
    "step": 4,
}


def _s_zadolzitvami(tmp_path, naloge):
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["_run"] = {"step": 6, "open_tasks": naloge, "image": {"chosen": "openai", "url": SHRAMBA}}
    pot = tmp_path / "state.json"
    pot.write_text(json.dumps(pkg, ensure_ascii=False), encoding="utf-8")
    slike = tmp_path / "images"
    slike.mkdir()
    (slike / "izbrana.png").write_bytes(_png(1536, 1024))
    return pot


def test_opozorila_prazen_seznam_je_tiho():
    from validate_package import opozorila
    assert opozorila({"open_tasks": []}) == []
    assert opozorila({}) == []
    assert opozorila(None) == []


def test_opozorila_izpisejo_kaj_kdo_in_korak():
    from validate_package import opozorila
    vrstice = opozorila({"open_tasks": [ZADOLZITEV]})
    assert len(vrstice) == 1
    assert "native pregled" in vrstice[0]
    assert "korak 4" in vrstice[0]
    assert "native govorec" in vrstice[0]


def test_opozorila_prenesejo_nepopolno_zadolzitev():
    """Zadolžitev brez who/step se izpiše, ne sesuje in ne izgine."""
    from validate_package import opozorila
    vrstice = opozorila({"open_tasks": [{"what": "vrstica v vrsti tem ni označena"}, "gol niz"]})
    assert any("ni označena" in v for v in vrstice)
    assert any("gol niz" in v for v in vrstice)


def test_opozorila_ob_napacnem_tipu_ne_padejo():
    from validate_package import opozorila
    vrstice = opozorila({"open_tasks": "ni seznam"})
    assert len(vrstice) == 1
    assert "ni seznam" in vrstice[0]


def test_odprte_zadolzitve_ne_spremenijo_izida_validacije():
    """open_tasks je v _run, ki ga validate() ne vidi - paket ostane veljaven."""
    from validate_package import validate
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["_run"] = {"open_tasks": [ZADOLZITEV]}
    assert validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY)) == []


def test_cli_z_odprto_zadolzitvijo_opozori_a_vrne_0(tmp_path):
    pot = _s_zadolzitvami(tmp_path, [ZADOLZITEV])
    r = subprocess.run([sys.executable, str(SKRIPTA), str(pot)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "odprte zadolžitve (1)" in r.stdout
    assert "native pregled" in r.stdout
    assert "Paket je pripravljen" in r.stdout


def test_cli_izpise_opozorilo_tudi_ko_paket_pade(tmp_path):
    """Opozorilo se ne sme izgubiti zato, ker so v paketu tudi kršitve."""
    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    pkg["languages"]["sl"]["featured_image_alt"] = ""
    pkg["_run"] = {"open_tasks": [ZADOLZITEV]}
    pot = tmp_path / "state.json"
    pot.write_text(json.dumps(pkg, ensure_ascii=False), encoding="utf-8")

    r = subprocess.run([sys.executable, str(SKRIPTA), str(pot)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "odprte zadolžitve (1)" in r.stdout
    assert "featured_image_alt" in r.stdout


def test_cli_brez_odprtih_zadolzitev_ne_izpise_opozorila(tmp_path):
    pot = _s_zadolzitvami(tmp_path, [])
    r = subprocess.run([sys.executable, str(SKRIPTA), str(pot)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "zadolžitve" not in r.stdout


# --- Slikovna pot: gate zavrne premajhno naslovno sliko ---

import struct

PNG_PODPIS = b"\x89PNG\r\n\x1a\n"


def _png(sirina: int, visina: int) -> bytes:
    return (
        PNG_PODPIS
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", sirina, visina)
        + b"\x08\x06\x00\x00\x00"
    )


def _tek(tmp_path, sirina=None, visina=None, ime="izbrana.png"):
    """Zgradi mapo teka s state.json in po želji z naslovno sliko."""
    state = tmp_path / "state.json"
    state.write_text("{}", encoding="utf-8")
    if sirina is not None:
        slike = tmp_path / "images"
        slike.mkdir()
        (slike / ime).write_bytes(_png(sirina, visina))
    return state


def test_preveri_sliko_brez_run_bloka_vrne_prazno(tmp_path):
    from validate_package import preveri_sliko
    assert preveri_sliko(None, _tek(tmp_path)) == []


def test_premajhna_slika_pade(tmp_path):
    from validate_package import preveri_sliko
    state = _tek(tmp_path, 784, 522)
    napake = preveri_sliko({"image": {"chosen": "openai", "url": SHRAMBA}}, state)
    assert any("784x522" in n for n in napake)


def test_ustrezna_slika_gre_skozi(tmp_path):
    from validate_package import preveri_sliko
    state = _tek(tmp_path, 1536, 1024)
    assert preveri_sliko({"image": {"chosen": "gemini", "url": SHRAMBA}}, state) == []


def test_manjkajoca_slika_pade(tmp_path):
    from validate_package import preveri_sliko
    state = _tek(tmp_path)
    napake = preveri_sliko({"image": {"chosen": "openai", "url": SHRAMBA}}, state)
    assert any("izbrana" in n for n in napake)


SHRAMBA = "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/a.png"


def test_manjkajoc_url_pade(tmp_path):
    from validate_package import preveri_sliko
    state = _tek(tmp_path, 1536, 1024)
    napake = preveri_sliko({"image": {"chosen": "openai"}}, state)
    assert any("url" in n for n in napake)


def test_url_na_tujem_gostitelju_pade(tmp_path):
    from validate_package import preveri_sliko
    state = _tek(tmp_path, 1536, 1024)
    napake = preveri_sliko(
        {"image": {"chosen": "openai", "url": "https://example.com/a.png"}}, state
    )
    assert any("example.com" in n for n in napake)


def test_url_brez_https_pade(tmp_path):
    from validate_package import preveri_sliko
    state = _tek(tmp_path, 1536, 1024)
    napake = preveri_sliko(
        {"image": {"chosen": "openai", "url": SHRAMBA.replace("https://", "http://")}},
        state,
    )
    assert any("https" in n for n in napake)


def test_url_samo_z_gostiteljem_brez_poti_pade(tmp_path):
    """Gol gostitelj ni slika. Brez te preverbe gate spusti `https://<host>` naprej."""
    from validate_package import preveri_sliko
    state = _tek(tmp_path, 1536, 1024)
    for url in ("https://umvjwjzdrtamfrcqhopa.supabase.co", "https://umvjwjzdrtamfrcqhopa.supabase.co/"):
        napake = preveri_sliko({"image": {"chosen": "openai", "url": url}}, state)
        assert any("nima poti" in n for n in napake), url


def test_veljaven_url_in_dovolj_velika_slika_gresta_skozi(tmp_path):
    from validate_package import preveri_sliko
    state = _tek(tmp_path, 1536, 1024)
    assert preveri_sliko({"image": {"chosen": "openai", "url": SHRAMBA}}, state) == []


# --- Socialne objave nosijo svojo sliko (od 18. 9. 2026) ---

def _napake(spremeni):
    """Vzame veljaven vzorec, ga spremeni in vrne seznam kršitev."""
    from validate_package import validate

    pkg = json.loads((FIXTURES / "package_valid.json").read_text(encoding="utf-8"))
    spremeni(pkg)
    return validate(pkg, load_campaigns(TAXONOMY), load_tags(TAXONOMY))


def test_social_brez_slike_pade():
    """Objava brez slike je po 18. 9. 2026 nepopolna - LinkedIn objava je tekst plus slika."""
    def spremeni(pkg):
        del pkg["social_posts"][0]["image_url"]

    assert any("social_posts[0].image_url" in n for n in _napake(spremeni))


def test_social_brez_alt_teksta_pade():
    def spremeni(pkg):
        pkg["social_posts"][0]["image_alt"] = "   "

    assert any("social_posts[0].image_alt" in n for n in _napake(spremeni))


def test_social_slika_na_tujem_gostitelju_pade():
    """Isti gostitelj kot naslovna slika - drugje aplikacija slike ne servira."""
    def spremeni(pkg):
        pkg["social_posts"][0]["image_url"] = "https://example.com/slika.png"

    napake = _napake(spremeni)
    assert any("social_posts[0].image_url" in n and "gostitelj" in n for n in napake)


def test_social_slika_brez_https_pade():
    """Ista veja kot pri naslovni sliki: `http://` aplikacija ne servira."""
    def spremeni(pkg):
        pkg["social_posts"][0]["image_url"] = (
            pkg["social_posts"][0]["image_url"].replace("https://", "http://")
        )

    napake = _napake(spremeni)
    assert any("social_posts[0].image_url" in n and "https" in n for n in napake)


def test_social_slika_samo_z_gostiteljem_brez_poti_pade():
    """Gol gostitelj ni slika - brez te preverbe gate spusti `https://<host>` naprej."""
    for url in (
        "https://umvjwjzdrtamfrcqhopa.supabase.co",
        "https://umvjwjzdrtamfrcqhopa.supabase.co/",
    ):
        def spremeni(pkg, url=url):
            pkg["social_posts"][0]["image_url"] = url

        napake = _napake(spremeni)
        assert any(
            "social_posts[0].image_url" in n and "nima poti" in n for n in napake
        ), url


def test_social_predolg_alt_pade():
    def spremeni(pkg):
        pkg["social_posts"][0]["image_alt"] = "a" * 161

    napake = _napake(spremeni)
    assert any("social_posts[0].image_alt" in n and "160" in n for n in napake)


def test_vec_objav_gate_ne_zavrne():
    """Spec: stevila objav gate ne preverja - to pravilo uveljavi Igor na gateu koraka 2.

    Tri veljavne objave morajo iti skozi; zavrne se lahko samo zaradi vsebine objave,
    nikoli zaradi njihovega stevila.
    """
    def spremeni(pkg):
        pkg["social_posts"] = pkg["social_posts"] * 3

    napake = _napake(spremeni)
    assert napake == []


def test_veljaven_paket_z_dvema_objavama_gre_skozi():
    assert _validate("package_valid.json") == []
