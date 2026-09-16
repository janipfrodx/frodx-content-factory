# Vir tem: HubSpot AEO

Vir ni datoteka. Teme bereš neposredno iz HubSpot AEO portala prek konektorja, ki je v Coworku na
voljo. Nič se ne prepisuje vmes in nič ne zastara.

## Business unit

`businessUnitId: 0`, ime `FrodX`. Portal ima danes eno samo enoto. Če bi jih kdaj bilo več, jih
našteje `get_aeo_metrics` z `include: ["BUSINESS_UNITS"]` - ID-ja ne ugibaj.

## Kandidati: sledeni prompti

`get_aeo_metrics`, `include: ["PROMPTS"]`, `maxPrompts: 100`.

| Polje | Kaj je |
| --- | --- |
| `id` | ključ prompta; gre v `AEO-Picks.prompt_id` in v `_run.topic_source.hubspot_prompt_id` |
| `prompt` | dobesedno vprašanje. **To JE `target_prompt`**, ne izpeljanka |
| `visibility` | delež tekov, v katerih je FrodX omenjen |
| `citationCount` | skupno število virov, ki jih AI na to vprašanje navede - **ne** FrodXovih |
| `averageCompetitorsMentioned` | koliko konkurentov AI povprečno našteje |
| `buyingJourneyPhase` | `AWARENESS`, `CONSIDERATION`, `EVALUATION`, `DECISION` |
| `language` | jezik prompta; informativno, veriga transkreira vedno v vse tri jezike |
| `icpNames`, `productNames` | na koga in na kateri storitveni sklop je prompt vezan |

**Kako nastane `visibility`.** Vsak prompt se požene trikrat, po enkrat na asistenta: ChatGPT,
Gemini, Perplexity. `visibility` je delež teh tekov, v katerih je FrodX omenjen, zato so edine možne
vrednosti 0, 33, 66 in 100. Vidnost 33 je ena sama omemba pri enem asistentu - to ni prisotnost.

**Prag:** obdrži prompte z `visibility < 66`.

## Kontekst: priporočila

`manage_aeo_recommendations`, operacija LIST, `businessUnitId: 0`, `status: "NEW"`.

Uporabna polja: `id`, `promptId`, `priority`, `score`, `title`, `summary`, `justification`,
`actionChannel`, `contentType`, `contentTitle`, `contentTopic`, `influencingCitations`.

**Vezava na prompt ima dve obliki in ju ne smeš mešati:**

- `promptId` je enak `prompt.id` - priporočilo **pripada** temu promptu;
- `promptId` je `0` - priporočilo je portalsko. Smeš ga navesti kot splošen kontekst, nikoli pa
  trditi, da je nastalo iz tega prompta.

**Kot predlog formata šteje samo** `actionChannel: "OWNED_CONTENT"` in `contentType` eden od
`COMPARISON`, `GUIDE`, `LISTICLE_COMPARISON`. `PRODUCT` je produktna stran, ne kolumna.

Priporočil za `YOUTUBE`, `LINKEDIN_ARTICLE`, `LINKEDIN_POST`, `REDDIT` in `AFFILIATE` ne izloči
tiho: če za izbrani prompt obstajajo, to povej Igorju kot dejstvo (»HubSpot za ta gap priporoča
video, ne članka«). Vpliva na to, ali se kolumne sploh splača lotiti.

## Česa ne kličeš

- **`START_ACTION`** na priporočilu. HubSpot zna priporočilo sam spremeniti v objavljen blog post.
  To obide Igorja, kritiko in transkreacijo - ni naša veriga.
- **`manage_aeo_prompts` CREATE.** Kapaciteta promptov je polna in izbira promptov je strateška
  odločitev, ne posledica izbire teme.

## Zgodovina izbir: `AEO-Picks`

n8n Data Table, projekt `Content Factory` (`projectId: "FucXmQlDiWLVsRHW"`),
`dataTableId: "ZiQz5Nb1Rm9W2hGZ"`.

| Stolpec | Tip | Vsebina |
| --- | --- | --- |
| `prompt_id` | string | `id` izbranega prompta |
| `recommendation_id` | string | `id` priporočila, prazen niz, če ga ni |
| `topic` | string | tema, kot jo je Igor izbral |
| `target_prompt` | string | dobesedno besedilo prompta |
| `run_slug` | string | slug teka, ki ga izpiše `init_run.py` |
| `picked_at` | date | ISO čas Igorjeve izbire |

**Branje:** `get_data_table_rows`. Prompt, katerega `id` je že med `prompt_id`, ni kandidat.

**Pisanje:** `add_data_table_rows`, ena vrstica ob izbiri.

**Posodobitve ni** in ni potrebna: tabela beleži izbire, ne izidov. Če tek propade in se tema
sprosti, vrstico ročno zbriše človek v n8n vmesniku. To je edino mesto, kjer se tabela kdaj
spreminja, in je človekova odločitev.
