#!/usr/bin/env python3
"""Izhod pisca novičnika (oblika EDITIONS) v izdaje paketa.

Uporaba: python3 iz_editions.py <state.json> <editions.json>

editions.json je slovar {jezik: izdaja} v obliki EDITIONS iz
vendor/frodx-newsletter/scripts/build_newsletter.py, zapisan kot JSON:
pari ("KLJUČ", vrednost) so seznami ["KLJUČ", vrednost]. Izdaji hr in en
sprejme šele, ko je Igor potrdil kritiko SI (_run.approvals.step3).
V SI in HR vstavi nedeljivi presledek pred % (tipografija.py).
"""
import json
import os
import sys
from pathlib import Path

from tipografija import nbsp_pred_odstotkom

JEZIKI = ("si", "en", "hr")
META = (
    "PACKAGE_ID", "EDITION_NAME", "LANGUAGE", "STATUS", "SEGMENT_REF", "FROM_NAME",
    "FROM_EMAIL", "REPLY_TO", "FOOTER_REF", "SUBJECT", "PREHEADER", "GREETING",
)
DOGODEK = ("EVENT_DATE", "EVENT_TIME", "EVENT_DURATION_MIN")


class NapakaPreslikave(ValueError):
    pass


def _pari(vrednost, polje):
    if isinstance(vrednost, dict):
        return dict(vrednost)
    try:
        return {k: v for k, v in vrednost}
    except (TypeError, ValueError):
        raise NapakaPreslikave(f"{polje} mora biti seznam parov [KLJUČ, vrednost]")


def _dogodek(surovo, bid):
    if not surovo:
        return None
    pari = _pari(surovo, f"{bid}.event")
    manjka = [k for k in DOGODEK if k not in pari]
    if manjka:
        raise NapakaPreslikave(f"{bid}.event: manjka {', '.join(manjka)}")
    trajanje = str(pari["EVENT_DURATION_MIN"]).strip()
    if not trajanje.isdigit():
        raise NapakaPreslikave(f"{bid}.event: EVENT_DURATION_MIN mora biti število minut, je {trajanje!r}")
    return {"date": pari["EVENT_DATE"], "time": pari["EVENT_TIME"], "duration_min": int(trajanje)}


def _blok(b):
    bid = b.get("id", "?")
    try:
        slika = None
        if b.get("img_file") or b.get("img_alt"):
            slika = {"alt": b.get("img_alt", ""), "file": b.get("img_file", "")}
        return {
            "block_id": b["id"],
            "type": b["type"],
            "image": slika,
            "title": b["title"],
            "body": list(b["body"]),
            "bullets": list(b.get("bullets") or []),
            "event": _dogodek(b.get("event"), bid),
            "cta": {"label": b["cta_label"], "url": b["cta_url"]},
        }
    except KeyError as napaka:
        raise NapakaPreslikave(f"blok {bid}: manjka {napaka.args[0]}")


def izdaja_iz_editions(jezik: str, ed: dict) -> dict:
    meta = _pari(ed.get("meta"), f"{jezik}.meta")
    manjka = [k for k in META if k not in meta]
    if manjka:
        raise NapakaPreslikave(f"{jezik}: manjka META {', '.join(manjka)}")
    if meta["LANGUAGE"] != jezik:
        raise NapakaPreslikave(f"{jezik}: META LANGUAGE je {meta['LANGUAGE']!r}")
    try:
        return nbsp_pred_odstotkom({
            "package_id": meta["PACKAGE_ID"],
            "edition_name": meta["EDITION_NAME"],
            "language": jezik,
            "status": meta["STATUS"],
            "delivery": {"segment_ref": meta["SEGMENT_REF"]},
            "sender": {
                "from_name": meta["FROM_NAME"],
                "from_email": meta["FROM_EMAIL"],
                "reply_to": meta["REPLY_TO"],
            },
            "subject": meta["SUBJECT"],
            "preheader": meta["PREHEADER"],
            "greeting": meta["GREETING"],
            "hook": {"archetype": ed["hook_archetype"], "paragraphs": list(ed["hook"])},
            "blocks": [_blok(b) for b in ed["blocks"]],
            "closing": {"type": ed["closing_type"], "paragraphs": list(ed["closing"])},
            "signoff": {"phrase": ed["signoff_phrase"], "name": ed["signoff_name"]},
            "ps": ed.get("ps") or None,
            "footer_ref": meta["FOOTER_REF"] or None,
        }, jezik)
    except KeyError as napaka:
        raise NapakaPreslikave(f"{jezik}: manjka {napaka.args[0]}")


def vpisi(stanje: dict, editions: dict) -> dict:
    neznani = [j for j in editions if j not in JEZIKI]
    if neznani:
        raise NapakaPreslikave(f"neznan jezik {neznani}; dovoljeni so {', '.join(JEZIKI)}")
    potrjeno = (stanje.get("_run") or {}).get("approvals") or {}
    if {"en", "hr"} & set(editions) and "step3" not in potrjeno:
        raise NapakaPreslikave(
            "HR in EN se zapišeta šele po potrjeni kritiki SI (_run.approvals.step3). "
            "Izdaje, ki so nastale pred tem, zavrzi in jih napiši znova iz popravljene SI."
        )
    nove = {j: izdaja_iz_editions(j, ed) for j, ed in editions.items()}
    obstojece = {i["language"]: i for i in stanje.get("editions") or []}
    obstojece.update(nove)
    nova = dict(stanje)
    nova["editions"] = [obstojece[j] for j in JEZIKI if j in obstojece]
    return nova


def main(argv) -> int:
    if len(argv) != 3:
        print("Uporaba: iz_editions.py <state.json> <editions.json>")
        return 1
    pot = Path(argv[1])
    try:
        stanje = json.loads(pot.read_text(encoding="utf-8"))
        editions = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
        nova = vpisi(stanje, editions)
    except NapakaPreslikave as napaka:
        print(f"NAPAKA: {napaka}")
        return 1
    except (OSError, json.JSONDecodeError, AttributeError) as napaka:
        print(f"NAPAKA: {napaka}")
        return 1
    zacasna = pot.with_name(pot.name + ".tmp")
    zacasna.write_text(json.dumps(nova, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(zacasna, pot)
    print(f"Zapisane izdaje: {', '.join(editions)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
