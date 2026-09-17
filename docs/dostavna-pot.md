# Dostavna pot: ID-ji in pogodbe

## `cf-deliver-draft`

- workflowId: `9jbBZ832E6NquY4I`
- n8n projekt: Content Factory (`FucXmQlDiWLVsRHW`)
- webhook pot (Trigger, `n8n-nodes-base.webhook`): `POST /webhook/cf-deliver-draft`
  - produkcijski URL: `https://frodxai.app.n8n.cloud/webhook/cf-deliver-draft`
  - testni URL: `https://frodxai.app.n8n.cloud/webhook-test/cf-deliver-draft`
- vozlišča (zaporedno): `Trigger` (webhook) -> `Create Draft` (httpRequest, POST na
  `https://frodx-content-app.lovable.app/api/drafts`) -> `Shape Response` (code) ->
  `Respond to Webhook`
- `Create Draft` uporablja predefiniran credential tipa Header Auth
  `FrodX Content App Ingest` (id `vS1Vj3wTuQUKF5WI`); `options.response.response.fullResponse`
  in `neverError` sta vklopljena, `onError` na nodu je `continueRegularOutput` - `409` in `400`
  sta veljavna izida, ne napaka.

### Tabela štirih izidov (razdelek 2 speca, kot ga implementira `Shape Response`)

| http_status aplikacije | status  |
|---|---|
| 201 | created |
| 409 | duplicate |
| 400 | rejected |
| 401 | misconfigured |
| 503 | misconfigured |
| 502 | retry |
| karkoli drugo | retry |

Odgovor navzgor (na `Respond to Webhook`) vedno vsebuje:
`status`, `http_status`, `draft_id`, `edit_url`, `detail`, `error`.

## `Generiraj sliko (Content Factory)`

- workflowId: `lHc3NdejxehMyc9O`
- webhook pot: `generate-image`
  - produkcijski URL: `https://frodxai.app.n8n.cloud/webhook/generate-image`
  - testni URL: `https://frodxai.app.n8n.cloud/webhook-test/generate-image`
- `Trigger.responseMode` = `responseNode` (prej `lastNode`) - potrebno, ker imata
  dve vzporedni veji (OpenAI, Gemini) vsaka svoj rezultat; `lastNode` bi tiho
  vrnil samo enega.
- vozlišča (zaporedno): `Trigger` -> `Normalize Input` -> razveji na `OpenAI Image`
  in `Gemini Image` -> `Extract OpenAI b64` / `Extract Gemini b64`
  (`extractFromFile`, `operation: binaryToPropery`) -> `Upload OpenAI` /
  `Upload Gemini` (httpRequest, POST na `https://frodx-content-app.lovable.app/api/images`)
  -> `Merge` (`mode: append`, dva vhoda) -> `Shape URLs` (code) ->
  `Respond to Webhook`.
- obvod, ki je pomanjševal sliki (`Shrink OpenAI`, `Shrink Gemini`, `B64 OpenAI`,
  `B64 Gemini` - 640x640 `maximumArea`, JPEG q60), je odstranjen. Prav ta obvod je
  14. 9. 2026 povzročil oddajo predogleda 784x522 namesto polne slike.
- `binaryPropertyName` se med vejama razlikuje in se ne poenoti: `data` na OpenAI
  veji, `geminiImage` na Gemini veji (OpenAI Image piše v `data`, Gemini Image ima
  `options.binaryPropertyOutput = "geminiImage"`).
- `Upload OpenAI` in `Upload Gemini` uporabljata predefiniran credential tipa
  Header Auth `FrodX Content App Ingest` (id `vS1Vj3wTuQUKF5WI`); v parametrih
  vozlišč ni nobene vrednosti ključa - avtentikacija gre izključno prek
  credentiala. Telo klica: `image_base64`, `filename` (`openai.png` /
  `gemini.png`), `mime_type` (`image/png`).

### Oblika odgovora webhooka `generate-image`

```json
{"openai": {"url": "<https URL>"}, "gemini": {"url": "<https URL>"}}
```

### Vrstni red vhodov v `Merge` (pomembno za `Shape URLs`)

Veja **OpenAI je vezana na prvi vhod** vozlišča `Merge` (`index 0`), veja
**Gemini na drugega** (`index 1`). To je bilo potrjeno tudi z dejanskim tekom:
`Upload OpenAI` je vrnil prvi URL, `Upload Gemini` drugega. `Shape URLs` bere
`items[0]` kot OpenAI in `items[1]` kot Gemini - to je pravilno, dokler ta
vrstni red vhodov ostane nespremenjen.

### Razmerje stranic pri `Gemini Image`

Shema vozlišča `@n8n/n8n-nodes-langchain.googleGemini` (`resource: image`,
`operation: generate`) parametra za razmerje stranic ne pozna - `options` ima
samo `sampleCount` (samo za Imagen modele) in `binaryPropertyOutput`. Edino
sredstvo za vplivanje na razmerje je besedilo prompta (`prompt_gemini`).

V teku, opisanem spodaj, je Gemini vrnil razmerje 2,36:1 (1584x672) namesto
pričakovanega ~1,9:1 - to pojasnjuje, zakaj je izmerjena širina precej večja od
zahtevane pri enaki (dovolj visoki) višini. Merilo koraka 8 (vsaj 1200x630) je
kljub temu doseženo.

### Preizkus 17. 9. 2026 - execution 204104

`execute_workflow`, `executionMode: manual`, vhod (webhook body) natanko po
brifu: `prompt_openai`, `prompt_gemini` (enak opisni prompt konferenčne sobe
brez besedila in logotipov), `size: "1536x1024"`.

- status: `success`
- čas: 2026-09-17 08:47:42 -> 08:48:53 UTC (71 s)

Dobesedni odgovor vozlišča `Respond to Webhook`:

```json
{"openai": {"url": "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/0618294a-bda8-48a6-8626-0c87b695bfc2.png"},
 "gemini": {"url": "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/39c91efe-b7ed-4b26-872f-0fd62cb38e7d.png"}}
```

Preneseni sliki (`curl` v `/tmp`, ne v repozitorij) in dobesedni izhod
`plugins/content-factory/skills/frodx-publish-send/scripts/dimenzije.py`:

```
/tmp/openai.png: 1536x1024
/tmp/gemini.png: 1584x672
exit: 0
```

Velikosti datotek: openai 3 263 566 bajtov, gemini 915 132 bajtov. Obe sliki sta
vsaj 1200x630; OpenAI je vrnil točno zahtevanih 1536x1024.

### Ugotovitve za naslednje naloge

- `update_workflow` samodejnega dodeljevanja credentialov za vozlišča tipa
  `httpRequest` ne opravi (vrne opozorilo "skipped during credential
  auto-assignment"). Credential je treba pripeti z ločenim klicem
  (`setNodeCredential`) in nato preveriti z `get_workflow_details`, da je res
  pripet.
- veja `Upload OpenAI` je na prvem vhodu `Merge` (`index 0`), veja
  `Upload Gemini` na drugem (`index 1`) - glej razdelek zgoraj.

### Popravek brifa (netočnost F10)

Brif naloge 2, korak 7, predpisuje vhod oblike
`inputs: {"type": "webhook", "webhookData": {...}}`. Shema orodja
`execute_workflow` polja `type` ne pozna in poleg tega zahteva `triggerNodeName`,
kadar so `inputs` podani. Delujoča oblika je:

```
triggerNodeName: "Trigger"
inputs: { "webhookData": { "method": "POST", "body": { ... } } }
```

## Skrivnost

`INGEST_API_KEY` živi izključno v n8n credentialu `FrodX Content App Ingest`
(id `vS1Vj3wTuQUKF5WI`, tip `httpHeaderAuth`, domači projekt Content Factory).
Ne sme priti v noben skill, commit ali pogovor. V to datoteko ni zapisana nobena
vrednost skrivnosti.

## Preverbe (16. 9. 2026)

Preizkušeno prek `execute_workflow` (executionMode `manual`) na živi produkciji
`frodx-content-app.lovable.app`, ne na lokalnem mocku.

**Opomba glede vsebine testa:** `tests/fixtures/package_valid.json` ima
`meta.version` = `"1.1"`, medtem ko aplikacija po specifikaciji privzema `"1.2"`.
To ni napaka te naloge - fixture datoteka ni bila spremenjena. Za spodnja dva
preizkusa (koraka 6 in 7) je bila v **telesu klica** (ne v fixture datoteki)
vrednost `meta.version` dvignjena na `"1.2"`, preostala vsebina fixtura pa je
ostala nespremenjena in v celoti (brez krajšanja).

**Izmerjeno dejstvo (dodaten preizkus, 16. 9. 2026):** aplikacija je bila nato
preizkušena tudi z `meta.version` = `"1.1"` - dobesedno tako, kot je v
`tests/fixtures/package_valid.json` - z enako preostalo vsebino in svežim
`run_slug` = `test-verzija-11-2026-09-16` (execution 203624). Odgovor:

```json
{
  "status": "created",
  "http_status": 201,
  "draft_id": "373be62f-8f8c-40ff-9e25-9d7c57d9fbf4",
  "edit_url": "https://frodx-content-app.lovable.app/draft/373be62f-8f8c-40ff-9e25-9d7c57d9fbf4",
  "detail": null,
  "error": null
}
```

Aplikacija je torej `"1.1"` sprejela (`created`/`201`), ne zavrnila. Zod shema na
strani aplikacije `meta.version` = `"1.1"` ne zavrača - dvig verige na `"1.2"` ni
nujen zaradi tega polja. Testna vrstica (`run_slug = 'test-verzija-11-2026-09-16'`)
je bila zbrisana takoj po preizkusu; `select count(*) from content_drafts;` je
vrnil `0`. Ta ugotovitev je vhod za nalogo 3, korak 7 (odločitev o dvigu sheme
verige na `1.2`).

### Korak 6 - prvi klic, pričakovan `created`

Telo: `content` = celotna vsebina `package_valid.json` (s popravljenim
`meta.version` = `"1.2"`), `featured_image_url` =
`https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/3ce803d7-1b09-47f0-926d-0600d45a9e72.png`,
`run_slug` = `test-predaje-2026-09-16`.

Dobesedni odgovor (execution 203618):

```json
{
  "status": "created",
  "http_status": 201,
  "draft_id": "dedfb831-2dd3-4eb0-95de-2e2a139feaa4",
  "edit_url": "https://frodx-content-app.lovable.app/draft/dedfb831-2dd3-4eb0-95de-2e2a139feaa4",
  "detail": null,
  "error": null
}
```

### Korak 7 - ponovljen klic z enakim telesom, pričakovan `duplicate`

Dobesedni odgovor (execution 203619):

```json
{
  "status": "duplicate",
  "http_status": 409,
  "draft_id": "dedfb831-2dd3-4eb0-95de-2e2a139feaa4",
  "edit_url": "https://frodx-content-app.lovable.app/draft/dedfb831-2dd3-4eb0-95de-2e2a139feaa4",
  "detail": null,
  "error": "duplicate"
}
```

Isti `draft_id` v obeh klicih dokazuje, da idempotenco nosi `UNIQUE (run_slug)`
v bazi in da ponovitev ni ustvarila drugega osnutka.

Testna vrstica (`run_slug = 'test-predaje-2026-09-16'`) je bila po preizkusu
zbrisana; `select count(*) from content_drafts;` je po brisanju vrnil `0`.
