---
name: frodx-publish-send
description: Validate a finished FrodX content package and hand it to the right app. A column goes through the binary contract check and the n8n workflow cf-deliver-draft into the publishing app; a newsletter edition goes through its branch check and the n8n workflow cf-deliver-newsletter into Newsletter Hub. Both return an edit link for Igor. Use as the last step of a content run, or when Igor says "pošlji", "daj v aplikacijo", "objavi to". Never sets the publish or send date - Igor picks that in the app.
metadata:
  version: 0.4.0
---

# Predaja paketa

Postopek spodaj je za kolumno. Novičnik ima svoj razdelek »Veja novičnik«.

Zadnji korak. Validira in preda.

## Postopek

1. Preberi `state.json`. Osveži `meta.exported_at` na trenutni čas v obliki `2026-08-10T09:00:00.000Z`.
2. Poženi gate:

```bash
python3 scripts/validate_package.py <pot-do-state.json>
```

Pot `scripts/validate_package.py` je relativna na mapo tega skilla (`plugins/content-factory/skills/frodx-publish-send/`); enako velja za `outbox/` v koraku 6 spodaj - nastane relativno na CWD ob zagonu ukaza.

**`outbox/` ne preživi seje - preverjeno 14.-15. 8. 2026.** V Cowork seji je CWD `/home/claude`, efemerni vsebnik. Zato telo predaje **izpiši tudi v pogovor** (vsaj `content` brez slike, ki je velika), ne samo v `outbox/<slug>.json`. Datoteka, ki umre s sejo, ni predaja; predaja gre prek `cf-deliver-draft` v koraku 5.

3. **Če gate pade (exit 1):** ne pošiljaj. Pokaži Igorju seznam kršitev in za vsako povej, kateri korak jo popravi:

   | Polje | Korak |
   |---|---|
   | `languages.*.content` | 2 (sl), 4 (en, hr) |
   | `languages.*.featured_image_alt` | 5 |
   | `_run.image.url` | 5 |
   | `slug`, `seo_title`, `meta_description`, `topic_cluster`, `campaign_name`, `tag_*` | 6 |
   | `social_posts[*].text` | 2 |
   | `social_posts[*].image_url`, `social_posts[*].image_alt` | 5 (faza B) |
   | `meta.version` | 1 - `init_run.py` jo zapiše; če ni `1.2`, je tek nastal s staro verzijo skilla |
   | dolgi pomišljaj, prepovedana fraza, manjkajoč podpis | 2 (sl), 4 (en, hr) |

   Ne popravljaj polj sam. Vrni Igorja na pristojni korak.

   **Opozorilo o odprtih zadolžitvah - ne blokira, a ga ne preslišiš.** Gate poleg kršitev izpiše tudi vrstice `Opozorilo: odprte zadolžitve (N) - oddaja ni blokirana:` iz `_run.open_tasks`. Te ne vplivajo na exit code (Janijeva odločitev 17. 8. 2026: opozori, ne blokiraj), ampak:

   - vsako odprto zadolžitev **preberi Igorju na glas** - kaj je odprto, kdo je odgovoren, iz katerega koraka je;
   - vprašaj ga izrecno, ali paket kljub temu odda. Šele njegov »oddaj« je gate za korak 7;
   - če reče, naj počaka, ne pošiljaj in ne piši v `outbox/` - tek ostane na koraku 6;
   - zadolžitev iz `state.json` **ne brisi**, da bi bil izpis čist. Odstrani jo samo, ko človek potrdi, da je opravljena.

   Tipičen primer je hrvaščina brez native pregleda: gate je ne vidi (vsa polja so izpolnjena), prevod je sicer strojno pregledan v koraku 4 (`frodx-transcreation-check`), a brez tega opozorila gre v objavo, ne da bi ga videl native govorec hrvaščine.

   **Opozorilo o manjkajočem auditu** (`Opozorilo: korak 4: audit transkreacije ni opravljen za ...`) prav tako ne blokira (Janijeva odločitev 29. 9. 2026). Po Igorjevem pravilu prevod brez audita ni pripravljen za objavo - preberi ga Igorju na glas in vprašaj, ali oddaja kljub temu.

4. **Če gate gre skozi (exit 0):** sestavi telo predaje.

   - `content` = `state.json` **brez ključa `_run`**
   - `featured_image_url` = `_run.image.url`, ki ga je zapisal korak 5
   - `run_slug` = `_run.slug`

   Slike ne kodiraš in ne pošiljaš. Naložil jo je slikovni workflow; ti nosiš samo njen URL.

5. **Predaj prek `cf-deliver-draft`.** Ključa do aplikacije nimaš in ga ne potrebuješ; nosi ga n8n credential. Kliči `execute_workflow` z gnezdenim telesom:

   ```json
   {
     "workflowId": "9jbBZ832E6NquY4I",
     "executionMode": "manual",
     "triggerNodeName": "Trigger",
     "inputs": {
       "webhookData": {
         "method": "POST",
         "body": {
           "content": {},
           "featured_image_url": "",
           "run_slug": ""
         }
       }
     }
   }
   ```

   Odgovor ima vedno isto obliko, ne glede na izid:

   | `status` | Kaj narediš |
   |---|---|
   | `created` | zapiši `draft_id` in `edit_url`; povej Igorju, naj odpre povezavo, preveri sliko in nastavi datume |
   | `duplicate` | ta tek je že predan. To **ni napaka.** Povej Igorju isti `edit_url` in ne pošiljaj znova |
   | `rejected` | aplikacija je paket zavrnila. Izpiši `detail` - to so zod očitki po polju. Popravi, kar očitek imenuje, in poskusi znova |
   | `misconfigured` | ključ ali skrivnost v aplikaciji nista v redu. Ustavi se in povej Janiju. Ne poskušaj znova in ne obhajaj poti |
   | `retry` | en sam ponovni poskus. Če tudi ta ne uspe, se ustavi in povej, kaj je vrnil |

6. **Zapiši izid.** V `state.json`:

   - `_run.delivery` = `{"status": "<created ali duplicate>", "draft_id": "<uuid>", "edit_url": "<povezava>", "delivered_at": "<ISO čas>"}`
   - `_run.status` = `sent`, `_run.step` = `7`

   Telo predaje zapiši tudi v `outbox/<slug>.json` in ga izpiši v pogovor. To ni več pot predaje, ampak zapis poslanega - edini, ki ga človek vidi, če predaja pade. Velja še naprej, da `outbox/` seje ne preživi.

## Veja novičnik

Preverba paketa in n8n workflow sta stvar veje. Za novičnik (`frodx-content-factory/veje/novicnik/`, poti relativne na mapo debla):

1. **Preverba.**

   ```bash
   python3 veje/novicnik/scripts/preveri_paket.py <state.json> --telo outbox/<run_slug>.json
   ```

   Skripta odstrani `_run`, preveri telo in ga zapiše v `outbox/` samo, če kršitev ni. Ob kršitvah (exit 1) ne pošiljaj: pokaži Igorju vrstice `KRŠITEV:` in za vsako povej pristojni korak, ki ga skripta navede. Sicer Igorju v enem sporočilu pokaži vrstice `Opozorilo:` (blok brez slike, manjkajoč audit), odprte zadolžitve iz `_run.open_tasks`, prebrane na glas kot pri kolumni, in vprašaj »Oddam?«. Njegov odgovor je potrditev za oddajo. Ne sprašuj drugič.

2. **Oddaja** prek `cf-deliver-newsletter`. Telo je vsebina datoteke iz točke 1 (paket brez `_run`, brez `send_datetime`):

   ```json
   {
     "workflowId": "Wd1gVtK77b29ePrJ",
     "executionMode": "manual",
     "triggerNodeName": "Trigger",
     "inputs": {
       "webhookData": {
         "method": "POST",
         "body": {"run_slug": "", "editions": []}
       }
     }
   }
   ```

   Workflow je neaktiven in ostane tak. Klic `manual` ga ne izpostavi javno. Ključa do Newsletter Huba nimaš in ga ne potrebuješ; nosi ga n8n credential.

3. **Odgovor:**

   | `status` | Kaj narediš |
   |---|---|
   | `created` | `_run.delivery` = `{status, draft_id, edit_url, delivered_at}`, `_run.status = sent`, `_run.step = 6`. Igorju napiši: »Osnutek je v Hubu: `<edit_url>`. Tam (1) pri blokih `<seznam blokov brez slike>` dodaj sliko z gumbom pri bloku, (2) nastavi čas, (3) klikni »Razporedi«. Šele »Razporedi« ustvari maile v HubSpotu.« Če so vsi bloki s sliko, točko (1) izpusti |
   | `duplicate` | ta tek je že oddan. Zapiši isti `draft_id` in Igorju daj `edit_url` z opombo, da osnutek že obstaja in se ni spremenil |
   | `rejected` | izpiši `detail` (očitki po polju). Ne poskušaj znova samodejno; vrni Igorja na pristojni korak |
   | `misconfigured` | ustavi se in povej Janiju. Ne poskušaj znova |
   | `retry` | ne poskušaj znova samodejno. Povej, kaj je vrnil, in vprašaj |

4. **Telo oddaje izpiši tudi v pogovor**, ker `outbox/` ne preživi seje.

Pri novičniku nikoli ne nastaviš `send_datetime` in v aplikaciji nikoli ne pritisneš »Razporedi«. Oboje je Igorjevo.

Ne ustvarjaš in ne kloniraš mailov v HubSpotu, tudi če Igor reče, da mu je vseeno kako. Hub osnutek in HubSpot mail bi bila dva izvora iste izdaje, kar pomeni tveganje dvojnega pošiljanja (tek 1. 10. 2026). Napoti ga na Hub.

## Kaj ne delaš

- Ne nastavljaš `publish_at` ne `publish_date`. Datum in uro izbere Igor v aplikaciji.
- Ne pošiljaš paketa, ki ni prestal gatea, tudi če Igor reče, da je vseeno. Če vztraja, povej, katera kršitev bo v HubSpotu vidna, in naj se odloči po tem.
- Ne odstranjuješ polj, da bi paket prestal gate.
- Ne sestavljaš base64 in ne pošiljaš bajtov slike. Aplikacija sprejme samo URL.
- Ne generiraš novega `run_slug`, da bi `duplicate` »šel skozi«. Podvojen slug pomeni, da je osnutek že tam.
- Ne kličeš `/api/drafts` neposredno in ne iščeš `INGEST_API_KEY`. Ključ je v n8n in tam ostane.
