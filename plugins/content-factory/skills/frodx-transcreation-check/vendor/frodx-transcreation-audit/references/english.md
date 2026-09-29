# English reference – fingerprint classes, variety discipline, typography, anchors

Target standard: natural contemporary English written by an educated native writer for the relevant market. Slovenian leaves two kinds of trace in English: what the source grammar lacks (articles, definiteness, aspect distinctions – errors of omission) and what it imports (calques, false friends, source-shaped syntax – errors of transfer). Check for both in every sentence.

**How to weight these rules.** Tags map to the report's finding classes: **[FAIL]** = incorrect for published English copy, drives the score down hard; **[FLAG]** = grammatical but marked or unedited in polished copy – classify as acceptable-but-unnatural and fix by default; **[STYLE]** = both options are correct, note the more polished one only when it genuinely improves the text – style notes never turn a PASS into a FAIL. Untagged rules are [FAIL].

## 1. Choose and hold one English variety

Follow the variety requested by the user or established by the brand, publication, or surrounding copy. If none is specified: infer from evidence; otherwise default to **EN-INTL** (British spelling, restrained punctuation, no regionalisms) and state the choice in the verdict line. Never mix varieties within a text:

- spelling pairs: `programme/program`, `behaviour/behavior`, `organisation/organization`, `-ise/-ize`, `licence/license` (BrE noun/verb);
- punctuation: AmE double quotes with periods inside; BrE commonly single quotes with logical punctuation; serial comma per house style, applied consistently;
- dates: `28 August 2026` (BrE/INTL) vs. `August 28, 2026` (AmE);
- collective nouns: AmE singular (`the team is`), BrE tolerant of plural.

## 2. Articles and definiteness – interference class no. 1

Slovenian has no articles, so every English noun phrase is a decision the source never made. For each one, resolve: first mention or already identifiable; specific or generic; singular countable, plural countable, or uncountable; role, institution, product, abstract, or proper name.

The two signature Slovenian errors:

- **Missing `the`** before nouns the context has already defined: `results of survey show` → `the results of the survey show`.
- **Spurious `the`** before generic plurals and abstracts: `the loyalty programmes fail when…` → `loyalty programmes fail when…`; `the loyalty is built through behaviour` → `loyalty is built through behaviour`.

Do not add articles mechanically – resolve intended definiteness from context.

## 3. Countability and determiners

Check nouns whose English countability differs from Slovenian usage: `information`, `advice`, `feedback`, `research`, `training` (`trainings` → `training sessions`), `equipment`, `work`, `staff`, `content`, `know-how`, `progress`; `data` per register and house style. Reject quantifiers, plurals, and agreement modelled on Slovenian number or case patterns (`feedbacks`, `an advice`, `many equipment`).

## 4. False friends and misleading cognates

| Slovenian source | Wrong in English | Natural English |
|---|---|---|
| aktualen | actual | **current, topical** |
| eventualno | eventually | **possibly, perhaps** |
| kontrolirati | control | **check, review, monitor** |
| realizirati | realise | **implement, deliver, achieve** |
| akcija | action | **promotion, campaign, sale** |
| termin | term | **appointment, slot, date** |
| provizija | provision | **commission** |
| evidenca | evidence | **records, register** |
| prospekt | prospect | **brochure, leaflet** |
| simpatičen | sympathetic | **likeable, appealing** |
| konkretno | concretely | **specifically, in concrete terms** |

Choose by intended meaning, never by orthographic similarity.

## 5. Calques and structural flab

The recurring Slovenian-shaped phrases in business English:

- `in the frame of / within the frame of` (v okviru) → **as part of, within**
- `from the side of X` (s strani) → **by X**, or restructure to active voice
- `you have the possibility to` / `gives you the possibility` (imate možnost) → **you can / lets you**
- `till Friday` for a deadline (do petka) → **by Friday** (deadline ≠ duration)
- `till now` → **so far, to date**
- `we are on the market already 15 years` → **we've been in business for 15 years** (company existence) or **we've operated in this market for 15 years** (industry presence); bare `in the market for` misreads as shopping intent
- `according to our opinion` → **in our view**
- `on a daily basis` → **daily**
- `the price is 500 €` → **€500** (symbol placement, flab cut)

## 6. Syntax and information order

Check natural placement of subjects, verbs, adverbs, and qualifiers; excessive front-loading of context before the point (`In the case that the customer…` → `If the customer…`); long noun stacks transplanted from Slovenian nominal phrases; overuse of passive, impersonal, and nominal constructions where English wants a verb; possessive spam (`your customers… your programme… your data` in one sentence); relative clauses and participles preserving source structure; emphasis that follows Slovenian rather than English discourse flow. When local edits cannot remove the source shape, rebuild the sentence from intent.

## 7. Tense, aspect, and modality

Do not map Slovenian tense forms directly. Choose deliberately between simple and progressive; past simple and present perfect (`since 15 years` → `for 15 years`, with the perfect); habitual and one-off; active and passive; `will/would/can/could/should/must` and non-modal alternatives. Check conditionals, sequence of tenses, and time expressions as complete units – Slovenian leaves aspect and definiteness implicit, so the English must make a choice the source never voiced.

## 8. Prepositions and phrasal verbs

Check every verb–preposition pair independently; the classic Slavic transfers: `discuss about` → `discuss`; `depends from` → `depends on`; `participate on` → `participate in`; `consist from` → `consist of`; `answer on the question` → `answer the question`; `on the meeting` → `at/in the meeting`; `on the market` → usually `in the market`. Prefer the natural phrasal verb over Latinate formality when register allows (`falls short` over `exhibits a deficiency`).

## 9. Register

Keep the text consistently formal or conversational, expert or accessible, corporate or human, direct or tactful. Use contractions when the chosen voice naturally calls for them. Do not let marketing or UX copy turn academic just because the source uses abstract nouns – and do not add enthusiasm the source does not carry.

**English slop vocabulary**, two tiers:

- **[FAIL] Hard-reject (no legitimate marketing use):** `delve`, `game-changer`, `in today's fast-paced world`, `the best part?`, `it's not just X, it's Y` scaffolding, formulaic triads, em-dash-driven rhythm, repetitive sentence openings.
- **[FLAG] Register-scoped (reject in marketing voice, legitimate in literal or technical use):** `robust`, `seamless`, `leverage` (verb), `unlock`, `elevate`, `empower`. "A robust retry mechanism" in developer docs passes; "a robust solution for your business" in a campaign does not. The problem is the marketing usage, not the word.

## 10. Typography and mechanics

**Client mode – per the chosen variety:** quotation marks, serial comma, title vs. sentence case, and dashes follow the variety and the client's house style. The em dash is legitimate in AmE prose – but flag AI-pattern overuse (several per paragraph, rhythm built on interruption). Numbers localize: Slovenian `1.500,00 EUR` becomes `€1,500.00`; decimal point, thousands comma; dates per variety. Buttons, labels, and headings keep functional meaning and consistent capitalization.

**House mode – FrodX overrides:** never the em dash (U+2014) in any English text; en dash `–` in newsletters and formal documents, spaced hyphen ` - ` on the blog; the banned phrase family (`here's the trick` and variants) fails the audit on sight.

## 11. Calibration anchors

Score against these before committing to a number:

- **≈96 (PASS):** `You'll see exactly where your programme falls short and what to fix first.` – native collocation, natural rhythm, correct articles; nothing to fix.
- **≈87 (PASS WITH MINOR EDITS):** `Our loyalty programme offers you the possibility to earn points with every purchase.` – grammatical, but `offers you the possibility to` is imported flab; a native writes `Our loyalty programme lets you earn points with every purchase.`
- **≈70 (FAIL):** `Within the frame of our loyalty programme, customers have the possibility to collect points with every purchase and use them already at the next visit.` – grammatically parseable, but the frame calque, the possibility flab, and the misplaced `already` reconstruct the Slovenian original almost clause for clause.

## Harvested corrections (append-only)

Patterns caught in production. Append: wrong form → natural form, one-line rationale, date.

- `add a new rewarded behaviour` → `start rewarding a new behaviour` – noun-stack calque; English resolves it verbally.
- `check which behaviours to encourage` → `review which behaviours we want to encourage` – bare infinitive question is source syntax.
- `programmes with a base above 30,000 customers` → `programmes with more than 30,000 members` – `customer base` misapplied; loyalty programmes have members.
- `where your programme misses` → `where your programme falls short` – collocation; `miss` needs an object here.
- `loyalty arises from behaviour and identity` → `loyalty is built through behaviour and identity` – `arises from` is register-mismatched for marketing copy.
- `when the customer is currently not buying` → `when customers aren't buying` – drop `currently` (redundant with the progressive) and the singular-generic `the customer`; the earlier fix `when customers are not making a purchase` failed its own native-origin test (nominalization).
