import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-publish-send" / "SKILL.md"
DOSTAVNA_POT = REPO / "docs" / "dostavna-pot.md"
NASLOV = "## Veja novičnik"


def _razdelek():
    vsebina = SKILL.read_text(encoding="utf-8")
    ostanek = vsebina[vsebina.index(NASLOV) + len(NASLOV):]
    konec = ostanek.find("\n## ")
    return ostanek if konec == -1 else ostanek[:konec]


def _id_iz_dostavne_poti(ime):
    v_razdelku = False
    for vrstica in DOSTAVNA_POT.read_text(encoding="utf-8").splitlines():
        if vrstica.startswith("## "):
            v_razdelku = ime in vrstica
            continue
        if v_razdelku:
            zadetek = re.match(r"- workflowId: `([^`]+)`", vrstica.strip())
            if zadetek:
                return zadetek.group(1)
    return ""


def test_razdelek_stoji_za_postopkom_kolumne():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert vsebina.index("## Postopek") < vsebina.index(NASLOV)
    prvi = re.search(r'"workflowId":\s*"([^"]+)"', vsebina).group(1)
    assert prvi == _id_iz_dostavne_poti("cf-deliver-draft")


def test_novicnik_klice_cf_deliver_newsletter_iz_dostavne_poti():
    razdelek = _razdelek()
    kanonicni = _id_iz_dostavne_poti("cf-deliver-newsletter")
    assert kanonicni
    zadetek = re.search(r'"workflowId":\s*"([^"]+)"', razdelek)
    assert zadetek and zadetek.group(1) == kanonicni
    assert '"executionMode": "manual"' in razdelek


def test_novicnik_najprej_preveri_paket():
    razdelek = _razdelek()
    assert "preveri_paket.py" in razdelek
    assert "--telo" in razdelek
    assert razdelek.index("preveri_paket.py") < razdelek.index('"workflowId"')


def test_novicnik_pozna_izide_in_ne_ponavlja_sam():
    razdelek = _razdelek()
    for izid in ("created", "duplicate", "rejected", "misconfigured", "retry"):
        assert izid in razdelek, izid
    assert "edit_url" in razdelek
    assert "detail" in razdelek
    assert "ne poskušaj znova" in razdelek


def test_novicnik_ne_nastavi_casa_in_ne_razporedi():
    razdelek = _razdelek()
    assert "send_datetime" in razdelek
    assert "Razporedi" in razdelek


def test_opis_skilla_omeni_newsletter():
    glava = SKILL.read_text(encoding="utf-8").split("---")[1]
    assert "cf-deliver-newsletter" in glava
    assert "cf-deliver-draft" in glava
