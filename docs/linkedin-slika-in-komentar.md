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

Urejeno 18. 9. 2026 (Task 3), dopolnjeno istega dne v popravnem krogu po pregledu (dve blokirni
luknji pred Janijevim živim testom). Objava na strani FrodX zdaj nosi sliko namesto kartice članka in
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

**Odprto vprašanje, ne ugotovljeno dejstvo** (popravljeno v popravnem krogu - prejšnja različica tega
razdelka je trditev o »zastarelem navzkrižnem sklicu« zapisala kot dejstvo, česar iz vira ne izhaja):
uradna stran za Images API pri koraku »Upload the Image« kaže na dokumentacijo Assets API
(`vector-asset-api`), ki nosi tekoči moniker in namenoma razlikuje sliko od videa - za sliko izrecno
pravi, da PUT **zahteva** `Authorization: Bearer` glavo. To je nasprotno od tega, kar predpisuje brief
(»brez credentiala, `uploadUrl` je podpisan«). Vira si nasprotujeta in iz uradnega vira samega ne
izhaja, da gre za zastarel navzkrižni sklic. Implementirano je brez glave, po treh neodvisnih
praktičnih virih iz leta 2026 (vključno z razčlenjenim vodičem za Node.js integracijo), ki eksplicitno
navajajo, da PUT na `uploadUrl` iz Images API (`/rest/images`, ne `/v2/assets`) ne sme nositi
`Authorization` glave, ker gre za podpisan URL. **Remediacija, če se izkaže narobe**: če PUT v Task 6
vrne `401` ali `403`, se nanj pripne isti credential (`vk2EcfcOdFxsOOjK`, »LI FrodX Page Igor P«), ki
je že uporabljen na ostalih dveh LinkedIn klicih v tej verigi.

### Veriga vozlišč (po vrsti, po popravnem krogu)

```
Route by Platform (linkedin_company)
  → LI Co - Fetch Image Bytes        (GET image_url iz vrstice, responseFormat: file)
       ├─→ LI Co - Init Image Upload  (POST /rest/images?action=initializeUpload)
       └─→ LI Co - Merge Image Data   (2. vhod - obvod, da $binary.image_bytes preživi Init)
  LI Co - Init Image Upload
       └─→ LI Co - Merge Image Data   (1. vhod)
  → LI Co - Merge Image Data          (combine, combineByPosition, 2 vhoda)
  → LI Co - Upload Image Bytes        (PUT na uploadUrl, telo = binarni podatek, brez credentiala)
  → LI Co - Wait Image Processing     (5 sekund)
  → LI Co - Check Image Status        (GET /rest/images/{urn}, urn iz Init Image Upload)
  → LI Co - Image Status Gate         (IF: status == AVAILABLE)
      ├─ (da) → Post LinkedIn Company        (POST /rest/posts, content.media, fullResponse: true)
      │             ├─ (uspeh) → LI Co - Store Post URN
      │             │              (status=published, published_at, platform_post_id ali prazen niz)
      │             │              → Delete Published LI Co
      │             └─ (napaka) → Telegram LI Co Post Failure   (nespremenjeno)
      └─ (ne) → LI Co - Image Not Available   (stopAndError - nič ni objavljeno, vrstica ostane
                                                scheduled za naslednji poskus)
```

Prvotna štiri vozlišča iz Task 3 so ostala, samo prevezana; predelan je `Post LinkedIn Company` (brez
sprememb telesa, samo vhodna povezava) in `LI Co - Store Post URN` (glej spodaj). Pet je novih:
`LI Co - Merge Image Data`, `LI Co - Wait Image Processing`, `LI Co - Check Image Status`,
`LI Co - Image Status Gate`, `LI Co - Image Not Available`. Vseh deset vozlišč v tej verigi je
`disabled: true`, vključno z `Delete Published LI Co`, ki je bilo doslej edino omogočeno vozlišče iz
Task 1 na tej poti - ker n8n skozi onemogočena vozlišča iteme prepušča naprej, bi ročni tek kopije
sicer pobrisal testne vrstice v `TEST-FrodX-Social-Posts`, ne da bi karkoli objavil (test bi pojedel
lastne testne podatke). Task 6 ga bo za svoj nadzorovani tek spet omogočila.

Zamenjava vrstnega reda `Fetch`/`Init` (popravni krog): prej je `Init Image Upload` tekel pred
`Fetch Image Bytes`, zato bi se ob nedosegljivi sliki na LinkedInu registriral nedokončan slikovni URN,
preden bi tek padel. Zdaj neveljaven `image_url` pade na `Fetch`, preden se LinkedIna sploh dotaknemo.

### Zakaj preverba statusa slike - izbira in utemeljitev

Images API ne podpira `SYNCHRONOUS_UPLOAD`; LinkedIn dokumentacija izrecno opozarja, da objava,
ustvarjena preden je slika obdelana, članom ni vidna - to bi bila živa objava brez vidne slike, ki bi
jo bilo treba ročno brisati. Izbran je **en poskus po čakanju, ne zanka s ponavljanjem**:
`LI Co - Wait Image Processing` počaka 5 sekund, `LI Co - Check Image Status` prebere
`GET /rest/images/{urn}`, `LI Co - Image Status Gate` nadaljuje na objavo samo, če je `status` enak
`AVAILABLE`; sicer se tek ustavi na `LI Co - Image Not Available` - nič ni objavljeno, vrstica ostane
`scheduled` za naslednji poskus. Razlog za en poskus namesto zanke: cela veriga je `disabled: true` in
se izvaja samo v Task 6, ki je človeško nadzorovan živi test - ustavljen tek z jasno napako se tam lahko
ročno ponovi, dodatna zapletenost zanke s ponavljanjem trenutno ni upravičena. Če se v Task 6 izkaže,
da 5 sekund ne zadošča, je čas čakanja edini parameter, ki ga je treba spremeniti.

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

`LI Co - Store Post URN` (popravni krog: `throw` je odstranjen, tek se nadaljuje tudi če glave ni;
poleg `platform_post_id` se v isti posodobitvi zapišeta še `status` in `published_at`):

```
platform_post_id:
={{ (() => {
  const h = $json.headers || {};
  const v = h['x-restli-id'] || h['X-RestLi-Id'] || h['X-Restli-Id'];
  return v || '';
})() }}

status: published
published_at: ={{ $now.toISO() }}
```

Invarianta, ki jo to zagotavlja: po uspešni objavi (`Post LinkedIn Company` vrne 201) vrstica dobi
`status: published` ne glede na to, ali je glava `x-restli-id` prisotna. Prej je manjkajoč URN sprožil
`throw`, ki je podrl vozlišče za celo serijo - objava je bila že na LinkedInu, vrstica pa je ostala
`scheduled` in bi jo naslednji tek ob 7:30 objavil še enkrat, poleg tega pa niso bile izbrisane niti
druge, uspešno objavljene vrstice iste serije. Prazen `platform_post_id` se zdaj pokaže v Task 4, ki
ima za manjkajoč URN svoje opozorilo - podvojena objava naslednje jutro pa se po tem popravku ne bi
pokazala nikjer, ker se ne more več zgoditi.

**Tehnična opomba k referencam**: brief za `LI Co - Fetch Image Bytes` navaja `={{ $json.image_url }}`,
kar bi po vrinjenju `LI Co - Init Image Upload` predenj brala odgovor tega vozlišča, ne vrstice objave.
Uporabljeno je `$("Route by Platform").item.json.image_url` - enak vzorec sklicevanja, kot ga že
uporabljajo obstoječa vozlišča v tej verigi (`Delete Published LI Co`, `Telegram LI Co Post Failure`).
Ta sklic ostane veljaven tudi po zamenjavi vrstnega reda `Fetch`/`Init` v popravnem krogu, ker je
poimenovan (`$("Route by Platform")`), ne pozicijski (`$json`). Enako za `image_alt` in `post_text` v
`Post LinkedIn Company`.

Glava `x-restli-id`: n8n privzeto vrača glave z malimi črkami (`lowercaseHeaders: true` je privzeta
nastavitev `httpRequest` vozlišča), a izraz, ki bi bral izključno `h['x-restli-id']`, bi bil odvisen od
tega, da ta privzetek dejansko velja na tej instanci. Zato `LI Co - Store Post URN` po popravnem krogu
bere vse tri pisave (`x-restli-id`, `X-RestLi-Id`, `X-Restli-Id`). Katera se dejansko pojavi, ni bilo
mogoče preveriti z živim tekom, ker je tek prepovedan do Task 6.

**Binarni podatek skozi Merge (dodano na lastno pobudo, ne del izrecnega besedila popravnega kroga)**:
`LI Co - Upload Image Bytes` bere `$binary.image_bytes` iz svojega neposrednega vhoda, ne prek
poimenovanega sklica na drug node - `inputDataFieldName` take sintakse nima. Ker `LI Co - Init Image
Upload` po zamenjavi vrstnega reda leži med `Fetch` in `Upload` in gre za httpRequest klic samo z JSON
telesom, obstaja dokumentirano tveganje (n8n skupnostna dokumentacija o binarnih podatkih), da tak node
binarnega podatka na vhodu ne prenese na izhod. Zato je vrinjen `LI Co - Merge Image Data` (combine,
combineByPosition, 2 vhoda): prvi vhod je izhod `Init Image Upload` (JSON z URN-om), drugi je obvod
neposredno iz `Fetch Image Bytes` (ohrani `$binary.image_bytes`). To varovalo ni bilo eksplicitno
naročeno - dodano je, ker bi zamenjava vrstnega reda brez njega lahko tiho izgubila sliko tik pred
nalaganjem.

### Odločitev: manjkajoč image_url ustavi tek (zaprto)

Prejšnja različica tega razdelka je vprašanje pustila odprto za Janijevo odločitev. Odločeno je v
popravnem krogu: **trda napaka ostane, pogojne veje za prazen `image_url` ni.** `LI Co - Fetch Image
Bytes` na prazen `image_url` naredi GET na prazen URL, kar pade in ustavi tek - to je namerno vedenje,
ne spregledan primer.

Utemeljitev: tiha objava brez slike je hujša napaka od glasnega padca teka. Objava brez slike bi šla v
živo na LinkedIn neopažena (nihče je ne bi preveril, ker je videti kot uspeh), medtem ko ustavljen tek
pusti vrstico v `scheduled` za ročni pregled in ponovni poskus - napaka je vidna in popravljiva.

Ugotovitev pregleda o dosegu škode: `Prepare Pipeline Row` in `Create Platform Posts` (Task 2)
postavita `image_url` na vseh treh kanalskih vrsticah iz istega vira v isti izvedbi. Ena vrstica s
praznim `image_url` zato ne ustavi samo LinkedIn strani - ustavi **celoten dnevni tek na vseh treh
kanalih** (LinkedIn stran, LinkedIn osebni profil, Facebook), ker gre za en `Telegram Callback Trigger`
tek, ki se ob padcu enega vozlišča ustavi v celoti. To ni popravljeno znotraj te naloge - ostaja
veljavno, namerno vedenje in je tu zabeleženo kot znana lastnost, ne kot odprta napaka.

### Objava brez povezave do Task 4

`commentary` v `Post LinkedIn Company` ne vsebuje nobene povezave na blog, kartica članka (`article` v
`content`) je odstranjena in nadomeščena s `content.media` (slika) - povezava pride šele v prvem
komentarju, ki ga doda Task 4. **Če se Task 6 (živi test) izvede pred Task 4, bo prava objava na
LinkedIn strani FrodX brez kakršnekoli povezave na članek**, dokler komentar ni pripet ročno ali dokler
Task 4 ni implementirana.
