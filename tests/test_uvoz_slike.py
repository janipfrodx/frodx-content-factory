import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOSTAVNA_POT = REPO / "docs" / "dostavna-pot.md"


def _razdelek(ime):
    vsebina = DOSTAVNA_POT.read_text(encoding="utf-8")
    zacetek = vsebina.index(f"## `{ime}`")
    ostanek = vsebina[zacetek + 4:]
    konec = ostanek.find("\n## ")
    return ostanek if konec == -1 else ostanek[:konec]


def id_uvoza():
    zadetek = re.search(r"- workflowId: `([^`]+)`", _razdelek("cf-import-image"))
    return zadetek.group(1) if zadetek else ""


def test_dostavna_pot_opisuje_uvoz_slike():
    razdelek = _razdelek("cf-import-image")
    assert re.fullmatch(r"[A-Za-z0-9]{16}", id_uvoza()), "workflowId manjka ali ni pravi ID"
    assert "`vS1Vj3wTuQUKF5WI`" in razdelek
    assert "content-images" in razdelek
    assert "/api/images" in razdelek
    assert '"url"' in razdelek and '"error"' in razdelek
