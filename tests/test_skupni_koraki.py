from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLI = REPO / "plugins" / "content-factory" / "skills"
PROMPT_NL = SKILLI / "frodx-content-factory" / "veje" / "novicnik" / "references" / "critique-prompt.md"
KRITIKA = SKILLI / "frodx-critique-loop" / "SKILL.md"
PREVERBA = SKILLI / "frodx-transcreation-check" / "SKILL.md"
RUBRIKA = (
    SKILLI / "frodx-content-factory" / "veje" / "novicnik" / "vendor" / "frodx-newsletter"
    / "references" / "self-eval-rubric.md"
)


def test_prompt_novicnika_ima_protokol_kritike():
    vsebina = PROMPT_NL.read_text(encoding="utf-8")
    assert "OBJAVLJIVO" in vsebina and "ZA POPRAVEK" in vsebina
    assert "{{DANES}}" in vsebina
    assert "Začasno" in vsebina


def test_prompt_novicnika_uporabi_igorjeva_vrata():
    vsebina = PROMPT_NL.read_text(encoding="utf-8")
    for vrata in ("HOOK", "STRUKTURA", "FRODX EDINSTVENOST", "JEZIK IN GLAS", "PRAVOPIS", "SUBJECT + PREHEADER"):
        assert vrata in vsebina, vrata
        assert vrata in RUBRIKA.read_text(encoding="utf-8"), f"{vrata} ni v Igorjevi rubriki"
    assert "self-eval-rubric.md" in vsebina


def test_prompt_novicnika_ohrani_pravili_iz_teka():
    vsebina = PROMPT_NL.read_text(encoding="utf-8")
    assert "letnic" in vsebina, "ocenjevalec ne sodi o verodostojnosti letnic"
    assert "oznak" in vsebina, "ocenjevalec mora vedeti, da so oznake del oblike, ne vsebine"


def test_prompt_novicnika_brez_dolgega_pomisljaja():
    assert "—" not in PROMPT_NL.read_text(encoding="utf-8")


def test_kritika_pozna_vhod_po_veji_in_ohrani_kolumno():
    vsebina = KRITIKA.read_text(encoding="utf-8")
    assert "## Vhod po veji" in vsebina
    assert "Skupni koraki" in vsebina
    assert "izdaja_besedilo.py" in vsebina
    assert "languages.sl.content" in vsebina
    assert "GZmnPGOcVANH2sfy" in vsebina


def test_preverba_prevoda_pozna_vhod_po_veji_in_ohrani_kolumno():
    vsebina = PREVERBA.read_text(encoding="utf-8")
    assert "## Vhod po veji" in vsebina
    assert "Skupni koraki" in vsebina
    assert "izdaja_besedilo.py" in vsebina
    assert "Pokliči `frodx-transcreation` znova" in vsebina
    assert "eGHQGAbgeQhfCcZu" in vsebina
