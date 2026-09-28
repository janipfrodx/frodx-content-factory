from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKILLI = REPO / "plugins" / "content-factory" / "skills"
KOLUMNA = SKILLI / "frodx-critique-loop" / "references" / "critique-prompt.md"
NOVICNIK = SKILLI / "frodx-content-factory" / "veje" / "novicnik" / "references" / "critique-prompt.md"
PREVERBA = SKILLI / "frodx-transcreation-check" / "references" / "transcreation-check-prompt.md"
VRATA = {
    KOLUMNA: ("Hook", "Teza", "Dokazi", "Ritem", "Glas", "Zaključek"),
    NOVICNIK: ("HOOK", "STRUKTURA", "FRODX EDINSTVENOST", "JEZIK IN GLAS", "PRAVOPIS", "SUBJECT + PREHEADER"),
}
VSI = [KOLUMNA, NOVICNIK, PREVERBA]
IME = {KOLUMNA: "kolumna", NOVICNIK: "novicnik", PREVERBA: "preverba"}


def _deli(pot):
    glava, locilo, prompt = pot.read_text(encoding="utf-8").partition("\n---\n")
    assert locilo, f"{pot.name}: manjka vrstica --- med glavo in promptom"
    return glava, prompt


@pytest.mark.parametrize("pot", VSI, ids=IME.get)
def test_uredniska_glava_je_nad_crto(pot):
    glava, prompt = _deli(pot)
    assert glava.strip()
    assert "{{DANES}}" in prompt
    assert "Začasno" not in prompt
    assert "system sporočilo" not in prompt


@pytest.mark.parametrize("pot", [KOLUMNA, NOVICNIK], ids=IME.get)
def test_sodba_ima_vrstico_za_vsako_merilo(pot):
    _, prompt = _deli(pot)
    odgovor = prompt[prompt.index("## Kako odgovoriš"):]
    assert "tudi kadar je sodba `OBJAVLJIVO`" in odgovor
    assert "ni ocena in se ne šteje" in odgovor
    assert "in končaj" not in prompt
    for vrata in VRATA[pot]:
        assert vrata in prompt, vrata


@pytest.mark.parametrize(
    "pot,naslov",
    [
        (KOLUMNA, "Zavrnjene pripombe iz prejšnjih krogov"),
        (NOVICNIK, "Zavrnjene pripombe iz prejšnjih krogov"),
        (PREVERBA, "Zavrnjene najdbe iz kroga 1"),
    ],
    ids=["kolumna", "novicnik", "preverba"],
)
def test_prompt_ne_ponavlja_zavrnjenih(pot, naslov):
    _, prompt = _deli(pot)
    assert naslov in prompt
    assert "nov argument" in prompt


@pytest.mark.parametrize("pot", VSI, ids=IME.get)
def test_brez_dolgega_pomisljaja(pot):
    assert "\u2014" not in pot.read_text(encoding="utf-8")
