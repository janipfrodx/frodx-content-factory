from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEBLO = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory"
NIKA = DEBLO / "veje" / "nika"
VEJA = NIKA / "VEJA.md"


def _razdelek(naslov):
    vsebina = VEJA.read_text(encoding="utf-8")
    ostanek = vsebina[vsebina.index(f"## {naslov}") + len(naslov) + 3:]
    konec = ostanek.find("\n## ")
    return ostanek if konec == -1 else ostanek[:konec]


def _vrstica_koraka(n):
    return next(v for v in _razdelek("Koraki").splitlines() if v.startswith(f"| {n} "))


def _opis_debla():
    glava = (DEBLO / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    vrstica = next(v for v in glava.splitlines() if v.startswith("description: "))
    return vrstica[len("description: "):]


def test_sprozilci_po_pomenu():
    sprozilci = _razdelek("Sprožilci")
    for fraza in ("nova Nikina zgodba", "HubSpot novost za Niko", "tedenski update za Niko"):
        assert fraza in sprozilci, fraza


def test_vse_poti_v_veji_obstajajo():
    vsebina = VEJA.read_text(encoding="utf-8")
    for pot in (
        "vendor/nika-update-writer/SKILL.md",
        "vendor/nika-update-writer/references/vir.md",
        "vendor/nika-update-writer/references/vertikale.md",
        "vendor/nika-update-writer/references/nacela.md",
        "vendor/nika-update-writer/references/rubrika.md",
        "vendor/nika-update-writer/scripts/check.py",
        "scripts/preveri_paket.py",
    ):
        assert pot in vsebina, pot
        assert (NIKA / pot).is_file(), pot


def test_stirje_koraki_vsi_z_gateom():
    for n in range(1, 5):
        assert "**da**" in _vrstica_koraka(n), n


def test_tek_nastane_po_izbiri_novosti():
    koraki = _razdelek("Koraki")
    assert "init_run.py --veja nika" in koraki
    assert "_run.kandidat" in _vrstica_koraka(1)


def test_korak_1_bere_samo_hubspotov_mail():
    koraki = _razdelek("Koraki")
    for niz in ("noreply@notifications.hubspot.com", "Weekly Product Updates Roundup", "14 dni",
                "Nobenega drugega iskanja", "ISO 27001", "app.hubspot.com", "prilepi"):
        assert niz in koraki, niz


def test_korak_2_brez_clanka_ni_zgodbe():
    koraki = _razdelek("Koraki")
    for niz in ("knowledge.hubspot.com", "Brez članka ni zgodbe", "web_fetch", "[PREVERI]", "_run.vnos"):
        assert niz in koraki, niz


def test_korak_3_check_py_v_obeh_nacinih_s_prev():
    koraki = _razdelek("Koraki")
    for niz in ("--blog --prev", "--linkedin --prev", "primeri/", "origin: skill", "9,0", "vrstice `---`"):
        assert niz in koraki, niz


def test_skupni_koraki_ne_tecejo():
    skupni = _razdelek("Skupni koraki")
    for niz in ("frodx-critique-loop", "frodx-transcreation-check", "frodx-image-run", "frodx-publish-send"):
        assert niz in skupni, niz


def test_preverba_in_oddaja_brez_izmisljenega_workflowa():
    assert "preveri_paket.py runs/<tek>/state.json --telo outbox/<run_slug>.json" in _razdelek("Preverba paketa")
    oddaja = _razdelek("Oddaja")
    assert "cf-deliver-nika" in oddaja
    assert "še ne obstaja" in oddaja
    assert "outbox/<run_slug>.json" in oddaja


def test_nika_ne_dobi_obrazca():
    posebnosti = _razdelek("Posebnosti")
    assert "obrazec.md" in posebnosti
    assert "nacela.md" in posebnosti


def test_brez_dolgega_pomisljaja():
    for pot in NIKA.rglob("*.md"):
        if "vendor" in pot.parts:
            continue
        assert "\u2014" not in pot.read_text(encoding="utf-8"), pot.name


def test_opis_debla_zajame_niko_in_je_pod_mejo():
    opis = _opis_debla()
    for fraza in ("Nika", "nova Nikina zgodba", "HubSpot novost za Niko", "tedenski update za Niko"):
        assert fraza in opis, fraza
    assert len(opis) <= 1024, len(opis)


def test_deblo_vprasa_tudi_za_niko():
    vsebina = (DEBLO / "SKILL.md").read_text(encoding="utf-8")
    assert "kolumna, novičnik ali Nikina zgodba" in vsebina
    assert "Gremo na Nikino zgodbo." in vsebina
