#!/usr/bin/env python3
"""Izračuna sha256 za vsako datoteko v drevesu vendoriranega skilla."""
import hashlib
import json
import sys
from pathlib import Path

VENDORED = ("igor-column-writer", "frodx-transcreation", "frodx-key-visual", "frodx-newsletter")


def hash_tree(root: Path) -> dict:
    result = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        result[str(path.relative_to(root))] = digest
    return result


def build_manifest(skills_dir: Path, source: str, package_version: str) -> dict:
    files = {}
    for name in VENDORED:
        for rel, digest in hash_tree(skills_dir / name).items():
            files[f"{name}/{rel}"] = digest
    return {"generated_from": source, "package_version": package_version, "files": files}


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    manifest = build_manifest(
        repo / "plugins" / "content-factory" / "skills",
        source="frodx-content-kit.zip",
        package_version="2026-08-06",
    )
    (repo / "vendor-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Zapisanih {len(manifest['files'])} datotek.")
    sys.exit(0)
