import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTE = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "nika" / "scripts"


def _nalozi(ime):
    spec = importlib.util.spec_from_file_location(f"{ime}_nika", SKRIPTE / f"{ime}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


z, iz = _nalozi("zavihek"), _nalozi("iz_zavihka")


def _telo():
    return json.loads((REPO / "tests" / "fixtures" / "nika_story_body.json").read_text(encoding="utf-8"))


def _izpolni(md, odlocitev="Potrdi", sodba="da", razlog="", komentar=""):
    md = md.replace("| Odločitev (Potrdi / Zavrni) |  |", f"| Odločitev (Potrdi / Zavrni) | {odlocitev} |")
    md = md.replace("| Bi se tako odločila? (da / ne / drugače) |  |", f"| Bi se tako odločila? (da / ne / drugače) | {sodba} |")
    md = md.replace("| Razlog zavrnitve (presoja / dejstvo / novost / slog) |  |", f"| Razlog zavrnitve (presoja / dejstvo / novost / slog) | {razlog} |")
    return md.replace("| Komentar |  |", f"| Komentar | {komentar} |")


def test_vsi_razdelki_v_vrstnem_redu():
    md = z.zgradi(_telo())
    mesta = [md.index(f"\n## {r}\n") for r in z.RAZDELKI]
    assert mesta == sorted(mesta)


def test_naslov_ni_podvojen():
    md = z.zgradi(_telo())
    assert md.count(_telo()["story"]["title"]) == 1


def test_nespremenjen_zavihek_vrne_isto_besedilo():
    telo = _telo()
    izid = iz.preberi(_izpolni(z.zgradi(telo)))
    assert izid["title"] == telo["story"]["title"]
    assert izid["blog_md"] == telo["story"]["blog_md"]
    assert izid["linkedin_text"] == telo["story"]["linkedin_text"]
    assert iz.spremenjene_povedi(telo["story"]["blog_md"], izid["blog_md"]) == 0


def test_odlocitev_potrdi():
    izid = iz.preberi(_izpolni(z.zgradi(_telo())))
    assert izid["odlocitev"] == {"decision": "approve", "judgment_answer": "da", "reason": "", "comment": ""}


def test_odlocitev_zavrni_z_razlogom():
    md = _izpolni(z.zgradi(_telo()), "**Zavrni**", "drugače", "Dejstvo", "Rok ni prav.")
    assert iz.preberi(md)["odlocitev"] == {"decision": "reject", "judgment_answer": "drugače", "reason": "dejstvo", "comment": "Rok ni prav."}


def test_neodlocena_je_none():
    assert iz.preberi(z.zgradi(_telo()))["odlocitev"]["decision"] is None


def test_neznana_odlocitev_je_napaka():
    with pytest.raises(ValueError, match="Potrdi / Zavrni"):
        iz.preberi(_izpolni(z.zgradi(_telo()), "OK"))


def test_manjkajoc_razdelek_je_napaka():
    md = _izpolni(z.zgradi(_telo())).replace("## LinkedIn\n", "## Objava\n")
    with pytest.raises(ValueError, match="LinkedIn"):
        iz.preberi(md)


def test_nikina_sprememba_se_steje():
    telo = _telo()
    md = _izpolni(z.zgradi(telo)).replace("Pogoj sta snemanje s prepisom in Notetaker.", "Pogoj je vklopljen Notetaker.")
    izid = iz.preberi(md)
    assert iz.spremenjene_povedi(telo["story"]["blog_md"], izid["blog_md"]) == 1


def test_zbrisana_poved_se_steje():
    telo = _telo()
    md = _izpolni(z.zgradi(telo)).replace(" Pogoj sta snemanje s prepisom in Notetaker.", "")
    assert iz.spremenjene_povedi(telo["story"]["blog_md"], iz.preberi(md)["blog_md"]) == 1


def test_cli_brez_odlocitve_ne_pise(tmp_path):
    import subprocess, sys
    telo = _telo()
    stanje = tmp_path / "state.json"
    stanje.write_text(json.dumps(telo, ensure_ascii=False), encoding="utf-8")
    zav = tmp_path / "zavihek.md"
    zav.write_text(z.zgradi(telo).replace("Pogoj sta snemanje s prepisom in Notetaker.", "Pogoj je Notetaker."), encoding="utf-8")
    izid = subprocess.run([sys.executable, str(SKRIPTE / "iz_zavihka.py"), str(zav), str(stanje)], capture_output=True, text=True)
    assert izid.returncode == 0 and '"decision": null' in izid.stdout
    assert json.loads(stanje.read_text(encoding="utf-8")) == telo


def test_odkljukana_oznaka_ni_odprta():
    md = _izpolni(z.zgradi(_telo()))
    prva = md.index("- [ ] ")
    md = md[:prva] + "- [x] " + md[prva + 6:]
    assert len(iz.preberi(md)["odprte"]) == len(_telo()["preveri"]) - 1


def test_cli_vpise_v_state(tmp_path):
    import subprocess, sys
    telo = _telo()
    stanje = tmp_path / "state.json"
    stanje.write_text(json.dumps(telo, ensure_ascii=False), encoding="utf-8")
    zav = tmp_path / "zavihek.md"
    zav.write_text(_izpolni(z.zgradi(telo)).replace("Pogoj sta snemanje s prepisom in Notetaker.", "Pogoj je Notetaker."), encoding="utf-8")
    izid = subprocess.run([sys.executable, str(SKRIPTE / "iz_zavihka.py"), str(zav), str(stanje)], capture_output=True, text=True)
    assert izid.returncode == 0, izid.stdout
    novo = json.loads(stanje.read_text(encoding="utf-8"))
    assert "Pogoj je Notetaker." in novo["story"]["blog_md"]
    assert novo["_run"]["nika_pregled"]["spremenjene_povedi"] == 1
    assert novo["_run"]["nika_pregled"]["decision"] == "approve"


def test_ponovno_branje_ohrani_izvirnik_in_stevilo_sprememb(tmp_path):
    import subprocess, sys
    telo = _telo()
    stanje = tmp_path / "state.json"
    stanje.write_text(json.dumps(telo, ensure_ascii=False), encoding="utf-8")
    zav = tmp_path / "zavihek.md"
    zav.write_text(_izpolni(z.zgradi(telo)).replace("Pogoj sta snemanje s prepisom in Notetaker.", "Pogoj je Notetaker."), encoding="utf-8")
    for _ in range(2):
        izid = subprocess.run([sys.executable, str(SKRIPTE / "iz_zavihka.py"), str(zav), str(stanje)], capture_output=True, text=True)
        assert izid.returncode == 0, izid.stdout
        novo = json.loads(stanje.read_text(encoding="utf-8"))
        assert novo["_run"]["nika_pregled"]["spremenjene_povedi"] == 1
        assert novo["_run"]["nika_izvirnik"] == {"blog_md": telo["story"]["blog_md"], "linkedin_text": telo["story"]["linkedin_text"]}
    assert "Pogoj je Notetaker." in novo["story"]["blog_md"]


@pytest.mark.parametrize("vrstica", ["* [ ] foo", "- \\[ \\] foo", "foo"])
def test_neprepoznana_oznaka_preveri_je_napaka(vrstica):
    md = _izpolni(z.zgradi(_telo())).replace("- [ ] Potrditev", f"{vrstica}\n- [ ] Potrditev", 1)
    with pytest.raises(ValueError, match="Odprte oznake PREVERI"):
        iz.preberi(md)


def test_placeholder_brez_oznak_je_dovoljen():
    telo = _telo()
    telo["preveri"] = []
    assert iz.preberi(_izpolni(z.zgradi(telo)))["odprte"] == []


def test_odkljukana_velika_x_je_sprejeta():
    md = _izpolni(z.zgradi(_telo())).replace("- [ ] Potrditev", "- [X] Potrditev", 1)
    assert len(iz.preberi(md)["odprte"]) == len(_telo()["preveri"]) - 1
