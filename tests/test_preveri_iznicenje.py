import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTE = REPO / "plugins" / "content-factory" / "skills" / "frodx-transcreation-check" / "scripts"
SKRIPTA = SKRIPTE / "preveri_iznicenje.py"
sys.path.insert(0, str(SKRIPTE))

from preveri_iznicenje import iznicene, nalozi_sprejete

TACNO = {"navedek": "tačno tako", "popravek": "točno tako", "razlog": "srbizem"}


def _krog(mapa, jezik, n, accepted):
    mapa.mkdir(parents=True, exist_ok=True)
    podatki = {"language": jezik, "round": n, "verdict": "revise"}
    if accepted is not None:
        podatki["accepted"] = accepted
    (mapa / f"{jezik}-round-{n}.json").write_text(json.dumps(podatki, ensure_ascii=False), encoding="utf-8")


def _cli(*args):
    return subprocess.run([sys.executable, str(SKRIPTA), *map(str, args)], capture_output=True, text=True)


def test_vrnjen_navedek_je_iznicen():
    assert iznicene([TACNO], "Bilo je točno tako.", "Bilo je tačno tako.") == [TACNO]


def test_preoblikovan_stavek_brez_napake_ni_iznicen():
    assert iznicene([TACNO], "Bilo je točno tako.", "Upravo je tako bilo.") == []


def test_navedek_ze_pred_auditom_ni_iznicenje():
    """Popravek ni prijel ali se niz legitimno ponovi - tega skripta ne sodi."""
    assert iznicene([TACNO], "tačno tako, in točno tako", "tačno tako") == []


def test_iznicenje_ne_skrije_velika_zacetnica_in_presledki():
    po = "Tačno \n tako je bilo."
    assert iznicene([TACNO], "Točno tako je bilo.", po) == [TACNO]


def test_nalozi_sprejete_zdruzi_vse_kroge_jezika(tmp_path):
    druga = {"navedek": "za vrijeme", "popravek": "tijekom", "razlog": "kalk"}
    _krog(tmp_path, "hr", 1, [TACNO])
    _krog(tmp_path, "hr", 2, [druga])
    _krog(tmp_path, "en", 1, [{"navedek": "x", "popravek": "y", "razlog": "z"}])
    assert nalozi_sprejete(tmp_path, "hr") == [TACNO, druga]


def test_stara_datoteka_kroga_brez_accepted(tmp_path):
    _krog(tmp_path, "hr", 1, None)
    assert nalozi_sprejete(tmp_path, "hr") == []


def test_prazen_navedek_se_preskoci(tmp_path):
    _krog(tmp_path, "hr", 1, [{"navedek": "  ", "popravek": "x", "razlog": "y"}, TACNO])
    assert nalozi_sprejete(tmp_path, "hr") == [TACNO]


def test_pokvarjen_accepted_je_napaka(tmp_path):
    _krog(tmp_path, "hr", 1, "tačno tako")
    with pytest.raises(ValueError):
        nalozi_sprejete(tmp_path, "hr")
    pred, po = tmp_path / "pred.txt", tmp_path / "po.txt"
    pred.write_text("a", encoding="utf-8")
    po.write_text("a", encoding="utf-8")
    izid = _cli(tmp_path, "hr", pred, po)
    assert izid.returncode == 2
    assert "NAPAKA" in izid.stdout


def test_pokvarjen_json_je_napaka(tmp_path):
    (tmp_path / "hr-round-1.json").write_text("{ni json", encoding="utf-8")
    pred, po = tmp_path / "pred.txt", tmp_path / "po.txt"
    pred.write_text("a", encoding="utf-8")
    po.write_text("a", encoding="utf-8")
    assert _cli(tmp_path, "hr", pred, po).returncode == 2


def test_koren_ni_objekt_je_napaka(tmp_path):
    (tmp_path / "hr-round-1.json").write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        nalozi_sprejete(tmp_path, "hr")
    pred, po = tmp_path / "pred.txt", tmp_path / "po.txt"
    pred.write_text("a", encoding="utf-8")
    po.write_text("a", encoding="utf-8")
    izid = _cli(tmp_path, "hr", pred, po)
    assert izid.returncode == 2
    assert "NAPAKA" in izid.stdout


def test_manjkajoca_mapa_je_napaka(tmp_path):
    pred, po = tmp_path / "pred.txt", tmp_path / "po.txt"
    pred.write_text("a", encoding="utf-8")
    po.write_text("a", encoding="utf-8")
    izid = _cli(tmp_path / "ni-je", "hr", pred, po)
    assert izid.returncode == 2
    assert "NAPAKA" in izid.stdout


def test_cli_izpise_izniceno_in_vrne_1(tmp_path):
    _krog(tmp_path, "hr", 1, [TACNO])
    pred, po = tmp_path / "pred.txt", tmp_path / "po.txt"
    pred.write_text("Bilo je točno tako.", encoding="utf-8")
    po.write_text("Bilo je tačno tako.", encoding="utf-8")
    izid = _cli(tmp_path, "hr", pred, po)
    assert izid.returncode == 1
    assert 'IZNIČENO: "tačno tako" -> "točno tako" (srbizem)' in izid.stdout


def test_cli_brez_iznicenja_vrne_0(tmp_path):
    _krog(tmp_path, "hr", 1, [TACNO])
    pred, po = tmp_path / "pred.txt", tmp_path / "po.txt"
    pred.write_text("Bilo je točno tako.", encoding="utf-8")
    po.write_text("Bilo je upravo tako.", encoding="utf-8")
    izid = _cli(tmp_path, "hr", pred, po)
    assert izid.returncode == 0
    assert izid.stdout.startswith("OK")


def test_cli_napacen_jezik_je_napaka(tmp_path):
    assert _cli(tmp_path, "sl", "a", "b").returncode == 2


def test_skripta_uporablja_samo_standardno_knjiznico():
    vsebina = SKRIPTA.read_text(encoding="utf-8")
    for modul in ("pytest", "requests", "yaml"):
        assert f"import {modul}" not in vsebina
