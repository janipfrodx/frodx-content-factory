---
name: frodx-publish-send
description: Validate a finished FrodX content package and hand it to the publishing app. Runs the binary contract check, then either posts the package and image to the app ingest endpoint or, while that endpoint does not exist yet, writes the request body to outbox for review. Use as the last step of a content run, or when Igor says "pošlji", "daj v aplikacijo", "objavi to". Never sets the publish date - Igor picks that in the app.
metadata:
  version: 0.1.0
---

# Predaja paketa

Zadnji korak. Validira in preda.

## Postopek

1. Preberi `state.json`. Osveži `meta.exported_at` na trenutni čas v obliki `2026-08-10T09:00:00.000Z`.
2. Poženi gate:

```bash
python3 scripts/validate_package.py <pot-do-state.json>
```

Pot `scripts/validate_package.py` je relativna na mapo tega skilla (`plugins/content-factory/skills/frodx-publish-send/`); enako velja za `outbox/` v koraku 5 spodaj - nastane relativno na CWD ob zagonu ukaza.

**`outbox/` ne preživi seje - preverjeno 14.-15. 8. 2026.** V Cowork seji je CWD `/home/claude`, efemerni vsebnik. Zato ob dry-runu telo zahtevka **izpiši tudi v pogovor** (vsaj `package` brez slike, ki je velika), ne samo v `outbox/<slug>.json`. Datoteka, ki umre s sejo, ni predaja.

3. **Če gate pade (exit 1):** ne pošiljaj. Pokaži Igorju seznam kršitev in za vsako povej, kateri korak jo popravi:

   | Polje | Korak |
   |---|---|
   | `languages.*.content` | 2 (sl), 4 (en, hr) |
   | `languages.*.featured_image_alt` | 5 |
   | `slug`, `seo_title`, `meta_description`, `topic_cluster`, `campaign_name`, `tag_*` | 6 |
   | `social_posts` | 2 |
   | dolgi pomišljaj, prepovedana fraza, manjkajoč podpis | 2 (sl), 4 (en, hr) |

   Ne popravljaj polj sam. Vrni Igorja na pristojni korak.

   **Opozorilo o odprtih zadolžitvah - ne blokira, a ga ne preslišiš.** Gate poleg kršitev izpiše tudi vrstice `Opozorilo: odprte zadolžitve (N) - oddaja ni blokirana:` iz `_run.open_tasks`. Te ne vplivajo na exit code (Janijeva odločitev 17. 8. 2026: opozori, ne blokiraj), ampak:

   - vsako odprto zadolžitev **preberi Igorju na glas** - kaj je odprto, kdo je odgovoren, iz katerega koraka je;
   - vprašaj ga izrecno, ali paket kljub temu odda. Šele njegov »oddaj« je gate za korak 7;
   - če reče, naj počaka, ne pošiljaj in ne piši v `outbox/` - tek ostane na koraku 6;
   - zadolžitev iz `state.json` **ne brisi**, da bi bil izpis čist. Odstrani jo samo, ko človek potrdi, da je opravljena.

   Tipičen primer je hrvaščina brez native pregleda: gate je ne vidi (vsa polja so izpolnjena) in brez tega opozorila gre nepregledana v objavo.

4. **Če gate gre skozi (exit 0):** sestavi telo zahtevka.
   - `package` = `state.json` brez ključa `_run`
   - `featured_image` = `images/izbrana.png`, kodiran v base64, `mime_type` `image/png`, `filename` `<slug>.png`
   - `source` = `{run_slug, generated_at, author: "igor"}`

5. **Dry-run (trenutno stanje):** zapiši telo v `outbox/<slug>.json` in povej Igorju, da endpointa v aplikaciji še ni. Nastavi `_run.status` = `ready` in `_run.step` = `7`.

6. **Živo pošiljanje (ko endpoint obstaja):** pošlji

```
POST <URL aplikacije>/api/ingest
X-API-Key: <iz okoljske spremenljivke FRODX_APP_API_KEY>
Idempotency-Key: <UUID, enak za vse ponovne poskuse istega teka>
Content-Type: application/json
```

   Odgovori:

   | Status | Kaj narediš |
   |---|---|
   | 202 | povej Igorju, naj odpre aplikacijo in potrdi osnutek; `_run.status` = `sent`, `_run.step` = `7` |
   | 401 | napačen API ključ - povej Janiju, ne poskušaj znova |
   | 409 | ta tek je že poslan; ne pošiljaj znova |
   | 422 | aplikacija je zavrnila paket - pokaži njen seznam napak |

   Ob 409 nikoli ne generiraj novega `Idempotency-Key`, da bi »šlo skozi«. Podvojen ključ pomeni, da je paket že tam.

   **Znano stanje (preverjeno 2026-08-10):** produkcijski n8n workflow `PROD 2 - FrodX Content Publishing Pipeline` (`3lK6pjOfOAa0BxDm`) ima webhook `frodx-publish` z natanko tem kontraktom - HMAC podpis, `Idempotency-Key`, in vozlišče `Validate + Parse Content`, ki že bere obliko `{meta, universal, languages}`, kot jo sestavi ta skill. Kljub temu ta skill živega pošiljanja ne izvaja - to je Janijeva namerna odločitev, ne vrzel v znanju. Živo pošiljanje odklene Jani, ko preveri natančno ujemanje oblike paketa s `Validate + Parse Content`. Do takrat velja korak 5 (dry-run) kot edino dejansko vedenje tega skilla.

## Kaj ne delaš

- Ne nastavljaš `publish_at` ne `publish_date`. Datum in uro izbere Igor v aplikaciji.
- Ne pošiljaš paketa, ki ni prestal gatea, tudi če Igor reče, da je vseeno. Če vztraja, povej, katera kršitev bo v HubSpotu vidna, in naj se odloči po tem.
- Ne odstranjuješ polj, da bi paket prestal gate.
- Ne pošiljaš v živo, dokler Jani tega izrecno ne odklene, tudi če endpoint videti deluje.
