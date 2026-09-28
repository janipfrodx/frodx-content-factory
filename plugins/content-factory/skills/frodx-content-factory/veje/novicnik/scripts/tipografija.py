"""Hišna tipografija izdaje novičnika, ki jo sicer naredi Igorjev docx korak.

Igorjev build_newsletter.py (pct) v SI in HR vstavi nedeljivi presledek
med števko in %. Tovarna docx koraka ne izvede, zato isto pretvorbo naredi
ob vpisu izdaje v state.json. EN ostane nespremenjen.
"""
import re

NBSP = "\u00a0"
JEZIKI_NBSP = ("si", "hr")
_PRED_ODSTOTKOM = re.compile(r"(\d)[ \t]+%")


def nbsp_pred_odstotkom(obj, jezik: str):
    if jezik not in JEZIKI_NBSP:
        return obj
    if isinstance(obj, str):
        return _PRED_ODSTOTKOM.sub(lambda m: m.group(1) + NBSP + "%", obj)
    if isinstance(obj, list):
        return [nbsp_pred_odstotkom(x, jezik) for x in obj]
    if isinstance(obj, dict):
        return {k: nbsp_pred_odstotkom(v, jezik) for k, v in obj.items()}
    return obj
