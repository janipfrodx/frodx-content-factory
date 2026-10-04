# n8n workflow cf-transkreacija-hr

HR transkreacija novičnika: GPT-6.1 Sol kot pisec in ločen pregled, največ 2 kroga popravka.

## Osnovno

- **ID workflowa:** `yerKUljx0ZsTTxvW`
- **URL:** https://frodxai.app.n8n.cloud/workflow/yerKUljx0ZsTTxvW
- **Projekt:** Content Factory (`FucXmQlDiWLVsRHW`), brez mape
- **Stanje:** neaktiven (ni objavljen); kliče se z `execute_workflow`, `executionMode: "manual"`
- **Webhook:** `POST`, path `cf-transkreacija-hr`, `responseMode: responseNode`, brez avtentikacije
- **Avtentikacija:** webhook je nima. Dokler je workflow neaktiven, produkcijski URL klicev ne sprejme in se kliče samo prek `execute_workflow`. Pred kakršnokoli aktivacijo ali objavo workflowa mora webhook dobiti avtentikacijo (npr. header auth); brez nje bi lahko vsak, ki pozna URL, porabljal klice Sola na naš račun.
- **Model:** `gpt-6.1-sol` (`@n8n/n8n-nodes-langchain.openAi` typeVersion 2.3, resource `text`, operation `response`)
- **Credential:** `openAiApi` `R57o8BoYHtoylkoX` (OpenAI API)
- **Napake OpenAI:** vseh šest OpenAI vozlišč ima `onError: continueRegularOutput`; `Razcleni`/`Odloci` napako zapišeta v `napaka`, izvedba se ne ustavi.
- **Ustvarjen:** 4. 10. 2026, različica `9b2353cf-042a-4466-972d-edb8014e92ca` ("Prva različica: pisec + pregled, največ 2 kroga popravka")

## Vozlišča (19)

```
Trigger (webhook)
 -> Prompti (Code)
 -> Vhod v redu? (IF naprej)
      false -> Odgovor
      true  -> Pisec 0 (OpenAI) -> Razcleni pisec 0 (Code) -> Pregled 0 (OpenAI) -> Odloci 0 (Code)
 -> Naprej 0? (IF naprej)
      false -> Odgovor
      true  -> Pisec 1 -> Razcleni pisec 1 -> Pregled 1 -> Odloci 1
 -> Naprej 1? (IF naprej)
      false -> Odgovor
      true  -> Pisec 2 -> Razcleni pisec 2 -> Pregled 2 -> Odloci 2 -> Odgovor
Odgovor (Code) -> Respond to Webhook (firstIncomingItem)
```

- Code (8): `Prompti`, `Razcleni pisec 0/1/2`, `Odloci 0/1/2`, `Odgovor`
- OpenAI (6): `Pisec 0/1/2` (system `$('Prompti').first().json.pisec_system`, user `$json.pisec_user`), `Pregled 0/1/2` (system `$('Prompti').first().json.pregled_system`, user `$json.pregled_user`)
- IF 2.3 (3): `Vhod v redu?`, `Naprej 0?`, `Naprej 1?`; pogoj `{{ $json.naprej }}` je boolean true (strict)
- Webhook 2.1 (`Trigger`), Respond to Webhook 1.5

Odgovor: `izid` (`PASS` | `UREDNIK` | `NAPAKA`), `krogi`, `blocks`, `review_reasons`, `pregled`, `prompt_fnv`, `napaka`.

## Kako nastane koda

JS vseh osmih Code vozlišč generira `tools/n8n_hr_sol.py` (`python3 tools/n8n_hr_sol.py <mapa>` zapiše 8 datotek `<ime vozlišča>.js`). Prompta pisca in pregleda se vgradita iz `veje/novicnik/vendor/igor-hr-sol/`; `Prompti` vrne njun FNV-1a (`prompt_fnv`), ki ga `hr_sol.py preveri_izid` primerja z vendorjem.

Ob ustvarjanju je bil jsCode vseh osmih vozlišč v n8n prebran nazaj in primerjan z izhodom generatorja (Python `==`): vseh 8 enakih. Sprememba prompta ali logike zahteva nov izhod generatorja in posodobitev workflowa z Janijevo odobritvijo.

## Živa preverba (4. 10. 2026)

| Izvedba | Vhod | izid | krogi | score | Čas | Vozlišča |
|---|---|---|---|---|---|---|
| `217298` | prazno telo `{}` | `NAPAKA` (`vhod brez source_blocks`) | 0 | - | 1,8 s | Trigger, Prompti, Vhod v redu?, Odgovor, Respond to Webhook; OpenAI ni tekel |
| `217299` | `docs/preizkus-prevajalca/2026-10-03-pisec-pregled/vhod_pisec_r0.json` (nadrejeni repo, izdaja 1. 10.) | `UREDNIK` | 2 | 96 (`PASS`) | 129,4 s | vseh 19; tekli so vsi trije krogi |

Obe izvedbi: `prompt_fnv` = `{"pisec": "e0b4683d", "pregled": "8553ec9f"}`.

Izvedba `217299` po krogih (OpenAI čas, žetoni vhod/izhod):

| Krog | Pisec | Pregled |
|---|---|---|
| 0 | 26,8 s, 6281/1306, `needs_review: false` | 20,5 s, 6465/980, `FAIL` 84, 2 blokirajoči |
| 1 | 22,4 s, 7402/1315, `needs_review: true` | 16,5 s, 6467/706, `FAIL` 84, 1 blokirajoča |
| 2 | 23,9 s, 7271/1408, `needs_review: true` | 9,1 s, 6470/340, `PASS` 96, 0 ugotovitev |

- `blocks`: `SUBJECT, PREHEADER, GREETING, HOOK, B1_TITLE, B1_BODY, B1_CTA, CLOSING` v tem vrstnem redu.
- Kroga 1 in 2 sta tekla, ker je pregled v krogih 0 in 1 vrnil `FAIL` 84 z blokirajočo ugotovitvijo za `SUBJECT` (v krogu 0 še ena za `HOOK`): zadeva govori o 12 milijonih Britancev, telo pa o 12 milijonih klicev na leto; neskladje je že v SI izvirniku.
- V krogu 2 je pisec zadevo uskladil s številom klicev ("12 milijonov Britancev" -> "Britanci 12 milijuna puta godišnje") in vrnil `needs_review: true` z enim vprašanjem v `review_reasons`: ali Igor potrjuje ta vsebinski popravek izvirnika. Pregled kroga 2 je dal `PASS` 96 brez ugotovitev. Izid je `UREDNIK` zaradi pisčevega vprašanja, ne zaradi pregleda.
- `hr_sol.py preveri_izid` na izidu: brez `NapakaIzida`, opozoril 0 (`[]`).
- Telo, ki ga je prejel `Trigger`, je enako `vhod_pisec_r0.json` (preverjeno s Pythonom `==`).
