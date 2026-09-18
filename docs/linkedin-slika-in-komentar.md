# LinkedIn: slika na objavi, link v prvem komentarju

Delo poteka v kopiji `ccAcIxMOEKlWkbg7` (`PROD - FrodX Content Publishing Pipeline copy`).
Produkcija je `3lK6pjOfOAa0BxDm` (`PROD - FrodX Content Publishing Pipeline`) - **ID je merodajen**,
starejši dokumenti v tem repozitoriju jo imenujejo »PROD 2«.

## Varnostno stanje kopije

Urejeno 18. 9. 2026. Pred tem je bila kopija čist klon produkcije in bi ob aktivaciji objavljala na
prave račune.

| Kaj | Stanje |
|---|---|
| `Daily 7:30 Publish Check` | onemogočen |
| 26 Telegram vozlišč | `chatId` preusmerjen z `-5299932503` (Igorjeva skupina) na `8773374711` (zasebni chat Jani + bot) |
| `Telegram Callback Trigger` | ostaja omogočen, ker se prek njega poganja ročni test |
| `Post LinkedIn Company` | onemogočen do živega testa |
| `LI Setup - Create Post via HTTP` | onemogočen do živega testa |
| `Facebook Graph API` | onemogočen - ta načrt Facebooka ne spreminja |
| data tabele | prevezane na `TEST-FrodX-Pipeline`, `TEST-FrodX-Social-Posts`, `TEST-FrodX-Idempotency` |
| 14 HubSpot pisalnih vozlišč (spodaj) | onemogočena |
| `active` | `false`, `triggerCount: 0` |

**Kopije se ne aktivira nikoli.** Bot `FrodXContentPublisher` ima en sam registriran webhook in ta
pripada produkciji. Aktivacija kopije bi ga prevzela in Igorjeve potrditve gumbov bi obtičale.

Iz istega razloga se v testnih sporočilih **ne pritiska inline gumbov**: pritisk pošlje
`callback_query` na produkcijski webhook z `run_id`, ki ga produkcija ne pozna. Odobritev se
simulira z ročnim tekom od `Telegram Callback Trigger` s pripeto vsebino.

Pot webhooka se s produkcijo ne prekriva: n8n je ob podvojitvi dal nov UUID.

## HubSpot: onemogočena pisalna vozlišča (dopolnjeno 18. 9. 2026)

Neodvisen pregled je odkril, da so poleg LinkedIn/Facebook v kopiji ostala omogočena tudi vsa
vozlišča, ki pišejo v pravi produkcijski HubSpot portal prek `api.hubapi.com`. Isti razred tveganja
kot objavna vozlišča - poln ročni tek bi na produkcijskem portalu ustvaril, planiral ali izbrisal
resnične blog zapise. Vseh 14 je zdaj `disabled: true`:

| Vozlišče | Endpoint | Metoda |
|---|---|---|
| `Schedule SL HubSpot Post` | `/cms/blogs/2026-03/posts/schedule` | POST |
| `Schedule EN HubSpot Post` | `/cms/blogs/2026-03/posts/schedule` | POST |
| `Schedule HR HubSpot Post` | `/cms/blogs/2026-03/posts/schedule` | POST |
| `Create SL HubSpot Draft` | `/cms/v3/blogs/posts` | POST |
| `Create EN HubSpot Variation` | `/cms/v3/blogs/posts/multi-language/create-language-variation` | POST |
| `Update EN HubSpot Variation` | `/cms/v3/blogs/posts/{id}` | PATCH |
| `Create HR HubSpot Variation` | `/cms/v3/blogs/posts/multi-language/create-language-variation` | POST |
| `Update HR HubSpot Variation` | `/cms/v3/blogs/posts/{id}` | PATCH |
| `Upload Featured Image to HubSpot` | `/files/v3/files` | POST |
| `Update SL with InstantFeedback` | `/cms/v3/blogs/posts/{id}` | PATCH |
| `Update HR with InstantFeedback` | `/cms/v3/blogs/posts/{id}` | PATCH |
| `Delete HubSpot Drafts (SL)` | `/cms/v3/blogs/posts/{id}` | DELETE |
| `Delete HubSpot Drafts (EN)` | `/cms/v3/blogs/posts/{id}` | DELETE |
| `Delete HubSpot Drafts (HR)` | `/cms/v3/blogs/posts/{id}` | DELETE |

`Download Featured Image` (GET, dinamični URL) ostaja omogočen - samo bere/prenaša datoteko, ne
spreminja stanja na noben produkcijski sistem.

Preverjenih je bilo vseh 17 vozlišč tipa `httpRequest` v kopiji; edina gostitelja sta
`api.hubapi.com` in `api.linkedin.com` (slednji je onemogočen že v prvotni varnostni pripravi).

**Popravek (18. 9. 2026):** zgornji pregled po URL-ju spregleda dedicirane tipe vozlišč, ki nimajo
polja `url`. Preverjeno je bilo zato tudi po **tipih** vseh 105 vozlišč kopije: edini dedicirani tip,
ki piše navzven mimo `httpRequest`, je `n8n-nodes-base.facebookGraphApi` - eno vozlišče, `Facebook
Graph API`, in je `disabled: true`. Preostali tipi v kopiji (`dataTable`, `telegram`, `code`,
`respondToWebhook`, `if`, `switch`, `webhook`, `telegramTrigger`, `scheduleTrigger`, `stickyNote`) ne
pišejo v zunanje produkcijske sisteme. Noben drug zunanji ponudnik v kopiji ne piše v produkcijo.

**Posledica za poznejše naloge:** ker so vsa HubSpot pisalna vozlišča onemogočena, poln ročni tek od
`Telegram Callback Trigger` naprej ne bo dobil pravega odgovora HubSpot API-ja na tej točki (ne bo
ustvarjenega osnutka, ne bo `id`-ja objave, ne bo planiranja). Izhod teh vozlišč je treba simulirati
s pripeto vsebino (`prepare_workflow_pin_data`), enako kot je za LinkedIn/Facebook objavo že
predvideno v prejšnjem razdelku - sicer se veriga po teh vozliščih prekine, ker naslednji koraki
pričakujejo polja iz HubSpot odgovora (npr. `id` objave).

## Pot slikovnih polj

`content.social_posts[].image_url` in `.image_alt` prideta iz paketa in potujeta:

`Prepare Pipeline Row` (v `social_posts_json`) → `Create Platform Posts` (v vse tri kanalske
vrstice) → `TEST-FrodX-Social-Posts` (dva nova stolpca) → objavno vozlišče.

Manjkajoči polji postaneta prazna niza, ne `undefined`. Star paket in ročni docx uvoz zato še naprej
tečeta, samo brez slike.

Facebookova vrstica polji dobi, a ju ta krog ne uporabi.

## LinkedIn stran

Urejeno 18. 9. 2026 (Task 3). Objava na strani FrodX zdaj nosi sliko namesto kartice članka in
zajame URN objave za komentar iz Task 4.

### Ugotovitev iz Step 1 (živa dokumentacija proti briefu)

Preverjeno z `WebFetch` proti uradni LinkedIn/Microsoft Learn dokumentaciji (`images-api` in
`posts-api`, oba z `defaultMoniker: li-lms-2026-09`, kar potrjuje da je `LinkedIn-Version: 202606`
med podprtimi verzijami - je v seznamu monikerjev). **Oblike iz briefa se ujemajo z živo
dokumentacijo dobesedno**, brez razlik:

- `POST /rest/images?action=initializeUpload` z `{"initializeUploadRequest": {"owner": "urn:li:organization:..."}}`
  vrne `{"value": {"uploadUrl": "...", "image": "urn:li:image:..."}}` - identično briefu.
- `POST /rest/posts` s `content.media` v obliki `{"id": "urn:li:image:...", "altText": "..."}` -
  identično briefu (vrstni red polj v JSON-u ni pomemben).
- Uspešna objava vrne `201 Created`, URN pa pride v odgovoru **v glavi `x-restli-id`**, ne v telesu -
  identično briefu.

**Eno odstopanje, ki ga je vredno zabeležiti**, ker ni šlo v prid briefu po sreči, ampak je bilo
preverjeno: uradna stran za Images API pri koraku »Upload the Image« kaže na dokumentacijo
**opuščenega** Assets API (`vector-asset-api`), ki za nalaganje slike (ne videa) zahteva
`Authorization: Bearer` glavo na PUT klicu - to je nasprotno od tega, kar predpisuje brief
(»brez credentiala, `uploadUrl` je podpisan«). To je zastarel navzkrižni sklic v uradni
dokumentaciji, ne veljavno navodilo za novi Images API: trije neodvisni praktični viri iz leta 2026
(vključno z razčlenjenim vodičem za Node.js integracijo) eksplicitno navajajo, da PUT na `uploadUrl`
iz **Images API** (`/rest/images`, ne `/v2/assets`) ne sme nositi `Authorization` glave, ker gre za
podpisan URL. Implementirano je po briefu (brez credentiala), kar se ujema z novejšim mehanizmom, ne
s starim navzkrižnim sklicem.

### Veriga vozlišč (po vrsti)

```
Route by Platform (linkedin_company)
  → LI Co - Init Image Upload       (POST /rest/images?action=initializeUpload)
  → LI Co - Fetch Image Bytes       (GET image_url iz vrstice, responseFormat: file)
  → LI Co - Upload Image Bytes      (PUT na uploadUrl, telo = binarni podatek, brez credentiala)
  → Post LinkedIn Company           (POST /rest/posts, content.media, fullResponse: true)
      ├─ (uspeh) → LI Co - Store Post URN   (zapiše platform_post_id, ustavi tek če je prazen)
      │              → Delete Published LI Co
      └─ (napaka) → Telegram LI Co Post Failure   (nespremenjeno)
```

Vseh pet vozlišč (štiri nova plus predelan `Post LinkedIn Company`) je `disabled: true`. Brisanje
vrstice (`Delete Published LI Co`) se je premaknilo za `LI Co - Store Post URN`, da URN pride v
vrstico, preden se ta izbriše - prej je vrstica izginila takoj po objavi.

### Telo zahtevka, kot je dejansko napisano

`LI Co - Init Image Upload` (telo je statično, brez izraza):

```json
{"initializeUploadRequest": {"owner": "urn:li:organization:1132284"}}
```

`Post LinkedIn Company` (telo, `options.response.fullResponse: true`):

```
={{ ({
  author: "urn:li:organization:1132284",
  commentary: $("Route by Platform").item.json.post_text,
  visibility: "PUBLIC",
  distribution: { feedDistribution: "MAIN_FEED", targetEntities: [], thirdPartyDistributionChannels: [] },
  content: { media: {
    id: $("LI Co - Init Image Upload").item.json.value.image,
    altText: $("Route by Platform").item.json.image_alt
  } },
  lifecycleState: "PUBLISHED",
  isReshareDisabledByAuthor: false
}) }}
```

`LI Co - Store Post URN` (stolpec `platform_post_id`, ustavi tek z `throw` če je prazen):

```
={{ (() => {
  const v = $json.headers && $json.headers['x-restli-id'];
  if (!v) { throw new Error('platform_post_id je prazen - LinkedIn objava je nastala, komentarja pa ne bo mogoce pripeti'); }
  return v;
})() }}
```

**Tehnična opomba k referencam**: brief za `LI Co - Fetch Image Bytes` navaja `={{ $json.image_url }}`,
kar bi po vrinjenju `LI Co - Init Image Upload` pred njim brala odgovor tega vozlišča, ne vrstice
objave. Uporabljeno je `$("Route by Platform").item.json.image_url` - enak vzorec sklicevanja, kot ga
že uporabljajo obstoječa vozlišča v tej verigi (`Delete Published LI Co`, `Telegram LI Co Post
Failure`). Enako za `image_alt` in `post_text` v `Post LinkedIn Company`. Glave HTTP odgovora
(`x-restli-id`) so v n8n privzeto male črke (`lowercaseHeaders: true` je privzeta nastavitev
`httpRequest` vozlišča) - to ni bilo mogoče preveriti z živim tekom, ker je tek prepovedan do Task 6;
če se izkaže drugače, je treba izraz v `LI Co - Store Post URN` popraviti po prvem ročnem teku.

### Odprto vprašanje za pregled: manjkajoč image_url

Vsa štiri nova vozlišča predpostavljajo, da `image_url` na vrstici objave ni prazen (brief tega
primera ne naslavlja - `LI Co - Fetch Image Bytes` bi na prazen niz naredil GET na prazen URL, kar bi
padlo in ustavilo tek, ker privzeti `onError` ni nastavljen na `continueErrorOutput`). To je v
neskladju z izrecno navedenim ciljnim vedenjem drugje v tem načrtu:

- Task 2 (ledger, 18. 9. 2026): »Star paket in ročni docx uvoz zato še naprej tečeta, samo brez
  slike« - torej star paket lahko pripelje prazen `image_url` do te verige.
- Sam načrt (`docs/superpowers/plans/2026-09-18-linkedin-slika-in-komentar.md:764`, razdelek o
  prenosu v produkcijo): »Brez njiju objavno vozlišče prebere prazno polje in objavi brez slike - brez
  napake.«

Implementirano je dobesedno po Step 2-5 brifa (brez pogojne veje za prazen `image_url`), ker brif
eksplicitno predpisuje natanko ta štiri vozlišča in ne omenja pogojne logike. Ni pa to isto kot
»brez napake« vedenje, ki ga sicer ta načrt obljublja - trenutna veriga se pri praznem `image_url`
ustavi s hard error, namesto da bi objavila brez slike. To presega obseg Task 3 brifa in ni
popravljeno na lastno pobudo; potrebna je Janijeva odločitev, ali se doda pogojna veja (in v katerem
tasku).
