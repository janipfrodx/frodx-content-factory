---
name: frodx-critique-loop
description: Run the FrodX critique loop on a draft column - send the text to GPT and Gemini through the n8n critique workflow, apply the feedback, and repeat until both approve or three rounds are spent. Use after a column draft exists and before transcreation, or whenever Igor asks to "daj v kritiko", "preveri kolumno", "kaj pravita GPT in Gemini". Writes the revised text back into the run state and logs every round.
metadata:
  version: 0.1.0
---

# Kritika loop

Slovensko kolumno da v pregled GPT-ju in Geminiju, popravi po pripombah in ponovi - največ trikrat.

## Postopek

1. Preberi `state.json`. Vzemi `languages.sl.content`. Če je prazen, povej Igorju, da kolumne še ni, in končaj.
2. Preberi `references/critique-prompt.md` v celoti. To je vsebina, ki jo pošlješ kot `critiquePrompt` - v vsakem krogu enaka, se med krogi ne spreminja.

   **Pred pošiljanjem zamenjaj `{{DANES}}` z današnjim datumom** v obliki `17. 8. 2026`. Zamenjava se zgodi v nizu, ki ga pošlješ - datoteke ne spreminjaj. Če `{{DANES}}` v prompt ne vstaviš, ocenjevalec ne ve, kateri dan je, in bo pravilne letnice razglašal za halucinacije: to se je zgodilo 15. 8. 2026, ko je Gemini kot napako navedel Gartnerjevo raziskavo iz leta 2025, ker jo je bral kot prihodnost. Ocenjevalca sta modela s presekom znanja pred današnjim datumom - oba, ne samo eden.
3. Nastavi delovno spremenljivko `besedilo` = `languages.sl.content` iz `state.json`. To je vhod v **krog 1**.
4. Za `krog` = 1, 2, 3 (največ trikrat), ponavljaj:

   a. Kliči n8n workflow `GZmnPGOcVANH2sfy` (webhook `critique-text`) prek orodja `execute_workflow`. Telo webhooka gre gnezdeno pod `inputs.webhookData.body` - ne kot plošček `text`/`context`/... na vrhu klica:

   ```json
   {
     "workflowId": "GZmnPGOcVANH2sfy",
     "executionMode": "manual",
     "inputs": {
       "type": "webhook",
       "webhookData": {
         "method": "POST",
         "body": {
           "text": "<besedilo>",
           "context": "<_run.brief.topic> | ciljani prompt: <_run.brief.target_prompt>",
           "language": "sl",
           "critiquePrompt": "<vsebina references/critique-prompt.md>"
         }
       }
     }
   }
   ```

   `executionMode` naj bo `"manual"` - workflow trenutno ni aktiven (`active: false`), `"production"` pa je namenjen samo objavljenemu (aktivnemu) workflowu kot živi izvedbi. `"manual"` orodje izrecno dovoljuje tudi za klice, ki dejansko kličejo zunanje storitve (OpenAI, Gemini) - ne samo za suha testiranja - zato je to pravi način tudi za resnično kritiko, ne le za preizkus.

   `<besedilo>` v polju `body.text` je vrednost delovne spremenljivke `besedilo` **v tem trenutku** - v krogu 1 je to `languages.sl.content` iz state.json (točka 3), v krogu 2 in 3 je to popravljena verzija iz prejšnjega kroga (točka e spodaj). Nikoli ne pošlji izvirnega besedila iz state.json v krog 2 ali 3 - poslati moraš rezultat zadnjega popravka.

   `body.context` je vedno niz (ne objekt) - `Normalize Input` polje `context` je tipizirano kot `string` in ga oba ocenjevalca (`OpenAI Critique`, `Gemini Critique`) v uporabniškem sporočilu dobita pred besedilom kolumne, kadar ni prazen (n8n stran tega ne pusti prazne glave, če je `context` prazen niz).

   b. Preberi izhod prek `get_execution` iz vozlišč `OpenAI Critique` in `Gemini Critique`.

   **Če je vozlišče padlo** (npr. HTTP 404, ker model ni več na voljo - to se je zgodilo 15. 8. 2026 z `models/gemini-3-pro-preview`), to **ni sodba `ZA POPRAVEK`**. Odpoved ocenjevalca ne sme šteti kot pripomba in ne sme tiho porabiti kroga:

   - Zapiši napako dobesedno v `round-<krog>.json` kot `openai_error` oz. `gemini_error` in v tisto polje kritike (`openai` / `gemini`) daj `null`, ne prazen niz.
   - **Če je padel eden:** nadaljuj s tistim, ki je odgovoril. V zapisu kroga in Igorju izrecno povej, da je polovica presoje manjkala - da ni videti, kot da sta se ocenjevalca strinjala.
   - **Če sta padla oba:** zanko ustavi takoj. Ne popravljaj besedila po nobeni pripombi (nobene ni) in kroga ne štej v `_run.critique_rounds`. Povej Igorju in Janiju, katero vozlišče je padlo in s katero napako. Popravek je v n8n, ne v besedilu - Jani ga naredi, potem se korak ponovi.

   c. Presodi obe kritiki. Nista enakovredni glasovi - ti si urednik. Pripombo, ki je napačna ali gre proti Igorjevemu glasu, zavrni in to zapiši (v `changes` ali v pogovoru z Igorjem, ne v `state.json` kot uradno spremembo).

   d. Ugotovi `verdict` za ta krog. Šteje samo tisti ocenjevalec, ki je **odgovoril** - padlo vozlišče ni glas:
      - **Če vsi ocenjevalci, ki so odgovorili, rečejo `OBJAVLJIVO`:** `verdict` = `"ok"`, `changes` = `[]`. Besedilo se ne spremeni. Če je odgovoril samo eden, je `verdict` `"ok"`, a v zapisu kroga in Igorju povej, da je sodba enoglasna zato, ker je drugi ocenjevalec padel - ne ker sta se strinjala.
      - **Sicer** (vsaj eden od tistih, ki so odgovorili, reče `ZA POPRAVEK`): `verdict` = `"revise"`. Popravi tisto, kar bi ustavilo objavo, ne vsega, kar je kdo omenil. Rezultat popravka je novo besedilo - imenuj ga `popravljeno`, in zapiši, kaj si spremenil, v `changes`.

   e. Zapiši `critique/round-<krog>.json`:

   ```json
   {
     "round": 1,
     "input": "<besedilo, kot je bilo POSLANO v ta krog v točki a, pred morebitnim popravkom>",
     "openai": "<kritika>",
     "gemini": "<kritika>",
     "openai_error": null,
     "gemini_error": null,
     "changes": ["skrajšal hook na en prizor", "zamenjal splošno trditev s številko iz vira"],
     "rejected": ["<pripomba, ki si jo zavrnil> - <zakaj>"],
     "verdict": "revise"
   }
   ```

   `openai_error` in `gemini_error` sta `null`, kadar je vozlišče odgovorilo. Če je padlo, gre vanj dobesedno sporočilo napake, pripadajoča kritika pa je `null` (glej točko b). `rejected` je seznam pripomb, ki jih kot urednik zavrneš, vsaka s kratko utemeljitvijo - to je zapis presoje, ne opravičilo.

   `input` je vedno besedilo, ki je šlo v n8n v točki a tega kroga - **ne** popravljena verzija. Če je `verdict` `"ok"`, je `changes` `[]` in `input` ostane veljavno besedilo (nespremenjeno).

   f. Če je `verdict` za ta krog `"revise"`: nastavi delovno spremenljivko `besedilo` = `popravljeno`, in **takoj** (preden zanka gre na naslednji krog ali se konča) zapiši `languages.sl.content` = `popravljeno` v `state.json`. To zapišeš po vsakem krogu, ne šele na koncu - če se tek prekine sredi zanke, `state.json` ne sme izgubiti zadnjega popravka.

   g. Odloči, ali se zanka nadaljuje:
      - Če je `verdict` `"ok"` - ustavi zanko zdaj (konec, ne glede na `krog`).
      - Če je `krog` = 3 - ustavi zanko po tem krogu (ne kliči četrtega kroga), ne glede na `verdict`.
      - Sicer nadaljuj z naslednjim `krog` (točka a, z novo vrednostjo `besedilo`).

5. Konec zanke. Nastavi `_run.critique_rounds` = število dejansko opravljenih krogov (1, 2 ali 3). `languages.sl.content` je že posodobljen (točka 4.f) ali je enak vrednosti, ki jo je state.json že imel (če je bil `verdict` `"ok"` že v krogu 1).

## Ustavitev

Ustavi se, ko:
- **vsi ocenjevalci, ki so odgovorili**, rečejo `OBJAVLJIVO` (v katerem koli krogu), ali
- si opravil **tri kroge**, ali
- sta **oba ocenjevalca padla** v istem krogu (glej postopek, točka b - takrat ni presoje, ki bi jo bilo mogoče uporabiti).

Po treh krogih ne padeš z napako. Igorju pokaži zadnjo verzijo (`languages.sl.content`), odprte pripombe iz zadnjega kroga in kaj si zavrnil ter zakaj. Odloči on.

## Zapis v stanje

Ob koncu (po zadnjem opravljenem krogu):

- `languages.sl.content` = zadnja verzija besedila (glej postopek, točka 4.f - to je bilo zapisano že med zanko, ne šele tu)
- `_run.critique_rounds` = število opravljenih krogov
- `_run.step` = 3, `_run.status` = `awaiting_approval`

Dirigent (`frodx-content-factory`) po tem vpraša Igorja, ali je popravljena verzija v redu, in šele po njegovi potrditvi zapiše čas v `_run.approvals` ter gre na korak 4. Ta skill sam ne sprašuje za potrditev in ne piše v `_run.approvals` - to je dirigentovo delo po generičnem pravilu za korake 2-7.

## Kaj ne delaš

- Ne pošiljaš v kritiko EN in HR verzij. Ta korak je samo za slovenščino; transkreacija ima svoj QA.
- Ne popravljaš zaključka s podpisom `igor.pauletic@frodx.com`. Ta vrstica ostane, kakor je - kritika se je ne dotika.
- Ne dodajaš številk, ki jih v izvirniku ni, da bi zadovoljil pripombo o dokazih. Če manjka dokaz, to povej Igorju.
- Ne pošiljaš v krog 2 ali 3 izvirnega besedila iz state.json - pošiljaš zadnjo popravljeno verzijo (glej postopek, točka 4.a).
- Ne kličeš četrtega kroga, tudi če bi Igor rekel »samo še enkrat« - to je njegova odločitev po tem, ko mu pokažeš zadnjo verzijo, ne del te zanke.
- **Ne popraviš pravilnega podatka, ker ocenjevalec trdi, da je časovno nemogoč.** Ocenjevalec ima starejši presek znanja kot ti. Preden se dotakneš letnice, datuma ali številke z navedenim virom, jo preveri pri viru (`WebFetch` na navedeno povezavo). Če vir potrdi podatek, pripombo zavrni in to zapiši v `rejected`. Kolumno drži pokonci prav preverljivost številk - popravek v napačno smer je hujši od neupoštevane pripombe.
- Ne obravnavaš padlega vozlišča kot sodbo. Napaka ocenjevalca ni »ZA POPRAVEK« in ni »OBJAVLJIVO« (glej postopek, točka b).
