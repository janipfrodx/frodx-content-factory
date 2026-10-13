#!/usr/bin/env python3
"""Najzgodnejši čas objave Nikine zgodbe: zdaj + 15 minut, zaokroženo navzgor na četrt ure.

Uporaba:
  python3 urnik.py [--zdaj <ISO z zamikom>]

Izpiše JSON v eni vrstici: {"publish_at": "<ISO>", "linkedin_date": "YYYY-MM-DD"}.
LinkedIn je na dan bloga, če je blog najkasneje ob 7.30, sicer naslednji dan.
"""
import argparse
import datetime as dt
import json
import sys
from zoneinfo import ZoneInfo

CASOVNI_PAS = "Europe/Ljubljana"
ZAMIK = dt.timedelta(minutes=15)
ZADNJI_BLOG_NA_DAN_LINKEDINA = dt.time(7, 30)


def najzgodnejsi(zdaj):
    utc = zdaj.astimezone(dt.timezone.utc) + ZAMIK
    ostanek = dt.timedelta(minutes=utc.minute % 15, seconds=utc.second, microseconds=utc.microsecond)
    if ostanek:
        utc += dt.timedelta(minutes=15) - ostanek
    return utc.astimezone(ZoneInfo(CASOVNI_PAS))


def predlog_linkedin(blog):
    dan = blog.date()
    if blog.time() <= ZADNJI_BLOG_NA_DAN_LINKEDINA:
        return dan
    return dan + dt.timedelta(days=1)


def _zdaj(niz):
    cas = dt.datetime.fromisoformat(niz)
    if cas.tzinfo is None:
        raise argparse.ArgumentTypeError("--zdaj mora imeti zamik, npr. 2026-10-13T10:47:00+02:00")
    return cas


def main(argv=None):
    razclenjevalnik = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    razclenjevalnik.add_argument("--zdaj", type=_zdaj, default=None)
    args = razclenjevalnik.parse_args(argv)
    blog = najzgodnejsi(args.zdaj or dt.datetime.now(dt.timezone.utc))
    print(json.dumps({"publish_at": blog.isoformat(), "linkedin_date": predlog_linkedin(blog).isoformat()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
