from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEBLO = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory"
NOVICNIK = DEBLO / "veje" / "novicnik"
VEJA = NOVICNIK / "VEJA.md"


def _razdelek(naslov):
    vsebina = VEJA.read_text(encoding="utf-8")
    ostanek = vsebina[vsebina.index(f"## {naslov}") + len(naslov) + 3:]
    konec = ostanek.find("\n## ")
    return ostanek if konec == -1 else ostanek[:konec]


def test_sprozilci_po_pomenu():
    sprozilci = _razdelek("Sprožilci")
    for fraza in ("delava nov newsletter", "dejva naredit nov NL", "pripravi novičnik", "GameChanger"):
        assert fraza in sprozilci, fraza


def test_vse_poti_v_veji_obstajajo():
    vsebina = VEJA.read_text(encoding="utf-8")
    for pot in (
        "vendor/frodx-newsletter/SKILL.md",
        "references/critique-prompt.md",
        "references/state-schema.md",
        "references/privzete-vrednosti.md",
        "scripts/izdaja_besedilo.py",
        "scripts/iz_editions.py",
        "scripts/preveri_paket.py",
    ):
        assert pot in vsebina, pot
        assert (NOVICNIK / pot).is_file(), pot


def test_koraki_si_kritika_nato_prevod():
    koraki = _razdelek("Koraki")
    for n in range(1, 7):
        assert f"| {n} " in koraki, n
    assert koraki.index("koraka 2-3") < koraki.index("frodx-critique-loop") < koraki.index("koraka 4-5")


def test_docx_se_ne_izvede_nikoli():
    vsebina = VEJA.read_text(encoding="utf-8")
    assert "korak 6 (docx" in vsebina
    assert "nikoli" in vsebina
    assert "present_files" in vsebina


def test_varovalka_prevoda_pred_kritiko():
    vsebina = VEJA.read_text(encoding="utf-8")
    assert "zavrž" in vsebina
    assert "step3" in vsebina


def test_skupni_koraki_podajo_vhod_prompt_in_zapis():
    skupni = _razdelek("Skupni koraki")
    for niz in ("frodx-critique-loop", "frodx-transcreation-check", "frodx-image-run", "frodx-publish-send",
                "Faza C", "izpis", "vpis", "critique-prompt.md", "open_tasks"):
        assert niz in skupni, niz


def test_oddaja_in_brez_casa():
    oddaja = _razdelek("Oddaja")
    assert "Wd1gVtK77b29ePrJ" in oddaja
    assert "manual" in oddaja
    vsebina = VEJA.read_text(encoding="utf-8")
    assert "send_datetime" in vsebina
    assert "Europe/Ljubljana" in vsebina


def test_privzete_vrednosti_kazejo_na_igorja():
    vsebina = (NOVICNIK / "references" / "privzete-vrednosti.md").read_text(encoding="utf-8")
    assert "docx-pipeline.md" in vsebina
    assert "Europe/Ljubljana" in vsebina
    assert "Europe/Zagreb" in vsebina


def test_opis_debla_zajame_obe_veji():
    glava = (DEBLO / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    for fraza in ("nova kolumna", "newsletter", "novičnik", "NL", "GameChanger", "zaženi tovarno"):
        assert fraza in glava, fraza


def test_brez_dolgega_pomisljaja():
    for pot in NOVICNIK.rglob("*.md"):
        if "vendor" in pot.parts:
            continue
        assert "\u2014" not in pot.read_text(encoding="utf-8"), pot.name


def test_korak_1_vpraša_za_pain_link_brez_izmisljanja():
    koraki = _razdelek("Koraki")
    vrstica = next(v for v in koraki.splitlines() if v.startswith("| 1 "))
    assert "pain link" in vrstica
    assert "ne izmišljaš" in vrstica
    assert "_run.gradivo_odlocitve" in vrstica


def test_korak_6_vprasa_o_odprtih_zadolzitvah():
    koraki = _razdelek("Koraki")
    vrstica = next(v for v in koraki.splitlines() if v.startswith("| 6 "))
    assert "samo pošlje" not in vrstica
    assert "vprašaš, ali oddaja kljub temu" in vrstica


def test_package_id_po_jeziku():
    vsebina = (NOVICNIK / "references" / "privzete-vrednosti.md").read_text(encoding="utf-8")
    assert "## PACKAGE_ID po jeziku" in vsebina
    for pripona in ("-hr", "-en"):
        assert pripona in vsebina


def test_shema_pozna_odlocitve_gradiva():
    vsebina = (NOVICNIK / "references" / "state-schema.md").read_text(encoding="utf-8")
    vrstica = next(v for v in vsebina.splitlines() if v.startswith("| `gradivo_odlocitve`"))
    for polje in ("bloki", "pain_link"):
        assert polje in vrstica
