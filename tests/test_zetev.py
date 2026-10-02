from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ZETEV = (
    REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory"
    / "veje" / "novicnik" / "references" / "zetev.md"
)


def test_opis_zetve_pove_kje_je_tabela():
    vsebina = ZETEV.read_text(encoding="utf-8")
    assert "`CF-Zetev`" in vsebina
    assert "FucXmQlDiWLVsRHW" in vsebina
    for stolpec in ("jezik", "prej", "potem", "razlog", "veja", "run_slug", "datum"):
        assert f"`{stolpec}`" in vsebina, stolpec


def test_opis_zetve_doloci_pravila():
    vsebina = ZETEV.read_text(encoding="utf-8")
    assert "get_data_table_rows" in vsebina
    assert "add_data_table_rows" in vsebina
    assert "samo dopolnjuje" in vsebina
    assert "izrecno potrdil" in vsebina


def test_opis_zetve_brez_dolgega_pomisljaja():
    assert "—" not in ZETEV.read_text(encoding="utf-8")
