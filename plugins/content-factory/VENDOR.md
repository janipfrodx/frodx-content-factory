# Vendorirani skilli

Štirje skilli v tem pluginu so delo Igorja Pauletiča in so tu **nespremenjeni**.

| Skill | Izvor | Verzija paketa |
|---|---|---|
| `igor-column-writer` | frodx-content-kit.zip | 6. 8. 2026 |
| `frodx-transcreation` | frodx-content-kit.zip | 6. 8. 2026 |
| `frodx-key-visual` | frodx-content-kit.zip | 6. 8. 2026 |
| `frodx-newsletter` | frodx-content-kit.zip | 6. 8. 2026 |

## Pravilo

Teh datotek ne urejaj neposredno. `tests/test_vendor_integrity.py` primerja sha256 vsake datoteke z `vendor-manifest.json` in pade, če se karkoli spremeni.

Sprememba gre tako:
1. Igor spremeni svojo verzijo skilla.
2. Sprememba pride v repo kot PR.
3. Ob merge se požene `python3 tools/vendor_hash.py`, da se manifest osveži.
4. `package_version` se dvigne na datum novega izvoza.

Namen ni birokracija. Namen je, da se Igorjeva in naša kopija ne razideta tiho - to je natanko tveganje, ki ga Igor opisuje v `README-JANI.md` §8.

## Znana napaka v izvoru

`README-JANI.md` v vrstici 77 trdi, da oba validatorja vračata exit code, uporabna kot n8n gate. To drži samo za `contract_check.py`. `eval_check.py` se vedno konča z 0 in izpiše le opozorila. Kdor ga uporabi kot blokirni gate za novičnik, dobi gate, ki nikoli ne blokira.
