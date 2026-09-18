import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / "plugins" / "content-factory" / "skills" / "frodx-transcreation-check"
PROMPT = SKILL_DIR / "references" / "transcreation-check-prompt.md"
SKILL = SKILL_DIR / "SKILL.md"

DIRIGENT = (
    REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "SKILL.md"
)
SHEMA = (
    REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory"
    / "references" / "state-schema.md"
)


def test_prompt_pozna_obe_sodbi():
    """Dvobesedni protokol je isti kot pri kritiki - brez njega se sodba ne da prebrati."""
    vsebina = PROMPT.read_text(encoding="utf-8")
    assert "OBJAVLJIVO" in vsebina
    assert "ZA POPRAVEK" in vsebina


def test_prompt_ima_oznako_za_datum():
    """Brez datuma ocenjevalec pravilne letnice razglasi za halucinacije (15. 8. 2026)."""
    assert "{{DANES}}" in PROMPT.read_text(encoding="utf-8")


def test_prompt_loci_merila_po_jezikih():
    """Hrvaščina in angleščina padeta na različnih stvareh; en sam splošen seznam ju zlije."""
    vsebina = PROMPT.read_text(encoding="utf-8").lower()
    for pojem in ("dvojin", "srbiz", "klijent", "korisnik", "kupac"):
        assert pojem in vsebina, pojem
    for pojem in ("idiom", "phrasal", "cee"):
        assert pojem in vsebina, pojem


def test_skill_ima_angleski_frontmatter():
    """Po `description` Claude izbira skill, zato je angleški; telo je slovensko."""
    vsebina = SKILL.read_text(encoding="utf-8")
    assert vsebina.startswith("---\n")
    glava = vsebina.split("---", 2)[1]
    assert "name: frodx-transcreation-check" in glava
    assert "description:" in glava
    assert "Croatian" in glava


def test_skill_klice_pravi_workflow():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "transcreation-check" in vsebina
    assert "execute_workflow" in vsebina
    assert '"manual"' in vsebina


def test_skill_bere_oceni_iz_odgovora_ne_iz_izvedbe():
    """Ta workflow odgovarja prek Respond to Webhook; loceno branje izvedbe ni potrebno."""
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "openai_error" in vsebina and "gemini_error" in vsebina
    assert "Respond to Webhook" in vsebina


def test_skill_ima_dva_kroga_in_popravek_skozi_transkreacijo():
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "dva kroga" in vsebina
    assert "frodx-transcreation" in vsebina
    assert "{{DANES}}" in vsebina


def test_skill_nima_vec_placeholderja_za_id_workflowa():
    """Ce ostane <ID-IZ-TASK-1>, skill poklice neobstojec workflow in tega nihce ne opazi."""
    vsebina = SKILL.read_text(encoding="utf-8")
    assert "ID-IZ-TASK-1" not in vsebina

    # n8n ID je 16 znakov iz crk in stevilk; poisci ga ob imenu workflowa.
    najdbe = re.findall(r'"workflowId":\s*"([A-Za-z0-9]{16})"', vsebina)
    assert najdbe, "v SKILL.md ni workflowId oblike, kot jo vrne n8n"


def test_dirigent_v_koraku_4_poklice_preverbo():
    vsebina = DIRIGENT.read_text(encoding="utf-8")
    assert "frodx-transcreation-check" in vsebina
    assert "pred Igorjevim gateom" in vsebina


def test_dirigent_ne_pise_vec_pogojne_zadolzitve_za_hrvascino():
    """Zadolžitev se odslej zapiše vedno, ne samo ob izrecni odločitvi."""
    vsebina = DIRIGENT.read_text(encoding="utf-8")
    assert "vedno" in vsebina
    assert "priporo" in vsebina.lower()


def test_shema_pozna_transcreation_check():
    vsebina = SHEMA.read_text(encoding="utf-8")
    assert "transcreation_check" in vsebina
    for polje in ("rounds", "verdict"):
        assert polje in vsebina, polje
