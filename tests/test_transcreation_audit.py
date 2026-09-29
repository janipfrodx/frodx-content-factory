from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SK = REPO / "plugins" / "content-factory" / "skills"
SKILL = SK / "frodx-transcreation-check" / "SKILL.md"
PROMPT = SK / "frodx-transcreation-check" / "references" / "transcreation-check-prompt.md"


def _skill():
    return SKILL.read_text(encoding="utf-8")


def test_krog_zapise_sprejete_najdbe_z_navedkom():
    vsebina = _skill()
    assert '"accepted"' in vsebina
    for polje in ('"navedek"', '"popravek"', '"razlog"'):
        assert polje in vsebina, polje


def test_audit_je_zadnji_korak_in_bere_vendorirani_skill():
    vsebina = _skill()
    assert "vendor/frodx-transcreation-audit/SKILL.md" in vsebina
    assert "references/croatian.md" in vsebina and "references/english.md" in vsebina
    assert "house" in vsebina


def test_audit_dobi_sprejete_najdbe_in_pravilo_fail():
    vsebina = _skill()
    assert "[FAIL]" in vsebina
    assert "ne vračaj" in vsebina.lower()


def test_izrocilo_se_med_zanko_ne_sprozi():
    """Ponovni klic frodx-transcreation v točki e ni konec transkreacije - audit bi sicer tekel vsak krog."""
    vsebina = _skill()
    assert "Obvezno izročilo" in vsebina
    assert "enkrat na jezik" in vsebina


def test_varovalo_pozene_skripto_in_vrne_mesto():
    vsebina = _skill()
    assert "scripts/preveri_iznicenje.py" in vsebina
    assert "povrnjeno" in vsebina
    assert "transcreation-audit/<jezik>-pred.txt" in vsebina
    assert "transcreation-audit/<jezik>-po.txt" in vsebina


def test_zapis_audita_v_stanje():
    vsebina = _skill()
    assert "_run.transcreation_audit" in vsebina
    for polje in ('"score"', '"verdict"', '"variant"', '"traces"', '"povrnjeno"', '"report"'):
        assert polje in vsebina, polje


def test_fail_ne_ustavi_teka_in_gre_na_gate():
    vsebina = _skill()
    assert "FAIL" in vsebina
    assert "oddanega" in vsebina


def test_audit_tece_tudi_ce_je_preverba_padla():
    vsebina = _skill()
    assert "tudi kadar je preverba" in vsebina


def test_novicnik_audit_ohrani_oznake_in_vpis_skozi_skripto():
    vsebina = _skill()
    razdelek = vsebina.split("## Vhod po veji", 1)[1]
    assert "audit" in razdelek.lower()
    assert "izdaja_besedilo.py vpis" in razdelek


def test_hrvaski_narekovaji_so_hisni_slog():
    prompt = PROMPT.read_text(encoding="utf-8")
    assert "„ … ”" in prompt
    assert "privzeto “ … ”" not in prompt
    assert "“ … ” v\n   hrvaščini" not in _skill()
    assert "“ … ” v hrvaščini" not in _skill()


def test_brez_dolgega_pomisljaja():
    assert "—" not in _skill()
    assert "—" not in PROMPT.read_text(encoding="utf-8")
