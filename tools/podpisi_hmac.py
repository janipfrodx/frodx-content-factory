"""Podpiše telo za cf-nika-decision ali cf-nika-publish.

Uporaba: NIKA_HMAC_SECRET=... python3 tools/podpisi_hmac.py <telo.json> [--set kljuc=vrednost ...]
Izpiše kompaktno telo (tako ga n8n vidi po JSON.stringify) in heks HMAC SHA-256 podpis.
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("telo")
    parser.add_argument("--set", action="append", default=[], metavar="KLJUC=VREDNOST")
    args = parser.parse_args()

    secret = os.environ.get("NIKA_HMAC_SECRET", "")
    if not secret:
        sys.exit("NIKA_HMAC_SECRET ni nastavljen")

    telo = json.loads(Path(args.telo).read_text(encoding="utf-8"))
    for par in args.set:
        kljuc, _, vrednost = par.partition("=")
        telo[kljuc] = vrednost

    kompaktno = json.dumps(telo, ensure_ascii=False, separators=(",", ":"))
    podpis = hmac.new(secret.encode("utf-8"), kompaktno.encode("utf-8"), hashlib.sha256).hexdigest()
    sys.stdout.reconfigure(encoding="utf-8")
    print(kompaktno)
    print(podpis)


if __name__ == "__main__":
    main()
