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

### Tabela petih izidov (razdelek 2 speca, kot ga implementira `Shape Response`)

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
  credentiala. Telo klica: `image_base64`, `filename`, `mime_type`. Na OpenAI
  veji sta `filename` in `mime_type` trdo zapisana (`openai.png` /
  `image/png` - preverjeno pravilno, glej spodaj). Na Gemini veji sta od
  popravnega kroga 1 (17. 9. 2026) **izpeljana**, ne trdo zapisana - glej
  razdelek "Gemini vrne JPEG, ne PNG" spodaj.

### Gemini vrne JPEG, ne PNG - popravek napačne oznake tipa datoteke (popravni krog 1, 17. 9. 2026)

Pregled je na datoteki iz izvedbe 204104 ugotovil, da vozlišče `Gemini Image`
dejansko vrača JPEG (magic bytes `ff d8 ff e0`, `file` ga prepozna kot
"JPEG image data, JFIF standard 1.01"), ne PNG. Brif naloge 2, korak 3, je za
Gemini vejo predpisal `filename = "gemini.png"` in `mime_type = "image/png"` -
to je bila napaka brifa, ne izvedbe: trdo zapisana vrednost, ki ni ustrezala
dejanski vsebini. OpenAI veja je bila preverjena in je pravilna - tam
`OpenAI Image` res vrača PNG (magic bytes `89 50 4e 47`).

Popravek: `Upload Gemini` zdaj `filename` in `mime_type` **izpelje iz dejanskih
metapodatkov binarnega polja `geminiImage`**, ne iz trdo zapisane vrednosti:

- `mime_type`: `={{ $("Gemini Image").item.binary.geminiImage.mimeType }}`
- `filename`: `={{ $("Gemini Image").item.binary.geminiImage.fileExtension ? ("gemini." + $("Gemini Image").item.binary.geminiImage.fileExtension) : ("gemini." + $("Gemini Image").item.binary.geminiImage.mimeType.split("/")[1]) }}`
  (če `fileExtension` ni nastavljen, se pripona izpelje iz podtipa `mimeType`)

To drži ne glede na to, kateri format Gemini v prihodnje vrne - vrednost sledi
dejanski vsebini, ne predpostavki. OpenAI veja ni bila spremenjena.

Popravek je bil preverjen **statično** (`get_workflow_details` po spremembi) -
nov plačljiv tek za to ni bil izveden in zanj ni bilo privolitve. Datoteka iz
izvedbe 204104 (`39c91efe-b7ed-4b26-872f-0fd62cb38e7d.png`) je v shrambi
aplikacije **ostala z napačno oznako** (`.png` ime in domnevno `image/png`
content-type, dejansko JPEG vsebina), ker je nastala pred tem popravkom -
popravek velja samo za bodoče teke, obstoječe datoteke se ne popravlja
retroaktivno.

### Trda rezerva na Gemini veji (popravni krog 2, 17. 9. 2026)

Izraza iz kroga 1 sta bila pravilna, a brez rezerve: če `geminiImage.mimeType`
ob teku ne bi bil nastavljen, bi se `mime_type` izpisal kot dobeseden niz
`"undefined"`, `filename` pa bi vrgel `TypeError` na `.split("/")` in podrl
Gemini vejo - huje od napake, ki jo je krog 1 odpravljal. Končna izraza:

- `mime_type`: `={{ ($("Gemini Image").item.binary.geminiImage || {}).mimeType || "image/jpeg" }}`
- `filename`: `={{ "gemini." + (($("Gemini Image").item.binary.geminiImage || {}).fileExtension || (($("Gemini Image").item.binary.geminiImage || {}).mimeType || "image/jpeg").split("/")[1]) }}`

Izpeljava ostaja prednostna; rezerva se uporabi samo, kadar izpeljava manjka.
Štirje primeri, prehojeni pri pregledu: `geminiImage` manjka -> `image/jpeg` /
`gemini.jpeg`; polji manjkata -> `image/jpeg` / `gemini.jpeg`; samo `mimeType`
(`image/png`) -> `image/png` / `gemini.png`; oboje -> `image/png` /
`gemini.png`. Nobeden ne vrže napake in nobeden ne da niza `"undefined"`.

Sintaksa `||` je potrjena posredno: `Normalize Input` v istem workflowu že
uporablja `?.` in `??`.

Tudi ta krog je preverjen **samo statično**. Prvi dovoljen plačljiv tek naj
potrdi, da Gemini datoteka pride v shrambo kot `gemini.jpg` ali `gemini.jpeg`
z `image/jpeg`.

### Rezerva za podtip brez poševnice (popravni krog 3, 17. 9. 2026)

Krog 2 je pokril manjkajoč `mimeType`, ne pa pokvarjenega. Če bi `mimeType` bil
nastavljen, a brez poševnice (na primer `imagejpeg`), bi `.split("/")[1]` vrnil
`undefined` in ime datoteke bi bilo `gemini.undefined`. Dodan je zadnji člen
verige, drugih sprememb ni:

- `filename`: `={{ "gemini." + (($("Gemini Image").item.binary.geminiImage || {}).fileExtension || (($("Gemini Image").item.binary.geminiImage || {}).mimeType || "image/jpeg").split("/")[1] || "jpeg") }}`

`mime_type` se **namenoma ne spreminja**. Pokvarjenega tipa ne smemo nadomestiti
z ugibanjem: aplikacija ga zavrne po svoji shemi (`^image/(png|jpe?g|webp|gif|avif)$`)
in napaka je glasna. Tiho popravljena vrednost bi pomenila datoteko, označeno
drugače, kot je njena vsebina - natanko napaka, ki jo je krog 1 odpravljal.

Sedem primerov, pognanih v `node` pred uveljavitvijo: `geminiImage` manjka,
prazen objekt, `fileExtension` `png`, samo `mimeType` `image/png`, `mimeType`
brez poševnice, `mimeType` `image/`, `mimeType` prazen niz. Izidi po vrsti:
`gemini.jpeg`, `gemini.jpeg`, `gemini.png`, `gemini.png`, `gemini.jpeg`,
`gemini.jpeg`, `gemini.jpeg`. Nikjer `undefined`, izpeljava ostaja prednostna.

Uveljavljeno prek `update_workflow` in preverjeno s ponovnim branjem workflowa:
`versionId` `b3b49843-03d3-41e6-bb14-232e9c54642d`, 11 vozlišč, `Upload OpenAI`
nedotaknjen (`openai.png` / `image/png`), credential `vS1Vj3wTuQUKF5WI` na mestu,
`active: false` nespremenjen. Tudi ta krog je preverjen **samo statično** - plačljiv
tek ni bil izveden.

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

## Prevzemni tek, 17. 9. 2026

Suhi tek naloge 8, korak 6. Brez plačljivih klicev; slika je bila vzeta iz
izvedbe 204104 slikovnega workflowa.

| Polje | Vrednost |
|---|---|
| `run_slug` | `2026-09-17-prevzemni-tek-predaje-17-9-2026` |
| `draft_id` | `57a9251a-d8ce-4ca3-aa28-c12d5498e977` |
| Izvedba `cf-deliver-draft` | 204313, `executionMode: manual` |
| Odgovor | `status: created`, `http_status: 201` |

Vsebina je bila `tests/fixtures/package_valid.json`, `_run` iz `init_run.py`.
Rubrika v `_run.image` je označena kot neopravljena - tek preizkuša pot, ne presoje.
`dimensions.gemini` nosi izmerjenih `1584x672` iz izvedbe 204104, ne vrednosti
iz brifa.

### Kaj je tek dokazal

- Gate prehaja na paketu z `meta.version` 1.2 in `_run.image.url` na lastni shrambi
  (`exit 0`).
- `run_slug` nosi datum: `2026-09-17-prevzemni-tek-predaje-17-9-2026`. Popravek
  `7f3aa08` je s tem preverjen v živo, ne le v testih.
- Predaja teče prek `execute_workflow` z `executionMode: manual`. **Workflowa ni
  treba aktivirati**; manualni klic ne gre skozi produkcijski webhook. Aktivacija
  ostane potrebna šele, kadar bo kdo klical webhook URL neposredno.
- Aplikacija je vrnila 201 in `edit_url`; vrstica je nastala s `status: new`.
- Jani je 17. 9. 2026 odprl `edit_url` in potrdil, da je čarovnik v redu.

### Kaj tek ni dokazal

Ne pokriva Igorjeve oddaje v `PROD 2` in ne nastanka članka. Zaprto bo šele, ko
en resničen tek pride od izbire teme do `edit_url`, Igor odda, in se vrstica
obrne na `dispatched` - brez ročnega prenosa katerekoli datoteke.

Testna vrstica je bila po preverjanju zbrisana;
`select count(*) from content_drafts where run_slug like '%prevzemni-tek%'`
je vrnil `0`.

## Prvi resnični tek skozi Cowork, 17. 9. 2026

Jani je pognal celotno verigo v Coworku, od teme do predaje, s pluginom 0.4.0
in objavljeno aplikacijo (commit `6491619`).

| Polje | Vrednost |
|---|---|
| `run_slug` | `2026-09-17-hubspot-ali-salesforce-za-srednje-veliko-b2b-podjetje-v-sloveniji-napacno` |
| `draft_id` | `fea85c31-06f4-460b-aac6-38d777524edb` |
| Izvedba `cf-deliver-draft` | 204412, `executionMode: manual`, 15:02:03-15:02:06 UTC |
| Odgovor | `status: created`, `http_status: 201` |
| Vrstica | `status: new`, `featured_image_url` na `umvjwjzdrtamfrcqhopa.supabase.co` |

Preverjeno v vrstici, ne v paketu na disku:

- `meta.version` je `1.2`.
- Trije jeziki, trije socialni zapisi.
- `campaign_name` je `Interest - Prodaja in lead management`; predpona `Blog - `
  se ni pojavila nikjer.
- Tag ID-ji se ujemajo s `hubspot-taxonomy.md` znak za znak: `sl` 209208755742,
  `en` 110457313457, `hr` 109956645711.
- SEO naslov je napisala veriga (`HubSpot ali Salesforce: prava primerjava za
  B2B prodajo`), aplikacija ga ni generirala - to je pravilo v1.2 v praksi.

S tem je zaprto vprašanje iz prevzemnega teka glede poti Cowork → aplikacija.
Odprt ostane zadnji člen: Igorjeva oddaja iz čarovnika v `PROD 2` in nastanek
članka. Vrstica danes stoji na `status: new`.
