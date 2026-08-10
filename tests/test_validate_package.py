import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.taxonomy import load_campaigns, load_tags

SKRIPTA = REPO / "plugins" / "content-factory" / "skills" / "frodx-publish-send" / "scripts" / "validate_package.py"
TAXONOMY = REPO / "plugins" / "content-factory" / "skills" / "frodx-publishing-meta" / "references" / "hubspot-taxonomy.md"
FIXTURES = REPO / "tests" / "fixtures"

sys.path.insert(0, str(SKRIPTA.parent))


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


def test_izmisljena_kampanja_pade():
    napake = _validate("package_bad_campaign.json")
    assert any("campaign_name" in n and "Zvestoba in nagrade" in n for n in napake)


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
