import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.taxonomy import load_campaigns, load_tags

TAXONOMY = REPO / "plugins" / "content-factory" / "skills" / "frodx-publishing-meta" / "references" / "hubspot-taxonomy.md"

PRICAKOVANE_KAMPANJE = {
    "Interest - AI agenti in Voice AI": "83ff3b4a-b380-4ed1-ab81-afb9a5704685",
    "Interest - Prodaja in lead management": "aa75dc5d-6025-4d83-8870-0b86a9e1397d",
    "Interest - Programi zvestobe": "bdeff9f6-7f4a-4f7d-8d54-b8590f94b203",
    "Interest - Loyalty programs": "47259292-c3a6-4a9a-844d-cda7476a403a",
    "Interest - HubSpot inbound marketing": "fa865065-1306-4f2c-952c-ea67203dc015",
    "Interest - Emarsys omnichannel marketing": "6784cc33-24a0-4c0a-bf5f-bc3ca6feabfc",
    "Interest - E-commerce in retail": "7549f0ea-1636-49fb-9c64-25b2f7629402",
    "Interest - Digitalna transformacija": "65e30f52-6459-4015-a244-af6d0663a52b",
    "Interest - CX Customer Experience": "d7d001a5-6f22-4cdb-9927-fd6862dfed3e",
    "Interest - AI Support & Service Hub": "fa41e141-7deb-412e-b72d-0f11c4e1249f",
}


def test_natanko_deset_kampanj_z_guidi():
    assert load_campaigns(TAXONOMY) == PRICAKOVANE_KAMPANJE


def test_tag_za_znan_par():
    tags = load_tags(TAXONOMY)
    assert tags[("Interest - AI agenti in Voice AI", "sl")] == {
        "id": "191973014556",
        "name": "AI agenti in voice AI",
        "slug": "ai-agenti-in-voice-ai",
    }
    assert tags[("Interest - Prodaja in lead management", "en")]["id"] == "110457313457"


def test_znane_vrzeli_ostanejo_vrzeli():
    """Te pare tag danes v HubSpotu nima. Nikoli jih ne izmišljamo."""
    tags = load_tags(TAXONOMY)
    for par in [
        ("Interest - Digitalna transformacija", "en"),
        ("Interest - Digitalna transformacija", "hr"),
        ("Interest - E-commerce in retail", "en"),
        ("Interest - E-commerce in retail", "hr"),
        ("Interest - Programi zvestobe", "en"),
        ("Interest - Programi zvestobe", "hr"),
        ("Interest - Loyalty programs", "sl"),
        ("Interest - Emarsys omnichannel marketing", "hr"),
        ("Interest - AI Support & Service Hub", "sl"),
        ("Interest - AI Support & Service Hub", "en"),
        ("Interest - AI Support & Service Hub", "hr"),
    ]:
        assert par not in tags, f"{par} ne bi smel imeti taga"


def test_vsaka_kampanja_z_tagi_ima_slovenskega_ali_je_na_seznamu_izjem():
    tags = load_tags(TAXONOMY)
    brez_sl = {"Interest - Loyalty programs", "Interest - AI Support & Service Hub"}
    for kampanja in PRICAKOVANE_KAMPANJE:
        if kampanja in brez_sl:
            continue
        assert (kampanja, "sl") in tags, f"{kampanja} nima slovenskega taga"
