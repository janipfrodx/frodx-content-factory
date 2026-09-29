# state.json veje novičnik - struktura stanja

`state.json` je od začetka telo `POST /api/drafts` Newsletter Huba (pogodba: `tests/fixtures/newsletter_draft_body.json` v repozitoriju) in blok `_run`. Vsak korak zapolni svojo rezino. Oddaja `_run` odstrani in pošlje ostalo.

Rezultat koraka se zapiše **takoj ob nastanku**, ne ob potrditvi (splošno pravilo debla).

## Paketni del

| Ključ | Kdo zapolni |
|---|---|
| `run_slug` | `init_run.py --veja novicnik` |
| `editions[]` `si` | korak 2 (`scripts/iz_editions.py`), korak 3 (`scripts/izdaja_besedilo.py vpis`) |
| `editions[]` `en`, `hr` | korak 4 (`scripts/iz_editions.py`, po preverbi prevoda `scripts/izdaja_besedilo.py vpis`) |
| `editions[].blocks[].image.file` | korak 2 (ime datoteke iz gradiva, če obstaja) |
| `editions[].blocks[].image.url`, `.alt` | korak 5 |

Paket nikoli ne nosi `send_datetime`, `timezone` ali kazala (TOC). Čas nastavi Igor v aplikaciji, časovni pas je v aplikaciji vedno `Europe/Ljubljana`.

## `_run` - samo za verigo

| Ključ | Pomen |
|---|---|
| `veja` | vedno `novicnik` |
| `slug` | ime teka, enako `run_slug` |
| `tema` | delovni naslov, iz katerega je nastal slug |
| `step` | zadnji dokončan korak, 0-6 |
| `status` | `awaiting_material`, `awaiting_approval`, `in_progress`, `sent` |
| `gradivo` | `[{vrsta, vrednost}]` iz koraka 1; `vrsta` je `url`, `webinar`, `novica` ali `slika` |
| `tip_izdaje` | tip izdaje po Igorjevem playbooku, iz koraka 1 |
| `gradivo_odlocitve` | Igorjeve odločitve iz gate-a koraka 1: `{bloki: [block_id po vrstnem redu], pain_link: <URL ali null>, opombe: <niz>}` |
| `approvals` | `{step1: <ISO čas>, ...}` |
| `critique_rounds` | koliko krogov kritike SI je bilo |
| `transcreation_check` | `{hr: {rounds, verdict, openai_error, gemini_error}, en: {...}}` iz koraka 4 |
| `transcreation_audit` | `{hr: {score, verdict, variant, traces, povrnjeno, report}, en: {...}}` iz koraka 4 - kot pri kolumni |
| `block_images` | `[{block_id, vir, url, razlog, kandidatke}]` iz koraka 5; `vir` je `prilozena`, `ponovna_raba`, `generirana` ali `brez` |
| `delivery` | `{status, draft_id, edit_url, delivered_at}` iz koraka 6 |
| `open_tasks` | odprte zadolžitve, ista pravila kot pri kolumni (`veje/kolumna/references/state-schema.md`) |
| `skill_versions` | verzije skillov, ki so tek obdelali |
