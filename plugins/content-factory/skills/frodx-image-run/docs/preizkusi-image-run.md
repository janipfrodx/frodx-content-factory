# Preizkusi image-run - navodilo za Janija

Ta korak (Step 3 in Step 4 iz načrta implementacije) je bil izpuščen iz avtomatske izvedbe, ker vsak klic porabi plačljiv OpenAI in Gemini klic za sliko. To navodilo je samostojno - ne rabiš prebrati načrta, da ga izvedeš.

## Preden začneš

Workflow `lHc3NdejxehMyc9O` (`Generiraj sliko (Content Factory)`) trenutno **ni aktiven** (`active: false`). Produkcijski webhook (`https://frodxai.app.n8n.cloud/webhook/generate-image`) zato ne bo sprejel klica, dokler ga ne aktiviraš. Za ročni preizkus imaš dve možnosti:

- **A: test webhook.** Odpri workflow v n8n UI, klikni "Listen for test event" na vozlišču `Trigger`, nato v 2 minutah pošlji zahtevo na `https://frodxai.app.n8n.cloud/webhook-test/generate-image`. Izvedba pristane v Executions kot testna.
- **B: aktiviraj workflow** in pošlji na produkcijski URL. Priporočeno samo, če nameravaš workflow pustiti aktiven tudi za pravo rabo v verigi.

Workflow sprejme telo `{ "prompt_openai": "...", "prompt_gemini": "...", "size": "1536x1024" }` in vrne binarna izhoda iz vozlišč `OpenAI Image` (model `gpt-image-1`) in `Gemini Image` (model `models/gemini-3-pro-image`, "Nano Banana Pro").

## Step 3: Živ preizkus

Vzemi `languages.sl.content` iz `tests/fixtures/package_valid.json` (v repu `frodx-content-factory`). Naslov kolumne je `meta.title`: "Zakaj lojalnostni programi kaznujejo zveste kupce".

1. Pokliči `frodx-key-visual` s tem naslovom in besedilom, da dobiš `prompt_openai` in `prompt_gemini`.
2. Pošlji ju skozi n8n workflow `lHc3NdejxehMyc9O` (glej "Preden začneš" zgoraj za URL).
3. Preberi izhod prek `get_execution` iz vozlišč `OpenAI Image` in `Gemini Image`, shrani binarna izhoda v `images/openai.png` in `images/gemini.png`.
4. Poglej obe sliki, odloči po `references/image-decision.md`, izbrano kopiraj v `images/izbrana.png`, napiši alt tekste za sl/en/hr in zapiši `_run.image` v `state.json`.

Primer s `curl` (test webhook, možnost A zgoraj):

```bash
curl -X POST https://frodxai.app.n8n.cloud/webhook-test/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt_openai": "<prompt iz frodx-key-visual>", "prompt_gemini": "<prompt iz frodx-key-visual>", "size": "1536x1024"}'
```

Preveri:
- [ ] `frodx-key-visual` vrne dva ločena prompta
- [ ] obe sliki prispeta kot binarno in se shranita v `images/`
- [ ] odločitev je obrazložena v enem stavku
- [ ] alt teksti so trije, vsak ≤160 znakov, noben se ne začne z »Slika prikazuje«
- [ ] `_run.image` je zapisan

**Opomba o stroških:** ta preizkus porabi en plačljiv OpenAI in en plačljiv Gemini klic za sliko. Za preizkus zadošča en tek brez ponovitev.

## Step 4: Preizkus zavrnitve

Ročno povej skillu (v pogovoru, po tem ko je pokazal obe sliki iz Step 3, ali z novim parom slik), da sta obe sliki neustrezni - na primer, da ena slika prikazuje izmišljeno številko na zaslonu ali grafu (merilo 1 iz `references/image-decision.md`).

Preveri:
- [ ] skill popravi oba prompta (`prompt_openai` in `prompt_gemini`) v isti smeri glede na povedano pomanjkljivost
- [ ] skill znova pokliče workflow `lHc3NdejxehMyc9O` s popravljenima promptoma (2. poskus)
- [ ] če ponovno zavrneš obe sliki, skill po **drugi** ponovitvi (torej po skupno največ dveh dodatnih poskusih od prvega zavrnjenega para) ne poskusi tretjič sam, ampak se obrne na Igorja in vpraša, ali naj nadaljuje

**Opomba o stroških:** vsaka ponovitev porabi nov plačljiv OpenAI in Gemini klic. Za preizkus meje zadostujeta dve ponovitvi (skupno največ trije pari slik: prvi + dve ponovitvi).

## Zapis rezultatov

<!-- Dopolni po vsakem izvedenem preizkusu: datum, kdo je izvedel, izid (prestal/ni prestal) in morebitne opombe. -->
