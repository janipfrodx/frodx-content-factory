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

**Rešitev:** workflow naj sliko naloži in vrne URL, ki ga dirigent pobere z enim ukazom.
Do takrat velja vmesni postopek: človek prenese sliki iz n8n UI v mapo teka
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
