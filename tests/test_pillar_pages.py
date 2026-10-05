import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "plugins" / "content-factory" / "skills" / "frodx-publish-send" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from taxonomy import JEZIKI, load_campaigns, load_pillars

REFS = (
    REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory"
    / "veje" / "kolumna" / "publishing-meta" / "references"
)
TAXONOMY = REFS / "hubspot-taxonomy.md"
PILLARS = REFS / "pillar-pages.md"


def _tabelne_vrstice():
    return [
        v for v in PILLARS.read_text(encoding="utf-8").splitlines()
        if v.startswith("| Interest - ")
    ]


def test_natanko_trideset_vrstic():
    assert len(_tabelne_vrstice()) == 30


def test_vsak_par_natanko_enkrat():
    pari = [tuple(c.strip() for c in v.strip().strip("|").split("|"))[:2] for v in _tabelne_vrstice()]
    assert len(pari) == len(set(pari))
    assert set(load_pillars(PILLARS)) == {(k, j) for k in load_campaigns(TAXONOMY) for j in JEZIKI}


def test_url_je_prazen_ali_absoluten_frodx():
    for par, url in load_pillars(PILLARS).items():
        if url:
            assert url.startswith("https://frodx.com/"), par
            assert "?" not in url and "#" not in url, par
            assert not url.endswith("/"), par


def test_bralnik_bere_prazen_in_poln_url(tmp_path):
    pot = tmp_path / "p.md"
    pot.write_text(
        "| campaign_name | lang | pillar_url |\n|---|---|---|\n"
        "| Interest - CX Customer Experience | sl | https://frodx.com/customer-experience-cx-vodic |\n"
        "| Interest - CX Customer Experience | en |  |\n",
        encoding="utf-8",
    )
    assert load_pillars(pot) == {
        ("Interest - CX Customer Experience", "sl"): "https://frodx.com/customer-experience-cx-vodic",
        ("Interest - CX Customer Experience", "en"): "",
    }


def test_taksonomija_nima_tristolpcnih_vrstic():
    assert load_pillars(TAXONOMY) == {}
import json

META_SKILL = REFS.parent / "SKILL.md"


def test_publishing_meta_bere_pillar_tabelo():
    vsebina = META_SKILL.read_text(encoding="utf-8")
    assert "references/pillar-pages.md" in vsebina
    assert "zadnjo vrstico" in vsebina.lower()
    assert "structure.md" in vsebina


def test_publishing_meta_verzija_dvignjena():
    glava = META_SKILL.read_text(encoding="utf-8").split("---")[1]
    assert "version: 0.2.0" in glava


def test_publishing_meta_brez_dolgega_pomisljaja():
    assert "\u2014" not in META_SKILL.read_text(encoding="utf-8")
    assert "\u2014" not in PILLARS.read_text(encoding="utf-8")


def test_plugin_verzija_0_7_2():
    plugin = json.loads((REPO / "plugins" / "content-factory" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert plugin["version"] == "0.7.2"


POTRJENO = {
    "Interest - AI agenti in Voice AI": (
        "https://frodx.com/ai-agenti-voice-ai",
        "https://frodx.com/en/ai-agenti-voice-ai",
        "https://frodx.com/hr/ai-agenti-voice-ai",
    ),
    "Interest - Prodaja in lead management": (
        "https://frodx.com/lead-management-prodajni-proces",
        "https://frodx.com/en/lead-management-sales-process",
        "https://frodx.com/hr/lead-management-prodajni-proces",
    ),
    "Interest - Programi zvestobe": (
        "https://frodx.com/program-zvestobe-openloyalty",
        "https://frodx.com/en/loyalty-program-openloyalty",
        "https://frodx.com/hr/program-lojalnosti-openloyalty",
    ),
    "Interest - Loyalty programs": (
        "https://frodx.com/program-zvestobe-openloyalty",
        "https://frodx.com/en/loyalty-program-openloyalty",
        "https://frodx.com/hr/program-lojalnosti-openloyalty",
    ),
    "Interest - HubSpot inbound marketing": (
        "https://frodx.com/hubspot-inbound-marketing-vodic",
        "https://frodx.com/en/hubspot-marketing-sales-guide",
        "https://frodx.com/hr/hubspot-inbound-marketing-vodic",
    ),
    "Interest - Emarsys omnichannel marketing": (
        "https://frodx.com/omnichannel-marketing-emarsys",
        "https://frodx.com/en/omnichannel-marketing-emarsys",
        "https://frodx.com/hr/omnichannel-marketing-emarsys",
    ),
    "Interest - E-commerce in retail": (
        "https://frodx.com/ecommerce-strategija-shopify",
        "https://frodx.com/en/ecommerce-strategy-shopify",
        "https://frodx.com/hr/ecommerce-strategija-shopify",
    ),
    "Interest - Digitalna transformacija": (
        "https://frodx.com/digitalna-transformacija-strategija",
        "https://frodx.com/en/digital-transformation-strategy",
        "https://frodx.com/hr/digitalna-transformacija-strategija",
    ),
    "Interest - CX Customer Experience": (
        "https://frodx.com/customer-experience-cx-vodic",
        "https://frodx.com/en/customer-experience-cx-guide",
        "https://frodx.com/hr/customer-experience-cx-vodic",
    ),
    "Interest - AI Support & Service Hub": ("", "", ""),
}


def test_potrjene_vrednosti_5_10_2026():
    """Jani je tabelo potrdil 5. 10. 2026. Tiha sprememba tabele mora pasti."""
    pricakovano = {
        (kampanja, jezik): url
        for kampanja, urlji in POTRJENO.items()
        for jezik, url in zip(("sl", "en", "hr"), urlji)
    }
    assert load_pillars(PILLARS) == pricakovano
