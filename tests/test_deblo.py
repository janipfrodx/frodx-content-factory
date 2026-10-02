from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLI = REPO / "plugins" / "content-factory" / "skills"
DEBLO = SKILLI / "frodx-content-factory"
VEJE = DEBLO / "veje"
RAZDELKI = [
    "Sprožilci", "Paket", "Koraki", "Pisec in preslikava",
    "Skupni koraki", "Preverba paketa", "Oddaja", "Posebnosti",
]
STARE_POTI = (
    "frodx-content-factory/references/",
    "skills/frodx-topic-pick",
    "skills/frodx-publishing-meta",
    "skills/igor-column-writer",
    "skills/frodx-newsletter",
)


def _naslovi(pot):
    return [v[3:].strip() for v in pot.read_text(encoding="utf-8").splitlines() if v.startswith("## ")]


def test_vsaka_veja_ima_isti_skelet():
    veje = sorted(VEJE.glob("*/VEJA.md"))
    assert veje, "ni nobene veje"
    for pot in veje:
        assert _naslovi(pot) == RAZDELKI, pot.parent.name


def test_veja_ni_samostojen_skill():
    for mapa in VEJE.iterdir():
        if mapa.is_dir():
            assert not (mapa / "SKILL.md").exists(), mapa.name


def test_skilli_ene_veje_niso_na_vrhu():
    for ime in ("igor-column-writer", "frodx-topic-pick", "frodx-publishing-meta", "frodx-newsletter"):
        assert not (SKILLI / ime).exists(), ime


def test_kolumna_ima_svoje_datoteke():
    kolumna = VEJE / "kolumna"
    for pot in (
        "VEJA.md",
        "topic-pick/SKILL.md",
        "publishing-meta/SKILL.md",
        "publishing-meta/references/hubspot-taxonomy.md",
        "vendor/igor-column-writer/SKILL.md",
        "references/state-schema.md",
        "references/igor-output-mapping.md",
    ):
        assert (kolumna / pot).is_file(), pot


def test_kolumna_ohrani_tabelo_sedmih_korakov():
    vsebina = (VEJE / "kolumna" / "VEJA.md").read_text(encoding="utf-8")
    for vrstica in (
        "| 1 | `frodx-topic-pick` | katero temo pišemo |",
        "| 2 | `igor-column-writer` | je kolumna v redu |",
        "| 3 | `frodx-critique-loop` | je popravljena verzija v redu |",
        "| 4 | `frodx-transcreation` + `frodx-transcreation-check` (z Igorjevim auditom na koncu) | sta EN in HR v redu (+ ocena audita za oba jezika) |",
        "| 5 | `frodx-image-run` | so slike v redu |",
        "| 6 | `frodx-publishing-meta` | so meta podatki v redu |",
        "| 7 | `frodx-publish-send` | (brez vprašanja, samo pošlje) |",
    ):
        assert vrstica in vsebina, vrstica


def test_kolumna_pove_kje_so_njeni_skilli():
    vsebina = (VEJE / "kolumna" / "VEJA.md").read_text(encoding="utf-8")
    for pot in ("topic-pick/SKILL.md", "publishing-meta/SKILL.md", "vendor/igor-column-writer/SKILL.md"):
        assert pot in vsebina, pot


def test_deblo_izbere_vejo_po_sprozilcih_in_vprasa_ob_dvomu():
    vsebina = (DEBLO / "SKILL.md").read_text(encoding="utf-8")
    assert "veje/<tip>/VEJA.md" in vsebina
    assert "Sprožilci" in vsebina
    assert "Kaj delamo" in vsebina, "ob dvoumnem stavku mora deblo vprašati"
    assert "Gremo na" in vsebina, "prvi odgovor potrdi vejo"


def test_star_tek_brez_veje_je_kolumna():
    vsebina = (DEBLO / "SKILL.md").read_text(encoding="utf-8")
    assert "`_run.veja` manjka" in vsebina


def test_deblo_nima_vec_korakov_kolumne():
    vsebina = (DEBLO / "SKILL.md").read_text(encoding="utf-8")
    assert "social_candidates" not in vsebina
    assert "| 7 | `frodx-publish-send`" not in vsebina


def test_nikjer_ni_starih_poti():
    for koren in (REPO / "plugins", REPO / "schema"):
        for pot in koren.rglob("*"):
            if not pot.is_file() or pot.suffix not in (".md", ".py", ".json"):
                continue
            if "vendor" in pot.parts:
                continue
            vsebina = pot.read_text(encoding="utf-8")
            for stara in STARE_POTI:
                assert stara not in vsebina, f"{pot.relative_to(REPO)}: {stara}"


def test_deblo_varcuje_s_kontekstom():
    vsebina = (DEBLO / "SKILL.md").read_text(encoding="utf-8")
    podrazdelek = vsebina[vsebina.index("### Kontekst"):]
    for niz in ('nodeNames: ["Respond to Webhook"]', "includeData: true", "get_workflow_sdk_reference", "get_node_types",
                "base64", "posnetk", "izdaja_besedilo.py izpis"):
        assert niz in podrazdelek, niz
