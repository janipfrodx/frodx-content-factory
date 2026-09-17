#!/usr/bin/env python3
"""Bere hubspot-taxonomy.md. Markdown je vir resnice, koda je samo bralec."""
import re
from pathlib import Path

PREDPONA = "Interest - "
GUID = re.compile(r"[0-9a-f-]{36}")
JEZIKI = ("sl", "en", "hr")


def _vrstice(path: Path):
    """Celice vsake tabelne vrstice, ki se začne s kampanjo `Interest - `."""
    for vrstica in Path(path).read_text(encoding="utf-8").splitlines():
        if not vrstica.startswith("|"):
            continue
        celice = [c.strip() for c in vrstica.strip().strip("|").split("|")]
        if len(celice) > 1 and celice[0].startswith(PREDPONA):
            yield celice


def load_campaigns(path: Path) -> dict:
    """Ime kampanje -> GUID. Bere samo vrstice z natanko dvema stolpcema."""
    return {
        celice[0]: celice[1]
        for celice in _vrstice(path)
        if len(celice) == 2 and GUID.fullmatch(celice[1])
    }


def load_tags(path: Path) -> dict:
    """(ime kampanje, jezik) -> {'id', 'name', 'slug'}. Bere vrstice s petimi stolpci."""
    return {
        (celice[0], celice[1]): {"id": celice[2], "name": celice[3], "slug": celice[4]}
        for celice in _vrstice(path)
        if len(celice) == 5 and celice[1] in JEZIKI
    }
