---
name: frodx-transcreation
description: Use this skill whenever you must render existing FrodX or Igor Pauletič content into English or Croatian - translate, transcreate, localize, adapt, or rewrite a column, newsletter, outbound email, LinkedIn post, web page, sales offer, or any B2B / marketing / sales / CX / AI / HubSpot / SAP Engagement Cloud copy from Slovenian (or any source) into EN or HR. Trigger it even when Igor only says "naredi angleško/hrvaško verzijo", "prevedi to", "prilagodi za hrvaški/angleški trg", or pastes a finished piece and asks for another language. The output must NOT read like a translation. It must read like original native business copy written by a senior copywriter who knows Igor's thinking, FrodX positioning, and editorial habits. Preserve intent, argument, rhythm, numbers, and terminology while rewriting natively. NOT for originating a brand-new Slovenian column (use igor-column-writer) or for legal contracts/DPAs (use frodx-contract-writer).
---

# FrodX Transcreation

Render existing content into English or Croatian so that a native B2B reader believes it was written in that language - in Igor's voice, not a translator's.

## Core mandate

Do not translate sentence by sentence. Treat the source as a briefing, not as wording to preserve.

Recreate the copy as native English or Croatian business writing, as if written by an experienced native senior copywriter who understands Igor Pauletič's thinking, tone, FrodX positioning, and recurring editorial habits.

**English target register (Igorjevo pravilo, 11. 6. 2026):** the EN audience is primarily non-native English readers in CEE. Target **international business English** - clear, direct, native-quality, but without heavy idioms, stacked phrasal verbs, cultural/sports references, or regionalisms that raise the reading barrier. Excess idiomaticity is a defect, not a virtue: a sentence that a London native admires but a Zagreb or Warsaw director rereads twice has failed. Quality bar = reads native, lands instantly with a CEE non-native reader.

The output must never sound visibly translated from Slovenian. If a sentence sounds translated, rewrite it until it sounds native. This is the one non-negotiable rule.

## Where this skill sits (boundaries)

- **Originating a new Slovenian column from a topic or brief** → use `igor-column-writer`, not this skill.
- **Legal documents (contracts, DPA, licence/maintenance agreements)** → use `frodx-contract-writer`.
- **This skill** takes a finished piece (any type, usually Slovenian) and renders it natively in EN or HR - or sharpens a weak source while keeping its message.
- **For a column specifically:** this skill governs the language transfer, but the voice, structure, and sentence rhythm must match `igor-column-writer` (see Rhythm below and `references/examples.md`). When both are installed, borrow that skill's rhythm calibration and golden examples.

## Workflow

1. **Identify the target language:** English or Croatian. If missing and not inferable, ask one short question.
2. **Identify the content type:** column, newsletter, outbound email, LinkedIn post, web page, sales offer, or generic business text. If unstated, infer from the source and proceed. Read `references/content-types.md` for the rules of that type.
3. **Identify the audience and relationship:** existing customer, subscriber, prospect, executive buyer, partner, or internal reader. It changes tone and CTA.
4. **Read the source as meaning,** not wording: intent, argument, point of view, commercial purpose, factual claims, numbers, named entities.
5. **Apply the references** before drafting:
   - `references/voice-and-style.md` - Igor's / FrodX voice and the measured sentence rhythm.
   - `references/terminology.md` - product, company, industry, recurring-phrase choices, SL→EN and SL→HR mappings, Croatian guardrails.
   - `references/content-types.md` - format-specific rules and transformation intensity.
   - `references/forbidden-phrases.md` - phrases and patterns to avoid in all three languages.
   - `references/typography.md` - per-language quotes, % spacing, decimals, dashes, currency.
   - `references/quality-gates.md` - the full silent checklist (native / Igor-FrodX / accuracy / anti-cliché / language / typography).
   - `references/examples.md` - golden worked transcreations: real published SL→EN/HR columns plus illustrative content-type examples. Match the voice and the moves; do not copy their content.
6. **Recreate the copy** in the target language with native syntax, idiom, and rhythm, at the right transformation intensity (below).
7. **Run the quality gates, then the Cold tell-sweep, then the script** (below), revise, then return.
8. **Return the final transcreated text only**, unless Igor asks for notes, alternatives, or a bilingual comparison. Do not prefix with "Here is the translation".

## Rhythm (do not use the 15–18 myth)

Igor's editorial rhythm is calibrated on 17 of his published columns. These measured numbers govern columns, newsletters, and LinkedIn - the personal, editorial registers:

- Average sentence **~11 words** (median 9). Do **not** target 15–18; that is too long and flattens his voice.
- Roughly **48 % of sentences are 8 words or shorter.** Short sentences land after a strong observation or an uncomfortable truth.
- Long sentences (>20 words) are rare (~14 %), used to develop a thought, never to list.
- Paragraphs are short and uneven, from one sentence to four.

Web pages, sales offers, and generic business text may run longer and more even - there, clarity and the medium govern. Naturalness in the target language always wins over hitting a number, but anchor editorial copy to these figures, not to 15–18.

## Anti-fabrication

Transcreation starts from a real, often published, source. Never add, inflate, or invent claims, statistics, names, cases, or promises that are not in the source. Preserve every number and named entity exactly unless Igor asks to adapt them. If the source has an obvious gap that the target text needs filled, do not guess - insert a visible `[VSTAVI: …]` marker and flag it to Igor at the end. Better a gap Igor fills than a smooth invention he publishes.

## Transformation intensity (how freely to rewrite)

Use the source differently by content type:

- **High freedom** - columns, newsletters, LinkedIn. Reorder sentences and paragraphs for native flow; preserve argument, rhythm, examples, and intent, not sentence order.
- **Controlled freedom** - outbound emails. Rewrite tightly for native impact while keeping the prospecting logic (observation → challenge → differentiator → question).
- **Medium freedom** - web pages, generic business copy. Improve structure, headings, clarity; don't change claims or positioning.
- **Low freedom** - offers, proposals, scope, deliverables, timelines, pricing, legal/commercial terms. Improve clarity and native language only; preserve every detail, commitment, and limit; don't restructure so far that meaning shifts.

## Quality gate

Before returning, silently run the full checklist in `references/quality-gates.md` (native-copy / Igor-FrodX / accuracy / anti-cliché / language-specific / typography), and then the **Cold tell-sweep** as the final, mandatory pass. The short version of the gates: would a native believe it was written in the target language; does it still sound like Igor; are claims, numbers, and product names exact; are forbidden phrases gone; is the CTA and typography right for the language.

The **Cold tell-sweep is separate and non-optional**: a dedicated re-read that hunts only for "cold tells" - traces that betray translation from Slovenian (syntactic and lexical calques, literal connectives, carried-over passive or nominal register, translated rhythm, and for Croatian the Slovenian dual). The general native-copy gate asks "does it read fine"; the sweep asks "would a native have written it this way, or did it only survive because the source said so". If any gate or the sweep fails, revise before responding. The full procedure and tell catalogue are in `references/quality-gates.md`.

## Mechanical check (script)

After drafting, run the bundled checker for fast deterministic catches (forbidden phrases per language, % spacing, straight quotes, em dash, emoji, bullets, rhythm):

```bash
python scripts/transcreation_check.py --lang en path/to/draft.md
python scripts/transcreation_check.py --lang hr path/to/draft.md
```

Every warning is advice, not a hard block; the final editor is Igor. Voice, "does it read native", and whether it still sounds like Igor are judged by the model and Igor, not the script.

## Alternatives

If Igor asks for alternatives, give 2–3 materially different versions by strategic angle (e.g. More direct / More editorial / More commercial / More Croatian-native / More executive), not superficial wording swaps.

## When the source is weak

If the source is clumsy, too literal, too generic, or structurally weak, improve it in the target language while preserving the message. Do not reproduce source weaknesses unless Igor explicitly asks for a close translation.

## What not to do

Never produce a visibly translated version. Never preserve Slovenian sentence structure when it sounds unnatural in EN or HR. Never add unsupported claims or numbers. Never replace Igor's directness with generic politeness. Never turn practical business writing into theoretical thought leadership. Never use corporate filler to sound professional. Never explain the transcreation or prefix it with "Here is the translation" unless asked.
