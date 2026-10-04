import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAKET = REPO / "plugins" / "content-factory" / "skills" / "frodx-content-factory" / "veje" / "novicnik" / "vendor" / "igor-hr-sol"

SHA256 = {
    "00-navodila-za-Janija.txt": "586efcb54a73ec7850cc8a1ba45bf1793fc8ffc591a1d7db7e26b187f34a3167",
    "01-transkreacija-system.txt": "575d087995edd3c43173b32d70c55df8e15e47386cfecf4f7c0bcadc8d7d0539",
    "02-pregled-system.txt": "fc73540d8034587a93c34c83ac8501a407dcf12f070f5ee9d87980312b2097eb",
    "03-primer-vhoda.json": "efb6a633348de5b5e1739be91827df7b6a84e38196db003ac767009a52aa35f6",
    "04-shema-transkreacije.json": "eea5c064592ba7571bf712991bcc6131b697ec24d8773e4768442fc2220ed247",
    "05-shema-pregleda.json": "3237d7306ef8b16af296fd5f61214175050d38ff7a46451f7638bcc2f5af817b",
}


def test_igorjev_paket_ni_spremenjen():
    for ime, pricakovano in SHA256.items():
        pot = PAKET / ime
        assert pot.is_file(), ime
        assert hashlib.sha256(pot.read_bytes()).hexdigest() == pricakovano, (
            f"{ime} je spremenjen - spremembe gredo skozi Igorja"
        )


def test_paket_ima_readme_z_izvorom():
    vsebina = (PAKET / "README.md").read_text(encoding="utf-8")
    assert "2. 10. 2026" in vsebina
    assert "ne urejaj" in vsebina.lower()
    assert "—" not in vsebina


def test_paket_ni_samostojen_skill():
    assert not (PAKET / "SKILL.md").exists()
