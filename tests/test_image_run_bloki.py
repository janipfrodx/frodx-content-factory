from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-image-run" / "SKILL.md"
NASLOV = "## Faza C - slike blokov novičnika"


def _faza_c():
    vsebina = SKILL.read_text(encoding="utf-8")
    zacetek = vsebina.index(NASLOV)
    ostanek = vsebina[zacetek + len(NASLOV):]
    konec = ostanek.find("\n## ")
    return ostanek if konec == -1 else ostanek[:konec]


def test_faza_c_stoji_za_fazo_b():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert vsebina.index("## Faza B") < vsebina.index(NASLOV) < vsebina.index("## Kako slike dejansko pridejo do tebe")


def test_faza_c_predlaga_vir_v_privzetem_vrstnem_redu():
    faza = _faza_c()
    prilozena = faza.index("Igorjeva priložena slika")
    ponovna = faza.index("Ponovna raba po URL-ju")
    generiranje = faza.index("Generiranje")
    nic = faza.index("Nič od tega")
    assert prilozena < ponovna < generiranje < nic


def test_faza_c_generira_kvadrat_z_dvema_kandidatkama():
    faza = _faza_c()
    assert "lHc3NdejxehMyc9O" in faza
    assert "1024x1024" in faza
    assert "dve kandidatki" in faza
    assert "frodx-key-visual" in faza


def test_faza_c_nikoli_ne_generira_resnicne_stranke():
    faza = _faza_c()
    assert "announcement" in faza
    assert "nikoli ne generira" in faza


def test_faza_c_igor_odloci_pri_vsakem_bloku():
    faza = _faza_c()
    for izbira in ("zamenjaj", "generiraj", "tu je moja", "pusti prazno"):
        assert izbira in faza, izbira


def test_faza_c_pise_v_vse_tri_izdaje_in_run():
    faza = _faza_c()
    assert "_run.block_images" in faza
    assert "image.url" in faza and "image.alt" in faza
    assert "vseh treh" in faza
    assert "https://" in faza


def test_faza_c_ne_obljublja_nalaganja_prilozene_slike():
    faza = _faza_c()
    assert "v aplikaciji" in faza
    assert "ne naloži" in faza


def test_opis_skilla_omeni_novicnik():
    glava = SKILL.read_text(encoding="utf-8").split("---")[1]
    assert "Phase C" in glava
    assert "newsletter" in glava
