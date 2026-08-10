---
name: frodx-content-factory
description: Run the FrodX content production chain end to end - pick an AEO topic, write the column, run the critique loop, transcreate to EN and HR, generate the key visual, enrich publishing metadata and hand the package to the publishing app. Use whenever Igor wants to start a new column, blog post or content run for frodx.com, including when he only says "nova kolumna", "nova vsebina", "zaženi tovarno" or names a topic he wants written. This is the single entry point - it calls the other frodx skills itself.
metadata:
  version: 0.1.0
---

# FrodX Content Factory - dirigent

Ta skill vodi produkcijo ene kolumne skozi sedem korakov. Igor kliče samo tega; ostale skille kličeš ti.

## Načelo

Ti si dirigent, ne pisec. Vsebino delajo podskilli. Tvoja naloga je: pripravi stanje, pokliči pravi skill, zapiši rezultat v `state.json`, počakaj na Igorjevo potrditev, pojdi naprej.

**Nikoli ne greš čez gate brez izrecne potrditve.** Ne domnevaj, da je »ok« pomenilo »in nadaljuj z vsem ostalim«. Potrditev velja za en korak.

## Zagon

1. Če Igor ni povedal teme, pokliči `frodx-topic-pick`. Ta prebere Excel in predlaga teme.
2. Ko je tema izbrana, ustvari tek:

```bash
python3 scripts/init_run.py "<naslov teme>" runs
```

Skripta izpiše pot do `state.json`. Če pove, da tek že obstaja, vprašaj Igorja, ali nadaljuje obstoječega ali začne novega z drugačnim naslovom.

3. Preberi `references/state-schema.md`, da veš, kdo zapolni katero polje.

## Koraki

Po vsakem koraku: zapiši rezultat v `state.json`, dvigni `_run.step`, nastavi `_run.status` na `awaiting_approval`, pokaži Igorju rezultat in vprašaj za potrditev. Ob potrditvi zapiši čas v `_run.approvals`.

| Korak | Skill | Kaj vprašaš Igorja |
|---|---|---|
| 1 | `frodx-topic-pick` | katero temo pišemo |
| 2 | `igor-column-writer` | je kolumna v redu |
| 3 | `frodx-critique-loop` | je popravljena verzija v redu |
| 4 | `frodx-transcreation` | sta EN in HR v redu |
| 5 | `frodx-image-run` | je slika v redu |
| 6 | `frodx-publishing-meta` | so meta podatki v redu |
| 7 | `frodx-publish-send` | (brez vprašanja, samo pošlje) |

Korak 2 je Igorjev skill in sme prekiniti z vprašanji o hooku, tezi in številkah. To je pričakovano - pusti ga.

Korak 4 kliči dvakrat: SL→EN in SL→HR. Hrvaščina rabi native pregled; če Igor pove, da ga bo opravil nekdo drug, počakaj in tega ne obidi.

## Nadaljevanje prekinjenega teka

Če Igor reče »nadaljuj kolumno X«, poišči `runs/*-<slug>/state.json`, preberi `_run.step` in nadaljuj z naslednjim korakom. Ne ponavljaj korakov, ki so že opravljeni, razen če Igor to izrecno zahteva.

## Kdaj se ustaviš

- Excel nima novih tem - povej in končaj. Ne izmišljaj tem.
- Podskill vrne napako, ki je ne znaš popraviti - povej, kaj je vrnil, in vprašaj.
- Korak 7 javi kršitve - povej, katera polja manjkajo, in ponudi vrnitev na pristojni korak. Ne popravljaj paketa mimo skilla, ki je za polje odgovoren.
