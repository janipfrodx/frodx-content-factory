import struct
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKRIPTA = REPO / "plugins" / "content-factory" / "skills" / "frodx-publish-send" / "scripts" / "dimenzije.py"

sys.path.insert(0, str(SKRIPTA.parent))

PNG_PODPIS = b"\x89PNG\r\n\x1a\n"


def _png(sirina: int, visina: int) -> bytes:
    """Najmanjši PNG, ki ima veljavno IHDR glavo. Ostanek datoteke za izmero ni potreben."""
    return (
        PNG_PODPIS
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", sirina, visina)
        + b"\x08\x06\x00\x00\x00"
    )


def _jpeg(sirina: int, visina: int, polnila: int = 0) -> bytes:
    """JPEG s segmentom APP0 pred SOF0, da test dokaže, da parser preskakuje segmente.

    `polnila` je število polnilnih bajtov 0xFF pred markerjem SOF0. Standard jih
    dovoli poljubno mnogo; parser jih mora preskočiti, ne pa jih brati kot marker.
    """
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
    sof0 = (
        b"\xff" * polnila
        + b"\xff\xc0"
        + struct.pack(">H", 17)
        + b"\x08"
        + struct.pack(">HH", visina, sirina)
        + b"\x03"
        + b"\x00" * 9
    )
    return b"\xff\xd8" + app0 + sof0


def test_png_dimenzije(tmp_path):
    from dimenzije import dimenzije
    pot = tmp_path / "a.png"
    pot.write_bytes(_png(1536, 1024))
    assert dimenzije(pot) == (1536, 1024)


def test_jpeg_dimenzije(tmp_path):
    from dimenzije import dimenzije
    pot = tmp_path / "a.jpg"
    pot.write_bytes(_jpeg(784, 522))
    assert dimenzije(pot) == (784, 522)


def test_neznan_format_vrze_napako(tmp_path):
    from dimenzije import dimenzije
    pot = tmp_path / "a.txt"
    pot.write_bytes(b"to ni slika")
    with pytest.raises(ValueError):
        dimenzije(pot)


def test_cli_izpise_dimenzije(tmp_path):
    pot = tmp_path / "a.png"
    pot.write_bytes(_png(1200, 630))
    r = subprocess.run([sys.executable, str(SKRIPTA), str(pot)], capture_output=True, text=True)
    assert r.returncode == 0
    assert "1200x630" in r.stdout


def test_jpeg_s_polnilnimi_bajti(tmp_path):
    """Veljavna slika ne sme pasti zaradi polnil - iz nje nastane trdi gate."""
    from dimenzije import dimenzije
    for polnila in (1, 3):
        pot = tmp_path / f"a{polnila}.jpg"
        pot.write_bytes(_jpeg(1536, 864, polnila))
        assert dimenzije(pot) == (1536, 864)
