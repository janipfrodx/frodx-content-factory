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
    assert stanje["_run"]["slug"] == "test-tema"
    assert stanje["_run"]["critique_rounds"] == 0
    assert stanje["_run"]["approvals"] == {}


def test_stanje_ima_verzijo_1_1():
    from init_run import zgradi_stanje
    stanje = zgradi_stanje("Test tema", "test-tema", "2026-08-10T09:00:00.000Z")
    assert stanje["meta"]["version"] == "1.1"
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
    assert "ze obstaja" in drugi.stdout.lower() or "že obstaja" in drugi.stdout.lower()
