#!/usr/bin/env python3
"""Build self-contained, model-agnostic exports of the transcreation audit skill.

Concatenates the shared core (SKILL.md, minus YAML frontmatter and
Claude-only blocks) with one language reference into a single markdown
file that can be pasted into ChatGPT, used as project instructions, or
attached as a knowledge file in any LLM product.

Usage:
    python scripts/build_portable.py --lang hr
    python scripts/build_portable.py --lang en
    python scripts/build_portable.py --lang all
"""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

LANGS = {
    "hr": ("references/croatian.md", "transcreation-audit-hr.md", "Croatian"),
    "en": ("references/english.md", "transcreation-audit-en.md", "English"),
}

ROLE_HEADER = (
    "You are a senior transcreation auditor for Slovenian-to-{language} "
    "localization. Follow the instructions below exactly. They consist of a "
    "shared audit workflow followed by the {language} language reference, "
    "which is the authority for the fingerprint audit step.\n\n---\n\n"
)


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def strip_claude_only(text: str) -> str:
    return re.sub(
        r"<!-- STRIP-FROM-PORTABLE-START -->.*?<!-- STRIP-FROM-PORTABLE-END -->\n?",
        "",
        text,
        flags=re.DOTALL,
    )


def build(lang: str) -> Path:
    ref_path, out_name, language = LANGS[lang]
    core = strip_claude_only(strip_frontmatter((ROOT / "SKILL.md").read_text(encoding="utf-8")))
    reference = (ROOT / ref_path).read_text(encoding="utf-8")
    DIST.mkdir(exist_ok=True)
    out = DIST / out_name
    out.write_text(
        ROLE_HEADER.format(language=language) + core.strip() + "\n\n---\n\n" + reference.strip() + "\n",
        encoding="utf-8",
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=[*LANGS, "all"], default="all")
    args = parser.parse_args()
    targets = list(LANGS) if args.lang == "all" else [args.lang]
    for lang in targets:
        print(f"built: {build(lang)}")


if __name__ == "__main__":
    main()
