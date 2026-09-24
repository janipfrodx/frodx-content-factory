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

### Task 4: prvi komentar in premik brisanja

Izvedeno 18. 9. 2026. Dodani sta dve novi vozlišči, obe `disabled: true`; obstoječih deset se ni
spremenilo, razen prevezave `LI Co - Store Post URN`.

```
Post LinkedIn Company
     ├─ (uspeh) → LI Co - Store Post URN
     │              → LI Co - Add First Comment      (POST /rest/socialActions/{urn}/comments)
     │                   ├─ (uspeh) → Delete Published LI Co
     │                   └─ (napaka) → LI Co - Comment Failed Alert   (novo, Telegram)
     └─ (napaka) → Telegram LI Co Post Failure   (nespremenjeno)
```

Brisanje vrstice (`Delete Published LI Co`) se je premaknilo za komentar: prej je sledilo takoj za
`LI Co - Store Post URN`, zdaj je edini predhodnik `LI Co - Add First Comment` po **uspešnem** izhodu.
Razlog: `LI Co - Store Post URN` že pred Task 4 vrstici nastavi `status: published`, s čimer je
izpolnjena invarianta »objavljena vrstica se nikoli več ne vrne v čakalno vrsto« ne glede na to, kaj
pade za tem. Če bi brisanje ostalo pred komentarjem, bi neuspel komentar pomenil izgubljeno vrstico -
edini zapis, iz katerega bi bilo URN mogoče še ročno prebrati za pripenjanje komentarja, bi izginil.
Zato brisanje čaka na uspešen komentar; ob napaki komentarja vrstica ostane v tabeli (s `status:
published`, torej je naslednji jutranji tek več ne pobere), Jani pa dobi URN po Telegramu za ročno
pripenjanje.

**Neveljavna predpostavka iz brief-a (preverjeno prek `get_node_types` za `n8n-nodes-base.dataTable`,
resource `row`, operation `update`, verzija 1.1):** izhod te operacije je `{ id, createdAt, updatedAt }`
- vrstice **ne** vrne. `{{ $json.platform_post_id }}` na vozliščih za `LI Co - Store Post URN` zato ne
bi delalo, prav tako pa niti branje prek `$("LI Co - Store Post URN")` ne bi pomagalo, ker ta vozel
sam nima `platform_post_id` na svojem izhodu - vrednost je bila izračunana iz njegovega **vhoda**
(odgovor `Post LinkedIn Company`), ne zapisana nazaj nanj. Zato `LI Co - Add First Comment` URN bere
neposredno iz `$("Post LinkedIn Company").item.json.headers`, po istem vzorcu treh pisav glave
(`x-restli-id` / `X-RestLi-Id` / `X-Restli-Id`), kot ga uporablja `LI Co - Store Post URN`. **Enako je
popravljeno besedilo Telegram opozorila v Step 4** - brief je za vrstico `URN:` predvidel
`{{ $json.platform_post_id }}`, kar je isti neveljavni sklic; nadomeščeno je z isto ekstrakcijo prek
`$("Post LinkedIn Company")`. Preostalo besedilo opozorila (vključno z `{{ $json.error?.message }}`)
je prevzeto dobesedno - ta izraz je že preverjen vzorec, ki ga `Telegram LI Co Post Failure` uspešno
uporablja na istem tipu napakovnega izhoda (`onError: continueErrorOutput`) enega vozlišča prej v isti
verigi.

**Step 1 - preverba proti živi dokumentaciji (`comments-api`, Microsoft Learn, `defaultMoniker:
li-lms-2026-09`):** telo zahtevka iz brief-a (`actor`, `object`, `message.text`) se ujema z živo
dokumentacijo dobesedno - polje z besedilom komentarja je res `message.text`. Pot je
`POST /rest/socialActions/{shareUrn|ugcPostUrn}/comments`.

**Popravek po pregledu (18. 9. 2026):** prejšnja različica tega razdelka je URL-kodiranje razglasila za
odprto vprašanje in implementirala nekodirano pot - to je bilo napačno branje dokumentacije. Stran
`comments-api`, ki sem jo prvotno preveril, res kaže samo abstraktne placeholderje
(`{shareUrn|ugcPostUrn|commentUrn}`) za primer »Create a Comment«, brez izpolnjenega konkretnega
primera. Obstaja pa vzporedna, prav tako trenutna stran istega API-ja, `network-update-social-actions`
(isti `defaultMoniker: li-lms-2026-09`, isti datum posodobitve), ki pod natanko istim naslovom »Create
Comment« doda konkreten »Sample Request Example« s pravim URN-om:

```
https://api.linkedin.com/rest/socialActions/urn%3Ali%3AugcPost%3A7096760097833439232/comments
```

- **Kodirani so vsi konkretni primeri s share/ugcPost URN-om** na tej strani: Retrieve a Summary of
  Social Actions, Batch_GET Summary, Retrieve Likes on Shares, Retrieve Comments on Shares, Get a
  Comment, Create Comment, Delete Comment from Share.
- **Nekodirana sta samo dva primera v celotnem dokumentu**, in oba so ugnezdeni primeri z drugačnim,
  že sestavljenim ključem oblike `urn:li:comment:(urn:li:activity:...,...)`: »Retrieve Comments on
  Comments« in »Create a Comment on a Comment«. To je drugačna uporaba (odgovor na komentar, ne prvi
  komentar pod objavo) - prejšnja različica tega razdelka je napačno posplošila ta dva primera na vse
  primere.
- `X-Restli-Protocol-Version: 2.0.0` (Rest.li 2.0), ki ga to vozlišče že pošilja, kodiranje ključev v
  poti pričakuje - to je dodatna, neodvisna potrditev iste smeri.
- Sklic na `LI Co - Check Image Status` kot precedens za nekodirano pot ne zdrži: gre za drug API
  (Images, ne socialActions), z URN-om druge oblike, in to vozlišče je poleg tega `disabled: true` in
  še nikoli ni teklo - ni preverjen precedens, samo neizvedena domneva.

**Implementirano je zdaj kodirano** - `encodeURIComponent(...)` samo okoli URN-a v URL-ju vozlišča
`LI Co - Add First Comment`. **Telo zahtevka ostane nekodirano**: polje `object` nosi navaden URN
(`urn:li:activity:...` oz. `urn:li:ugcPost:...`), enako kot v obeh uradnih primerih telesa.

**Neujemanje imena obsega (scope) v brief-u:** brief v Step 4 kot manjkajoč obseg navaja
`w_organization_social`. Živa dokumentacija (`comments-api`, tabela »Permissions«) ta obseg imenuje
`w_organization_social_feed`. Popravek obsega na credentialu »LI FrodX Page Igor P« ostaja Janijev in
je izven te naloge - tu je zabeleženo samo pravilno ime za LinkedIn Developer portal.

**Neodvisno od kodiranja - nepreverjeno tveganje za Task 6 (podedovano iz Task 3):** oba izraza na
`LI Co - Add First Comment` (URL in telo) ter besedilo `LI Co - Comment Failed Alert` uporabljajo
`$("Post LinkedIn Company").item` in `$("Route by Platform").item` - poimenovan sklic na vozlišče, ki
stoji **pred** `LI Co - Store Post URN` (`dataTable`, operacija `update`). Ni preverjeno, ali `dataTable`
`update` naprej prenese `pairedItem` skozi verigo. Če ga ne, `.item` na teh sklicih vrže napako oblike
»Can't determine which item to use« - to bi se pokazalo šele pri živem teku v Task 6, ker je vozlišče do
takrat `disabled: true`. Izpad je varen (tek se ustavi z jasno napako, invarianta `status: published` je
takrat na vrstici že zapisana, torej vrstica ne gre nazaj v čakalno vrsto) - to ni novo tveganje te
naloge, isti vzorec sklicevanja (`$("Route by Platform").item` prek `dataTable` vozlišč) že uporabljajo
`Delete Published LI Co` in `Telegram LI Co Post Failure` iz Task 3. Če se v Task 6 pokaže ta napaka, je
popravek zamenjava `.item` z `.first()` ali z eksplicitnim `itemMatching(0)`.

## Igorjev osebni profil

Urejeno 18. 9. 2026 (Task 5). Objava na `urn:li:person:EeNh9CVHnh` gre po **legacy UGC poti**
(`/v2/ugcPosts`, `/v2/assets`), ne po REST poti, ki jo uporablja stran. Vseh deset novih vozlišč je
`disabled: true`; `LI Setup - Create Post via HTTP` je bil predelan in ostaja `disabled: true`.

### Tabela razlik med potema

| | Stran (`urn:li:organization:1132284`) | Osebni (`urn:li:person:EeNh9CVHnh`) |
|---|---|---|
| API | REST `/rest/posts`, `LinkedIn-Version: 202606` | legacy UGC `/v2/ugcPosts`, brez verzijske glave |
| nalaganje slike | `/rest/images?action=initializeUpload` | `/v2/assets?action=registerUpload` z `recipes: ["urn:li:digitalmediaRecipe:feedshare-image"]` |
| kje je uploadUrl v odgovoru | `value.uploadUrl` | `value.uploadMechanism["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"].uploadUrl` |
| URN sredstva | `value.image` (`urn:li:image:...`) | `value.asset` (`urn:li:digitalmediaAsset:...`) |
| avtentikacija pri PUT bajtov | brez - podpisan URL | `Authorization: Bearer` **potreben** |
| preverba obdelave | `GET /rest/images/{urn}`, polje `status` == `AVAILABLE` | `GET /v2/assets/{assetId}`, polje `recipes[].status` == `AVAILABLE` |
| kje je URN objave | glava `x-restli-id` (zahteva `fullResponse`) | glava `x-restli-id` (zahteva `fullResponse`) - glej popravek spodaj |
| komentar | `/rest/socialActions/{urn}/comments` | `/v2/socialActions/{urn}/comments` |
| vrstni red slikovnih korakov | `Fetch -> Init -> Merge -> Upload` | `Register -> Fetch -> Upload` (brez Merge) |

Poti nista zamenljivi. Prepisovanje ene v drugo je najverjetnejši vzrok tihe napake pri prihodnjem
posegu.

### Veriga vozlišč

```
Route by Platform (linkedin_personal)
  → LI Pe - Register Upload        (POST /v2/assets?action=registerUpload)
  → LI Pe - Fetch Image Bytes      (GET image_url, responseFormat: file, image_bytes)
  → LI Pe - Upload Image Bytes     (PUT uploadUrl, binarni podatek, S credentialom)
  → LI Pe - Wait Image Processing  (5 sekund)
  → LI Pe - Check Asset Status     (GET /v2/assets/{assetId})
  → LI Pe - Asset Status Gate      (IF: recipes[].status == AVAILABLE)
      ├─ (da) → LI Setup - Create Post via HTTP   (POST /v2/ugcPosts, shareMediaCategory IMAGE)
      │             ├─ (uspeh) → LI Pe - Store Post URN
      │             │              (platform_post_id ali prazen niz, status=published, published_at)
      │             │              → LI Pe - Add First Comment
      │             │                   ├─ (uspeh) → Delete Published LI Pe
      │             │                   └─ (napaka) → LI Pe - Comment Failed Alert
      │             └─ (napaka) → Telegram LI Pe Post Failure   (nespremenjeno)
      └─ (ne) → LI Pe - Image Not Available   (stopAndError - nič ni objavljeno)
```

Ni več neposredne povezave `Route by Platform → LI Setup` niti `LI Setup → Delete Published LI Pe`;
`Delete Published LI Pe` ima natanko enega predhodnika, uspešni izhod `LI Pe - Add First Comment`.

`Delete Published LI Pe` je bil poleg tega **onemogočen** (prej edino omogočeno vozlišče te veje),
iz istega razloga kot `Delete Published LI Co` v Tasku 3: n8n iteme prepušča skozi onemogočena
vozlišča, zato bi ročni tek pobrisal testne vrstice v `TEST-FrodX-Social-Posts`, ne da bi karkoli
objavil. Task 6 ga za nadzorovani tek spet omogoči.

### Telesa zahtevkov, kot so dejansko napisana

`LI Pe - Register Upload` (statično telo, brez izraza):

```json
{"registerUploadRequest": {"recipes": ["urn:li:digitalmediaRecipe:feedshare-image"], "owner": "urn:li:person:EeNh9CVHnh", "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]}}
```

`LI Setup - Create Post via HTTP` (`options.response.response.fullResponse: true`):

```
={{ JSON.stringify({
  author: 'urn:li:person:EeNh9CVHnh',
  lifecycleState: 'PUBLISHED',
  specificContent: { 'com.linkedin.ugc.ShareContent': {
    shareCommentary: { text: $("Route by Platform").item.json.post_text },
    shareMediaCategory: 'IMAGE',
    media: [{
      status: 'READY',
      media: $("LI Pe - Register Upload").item.json.value.asset,
      description: { text: $("Route by Platform").item.json.image_alt }
    }]
  } },
  visibility: { 'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC' }
}) }}
```

`LI Pe - Add First Comment` (URN v poti percent-kodiran, v telesu nekodiran):

```
url:  ={{ 'https://api.linkedin.com/v2/socialActions/' + encodeURIComponent(<URN>) + '/comments' }}
body: ={{ ({ actor: "urn:li:person:EeNh9CVHnh", object: <URN>, message: { text: $("Route by Platform").item.json.post_url } }) }}
```

kjer je `<URN>`:

```
(() => { const r = $("LI Setup - Create Post via HTTP").item.json; const h = r.headers || {};
  const b = r.body || {};
  return h['x-restli-id'] || h['X-RestLi-Id'] || h['X-Restli-Id'] || b.id || r.id || ''; })()
```

### Popravek briefa: URN objave je v glavi, ne v telesu

Brief je v Step 4 trdil, da pri legacy poti URN objave pride **v telesu odgovora (polje `id`)** in da
`fullResponse` zato ni potreben. **Živa dokumentacija pravi nasprotno**, na dveh neodvisnih straneh:

- UGC Post API (Legacy), `defaultMoniker: li-lms-2026-09`:
  »The UGC Post is created with a `201 Created` response and the response header `x-restli-id`
  contains the ugcPost ID.«
  <https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/ugc-post-api>
- Share on LinkedIn (potrošniška stran za `/v2/ugcPosts`), pri vseh treh primerih (tekst, članek,
  slika): »A successful response will return `201 Created`, and the newly created post will be
  identified by the `X-RestLi-Id` response header.«
  <https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin>

Torej je URN pri **obeh** poteh v glavi, ne samo pri REST poti. Na `LI Setup - Create Post via HTTP`
je zato vklopljen `fullResponse: true`, izraz pa bere glavo v treh pisavah in **šele nato** pade
nazaj na `body.id` in `id` - tako ostane pravilen tudi v primeru, da LinkedIn v praksi vrne `id`
tudi v telesu. Ta rezerva je edini ostanek prvotne trditve briefa.

Posledica: s `fullResponse: true` je izhod tega vozlišča `{body, headers, statusCode}`, zato
`{{ $json.id }}` iz Step 5 briefa ne bi delal niti, če bi bila trditev pravilna.

### Popravek briefa: `GET /v2/assets/{assetId}` hoče ID, ne URN

Dokumentacija: »Retrieve asset information using the Asset ID from the `digitalmediaAsset` URN«, s
primerom `GET https://api.linkedin.com/rest/assets/C5400AQHpR1ANqMWqNA`.
<https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/vector-asset-api>

`value.asset` vrne poln URN (`urn:li:digitalmediaAsset:C5622AQHdBDflPp0pEg`), zato
`LI Pe - Check Asset Status` odreže predpono:
`String(...value.asset || '').split(':').pop()`. Vstavljanje polnega URN-a v pot bi vrnilo 404.

To je razlika proti REST poti, kjer `LI Co - Check Image Status` v pot vstavi **poln** URN
(`urn:li:image:...`). Še ena točka, kjer prepisovanje ene poti v drugo tiho odpove.

### Preverba obdelave slike: polje je `recipes[].status`, ne `status`

Ista stran navaja dve različni polji s tem imenom:

- `recipes[*].status`: `NEW`, `PROCESSING`, `AVAILABLE`, `INCOMPLETE`, `WAITING_UPLOAD`,
  `CLIENT_ERROR`, `SERVER_ERROR`, `MUTATING` - to je stanje **obdelave**.
- `status` (na vrhu odgovora): `ALLOWED`, `BLOCKED`, `ABANDONED`, `DELETED`, `SCHEDULED_DELETION` -
  to je stanje **strežljivosti**, in je `ALLOWED` že dolgo preden je obdelava končana.

`LI Pe - Asset Status Gate` zato preverja `recipes[].status == AVAILABLE` (vzame vnos za recept
`feedshare-image`, sicer prvega). Branje vrhnjega `status` bi bila tiha napaka: `ALLOWED` bi
prepustil objavo z neobdelano sliko, kar je natanko okvara, ki jo ta vrata preprečujejo.

Utemeljitev vrat je ista kot pri strani in izhaja iz iste dokumentacije: »It's required that image
upload completes successfully before creating a UGC Post or Share. If the post is created before
confirming image upload success and the image upload fails to process, the post won't be visible to
members.«

**Znano odstopanje od priporočila:** dokumentacija za slike priporoča sinhroni način
(`"supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]` v telesu `registerUpload`), ki bi vrata
naredil nepotrebna. Implementirano je asinhrono telo iz briefa z vrati, kar isti dokument izrecno
dopušča: »If you opt to use asynchronous upload, it's crucial you confirm the upload succeeded
before using the asset in a UGC Post or Share. Use the Check Status of Upload endpoint to validate
success.« Če se v Task 6 pokaže, da 5 sekund ne zadošča, sta na izbiro daljše čakanje ali prehod na
`SYNCHRONOUS_UPLOAD`.

### PUT bajtov pri legacy poti **potrebuje** `Authorization: Bearer`

To je obratno od REST poti. Dokumentacija (ista stran, razdelek »Upload the Image«): »The upload
call requires a valid OAuth token in the 'Authorization' header. This is different than the upload
video call which doesn't accept an OAuth token.«

`LI Pe - Upload Image Bytes` ima zato credential `LinkedIn Igor P` (`c4dfONautfLbEVYn`), isti kot
`LI Setup - Create Post via HTTP`. `LI Co - Upload Image Bytes` na REST poti ga nima.

Metoda je `PUT`. Potrošniška stran »Share on LinkedIn« v besedilu omenja `POST`, a njen lastni curl
primer uporablja `--upload-file`, kar je PUT; marketinška stran to pove nedvoumno: »Use a PUT method
to upload the image.«

### Komentar: percent-kodiran URN v poti, nekodiran v telesu

Preverjeno na `network-update-social-actions` (`defaultMoniker: li-lms-2026-09`, posodobljeno
30. 4. 2026) - **konkretni primer, ne opis parametra**:

```
POST https://api.linkedin.com/rest/socialActions/urn%3Ali%3AugcPost%3A7096760097833439232/comments
{ "actor": "urn:li:organization:{{organization_id}}", "object": "urn:li:activity:7096760097833439232",
  "message": { "text": "commentV2 with image entity" } }
```

<https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/network-update-social-actions>

Kodirani so vsi konkretni primeri s share/ugcPost URN-om (Retrieve Summary, Batch_GET, Retrieve
Likes, Retrieve Comments, Get a Comment, Create Comment, Delete Comment). Nekodirana sta samo primera
z ugnezdenim `commentUrn` oblike `urn:li:comment:(urn:li:activity:...,...)`, kar je druga uporaba.
Enako kot pri strani: pot kodirana, polje `object` v telesu navaden URN.

Odgovor: glava `x-restli-id` nosi ID komentarja, telo pa poln `commentUrn`. Tega ne beremo - komentar
je zadnji korak pred brisanjem vrstice.

Pravica za osebni profil je `w_member_social_feed` (tabela »Permissions« iste strani), ne
`w_organization_social_feed`, ki velja za stran. Preverba oziroma dodajanje obsega na credentialu
`LinkedIn Igor P` ostaja Janijevo delo, izven te naloge.

### Invarianta čakalne vrste

`LI Pe - Store Post URN` v **isti** posodobitvi zapiše `platform_post_id`, `status: published` in
`published_at`. Če URN-a ni, zapiše prazen niz in tek nadaljuje; napake ne meče. Objavljena vrstica
zato nikoli ne ostane `scheduled`, tudi če kasnejši korak pade - `Get Scheduled Posts` je naslednji
dan ne pobere in objave ne ponovi.

Ob napaki komentarja vrstica ostane v tabeli (s `status: published`), Jani pa dobi URN po Telegramu
za ročno pripenjanje.

### Kaj namerno ni preneseno iz Taska 3

Zamenjava vrstnega reda `Fetch`/`Init` in vozlišče `Merge` se tu **ne** ponovita. Vrstni red ostaja
`Register → Fetch → Upload`, binarni podatek gre naravnost iz `Fetch` v `Upload` in ga noben vmesni
JSON klic ne more izgubiti. Cena je znana in sprejeta: ob nedosegljivem `image_url` ostane pri
LinkedInu registrirano nedokončano sredstvo, preden tek pade na `Fetch`. Nedokončano sredstvo ni
objavljeno in ni vidno nikomur.

### Nepreverjeno pri predaji v Task 6

- Nič od tega ni bilo pognano. Workflow ostaja `active: false`, vseh deset novih vozlišč je
  `disabled: true`, `LI Setup - Create Post via HTTP` prav tako. Pravilnost izrazov je preverjena
  statično in proti dokumentaciji, ne z živim klicem.
- Pot `value.uploadMechanism["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"].uploadUrl`
  je prepisana iz vzorčnega odgovora v dokumentaciji, ne iz dejanskega odgovora instance - tek je
  prepovedan do Task 6. To je najdaljši in najkrhkejši izraz v tej veji; če kaj odpove, začni tu.
- Podedovano tveganje `pairedItem` (iz Taska 3 in 4) velja tudi tu, in sicer ostreje: izrazi na
  `LI Pe - Add First Comment` in `LI Pe - Comment Failed Alert` uporabljajo
  `$("LI Setup - Create Post via HTTP").item` in `$("Route by Platform").item` prek vozlišča
  `LI Pe - Store Post URN` (`dataTable`, `update`), za katero ni dokazano, da prenaša `pairedItem`.
  Če ga ne, `.item` vrže »Can't determine which item to use«. Izpad je varen: `status: published` je
  takrat že zapisan, torej podvojene objave ni, izgubljen je samo komentar. Popravek bi bil `.first()`
  ali `itemMatching(0)`. Ne popravljeno vnaprej, ker se to lahko pokaže šele pri živem teku.
