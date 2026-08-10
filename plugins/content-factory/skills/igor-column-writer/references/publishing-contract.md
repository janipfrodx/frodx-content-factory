# Publishing pogodba: docx → Janijeva aplikacija → n8n

Izpeljano iz realnega para vhod/izhod (11. 6. 2026):
- vhod: `Publishing_CRM-zaposlujete__1__1.docx`
- izhod: `ne-kupujete-crm-ja-zaposlujete-n8n-payload-2026-06-11.json` (parser verzija **1.1**)
- webhook: `https://frodxai.app.n8n.cloud/webhook/frodx-publish`

Ta dokument je **API pogodba**. Struktura docx-a, ki jo generira
`scripts/build_publishing.py`, ni redakcijska konvencija, ampak vhodni format
Janijevega parserja. Vsaka sprememba strukture mora iti skozi
`scripts/contract_check.py` in mimo te datoteke.

## 1. Struktura docx (kar parser bere)

Natančno zaporedje Heading nivojev:

```
## Slovenščina          (Heading 2 - ime jezikovne sekcije, dobesedno)
# <SL naslov>           (Heading 1 - postane meta.title in languages.sl)
### <podnaslovi>        (Heading 3 - ostanejo del contenta)
## English
# <EN naslov>
### ...
## Hrvatski
# <HR naslov>
### ...
## Socialne objave      (Heading 2 - zadnja sekcija)
## Objava 1             (Heading 2 - build_publishing.py normalizira ### → ##)
## Objava 2
...
```

Pravila:
- Imena jezikovnih sekcij so dobesedna: `Slovenščina`, `English`, `Hrvatski`.
  Vrstni red: SL → EN → HR.
- Vsaka jezikovna sekcija ima **natanko en** Heading 1 (naslov kolumne).
- `## Socialne objave` je zadnja H2 sekcija; v njej so samo `## Objava N`,
  oštevilčene zaporedno od 1.
- Newsletter NI del paketa (odločitev 11. 6. 2026) - n8n pokriva samo
  HubSpot osnutke kolumn in social objave.

## 2. Kaj parser naredi z vsebino (opazovano v JSON v1.1)

- `content.meta.title` = H1 slovenske sekcije.
- `content.languages.{sl,en,hr}.content` = celoten markdown sekcije,
  vključno z `# naslovom`, `### podnaslovi` in **markdown povezavami
  `[besedilo](url)`, ki se ohranijo**. Hiperpovezani viri v kolumni torej
  preživijo pot do HubSpota - v docx jih vedno vgradi kot žive povezave.
- `content.social_posts[]` = po ena postavka na `## Objava N`:
  `{ text, publish_date }`. Besedilo je gol tekst z `\n\n` med odstavki.
- `featuredImageUrl` = **ena** slika (Supabase storage URL) za vse tri
  jezike. Polja za alt tekst NI → frodx-key-visual zaenkrat ne rabi
  generirati trijezičnega alt teksta. (Odprto: ali HubSpot osnutek dobi
  alt - preveri ob prvem e2e pregledu.)
- `publishDate` na korenu + `publish_date` na vsaki social objavi.

## 3. Social objave - posebnosti pogodbe

- **Brez `[povezava]` placeholderja in brez URL-jev.** V opazovanem payloadu
  objave nimajo povezav; povezavo do kolumne doda n8n. Vsaka povezava ali
  placeholder v social besedilu je napaka.
- **Samo SL.** JSON na social objavi nima polja za jezik ali kanal - parser
  vse objave obravnava enako. Dokler parser ne loči jezikov, EN/HR social
  objave NE sodijo v docx (sicer bi šle na napačni kanal).
- Brez podnaslovov, brez markdown formatiranja (bold/italic se splošči).

## 4. Kaj NE prihaja iz docx-a (generira/vnese aplikacija)

Per-language SEO polja v JSON-u ne izvirajo iz docx-a:
`slug`, `seo_title`, `meta_description`, `topic_cluster`, `campaign_name`,
`tag_id/name/slug`.

Posledica: SEO meta opis, ki ga generira skill (kalibriran, Igorjev glas),
se trenutno IZGUBI - aplikacija ga nadomesti z generičnim. Znana šibkost
v1.1; rešitev zahteva spremembo na Janijevi strani (npr. da aplikacija
ponudi polje za prilepljen meta opis) in ni naša odločitev.

## 5. Validacija

Pred vsako oddajo v aplikacijo:

```
python scripts/contract_check.py <Publishing.docx>
```

Check je deterministična vrata (kot style_check / golden_check): ob kršitvi
vrne neničelno kodo in oddaja se ustavi. Številčne samoocene ne odločajo.

## 6. Verzioniranje

Parser ima `content.meta.version` (opazovano: `1.1`). Ob spremembi verzije
v payloadu: ponovno izpelji to pogodbo iz svežega para vhod/izhod in
posodobi contract_check.py.
