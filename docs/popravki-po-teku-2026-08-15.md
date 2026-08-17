# Popravki po prvem živem teku (14.-15. 8. 2026)

Odgovor na `NAPAKE-IN-ODPRTE-TOCKE.md`, ki ga je napisala Cowork seja po prvem teku verige od konca
do konca. Ta datoteka pove, katera točka je zaprta, kje in kako, in katere ostajajo odprte.

**Kdaj:** 17. 8. 2026. **Kdo:** Jani + Claude Code. **Obseg:** popravki v repu; posegi v n8n so odprti.

---

## Kaj se je izkazalo za drugačno, kot je poročilo trdilo

**A1 (Excel ni na dogovorjeni poti) v kodi ni bila napaka.** Pot je bila v repu popravljena že
14. 8. s commitom `7afdda6`; `references/excel-contract.md` je takrat že navajal OneDrive in
`aeo-themes.xlsx` z Graph ID-ji. Cowork je bral **zastarelo sinhronizirano kopijo** plugina.
Popravek je zato operativen, ne vsebinski: pred vsakim tekom mora biti plugin resinhroniziran.
Zapisano v `README.md`, razdelek »Pred vsakim tekom«.

**A2 in prva polovica A3 sta bili res izvedeni.** Preverjeno 17. 8. 2026 neposredno v živi n8n
instanci, ne po poročilu:

- `GZmnPGOcVANH2sfy` → `Gemini Critique.modelId` = `models/gemini-3.1-pro-preview` (posodobljeno 14. 8. 18:19)
- `lHc3NdejxehMyc9O` → vozlišča `Shrink OpenAI`, `Shrink Gemini`, `B64 OpenAI`, `B64 Gemini` obstajajo (posodobljeno 15. 8. 11:46)

**Novo, česar poročilo ne omenja:** OpenAI ocenjevalec v critique workflowu teče na `gpt-4o`.
Past C2 (»ocenjevalec razglaša pravilne letnice za halucinacije«) zato ne velja samo za Gemini -
velja za oba ocenjevalca, in za `gpt-4o` še bolj, ker je njegov presek znanja starejši.

**Podatki v vrsti tem preverjeni neposredno v datoteki** (17. 8. 2026, `aeo-themes.xlsx`):
vseh 11 vrstic `status = new`, `target_prompt` prazen v vseh 11, `format = kolumna` samo pri
`aeo-009`. Vrstice s `priority HIGH` imajo najnižji citation lift (+0,7 % / +1,4 % / +1,7 %).
Poročilo se z datoteko ujema.

---

## Zaprte točke

| Točka | Kje je popravljeno |
|---|---|
| **A2** (odpoved ocenjevalca tiho porabi kroge) | `frodx-critique-loop/SKILL.md`: padlo vozlišče ni glas; `openai_error`/`gemini_error` v zapisu kroga; en ocenjevalec dovolj, a to se izrecno pove; oba padla = zanka se ustavi in krog se ne šteje |
| **C1** (kritika meri na kontekst) | `critique-prompt.md`, nov razdelek »Predmet presoje«: ocenjuje se samo besedilo kolumne |
| **C2** (ocenjevalec razglaša pravilne letnice za halucinacije) | `critique-prompt.md`: današnji datum kot `{{DANES}}` + prepoved sodb o letnicah; `frodx-critique-loop/SKILL.md`: dirigent datum vstavi in pred popravkom letnice preveri pri viru |
| **B1** (`target_prompt` prazen) | `frodx-topic-pick/references/scoring.md`: dovoljena izpeljava iz `topic`, obvezno označena kot izpeljava; gola kategorija se ne ugiba |
| **B2** (dva nasprotujoča si signala) | `scoring.md`, razdelek »Kateri signal je merodajen«: `priority` primarni, `citation lift` samo za enako prioriteto, brez izmišljenih uteži |
| **C4** (veriga zna samo kolumno) | `scoring.md`, razdelek »Veriga zna izdelati samo kolumno« + `frodx-topic-pick/SKILL.md`, točka 5: neskladje formata se pove ob izbiri teme |
| **C5** (ni polja za odprte zadolžitve) | `_run.open_tasks` v `state-schema.md`, `init_run.py`, `validate_package.py` (funkcija `opozorila`), `frodx-publish-send/SKILL.md`, dirigent (korak 4). Gate **opozori, ne blokira** - odločitev Janija 17. 8. 2026. 10 novih testov |
| **C3** (terminologija trči ob AEO cilj) | Izjema zapisana na naši strani: dirigent, razdelek »Terminologija in AEO ciljni prompt«. Vendorirani `terminology.md` nedotaknjen; točka vpisana v `VENDOR.md` za Igorja |
| **D1** (mapa teka umre s sejo) | Dokumentirano kot omejitev: dirigent (»Mapa teka ne preživi seje«) in `frodx-publish-send` (`outbox/`). Tek naj steče v eni seji, vsebina se izpiše v pogovor, edina obstojna točka je korak 7 |
| **D2** (stroški slik) | `frodx-image-run/SKILL.md`, razdelek »Stroški«: ne zaganjaj znova zaradi binarnega izhoda, sliki iz stare izvedbe sta še v n8n |
| **A1** (operativni del) | `README.md`: obvezna resinhronizacija plugina pred tekom |
| **A3** (dokumentacijski del) | `frodx-image-run/SKILL.md`, razdelek »Kako sliki dejansko prideta do tebe«: kaj ne deluje in se ne ponavlja, in vmesni postopek s človekom |

Testi: `python3 -m pytest tests/ -q` → **63 prehaja** (prej 53). `test_vendor_integrity.py` prehaja,
kar dokazuje, da noben Igorjev skill ni bil spremenjen.

---

## Odprte točke

### 1. A3 - slike niso dosegljive dirigentu (edina blokada sredi teka)

Base64 veja v workflowu obstaja in deluje, a prepis ~45.000 znakov skozi kontekst na disk je bil
preizkušen 15. 8. in **ni** deloval (17 kB namesto ~35 kB, `OSError: broken data stream`).
Ponovni poskus je ista operacija z istim razlogom za odpoved.

**Pot je zdaj znana, ne ugibana.** Preverjeno 17. 8. 2026: Microsoft 365 konektor prek
`read_resource` na URI `file:///{driveId}/{itemId}` vrne **sliko, ki jo Claude res vidi** - ne
besedilnega izvlečka in ne imena datoteke. Preizkušeno na obstoječi datoteki
`key-visual lasten-crm 1200x630.png` v Igorjevem OneDrive; vsebina slike je bila opisana iz
same slike.

Zasnova rešitve:

```
n8n generira sliko -> naloži jo prek Graph API na SharePoint -> vrne driveId + itemId
   -> dirigent pokliče read_resource("file:///{driveId}/{itemId}") -> Claude vidi sliko
```

Brez base64, brez `curl`, brez javnih povezav, vse ostane v FrodX okolju (ISO 27001 neoporečno).
`read_resource` je bil v Cowork seji na voljo že med tekom (poročilo, razdelek 3).

**Kaj to blokira: v n8n ni credentiala za OneDrive ne za SharePoint.** Preverjeno 17. 8. 2026 prek
`list_credentials` (78 credentialov): obstajajo `microsoftOutlookOAuth2Api`, `microsoftTeamsOAuth2Api`,
`microsoftExcelOAuth2Api` in en generični `microsoftOAuth2Api` (»Microsoft Teams Jani P«), **nobenega
za datoteke**. Preden se workflow gradi, mora Jani ustvariti OneDrive ali SharePoint OAuth2 credential
(potrebni obsegi: pisanje datotek na ciljni drive). To je edini korak, ki ga ne more narediti nihče drug.

**Dve stvari, ki ju je pri gradnji dobro vedeti:**

- `read_resource` na **mapo** prek poti (`file:///{driveId}/{ime mape}`) vrne `invalidRequest` -
  mapo je treba naslavljati z `itemId`, ki ga da `sharepoint_folder_search`. Za datoteke pot deluje.
- SharePoint iskanje (`sharepoint_search`) rastrskih slik ne indeksira - `fileType: png` vrne nič.
  Sliko se najde prek `sharepoint_folder_search` ali prek `itemId`, ki ga vrne workflow ob nalaganju.
  Zato naj workflow `driveId` in `itemId` **vrne v odgovoru** in ne pričakuje, da jih bo dirigent iskal.

Do izvedbe velja vmesni postopek: človek prenese sliki iz n8n UI v mapo teka
(`frodx-image-run/SKILL.md`).

### 2. A4 - vrsta tem se ne premika

**Odločena smer (Jani, 17. 8. 2026):** vrsta se preseli iz Excela v **n8n Data Table**, z dvema
kratkima workflowoma - eden zapiše priporočila, ki jih Claude pobere iz HubSpot AEO, drugi ob izbiri
označi vrstico (`status = picked`, `run_slug`).

**Pri gradnji ne pozabi na branje.** n8n MCP zna v Data Table samo vstavljati vrstice
(`add_data_table_rows`); orodja za **branje** ali **posodabljanje** vrstic ni - preverjeno 17. 8. 2026,
cel nabor je `search_data_tables`, `create_data_table`, `rename_data_table`,
`add/delete/rename_data_table_column`, `add_data_table_rows`. Branje vrste in posodobitev vrstice
morata torej oba teči skozi workflow z Data Table vozliščem.

**Krajša pot, odkrita 17. 8. 2026.** V n8n že obstaja credential **`Microsoft Excel Jani P`**
(`microsoftExcelOAuth2Api`, ID `Mk9bvadCRqU8Oy2K`, domači projekt: Janijev osebni). Z n8n-ovim
Microsoft Excel vozliščem je torej mogoče nastaviti celico `status = picked` **neposredno v
`aeo-themes.xlsx`** - brez Data Table, brez migracije vrstic in brez novega credentiala. Excel ostane
tam, kjer je, in se ureja naprej ročno. Edino opravilo: credential je treba deliti s timskim projektom
`Content Factory`, kjer živijo ti workflowi.

Odločitev za Data Table s tem ni razveljavljena - sta pa zdaj dve izvedljivi poti, in Excel pot je
občutno krajša. Tehtati je treba, ali je vrsta tem dolgoročno Excel (ročno urejanje, osebni OneDrive)
ali n8n Data Table (skupna, strojno berljiva, brez odvisnosti od osebnega diska).

Do izvedbe velja ročno označevanje, izrecno zapisano v `frodx-topic-pick/SKILL.md`, točka 8, z zapisom
v `_run.topic_source.writeback_status` in `_run.open_tasks`.

### 3. Modela ocenjevalcev - ZAPRTO 17. 8. 2026

Kar je na teh dveh credentialih dejansko na voljo (preverjeno 17. 8. 2026 prek `explore_node_resources`,
metoda `modelSearch`):

- **OpenAI:** cela linija GPT-5, do `gpt-5.5-pro` (2026-04-23) in `gpt-5.6-luna` / `gpt-5.6-sol` /
  `gpt-5.6-terra` (te tri brez datuma in brez podatka, kaj so).
- **Gemini:** najboljši *pro* je `models/gemini-3.1-pro-preview` - **novejšega pro modela na tem računu ni**.
  Obstajata še alias `models/gemini-pro-latest` in stabilna flash linija do `models/gemini-3.7-flash`.

**Izvedeno v `GZmnPGOcVANH2sfy`** (zadnja verzija »OpenAI ocenjevalec: gpt-5.5-pro -> gpt-5.6-sol«):

- `OpenAI Critique.modelId` = **`gpt-5.6-sol`** (bilo `gpt-4o`, vmes kratko `gpt-5.5-pro`).
  Izbira Janija, 17. 8. 2026: najnovejši model na tem credentialu.

  **Preveri ob prvi živi kritiki.** O `gpt-5.6-sol` ni znanega nič razen imena v seznamu modelov -
  ni datuma, ni podatka, ali je reasoning ali chat varianta. Ob prvem krogu poglej troje: ali vrne
  sodbo v pričakovani obliki (`OBJAVLJIVO` / `ZA POPRAVEK` v prvi vrstici), ali se drži meje petih
  pripomb, in ali pripombe merijo na vsebino, ne na slog. Če katerokoli od tega odpove, je popravek
  en parameter: `gpt-5.5-pro` je znana varna izbira.
- `Gemini Critique.modelId` **ostaja** `models/gemini-3.1-pro-preview`. Nadgraditi ga ni kam.
  Alias `gemini-pro-latest` bi tveganje 404 zamenjal s tveganjem, da se model tiho zamenja; ker skill
  zdaj odpoved ocenjevalca obravnava (glej A2), je 404 obvladljiv, tiha zamenjava pa ne bi bila.

Nič drugega v workflowu ni spremenjeno. Oba modela imata presek znanja pred današnjim datumom, zato
popravek prompta z datumom (C2) ostane nujen - nadgradnja modela ga ne nadomesti.

### 3b. Predaja paketa aplikaciji - preverjeno 17. 8. 2026

Pregledan je bil Lovable projekt **`frodx-content-app`** (`90b43584-6783-4de3-aca2-e95435c76de7`,
https://frodx-content-app.lovable.app), cel seznam 101 datoteke.

**Ingest API ne obstaja.** V `src/routes/` sta samo `auth.tsx` in `_authenticated/index.tsx`; API poti
ni, v `supabase/` so samo migracije, brez edge funkcij. `/api/ingest`, na katerega cilja
`frodx-publish-send`, torej nima ničesar na drugi strani. Dry-run ostaja edino možno vedenje - ne po
odločitvi, ampak ker endpointa ni.

**Kar aplikacija že ima in olajša gradnjo:**

- `src/lib/content-schema.ts` → `contentJsonSchema` je **identičen našemu paketu**: `meta` (title,
  exported_at, version), `universal.slug`, `social_posts[{text, publish_date}]`, `languages.{sl,en,hr}`
  z vsemi polji, vključno s `featured_image_alt`, `topic_cluster`, `campaign_name`, `tag_id/name/slug`.
  Gate torej že proizvaja obliko, ki jo aplikacija razume - preslikave ne bo treba pisati.
- Javni Supabase bucket **`content-images`** (migracija 28. 5. 2026), z branjem za vse in pisanjem
  samo prek `service_role` (migracija 3. 6. 2026 je permisivne politike odstranila). Slike se
  nalagajo strežniško prek `supabaseAdmin`.

**Predlagana delitev vlog v verigi:**

| Kdo | Kaj nosi |
|---|---|
| n8n | vse bajte: generira sliki, naloži na SharePoint, ob predaji sliko prenese in odda aplikaciji |
| Claude | samo besedilo in presojo: pogleda sliki prek `read_resource`, izbere, napiše alt tekste in meta podatke, pošlje paket kot JSON |
| aplikacija | ingest: validira po `contentJsonSchema`, sliko da v `content-images`, ustvari osnutek, vrne 202 / 409 / 422 |

Ključno načelo: **Claude nikoli ne prenaša binarnih podatkov.** `read_resource` mu sliko pokaže, ne da
mu bajtov - kodiranja v base64 zato ne more opraviti, in vsak poskus tega je isti razred napake, ki je
ubil korak 5. Posledica za `frodx-publish-send`: neha sestavljati base64 in namesto tega kliče dostavni
workflow z `{package, image: {driveId, itemId}, run_slug, idempotency_key}`. Stranski dobitek je, da
API ključ aplikacije ostane v n8n credentialu in nikoli ne pride v Claudov kontekst.

**Opomba o nasprotju v zapisih:** obstaja opomba, da ingest endpoint že obstaja. Koda aplikacije to
zavrača. Najverjetnejša razlaga je, da je opomba merila na n8n webhook `frodx-publish` v
`PROD 2 - FrodX Content Publishing Pipeline` (`3lK6pjOfOAa0BxDm`), ne na Lovable aplikacijo. Preden se
gradi dostava, je treba razmejiti, kaj dela tisti pipeline in kaj naj dela nov ingest, da se predaja
ne podvoji.

### 4. Obstojnost mape teka (D1, trajna rešitev)

Zdaj samo dokumentirano. Trajna rešitev je sinhronizacija mape teka na SharePoint prek istega
Graph vzorca kot A3.

### 5. Preostalo iz poročila, kar ni bilo popravljeno namenoma

- **`frodx-aeo-watch`** (polnjenje `target_prompt`) ima svoj načrt in ni del tega popravka.
- **Podpis se v produkciji doda dvakrat** - zahteva poseg v aktiven `3lK6pjOfOAa0BxDm`, ostaja odprto
  iz prejšnje seje.
- **Živo pošiljanje na `/api/ingest`** ostaja zaklenjeno, dokler ga Jani ne odklene.
- **Opozorilo validacijske sheme MCP orodja** pri vozlišču `Gemini Image`
  (`Invalid value for "parameters.resource"`) - označeno kot `preExisting`, workflow deluje.
  Ni preverjeno, ali je napaka v shemi orodja ali v workflowu.

## Dopolnitev 17. 8. 2026: preverjena dostavna pot

Ta razdelek **nadomešča** ugotovitve iz razdelka 3b tam, kjer si nasprotujeta. Prebrani so bili vsi
nodei `PROD 2 - FrodX Content Publishing Pipeline` (`3lK6pjOfOAa0BxDm`) in strežniške funkcije
Lovable aplikacije `frodx-content-app` (`90b43584-6783-4de3-aca2-e95435c76de7`).

### Kaj `PROD 2` je in kaj zahteva

Webhook `POST https://frodxai.app.n8n.cloud/webhook/frodx-publish`, aktiven, v produkciji.
Zaporedje: HMAC preverba (`x-signature`, `$vars.HMAC_SECRET`, podpis nad `JSON.stringify(body)`) ->
zahteva `body.meta.idempotency_key` (sicer 400) -> pogled v idempotenčno tabelo (409 ob ponovitvi) ->
202 -> validacija -> markdown v HTML -> prenos slike z URL-ja in nalaganje v HubSpot files ->
SL osnutek + EN/HR variaciji -> Telegram potrditve po jezikih -> HubSpot razporejanje ->
socialne objave (LinkedIn Co/Pe, Facebook) -> dnevni preverjalnik ob 7:30.

Obvezna polja, ki jih validacija zahteva (drugače vrže `Validation failed`):

- `publish_at` ali `meta.publish_date`, **vsaj 10 minut v prihodnosti**, brano kot ura po Europe/Ljubljana
- `featured_image_url` - **mora biti anonimno dosegljiv `http(s)` URL**
- `meta`, slug, HubSpot author id (ima privzetega), `social_posts[0]`
- kampanja: `campaign.name` ali `campaign.utm.campaign` ali `topic_cluster` (dovolj eno)
- tagi: `hubspot_tag_ids` ali `languages.<jezik>.tag_id`; pogoj je `some`, ne `every`, zato
  **nepopolna tag-taksonomija dostave ne blokira**
- za vse tri jezike: `content`, `seo_title`, `meta_description`

Posledica za sliko: vozlišče `Download Featured Image` je navaden HTTP klic **brez avtentikacije**.
SharePoint zato ne more biti vir slike za objavo. Slika potrebuje javni URL.

### Kaj aplikacija že zna

Strežniške funkcije v `src/lib/content.functions.ts`, vse z `requireSupabaseAuth`:

- `extractContent(docxBase64)` - docx v `ContentJson`, SEO in kampanjo naredi Gemini prek Lovable
  gatewaya, tage izpelje iz kampanje, prvo vdelano sliko naloži v `content-images` in vrne javni URL
- `uploadFeaturedImage(imageBase64, filename, mimeType)` - naloži v `content-images`, vrne javni URL
- `generateImageAlts(imageUrl, titles)` - alt teksti prek vision modela
- `dispatchToN8n(content, publishDate, featuredImageUrl, idempotencyKey)` - **sam podpiše HMAC** in
  pošlje na webhook, vrne 202 / 409 / 401 / 400 kot razumljivo sporočilo

Čarovnik: `Step1Upload` -> `Step2Processing` -> `Step3EditForm` -> `Step4Schedule` -> `Step5Confirm`.

**Zato `/api/ingest` ne obstaja:** vse to so `createServerFn`, ki jih kliče prijavljen brskalnik.
Doslej ni bilo klicalca brez seje. Manjka torej strojni vhod, ne zmožnost.

### Odločena zasnova (Jani, 17. 8. 2026)

Aplikacija **ostane v verigi** in ostane taka, kot je. Igor v njej pregleda paket ter nastavi datum
objave bloga in datume socialnih objav. To se ne podvaja s Telegramom: aplikacija je **pred**
`frodx-publish`, Telegram potrjuje osnutke **za njim**.

Zato tudi velja naprej pravilo v `frodx-publishing-meta` in `frodx-publish-send`, da veriga
`publish_at` ne nastavlja - datum doda `dispatchToN8n` iz Igorjevega izbirnika.

```
Claude -> n8n cf-generate-image {oba prompta, run_slug}
            OpenAI Image + Gemini Image
            obe POST -> aplikacija /api/images (x-api-key) -> dva javna URL-ja
            (opcijsko) obe na SharePoint za arhiv
          <- {openai: {url, ...}, gemini: {url, ...}}
Claude    pogleda obe, izbere, napise alt tekste
          -> n8n cf-deliver-draft {paket, featured_image_url, run_slug}
               POST -> aplikacija /api/drafts (x-api-key)
Igor      odpre osnutek v carovniku na koraku 3, pregleda, nastavi datume, potrdi
          -> dispatchToN8n (nedotaknjen) -> PROD 2 -> HubSpot + Telegram + social
```

Claude nosi samo nize: URL slike, besedilo, presojo. Nikoli bajtov, nikoli HMAC skrivnosti, nikoli
API ključa aplikacije - ta je v n8n credentialu.

**Zavrnjeni možnosti in zakaj:**

- *MCP strežnik za aplikacijo, da Claude piše neposredno.* Ne reši ničesar: sliko bi še vedno bilo
  treba prenesti skozi kontekst kot base64, kar je dokazano pokvarjeno. Poleg tega da Claudu pisalni
  dostop do cele aplikacije, medtem ko dve ozki poti data točno toliko, kolikor je treba.
- *Vse v Coworku brez aplikacije.* Vrže stran izbirnik datumov, mapiranje kampanj in tagov ter
  `dispatchToN8n`, ki že podpisuje pravilno, in Igorju vzame vizualni pregled pred objavo.

**`PROD 2` ostane v produkciji, dokler nov ni pripravljen za produkcijo** (Janijeva odločitev). Nič v
njem se ne spreminja, tudi dvojni podpis ne, dokler se ga ne loti posebej.

### Kaj je treba zgraditi

| kdo | delo |
| --- | --- |
| aplikacija | `POST /api/images` (base64 -> javni URL, obstoječa logika `uploadFeaturedImage`, `x-api-key`) |
| aplikacija | `POST /api/drafts` (`{content, featured_image_url, run_slug}` -> vrstica osnutka, vrne `draft_id`) |
| aplikacija | tabela osnutkov in pot, ki osnutek odpre v čarovniku na koraku 3 |
| n8n | `cf-generate-image` dopolniti z nalaganjem obeh slik na `/api/images` |
| n8n | nov kratek `cf-deliver-draft` |
| skilli | `frodx-publish-send` neha delati base64, pošilja `featured_image_url` |
| skilli | `frodx-image-run` dobi pravo pot do slik |

Nedotaknjeno: `PROD 2`, `dispatchToN8n`, čarovnikovi koraki 3-5.

### Kako Claude sliki vidi - preverjeno 17. 8. 2026 v Coworku

Vprašanje »ali zadošča javni URL« je zdaj zaprto. **Ne zadošča.**

- `web_fetch` na slikovni URL vrne `Image content is not supported` - orodje podpira samo besedilne
  in HTML vsebine.
- `bash_tool` + `curl` je blokiran na omrežni ravni. Egress allowlist obsega samo pakirne vire
  (`api.anthropic.com`, npm, pypi, crates, GitHub, Ubuntu). `frodx.com` in `*.supabase.co` sta zunaj
  njega. Vrnjeni 403 je proxyjev status za »blokirano«, ne odgovor Supabase - iz njega se o bucketu
  ne sme sklepati nič.
- `read_resource` na `file:///{driveId}/{itemId}` **deluje**. MCP konektorji niso omejeni z istim
  allowlistom kot `bash_tool`.

Trajni poti sta zato dve, obe najbrž zahtevata administratorja: lastnik organizacije doda host
`umvjwjzdrtamfrcqhopa.supabase.co` v nastavitve network egressa (manj dela, n8n nalaga samo v
aplikacijo), ali pa gremo prek Microsoft 365 (dokazano, a nov credential v n8n in dodatna vozlišča).

Vmesna pot, ki ne potrebuje nikogar: ko `/api/images` obstaja, človek odpre dva javna URL-ja in sliki
povleče v Coworkov pogovor. Podrobneje v `docs/spec-app-strojni-vhod.md`, razdelek
»Pogoj zunaj aplikacije«.
