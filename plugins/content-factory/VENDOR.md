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

## Čakajoče točke za Igorja

Te izhajajo iz živega teka 14.-15. 8. 2026. Vendoriranih datotek se ne dotikamo, zato so tu - ob Igorjevi vrnitvi gredo v pogovor z njim in nato skozi PR.

### 1. `frodx-transcreation/references/terminology.md` - izjema za AEO ciljni prompt

Pravilo v vrstici 20 zahteva »SAP Engagement Cloud« in odsvetuje »Emarsys« kot samostojno ime izdelka. Kadar je ciljni AEO prompt dobesedno »Emarsys vs HubSpot«, kolumna brez te besede zgreši edini razlog, da je bila napisana. Izjema (»unless the source context explicitly requires reference to the former name«) to sicer že dopušča, a jo je treba brati posredno.

Predlog za Igorja: zapisati AEO ciljni prompt kot izrecno imenovan primer te izjeme. Do takrat je pravilo za našo stran verige zapisano v `skills/frodx-content-factory/SKILL.md`, razdelek »Terminologija in AEO ciljni prompt«.

### 2. `references/critique-prompt.md` je začasen

Prompt za kritiko sta napisala Jani in Claude, da veriga lahko teče. Ni Igorjev. Ob vrnitvi ga zamenja njegova verzija. Ob zamenjavi naj ostaneta dve pravili, ki sta se v teku izkazali za nujni: da se presoja **samo besedilo kolumne** (ne konteksta) in da ocenjevalec **ne sodi o verodostojnosti letnic** - oba ocenjevalna modela imata presek znanja pred današnjim datumom.

### 3. `igor-column-writer` sam ne vrne socialnih objav

V osnovnem teku jih je bilo treba izrecno naročiti po `references/social-posts.md`. Preslikava je opisana v `skills/frodx-content-factory/references/igor-output-mapping.md`. Vprašanje za Igorja: ali naj jih skill vrača sam kot del izhoda koraka 2.

## Znana napaka v izvoru

`README-JANI.md` v vrstici 77 trdi, da oba validatorja vračata exit code, uporabna kot n8n gate. To drži samo za `contract_check.py`. `eval_check.py` se vedno konča z 0 in izpiše le opozorila. Kdor ga uporabi kot blokirni gate za novičnik, dobi gate, ki nikoli ne blokira.
