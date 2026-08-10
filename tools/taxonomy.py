#!/usr/bin/env python3
"""Bere hubspot-taxonomy.md. Markdown je vir resnice, koda je samo bralec."""
import re
from pathlib import Path

VRSTICA = re.compile(r"^\|\s*(Interest - [^|]+?)\s*\|(.+)$")


def _celice(vrstica: str) -> list:
    return [c.strip() for c in vrstica.strip().strip("|").split("|")]


def load_campaigns(path: Path) -> dict:
    """Ime kampanje -> GUID. Bere samo vrstice z natanko dvema stolpcema."""
    rezultat = {}
    for vrstica in Path(path).read_text(encoding="utf-8").splitlines():
        if not VRSTICA.match(vrstica):
            continue
        celice = _celice(vrstica)
        if len(celice) == 2 and re.fullmatch(r"[0-9a-f-]{36}", celice[1]):
            rezultat[celice[0]] = celice[1]
    return rezultat


def load_tags(path: Path) -> dict:
    """(ime kampanje, jezik) -> {'id', 'name', 'slug'}. Bere vrstice s petimi stolpci."""
    rezultat = {}
    for vrstica in Path(path).read_text(encoding="utf-8").splitlines():
        if not VRSTICA.match(vrstica):
            continue
        celice = _celice(vrstica)
        if len(celice) == 5 and celice[1] in ("sl", "en", "hr"):
            kampanja, jezik, tag_id, ime, slug = celice
            rezultat[(kampanja, jezik)] = {"id": tag_id, "name": ime, "slug": slug}
    return rezultat
