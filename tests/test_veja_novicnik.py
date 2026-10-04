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


def _vrstica_sheme(kljuc):
    vsebina = (NOVICNIK / "references" / "state-schema.md").read_text(encoding="utf-8")
    return next(v for v in vsebina.splitlines() if v.startswith(f"| `{kljuc}`"))


def test_shema_odlocitev_pozna_hook_zgodbo_in_jezike():
    vrstica = _vrstica_sheme("gradivo_odlocitve")
    for polje in ("hook", "zgodba_kolumne", "jeziki", "transkreacija", "lokalni_vir", "block_id", "url"):
        assert polje in vrstica, polje


def test_shema_slik_je_po_jeziku():
    assert "jezik" in _vrstica_sheme("block_images")


def test_shema_pozna_zetev():
    vrstica = _vrstica_sheme("zetev")
    for polje in ("prej", "potem", "CF-Zetev"):
        assert polje in vrstica, polje


def _vrstica_koraka(n):
    return next(v for v in _razdelek("Koraki").splitlines() if v.startswith(f"| {n} "))


def test_gate_samo_pri_korakih_1_3_4_6():
    for n in (1, 3, 4, 6):
        assert "**da**" in _vrstica_koraka(n), n
    for n in (2, 5):
        assert "**ne**" in _vrstica_koraka(n), n


def test_korak_1_pripravi_vse_pred_gateom():
    koraki = _razdelek("Koraki")
    podrazdelek = koraki[koraki.index("### Korak 1"):koraki.index("### Korak 4")]
    for niz in ("preklopnik jezikov", "web_fetch", "HubSpot konektor", "LIST_BLOG_POSTS", "po slugu",
                "pravem jeziku", "URL-ja ne ugibaš",
                "transkreacija", "lokalni_vir", "Korak 1 veje", "rotacij", "reakcij",
                "block_id", "_run.gradivo_odlocitve"):
        assert niz in podrazdelek, niz


def test_korak_4_prevaja_iz_si_z_referenco_in_zetvijo():
    koraki = _razdelek("Koraki")
    podrazdelek = koraki[koraki.index("### Korak 4"):]
    for niz in ("prevod_vhod.py", "zetev.json", "get_data_table_rows", "add_data_table_rows",
                "referenc", "Zgodba, dolžina in struktura", "preveri_iznicenje.py", "/dev/null",
                "izrecno potrdi", "step4", "_run.zetev"):
        assert niz in podrazdelek, niz


def test_korak_4_ne_klice_gpt_gemini_preverbe():
    vrstica = _vrstica_koraka(4)
    assert "brez GPT/Gemini preverbe" in vrstica


def test_brez_popravkov_tek_gre_naprej():
    koraki = _razdelek("Koraki")
    assert "Če Igor nima popravkov" in koraki


def test_podniz_zetve_presodi_claude():
    koraki = _razdelek("Koraki")
    assert "del druge besede" in koraki


def test_korak_1_zapise_gradivo_in_tip_izdaje():
    vrstica = _vrstica_koraka(1)
    assert "`_run.gradivo`" in vrstica
    assert "_run.tip_izdaje" in vrstica


def test_skupni_koraki_kritika_dva_kroga_preverba_samo_audit():
    skupni = _razdelek("Skupni koraki")
    assert "največ dva kroga" in skupni
    assert "samo točka 6" in skupni
    assert "round-zetev" in skupni


def test_oddaja_da_igorju_navodilo_za_hub():
    oddaja = _razdelek("Oddaja")
    assert "Razporedi" in oddaja
    assert "z gumbom" in oddaja


def test_posebnosti_prepovejo_obvode():
    posebnosti = _razdelek("Posebnosti")
    for niz in ("mailov v HubSpotu", "dva izvora", "HubSpot strani", "brskalnik", "base64",
                "Po oddaji", "workflowov"):
        assert niz in posebnosti, niz


def _korak_4():
    koraki = _razdelek("Koraki")
    return koraki[koraki.index("### Korak 4"):]


def test_korak_4_zanka_loci_tocke_po_jeziku_in_enkrat():
    korak = _korak_4()
    for niz in ("točka b enkrat na tek", "Za `hr` nato tečejo c2, d-hr in e-hr", "točka g samo za `en`",
                "točka h enkrat za oba"):
        assert niz in korak, niz
    assert "Za vsak jezik (`hr`, nato `en`):" not in korak


def test_korak_4_zetev_po_straneh_in_napaka():
    korak = _korak_4()
    assert '`{"rows": [], "count": 0}`' in korak
    assert "NAPAKA:" in korak
    assert "references/zetev.md" in korak


def test_korak_4_cta_bloka_iz_jezikovne_razlicice():
    assert "jeziki.<jezik>.<block_id>.url" in _korak_4()


def test_shema_transcreation_check_ostane_prazen_pri_novicniku():
    assert "pri novičniku ostane prazen" in _vrstica_sheme("transcreation_check")


def test_korak_4_hr_na_solu():
    korak = _korak_4()
    for niz in ("hr_sol.py vhod", "cf-transkreacija-hr", "hr-meta.json", "hr_sol.py izdaja",
                "_run.prevod_hr", "Claude HR besedila ne piše", "UREDNIK", "NAPAKA", "nereseno",
                "review_reasons", "includeData"):
        assert niz in korak, niz


def test_korak_4_audit_samo_za_en():
    korak = _korak_4()
    assert "Audit (samo `en`)" in korak
    assert "za `hr` audit ne teče" in korak


def test_vrstica_koraka_4_omeni_sola():
    vrstica = _vrstica_koraka(4)
    assert "GPT-6.1 Sol" in vrstica
    assert "brez GPT/Gemini preverbe" in vrstica


def test_skupni_koraki_preverba_samo_za_en():
    skupni = _razdelek("Skupni koraki")
    assert "samo za `en`" in skupni


def test_shema_prevod_hr():
    vrstica = _vrstica_sheme("prevod_hr")
    for niz in ("izid", "krogi", "score", "nereseno", "execution_id"):
        assert niz in vrstica, niz


def test_korak_4_f_zamenjava_samo_za_en_hr_na_gate():
    korak = _korak_4()
    f = korak[korak.index("f. **Preverba žetve.**"):korak.index("g. **Audit")]
    assert "samo za `en`" in f
    assert "Za `hr` ne zamenjaš ničesar" in f
    assert "gate-u (točka h)" in f
    h = korak[korak.index("h. **Gate.**"):]
    assert "IZNIČENO" in h
    assert "Točka f teče za vsak jezik (preverba), zamenjava samo za `en`" in korak


def test_pisec_in_preslikava_hr_ne_prek_iz_editions():
    razdelek = _razdelek("Pisec in preslikava")
    assert "Po koraku 4 enako za `hr` in `en`" not in razdelek
    assert "HR vpiše `hr_sol.py izdaja`" in razdelek


def test_skupni_koraki_gate_audit_samo_en():
    skupni = _razdelek("Skupni koraki")
    assert "oceno in sodbo audita za oba jezika" not in skupni
    assert "_run.prevod_hr" in skupni


def test_e_hr_po_ponovitvi_znova_z_novim_izidom():
    korak = _korak_4()
    assert "e-hr znova z novim `prevod/hr-sol-izid.json` in novim `executionId`" in korak


def test_d_hr_ima_pravi_id_workflowa_iz_dokumentacije():
    import re

    veja = VEJA.read_text(encoding="utf-8")
    assert "ID_CF_TRANSKREACIJA_HR" not in veja
    v_veji = re.search(r"n8n `cf-transkreacija-hr`\*\* \(`([A-Za-z0-9]{16})`\)", veja)
    dok = (REPO / "docs" / "n8n-cf-transkreacija-hr.md").read_text(encoding="utf-8")
    v_dok = re.search(r"\*\*ID workflowa:\*\* `([A-Za-z0-9]{16})`", dok)
    assert v_veji and v_dok
    assert v_veji.group(1) == v_dok.group(1)
