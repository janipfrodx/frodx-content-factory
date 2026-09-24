---
name: frodx-transcreation-check
description: Second-opinion review of a finished Croatian or English transcreation. Sends the Slovenian source and the translation to GPT and Gemini through the n8n workflow cf-transcreation-check, judges their findings, and has frodx-transcreation redo the passages that fail. Use after a transcreation is produced and before it is approved, or when Igor asks "preveri hrvaščino", "je prevod v redu", "daj prevod v pregled". Catches Slovenian calques, Serbian vocabulary in Croatian, and over-idiomatic English for CEE readers.
metadata:
  version: 0.1.0
---

# Preverba transkreacije

Hrvaški in angleški prevod da v pregled GPT-ju in Geminiju, popravi po najdbah in ponovi. Na jezik
sta dovoljena največ **dva kroga**.

Ta skill teče znotraj koraka 4, po `frodx-transcreation` in **pred** Igorjevim gateom. Dirigent ga
pokliče dvakrat: enkrat za `hr`, enkrat za `en`.

## Zakaj obstaja

Claude pri hrvaščini občasno zgreši - slovenizem, srbizem, prenesena dvojina. Napake ne vidi sam,
ker jo je sam naredil. Drugo mnenje lovi; popravlja pa še vedno Igorjev transkreacijski skill, da
popravek ne obide njegovih pravil glasu.

## Postopek

Za dani jezik (`hr` ali `en`):

1. Preberi `state.json`. Vzemi `languages.sl.content` (izvirnik) in `languages.<jezik>.content`
   (prevod). Če je katero prazno, povej Igorju in končaj - preverjati ni česa.
2. Preberi `references/transcreation-check-prompt.md` v celoti. **Zamenjaj `{{DANES}}` z današnjim
   datumom** v obliki `18. 9. 2026`. Zamenjava se zgodi v nizu, ki ga pošlješ; datoteke ne
   spreminjaj. Brez tega ocenjevalca pravilne letnice razglasita za halucinacije - to se je
   15. 8. 2026 zgodilo pri kritiki kolumne, in oba modela imata presek znanja pred današnjim dnem.
3. Nastavi delovno spremenljivko `besedilo` = `languages.<jezik>.content`. To je vhod v **krog 1**.
4. Za `krog` = 1, 2 (največ dvakrat), ponavljaj:

   a. Kliči n8n workflow `eGHQGAbgeQhfCcZu` (webhook `transcreation-check`) prek `execute_workflow`.
   Telo gre gnezdeno pod `inputs.webhookData.body`:

   ```json
   {
     "workflowId": "eGHQGAbgeQhfCcZu",
     "executionMode": "manual",
     "triggerNodeName": "Trigger",
     "inputs": {
       "webhookData": {
         "method": "POST",
         "body": {
           "source_text": "<languages.sl.content>",
           "source_lang": "sl",
           "target_text": "<besedilo>",
           "target_lang": "<jezik>",
           "checkPrompt": "<vsebina prompta z vstavljenim datumom>"
         }
       }
     }
   }
   ```

   `target_lang` je jezik tega teka (`"hr"` ali `"en"`) - workflow `hr` privzame **samo**, kadar
   polje manjka; napačno trdo vpisan `"hr"` pri angleškem teku gre skozi nespremenjen.

   `executionMode` je `"manual"`, ker workflow ni aktiven. `"manual"` je izrecno dovoljen tudi za
   klice, ki dejansko kličejo zunanje storitve, ne le za suha testiranja.

   `source_text` je **vedno** izvirni `languages.sl.content` in se med krogi ne spreminja.
   `target_text` je vrednost `besedilo` v tem trenutku - v krogu 2 torej popravljena verzija iz
   kroga 1, nikoli izvirni prevod.

   b. Preberi odgovor. Ima vedno štiri polja:

   ```json
   {"openai": "<ocena>", "gemini": "<ocena>", "openai_error": null, "gemini_error": null}
   ```

   Ločenega klica `get_execution` ne potrebuješ - ta workflow odgovarja prek `Respond to Webhook`.

   **Če je polje `<model>_error` neprazno**, je tisto vozlišče padlo. To **ni sodba `ZA POPRAVEK`**:

   - **Padel eden:** nadaljuj s tistim, ki je odgovoril. V zapisu kroga in Igorju izrecno povej, da
     je polovica presoje manjkala - da ni videti, kot da sta se ocenjevalca strinjala.
   - **Padla oba:** zanko ustavi takoj. Kroga **ne štej**. Povej Janiju, katero vozlišče je padlo in
     s katero napako. Popravek je v n8n, ne v besedilu. **Če do takrat še noben krog ni bil
     dokončan** (torej `rounds` ostane `0`), v `_run.transcreation_check.<jezik>` namesto `"ok"`
     ali `"revise"` zapiši `"verdict": "napaka"` - sodbe namreč ni bilo, ne prve ne druge.

   c. Presodi obe oceni. Nista enakovredna glasova - urednik si ti. Najdbo, ki je napačna ali gre
   proti Igorjevemu glasu, zavrni in to zapiši v `rejected` z utemeljitvijo.

   Zavrni tudi najdbo, ki je samo druga, enako dobra rešitev (sinonim, drug vrstni red, »bolj
   tekoče«), in najdbo, ki gre proti hišni tipografiji v promptu (npr. `14 eura` ali “ … ” v
   hrvaščini). Živi tek 24. 9. 2026 je pokazal, da oba modela take najdbe dajeta v vsakem krogu.

   d. Sodba kroga je tvoja, ne modelov. Odloča, ali po točki c ostane **vsaj ena sprejeta najdba**:
      - ne ostane nobena → `verdict` = `"ok"`, `changes` = `[]`, besedilo se ne spremeni - tudi
        če je model napisal `ZA POPRAVEK`;
      - ostane vsaj ena → `verdict` = `"revise"`.

      Šteje samo ocenjevalec, ki je **odgovoril**. Brez tega pravila sodba nikoli ne postane `ok`,
      ker model v krogu 2 vedno najde novo slogovno drobnarijo (tek 24. 9. 2026: po dveh krogih
      `revise` pri obeh jezikih, pa čeprav so bile najdbe kroga 2 večinoma slogovne).

   e. Ob `revise` **popravek ni ročno krpanje stavka.** Pokliči `frodx-transcreation` znova, za isti
   jezik, in mu kot vhod daj izvirnik, trenutni prevod in sprejete najdbe kot izrecne zahteve.
   Drugo mnenje lovi, ne popravlja - popravek mora nazaj skozi Igorjeva pravila glasu. Rezultat
   imenuj `popravljeno`.

   f. Zapiši `transcreation-check/<jezik>-round-<krog>.json`:

   ```json
   {
     "language": "<jezik>",
     "round": 1,
     "input": "<besedilo, kot je bilo POSLANO v ta krog, pred popravkom>",
     "check_prompt": "<checkPrompt, kot je bil POSLAN, z vstavljenim datumom>",
     "openai": "<ocena>",
     "gemini": "<ocena>",
     "openai_error": null,
     "gemini_error": null,
     "changes": ["zamenjal 'podjetje' s 'tvrtka' na treh mestih"],
     "rejected": ["<najdba, ki si jo zavrnil> - <zakaj>"],
     "verdict": "revise"
   }
   ```

   g. Ob `revise` nastavi `besedilo` = `popravljeno` in **takoj** zapiši
   `languages.<jezik>.content` = `popravljeno` v `state.json`, preden zanka gre naprej. Če se tek
   prekine sredi zanke, `state.json` ne sme izgubiti zadnjega popravka.

   h. Zanka se nadaljuje samo, če je `verdict` `"revise"` in je `krog` = 1. Tretjega kroga ni.

   Če je krog 2 sodba `"revise"`, se popravek iz točke e še vedno izvede in zapiše (točka g), a se
   **ne oceni ponovno** - tretje ocene ni. `verdict: "revise"`, ki ostane zapisan za ta jezik, se
   torej nanaša na **vhod** kroga 2 (besedilo pred tem zadnjim popravkom), ne na končno besedilo, ki
   dejansko pristane v `languages.<jezik>.content`. Zadnji popravek gre naravnost v paket, brez
   tretjega mnenja.

5. Konec zanke za ta jezik. Zapiši v `state.json`:

   ```json
   "_run": {
     "transcreation_check": {
       "<jezik>": {"rounds": 1, "verdict": "ok", "openai_error": null, "gemini_error": null}
     }
   }
   ```

   Ključ je jezik, ki ga ta tek obdela (`"hr"` ali `"en"`) - vpiši samo pod ta ključ in ne prepiši
   ključa drugega jezika, ki ga je zapisal prejšnji tek.

   `rounds` je število **dejansko opravljenih** krogov. Krog, v katerem sta padla oba ocenjevalca,
   se ne šteje.

   Če sta oba ocenjevalca padla, preden je bil dokončan sploh en krog, je `rounds` `0` in
   `verdict` je `"napaka"` - ne `"ok"`, ne `"revise"`, ker sodbe o prevodu ni bilo, samo napaka
   klica. `openai_error`/`gemini_error` v tem primeru nosita zadnjo napako vsakega vozlišča.

## Odprta zadolžitev za človeka

Po obeh jezikih zapiši v `_run.open_tasks` zadolžitev za hrvaščino - **vedno**, tudi kadar sta oba
ocenjevalca rekla `OBJAVLJIVO`:

```json
{"what": "hrvaška različica: GPT in Gemini sta jo pregledala (<verdict>, <rounds> krog/a), native pregled ni bil opravljen",
 "who": "native govorec hrvaščine", "created_at": "<ISO čas>", "step": 4}
```

**Če je `verdict` `"napaka"`** (oba ocenjevalca sta padla in do sodbe ni prišlo), zgornje predloge
ne uporabi - besedilo z `<verdict>, <rounds> krog/a` bi bralca zavedlo, da je pregled tekel. Namesto
tega zapiši:

```json
{"what": "hrvaška različica: preverba ni bila opravljena (oba ocenjevalca sta padla), native pregled ni bil opravljen",
 "who": "native govorec hrvaščine", "created_at": "<ISO čas>", "step": 4}
```

Zadolžitev nastane enako - vedno, ne glede na to, ali je preverba sploh stekla.

Igorju ob gateu izrecno povej, da **priporočaš še native pregled**. Dva modela nista Hrvat. To je
Janijeva odločitev z 18. 9. 2026 in ni stvar presoje v posameznem teku.

Za angleščino zadolžitve privzeto ni. Zapiše se **samo**, če je po dveh krogih sodba še vedno
`revise`:

```json
{"what": "angleška različica po dveh krogih preverbe še vedno ni potrjena", "who": "Igor",
 "created_at": "<ISO čas>", "step": 4}
```

## Kaj ne delaš

- Ne pošiljaš slovenske kolumne v ta pregled. Za slovenščino je `frodx-critique-loop`.
- Ne popravljaš prevoda sam, mimo `frodx-transcreation`.
- Ne urejaš `frodx-transcreation` ne njegovih referenc - Igorjev vendoriran skill je, njegova
  merila samo bereš.
- Ne kličeš tretjega kroga, tudi če bi bilo skušnjava. Po dveh krogih odloči Igor.
- Ne obravnavaš padlega vozlišča kot sodbo in ne šteješ kroga, v katerem sta padla oba.
- Ne odstranjuješ zadolžitve za hrvaščino iz `_run.open_tasks`, da bi bil izpis gatea čist.
