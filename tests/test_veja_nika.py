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
        "scripts/besedilo.py",
        "scripts/zavihek.py",
        "scripts/iz_zavihka.py",
    ):
        assert pot in vsebina, pot
        assert (NIKA / pot).is_file(), pot


def test_tek_nastane_po_izbiri_novosti():
    koraki = _razdelek("Koraki")
    assert "init_run.py --veja nika" in koraki
    assert "_run.kandidat" in _vrstica_koraka(1)


def test_korak_2_brez_clanka_ni_zgodbe():
    koraki = _razdelek("Koraki")
    for niz in ("knowledge.hubspot.com", "Brez članka ni zgodbe", "web_fetch", "[PREVERI]", "_run.vnos"):
        assert niz in koraki, niz


def test_korak_3_check_py_v_obeh_nacinih_s_prev():
    koraki = _razdelek("Koraki")
    for niz in ("--blog --prev", "primeri/", "origin: skill", "9,0", "vrstice `---`"):
        assert niz in koraki, niz


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


def test_korak_2_dejstva_iz_besedila_clanka():
    korak = _razdelek("Koraki").split("### Korak 2")[1].split("### Korak 3")[0]
    for niz in ("dobesedno", "povzetek", "vir ne pove"):
        assert niz in korak, niz


def test_koraki_do_nadaljevanja():
    for n, gate in ((1, True), (2, True), (3, True), (4, True), (5, False), (6, True)):
        assert ("**da**" in _vrstica_koraka(n)) is gate, n


def test_korak_1_igor_prilepi_novost():
    korak = _razdelek("Koraki").split("### Korak 1")[1].split("### Korak 2")[0]
    assert "prilepi" in korak
    assert "noreply@notifications.hubspot.com" not in VEJA.read_text(encoding="utf-8")


def test_kritika_pred_nikinim_pregledom():
    koraki = _razdelek("Koraki")
    assert koraki.index("frodx-critique-loop") < koraki.index("cf-deliver-nika")
    assert "besedilo.py vpis" in _razdelek("Skupni koraki")


def test_oddaja_niki():
    oddaja = _razdelek("Oddaja Niki")
    for niz in ("zavihek.py", "cf-deliver-nika", "notify_failed", "--faza niki", "Pregled", "execute_workflow"):
        assert niz in oddaja, niz
    assert "še ne obstaja" not in VEJA.read_text(encoding="utf-8")


def test_nadaljevanje():
    nad = _razdelek("Nadaljevanje")
    for niz in ("nadaljuj Niko", "Nika je pregledala", "CF-Teki", "iz_zavihka.py", "[PREVERI", "Zavrni", "caka_niko"):
        assert niz in nad, niz


def test_kratka_linkedin_objava():
    vsebina = VEJA.read_text(encoding="utf-8")
    assert "igor-column-writer/references/social-posts.md" in vsebina
    assert "--linkedin" not in _razdelek("Koraki")


def test_preverba_paketa_obe_fazi():
    preverba = _razdelek("Preverba paketa")
    assert "preveri_paket.py runs/<tek>/state.json --faza niki --telo outbox/<run_slug>.json" in preverba
    assert "preveri_paket.py runs/<tek>/state.json --faza objava" in preverba
    assert "`1.1`" in preverba


def test_izid_se_bere_samo_iz_vozlisca_izid():
    oddaja = _razdelek("Oddaja Niki")
    assert 'includeData: true' in oddaja
    assert 'nodeNames: ["Izid"]' in oddaja


def test_tab_id_ima_vir():
    oddaja = _razdelek("Oddaja Niki")
    nad = _razdelek("Nadaljevanje")
    assert "`_run.tab_id`" in oddaja and "`file` id" in oddaja
    assert "`tab_id` (`_run.tab_id`)" in oddaja
    assert "stolpca `tab_id`" in nad
    assert "get_data_table_rows" in nad


def test_stanje_v_pregledu_po_odlocitvi():
    nad = _razdelek("Nadaljevanje")
    korak5 = nad.split("\n5. ")[1].split("\n6. ")[0]
    korak7 = nad.split("\n7. ")[1]
    assert "»zavrnjeno«" in korak5
    assert "»potrjeno«" in korak7


def test_zavrni_izbrise_izvirnik_pred_ponovno_oddajo():
    korak5 = _razdelek("Nadaljevanje").split("\n5. ")[1].split("\n6. ")[0]
    assert "`_run.nika_izvirnik`" in korak5
    assert korak5.index("izbriši") < korak5.index("ponovi »Oddaja Niki«")


def test_opis_debla_ima_sprozilce_nadaljevanja_nike():
    opis = _opis_debla()
    for fraza in ("nadaljuj Niko", "Nika je pregledala", "Nika je potrdila"):
        assert fraza in opis, fraza
    assert "weekly mail" not in opis
    assert len(opis) <= 1024, len(opis)


def test_deblo_nadaljuje_niko_prek_cf_teki():
    vsebina = (DEBLO / "SKILL.md").read_text(encoding="utf-8")
    razdelek = vsebina.split("## Nadaljevanje prekinjenega teka")[1].split("\n## ")[0]
    assert "CF-Teki" in razdelek and "run_slug" in razdelek


def test_nadaljevanje_bere_xml_ne_izvoza():
    nad = _razdelek("Nadaljevanje")
    korak2 = nad.split("\n2. ")[1].split("\n3. ")[0]
    for niz in ("xml_v_zavihek.py", "zavihek.xml", "zavihek-2.xml", '"object":"node"', "f307990d-76ae-4e30-b9b2-9635fc39d412", "next"):
        assert niz in korak2, niz
    vsebina = VEJA.read_text(encoding="utf-8")
    for niz in ("export", "base64", "bytes_b64"):
        assert niz not in vsebina, niz
    assert (NIKA / "scripts" / "xml_v_zavihek.py").is_file()


def test_get_data_table_rows_je_izpisan():
    nad = _razdelek("Nadaljevanje")
    korak1 = nad.split("\n1. ")[1].split("\n2. ")[0]
    korak2 = nad.split("\n2. ")[1].split("\n3. ")[0]
    for niz in ('dataTableId: "qXM8KuxMDyNQ9C0y"', 'projectId: "FucXmQlDiWLVsRHW"',
                '{"filters":[{"columnName":"veja","value":"nika"},{"columnName":"stanje","value":"caka_niko"}]}'):
        assert niz in korak1, niz
    assert '{"columnName":"run_slug","value":"<run_slug>"}' in korak2


def test_oddaja_klic_execute_workflow_v_celoti():
    oddaja = _razdelek("Oddaja Niki")
    korak4 = oddaja.split("\n4. ")[1].split("\n5. ")[0]
    for niz in ('"workflowId": "o8L8DsTaqQT3wi9B"', '"executionMode": "manual"', '"triggerNodeName": "Trigger"',
                '"method": "POST"', '"run_slug"', '"doc_url"', '"tab_id"', '"title"', '"activity"', '"paket_json"'):
        assert niz in korak4, niz
    assert "ne javi kot uspešne" in korak4


def test_pregled_ime_zavihka_brez_povezave():
    oddaja = _razdelek("Oddaja Niki")
    assert "71a36976-ec9a" in oddaja
    assert "navadno besedilo" in oddaja
    assert "povezava na zavihek" not in oddaja
    assert "zavihek.py runs/<tek>/state.json --celice" in oddaja


def test_koraki_po_6_se_niso_zapisani():
    assert "Koraki 7-12 (naslovnica, objava) še niso zapisani" in _razdelek("Nadaljevanje")


def test_potrdi_osvezi_blog_pred_check():
    korak6 = _razdelek("Nadaljevanje").split("\n6. ")[1].split("\n7. ")[0]
    assert korak6.index("besedilo.py izpis") < korak6.index("check.py")


def test_brez_zastarelih_besedil():
    vsebina = VEJA.read_text(encoding="utf-8")
    for niz in ("katero novost vzamemo ta teden", "drugo novost iz tabele"):
        assert niz not in vsebina, niz


def test_deblo_izjeme_za_niko():
    vsebina = (DEBLO / "SKILL.md").read_text(encoding="utf-8")
    assert "razen veje Nika: nadaljuje se v novem chatu prek `CF-Teki` in zavihka v Docu" in vsebina
    assert "(veja lahko predpiše drugo vozlišče, npr. Nika `Izid`)" in vsebina
    assert "version: 0.6.0" in vsebina.split("---")[1]


def test_kritika_nika_korak_4():
    vsebina = (DEBLO.parent / "frodx-critique-loop" / "SKILL.md").read_text(encoding="utf-8")
    nika = vsebina.split("Za **Niko**")[1].split("\n## ")[0]
    assert "po vsakem krogu, namesto `languages.sl.content`" in nika
    assert "`_run.step = 4`" in nika
