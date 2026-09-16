from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "plugins" / "content-factory" / "skills" / "frodx-topic-pick"


def test_pogodba_o_viru_je_hubspot_ne_excel():
    assert (SKILL / "references" / "aeo-source.md").is_file()
    assert not (SKILL / "references" / "excel-contract.md").exists()


def test_v_skillu_ni_vec_sledi_starega_vira():
    prepovedano = ["aeo-themes.xlsx", "OneDrive", "Microsoft 365", "excel-contract"]
    for pot in SKILL.rglob("*.md"):
        vsebina = pot.read_text(encoding="utf-8")
        for niz in prepovedano:
            assert niz not in vsebina, f"{pot.name} se sklicuje na {niz}"


def test_pogodba_nosi_projekt_in_tabelo():
    vsebina = (SKILL / "references" / "aeo-source.md").read_text(encoding="utf-8")
    assert "FucXmQlDiWLVsRHW" in vsebina
    assert "AEO-Picks" in vsebina
