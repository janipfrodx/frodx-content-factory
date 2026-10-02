import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-image-run" / "SKILL.md"
NASLOV = "## Faza C - slike blokov novičnika"

sys.path.insert(0, str(REPO / "tests"))
from test_uvoz_slike import id_uvoza


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


def test_ponovna_raba_gre_skozi_uvoz():
    faza = _faza_c()
    assert f'"workflowId": "{id_uvoza()}"' in faza
    assert '"triggerNodeName": "Trigger"' in faza
    assert "nikoli izvirni s frodx.com" in faza
    assert "brez prenosa" not in faza


def test_alt_po_sliki_ki_si_jo_pogledal():
    faza = _faza_c()
    assert "curl" in faza and "dimenzije.py" in faza
    assert "napisan po sliki, ki si jo prenesel in pogledal" in faza


def test_verzija_image_run():
    assert "version: 0.4.0" in SKILL.read_text(encoding="utf-8")


def test_faza_c_je_razdeljena_na_korak_1_in_5():
    faza = _faza_c()
    assert faza.index("### Korak 1 veje") < faza.index("### Korak 5 veje")


def test_faza_c_odloca_na_gateu_koraka_1_po_jeziku():
    faza = _faza_c()
    korak_1 = faza[faza.index("### Korak 1 veje"):faza.index("### Korak 5 veje")]
    assert "gate-u koraka 1" in korak_1
    assert "jezik" in korak_1
    assert "sumljiva" in korak_1


def test_faza_c_korak_5_brez_gatea_claude_izbere_kandidatko():
    faza = _faza_c()
    korak_5 = faza[faza.index("### Korak 5 veje"):]
    assert "brez gate-a" in korak_5
    assert "izbereš sam" in korak_5
    assert "awaiting_approval" not in korak_5


def test_faza_c_korak_5_generira_enkrat_na_blok_in_prenese_napako():
    faza = _faza_c()
    korak_5 = faza[faza.index("### Korak 5 veje"):]
    assert "enkrat na blok" in korak_5
    assert "vseh zapisov tega bloka" in korak_5
    assert "doda v Hubu" in korak_5
