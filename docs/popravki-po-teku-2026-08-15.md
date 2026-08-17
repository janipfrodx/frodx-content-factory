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
