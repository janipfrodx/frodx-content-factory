import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKRIPTA = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "scripts" / "init_run.py"
sys.path.insert(0, str(SKRIPTA.parent))


def test_slugify_odstrani_sumnike():
    from init_run import slugify
    assert slugify("Zakaj lojalnostni programi kaznujejo zveste") == "zakaj-lojalnostni-programi-kaznujejo-zveste"
    assert slugify("Čigav je čas? Šumniki & žveplo!") == "cigav-je-cas-sumniki-zveplo"


def test_slugify_ne_pusti_vodilnih_ali_koncnih_vezajev():
    from init_run import slugify
    assert slugify("  ...Test...  ") == "test"


def test_stanje_ima_vse_tri_jezike():
    from init_run import zgradi_stanje
    stanje = zgradi_stanje("Test tema", "test-tema", "2026-08-10T09:00:00.000Z")
    assert set(stanje["languages"]) == {"sl", "en", "hr"}
    for jezik in ("sl", "en", "hr"):
        assert stanje["languages"][jezik]["language_code"] == jezik
        assert stanje["languages"][jezik]["content"] == ""


def test_stanje_ima_run_blok_na_koraku_ena():
    from init_run import zgradi_stanje
    stanje = zgradi_stanje("Test tema", "test-tema", "2026-08-10T09:00:00.000Z")
    assert stanje["_run"]["step"] == 1
    assert stanje["_run"]["status"] == "awaiting_topic"
    assert stanje["_run"]["slug"] == "2026-08-10-test-tema"
    assert stanje["universal"]["slug"] == "test-tema"
    assert stanje["_run"]["critique_rounds"] == 0
    assert stanje["_run"]["approvals"] == {}
    # open_tasks mora obstajati ze od zacetka - koraka 1 in 4 vanj piseta,
    # korak 7 ga bere. Ce ga init ne ustvari, ga korak, ki pise, tiho izpusti.
    assert stanje["_run"]["open_tasks"] == []


def test_stanje_ima_verzijo_1_2():
    from init_run import zgradi_stanje
    stanje = zgradi_stanje("Test tema", "test-tema", "2026-08-10T09:00:00.000Z")
    assert stanje["meta"]["version"] == "1.2"
    assert stanje["meta"]["title"] == "Test tema"
    assert stanje["universal"]["slug"] == "test-tema"


def test_cli_ustvari_mapo_in_datoteko(tmp_path):
    r = subprocess.run(
        [sys.executable, str(SKRIPTA), "Zakaj lojalnostni programi kaznujejo zveste", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    pot = Path(r.stdout.strip())
    assert pot.is_file()
    assert pot.name == "state.json"
    assert "zakaj-lojalnostni-programi" in str(pot)
    stanje = json.loads(pot.read_text(encoding="utf-8"))
    assert stanje["_run"]["step"] == 1


def test_cli_ne_povozi_obstojecega(tmp_path):
    args = [sys.executable, str(SKRIPTA), "Ista tema", str(tmp_path)]
    prvi = subprocess.run(args, capture_output=True, text=True)
    assert prvi.returncode == 0
    drugi = subprocess.run(args, capture_output=True, text=True)
    assert drugi.returncode == 1
    # sporocilo "ze obstaja" je izpisano samo v veji FileExistsError - ce bi
    # drugi klic padel skozi splosno OSError vejo, bi bilo sporocilo drugacno
    # ("Ni bilo mogoce ustvariti mape teka ..."), zato ta trditev dokazuje
    # pravi razlog neuspeha, ne le neuspeh sam.
    assert "ze obstaja" in drugi.stdout.lower() or "že obstaja" in drugi.stdout.lower()


def test_cli_ne_izbrise_obstojecega_teka(tmp_path):
    """Ce mapa teka ze obstaja (npr. dokoncan tek drugega zagona), CLI ne
    sme pobrisati nic - niti mape same, niti njene vsebine."""
    from datetime import datetime, timezone
    from init_run import _okrajsaj_slug, slugify

    naslov = "Zasedena tema za test brisanja"
    danes = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = _okrajsaj_slug(slugify(naslov))
    mapa = tmp_path / f"{danes}-{slug}"
    mapa.mkdir(parents=True)
    oznaka = mapa / "oznaka.txt"
    oznaka.write_text("dokoncan tek drugega zagona")

    r = subprocess.run(
        [sys.executable, str(SKRIPTA), naslov, str(tmp_path)],
        capture_output=True, text=True,
    )

    assert r.returncode == 1
    assert mapa.exists()
    assert oznaka.exists()
    assert oznaka.read_text() == "dokoncan tek drugega zagona"


def test_okrajsaj_slug_reze_na_meji_besede():
    from init_run import _okrajsaj_slug
    dolg = "-".join(["beseda"] * 20)
    okrajsan = _okrajsaj_slug(dolg, 80)
    assert len(okrajsan) <= 80
    assert not okrajsan.endswith("-")
    assert dolg.startswith(okrajsan)
    # naslednji znak za odrezanim slugom je vezaj - dokaz, da smo rezali na meji besede
    assert dolg[len(okrajsan)] == "-"


def test_okrajsaj_slug_pusti_kratek_slug_nedotaknjen():
    from init_run import _okrajsaj_slug
    kratek = "kratek-slug-brez-potrebe-po-rezanju"
    assert _okrajsaj_slug(kratek, 80) == kratek
    na_meji = "a" * 80
    assert _okrajsaj_slug(na_meji, 80) == na_meji
    tik_pod_mejo = "a" * 79
    assert _okrajsaj_slug(tik_pod_mejo, 80) == tik_pod_mejo


def test_cli_z_zelo_dolgim_naslovom_ne_sesuje_programa(tmp_path):
    from init_run import SLUG_MAX
    naslov = " ".join(["beseda"] * 60)
    r = subprocess.run(
        [sys.executable, str(SKRIPTA), naslov, str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    pot = Path(r.stdout.strip())
    assert pot.is_file()

    ime_mape = pot.parent.name
    _, _, _, slug_iz_imena = ime_mape.split("-", 3)
    assert len(slug_iz_imena) <= SLUG_MAX
    assert not slug_iz_imena.endswith("-")

    stanje = json.loads(pot.read_text(encoding="utf-8"))
    assert stanje["universal"]["slug"] == slug_iz_imena


def test_cli_napacno_stevilo_argumentov(tmp_path):
    r = subprocess.run(
        [sys.executable, str(SKRIPTA), "samo-en-argument"],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "uporaba" in r.stdout.lower()


def test_cli_prazna_tema_vrne_1(tmp_path):
    r = subprocess.run(
        [sys.executable, str(SKRIPTA), "   ", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "prazen" in r.stdout.lower()


def test_cli_prazen_slug_vrne_1(tmp_path):
    r = subprocess.run(
        [sys.executable, str(SKRIPTA), "???", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "sluga" in r.stdout.lower()


def test_tek_slug_nosi_datum_clanek_pa_ne():
    from init_run import zgradi_stanje
    stanje = zgradi_stanje("Test tema", "test-tema", "2026-09-17T09:00:00.000Z")
    assert stanje["_run"]["slug"] == "2026-09-17-test-tema"
    assert stanje["universal"]["slug"] == "test-tema"
    assert stanje["_run"]["slug"] != stanje["universal"]["slug"]


import re

RUN_SLUG = re.compile(r"^[a-z0-9-]{3,120}$")


def test_kolumna_nosi_vejo():
    from init_run import zgradi_stanje
    stanje = zgradi_stanje("Test tema", "test-tema", "2026-09-28T09:00:00.000Z")
    assert stanje["_run"]["veja"] == "kolumna"


def test_novicnik_ima_obliko_telesa_za_api_drafts():
    from init_run import zgradi_stanje_novicnik
    stanje = zgradi_stanje_novicnik("Oktobrski novičnik", "oktobrski-novicnik", "2026-09-28T09:00:00.000Z")
    assert set(stanje) == {"run_slug", "editions", "_run"}
    assert stanje["run_slug"] == "2026-09-28-oktobrski-novicnik"
    assert stanje["editions"] == []
    run = stanje["_run"]
    assert run["veja"] == "novicnik"
    assert run["slug"] == stanje["run_slug"]
    assert run["step"] == 0
    assert run["status"] == "awaiting_material"
    assert run["open_tasks"] == []
    assert run["approvals"] == {}
    assert "send_datetime" not in json.dumps(stanje)


def test_cli_novicnik(tmp_path):
    r = subprocess.run(
        [sys.executable, str(SKRIPTA), "--veja", "novicnik", "Oktobrski novičnik", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    stanje = json.loads(Path(r.stdout.strip()).read_text(encoding="utf-8"))
    assert stanje["_run"]["veja"] == "novicnik"
    assert RUN_SLUG.match(stanje["run_slug"])


def test_cli_brez_veje_je_kolumna(tmp_path):
    r = subprocess.run([sys.executable, str(SKRIPTA), "Tema brez veje", str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    stanje = json.loads(Path(r.stdout.strip()).read_text(encoding="utf-8"))
    assert stanje["_run"]["veja"] == "kolumna"
    assert "languages" in stanje


def test_cli_neznana_veja(tmp_path):
    r = subprocess.run(
        [sys.executable, str(SKRIPTA), "--veja", "podcast", "Tema", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "neznana veja" in r.stdout.lower()
    assert not any(tmp_path.iterdir())


def test_cli_veja_brez_vrednosti(tmp_path):
    r = subprocess.run([sys.executable, str(SKRIPTA), "--veja"], capture_output=True, text=True)
    assert r.returncode == 1


def test_run_slug_novicnika_z_dolgim_naslovom_ustreza_aplikaciji(tmp_path):
    naslov = " ".join(["beseda"] * 60)
    r = subprocess.run(
        [sys.executable, str(SKRIPTA), "--veja", "novicnik", naslov, str(tmp_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    stanje = json.loads(Path(r.stdout.strip()).read_text(encoding="utf-8"))
    assert RUN_SLUG.match(stanje["run_slug"]), stanje["run_slug"]
