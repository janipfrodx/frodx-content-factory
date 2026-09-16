#!/usr/bin/env python3
"""Izmeri širino in višino slike iz glave datoteke. Samo standardna knjižnica.

`PIL` v Coworkovem okolju ni zagotovljen in pravilo projekta ga prepoveduje
v skriptah, ki jih poganja skill. Za PNG in JPEG glava zadošča.

Uporaba: python3 dimenzije.py <slika> [<slika> ...]
"""
import struct
import sys
from pathlib import Path

PNG_PODPIS = b"\x89PNG\r\n\x1a\n"

# SOF okvirji, ki nosijo dimenzije. 0xC4 (DHT), 0xC8 (JPG) in 0xCC (DAC) to niso.
SOF_MARKERJI = frozenset({0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF})

# Markerji brez dolžinskega polja: SOI, TEM in osem RST.
BREZ_DOLZINE = frozenset({0xD8, 0x01}) | frozenset(range(0xD0, 0xD8))


def dimenzije(pot) -> tuple:
    pot = Path(pot)
    bajti = pot.read_bytes()

    if bajti[:8] == PNG_PODPIS:
        if len(bajti) < 24:
            raise ValueError(f"{pot.name}: PNG glava je prekratka")
        sirina, visina = struct.unpack(">II", bajti[16:24])
        return sirina, visina

    if bajti[:2] == b"\xff\xd8":
        i = 2
        while i < len(bajti) - 9:
            if bajti[i] != 0xFF:
                i += 1
                continue
            marker = bajti[i + 1]
            if marker in SOF_MARKERJI:
                visina, sirina = struct.unpack(">HH", bajti[i + 5:i + 9])
                return sirina, visina
            if marker in BREZ_DOLZINE:
                i += 2
                continue
            i += 2 + struct.unpack(">H", bajti[i + 2:i + 4])[0]
        raise ValueError(f"{pot.name}: JPEG brez SOF okvirja")

    raise ValueError(f"{pot.name}: ni PNG ne JPEG")


def main() -> int:
    if len(sys.argv) < 2:
        print("Uporaba: dimenzije.py <slika> [<slika> ...]")
        return 1

    izhod = 0
    for arg in sys.argv[1:]:
        try:
            sirina, visina = dimenzije(arg)
        except (ValueError, OSError) as e:
            print(f"{arg}: NAPAKA - {e}")
            izhod = 1
        else:
            print(f"{arg}: {sirina}x{visina}")
    return izhod


if __name__ == "__main__":
    sys.exit(main())
