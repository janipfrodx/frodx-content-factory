# Croatian reference – fingerprint classes, Serbian discrimination, typography, anchors

Target standard: contemporary Croatian as used in Croatia by an educated native copywriter in the relevant context. Two contaminations disqualify a text: Slovenian traces (the source bleeding through) and Serbian/Bosnian/Montenegrin forms (the wrong standard bleeding in). Check for both in every sentence.

**How to weight these rules.** Not every rule below carries the same force. Each is tagged, and the tag maps to the report's finding classes: **[FAIL]** = incorrect for published Croatian copy, drives the score down hard; **[FLAG]** = acceptable Croatian but marked or unedited in polished copy – classify as acceptable-but-unnatural and fix by default; **[STYLE]** = both options are correct, note the more polished one only when it genuinely improves the text – style notes never turn a PASS into a FAIL. Untagged rules are [FAIL].

## 1. Croatian, not Serbian

LLMs and non-native writers drift into Serbian more often than into any other error class. Unless the user explicitly requests a regional variant:

**Umbrella rule:** any ekavian form (`gde`, `lepo`, `vreme`, `uspešno`, `celokupan`, `posle`…) is an instant FAIL flag – Croatian is ijekavian (`gdje`, `lijepo`, `vrijeme`, `uspješno`, `cjelokupan`, `poslije`).

**Standard-pair table** (Croatian ✓ / Serbian ✗) – business-relevant selection:

| Croatian ✓ | Serbian ✗ |
|---|---|
| tisuća | hiljada |
| uvjet | uslov |
| također | takođe |
| tko, netko, nitko | ko, neko, niko |
| opći | opšti |
| točno, točka | tačno, tačka |
| tjedan | sedmica, nedelja |
| Europa, europski | Evropa, evropski |
| izvješće, izvještaj | izveštaj |
| suradnja | saradnja |
| suvremen | savremen |
| vjerojatno | verovatno |
| kvaliteta (f.) | kvalitet (m.) |
| povijest | istorija |
| posjet | poseta |
| prosinac, siječanj… | decembar, januar… |

**[FLAG] Marked internationalisms:** `sistem` and `nivo` are not Serbian-exclusive – both occur in informal Croatian – but in published B2B copy they read eastern or unedited. Default to `sustav` and `razina`; classify occurrences as acceptable-but-unnatural, not incorrect, and respect an explicit client glossary that says otherwise.

**Verb morphology (borrowed stems only):** for verbs built on international stems, Croatian uses `-irati` (organizirati, realizirati, definirati, funkcionirati); the Serbian counterparts end in `-ovati`/`-isati` (organizovati, realizovati, definisati, funkcionisati). This rule covers borrowed stems only – native `-ovati` verbs (kupovati, poslovati, putovati, radovati se, sudjelovati) are fully Croatian and must never be flagged.

**[FLAG] `da` + present vs. infinitive (same subject only):** when the subject of both verbs is the same, Croatian complements modal and volitional verbs with the infinitive – `želimo postići`, `moramo provjeriti`, `planiramo pokrenuti` – while Serbian uses `da` + present (`želimo da postignemo`). With different subjects, `da` + present is correct and obligatory Croatian (`želimo da vi odlučite`); never "fix" those. A single same-subject da-construction is marked, not incorrect; a pattern of them across the text is an eastern fingerprint and sinks the score through accumulated flags.

**[FLAG] `da li` vs. inversion:** prefer `je li…`, `možete li…`, `koristite li…`; `da li` is common in speech but reads Serbian-leaning in polished Croatian copy.

**Months:** Croatian months are siječanj, veljača, ožujak, travanj, svibanj, lipanj, srpanj, kolovoz, rujan, listopad, studeni, prosinac. Here Slovenian and Serbian conspire: Slovenian `januar`–`december` left in a Croatian text reads Serbian. Every date is a checkpoint.

## 2. Slovenian → Croatian false friends and calques

Words and phrases that survive translation because they look Croatian but are not, or not in that meaning:

| Slovenian source | Wrong in Croatian | Natural Croatian |
|---|---|---|
| stranka (= klient) | stranka | **klijent** or **kupac** in marketing/CRM/B2B copy; hr. `stranka` is itself correct for legal clients, parties in proceedings, and counter service (`primamo stranke`) – context decides |
| trg (= tržišče) | trg | **tržište** (hr. trg = gradski trg) |
| naslov (= poštni) | naslov | **adresa** (hr. naslov = title) |
| zvestoba, program zvestobe | zvestoba | **vjernost, program vjernosti** |
| izkušnja, uporabniška izkušnja | izkušnja | **iskustvo, korisničko iskustvo** |
| zaenkrat | za enkrat | **zasad, zasada** |
| v kolikor | u kolikor | **ako** (or ukoliko, sparingly) |
| izpostaviti | izpostaviti | **istaknuti, naglasiti** |
| obravnavati | obravnavati | **obraditi, razmatrati** |
| spletna stran | spletna stranica | **web-stranica, internetska stranica** |
| hitro | hitro | **brzo** (hr. hitro is marked/archaic) |
| tudi (clause-initial) | takođe/također as filler | usually **i** woven into the clause, or restructure |

Treat these as patterns: the table is a detector, not a substitution list. Always decide from context.

## 3. Grammar fingerprints of a Slovenian writer

**Conditional agreement – the loudest single tell.** Slovenian `bi` is invariant across persons; Croatian conjugates: `bih, bi, bi, bismo, biste, bi`. A Slovenian hand writes `mi bi napravili`, `da bi ste vidjeli` – Croatian requires `mi bismo napravili`, `da biste vidjeli`. Check every conditional.

**[FLAG] Purpose clauses:** `kako bi` (with agreement: `kako bismo poboljšali prodaju`) is the characteristic Croatian purpose connector in polished copy; `da bi` purpose clauses are acceptable Croatian. Flag `da bi` when it mirrors the Slovenian clause shape sentence for sentence – that is shadow-test evidence, not an error on its own. Conditional agreement inside the connector stays [FAIL] either way (`kako bi ste` → `kako biste`).

**Future formation:** Slovenian builds the future as `bomo poslali`; Croatian as `poslat ćemo` / `mi ćemo poslati`, with the enclitic in second position. Watch for source-shaped futures and for pseudo-futures like `budemo poslali` outside genuine conditional/temporal contexts.

**[STYLE] Clitic placement (second position):** both orders are grammatical Croatian, but enclitics (`je, se, ćemo, mi, ga…`) gravitating to the Wackernagel position is what distinguishes polished copywriting: `Vaš će tim dobiti pristup u roku od 24 sata` over `Vaš tim će dobiti pristup…`. Suggest the split only where it reads better; never count the unsplit order against the score. A clitic in sentence-initial position, however, is [FAIL].

**Aspect:** verify that verb aspect expresses the intended completion, repetition, duration, or habit; do not copy the Slovenian choice mechanically. Recurring benefit statements usually want the imperfective (`ostvarujete popust pri svakoj kupnji`), one-time actions the perfective.

## 4. Prepositions and cases

Check every prepositional phrase independently – cognate nouns do not guarantee the same government:

- `posjet` + **dative**: `posjet muzeju`, `posjet web-stranici` (Slovenian obisk + genitive bleeds in as `posjet muzeja`).
- `radovati se` + **dative**: `radujemo se vašem dolasku` (not the Slovenian-shaped genitive `veselimo se vašega prihoda` pattern).
- **[FLAG]** `zahvaliti komu **na** čemu`: `zahvaljujemo na povjerenju` is the editor's choice in business copy; `zahvaljujemo se za povjerenje` also occurs natively, so alone it proves nothing about translated origin – flag and fix, don't treat it as decisive evidence.
- `čestitati komu **na** čemu` (not `za`).
- `u vezi **s** čime` (instrumental): `u vezi s time`; `u vezi toga` is colloquial/Serbian-leaning.
- Prefer `kod njih` for "at that company" (`tamo dobiješ popust` → `kod njih ostvarujete popust`).

## 5. Register and rhythm

Keep the text consistently formal or conversational, expert or accessible, corporate or human. Croatian B2B copy addresses the reader with **vi** (FrodX house rule: vikanje in all client-facing documents). Avoid mixing conversational directness with bureaucratic abstraction unless the contrast is intentional. Read every sentence aloud mentally: if the stress lands on the wrong information or the sentence needs rereading, it fails regardless of grammar.

**Croatian slop vocabulary** (AI-generated marketing filler – reject in any mode): `u današnjem dinamičnom poslovnom okruženju`, `podignite svoje poslovanje na višu razinu`, `revolucionarno rješenje`, `nije samo X, već Y` scaffolding, formulaic triads, exclamation-mark enthusiasm absent from the source.

## 6. Typography

**Client mode – Croatian standard:**

- Quotation marks: `„…”` – opening low double (U+201E), **closing right double (U+201D)**. The Slovenian/German closing `“` (U+201C) in a Croatian text is itself a source fingerprint. `»…«` is an accepted alternative; interface strings may require straight quotes.
- Dashes: **crtica** `–` (en dash, U+2013) with spaces for parenthetical breaks; **spojnica** `-` inside compounds; numeric ranges without spaces (`10–15`). The em dash (U+2014) is not Croatian typography – never use it.
- Decimal comma, thousands separated by a dot or thin space: `30.000 članova`, `1.500,00 EUR`.
- Dates written out use Croatian months in the genitive: `28. kolovoza 2026.` – with the terminal period after the year.

**House mode – FrodX overrides (on top of the standard):** en dash `–` in newsletters and formal documents, spaced hyphen ` - ` on the blog, never U+2014 anywhere; the banned phrase family (`ovdje je trik` and variants) fails the audit on sight.

## 7. Calibration anchors

Score against these before committing to a number:

- **≈96 (PASS):** `Kod njih ostvarujete popust pri svakoj kupnji, a bodove možete iskoristiti već sljedeći mjesec.` – natural collocations, native clitic and case behaviour, nothing to fix.
- **≈87 (PASS WITH MINOR EDITS):** `Naš program vjernosti nudi vam mogućnost da ostvarite popust pri svakoj kupnji.` – grammatical and mostly natural, but `nudi vam mogućnost da` is imported flab; a native writes `U našem programu vjernosti ostvarujete popust pri svakoj kupnji.`
- **≈70 (FAIL):** `U kolikor želite dodati novo nagrađivano ponašanje, provjerite koja ponašanja želite poticati kod vaših kupaca.` – grammatically parseable, but `u kolikor` is Slovenian, `dodati nagrađivano ponašanje` is a calque, and `kod vaših kupaca` is source-shaped; the sentence reconstructs its Slovenian original almost word for word.

## Harvested corrections (append-only)

Patterns caught in production. Append: wrong form → natural form, one-line rationale, date.

- `dodati novo nagrađivano ponašanje` → `početi nagrađivati neko novo ponašanje` – noun-stack calque of the Slovenian nominal phrase; Croatian resolves it verbally.
- `provjeravati koja ponašanja poticati` → `preispitivati koja ponašanja želimo potaknuti` – bare infinitive question is source syntax; Croatian wants the finite clause.
- `tamo dobiješ popust` (about a company) → `kod njih dobiješ popust` – locative `tamo` is the Slovenian deixis; Croatian points at the party, not the place.
- `programi s bazom iznad 30.000 kupaca` → `programi s više od 30.000 članova` – `baza kupaca` is CRM-Slovenian; loyalty programmes have members.
