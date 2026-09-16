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
