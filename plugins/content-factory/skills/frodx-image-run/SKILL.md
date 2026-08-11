---
name: frodx-image-run
description: Produce the key visual for a FrodX column - get the two image prompts from frodx-key-visual, run them through the n8n image workflow, judge the two results and write alt text in all three languages. Use after the column text is final, or when Igor asks for "naslovna slika", "key visual", "generiraj sliko". Stores the chosen image in the run folder and the alt texts in the run state.
metadata:
  version: 0.1.0
---

# Naslovna slika

Iz besedila kolumne naredi naslovno sliko in alt tekste.

## Postopek

1. Preberi `state.json`. Če je `languages.sl.content` prazen, povej in končaj.
2. Pokliči skill `frodx-key-visual` z naslovom in besedilom kolumne. Vrne dva prompta - enega za Nano Banana, enega za GPT-Image. Slik namenoma ne generira; to je tvoja naloga.
3. Kliči n8n workflow `lHc3NdejxehMyc9O` (`Generiraj sliko (Content Factory)`), webhook `generate-image`, prek orodja `execute_workflow`. Workflow trenutno **ni aktiven** (`active: false`), zato je `executionMode` `"manual"` - enako kot pri `frodx-critique-loop`, `"manual"` orodje izrecno dovoljuje tudi za klice, ki dejansko kličejo zunanje storitve (OpenAI, Gemini), ne samo za suha testiranja. Telo webhooka gre gnezdeno pod `inputs.webhookData.body`:

```json
{
  "workflowId": "lHc3NdejxehMyc9O",
  "executionMode": "manual",
  "inputs": {
    "type": "webhook",
    "webhookData": {
      "method": "POST",
      "body": {
        "prompt_openai": "<GPT-Image prompt iz frodx-key-visual>",
        "prompt_gemini": "<Nano Banana prompt iz frodx-key-visual>",
        "size": "1536x1024"
      }
    }
  }
}
```

4. Preberi binarna izhoda prek `get_execution` (`includeData: true`, `nodeNames: ["OpenAI Image", "Gemini Image"]`) in shrani v `images/openai.png` in `images/gemini.png`. Ime binarnega polja v izhodu vsakega vozlišča preveri v dejanskem odgovoru `get_execution` - ne predvidevaj ga vnaprej.
5. Preberi `references/image-decision.md` in `frodx-key-visual/references/visual-style.md`. Poglej obe sliki in odloči.
6. Če zavrneš obe: popravi oba prompta v isti smeri in ponovi od točke 3. Največ dve ponovitvi.
7. Izbrano sliko kopiraj v `images/izbrana.png`.
8. Napiši alt tekst za vse tri jezike. Opiši, **kar je na sliki**, ne o čem je članek. Naslov uporabi samo za razdvoumljenje. En stavek, do 160 znakov, ciljno okoli 125. Ne začenjaj z »Slika prikazuje«, »Image of«, »Fotografija«.
9. Zapiši v `state.json`:
   - `languages.sl.featured_image_alt`, `languages.en.featured_image_alt`, `languages.hr.featured_image_alt`
   - `_run.image` = `{"chosen": "openai" | "gemini", "attempts": N, "reason": "<en stavek>"}`
   - `_run.step` = 5, `_run.status` = `awaiting_approval`
10. Pokaži Igorju obe sliki, svojo izbiro in razlog. Če izbere drugo, spoštuj to in popravi `_run.image`.

## Kaj ne delaš

- Ne nalagaš slike nikamor. URL naredi aplikacija ob sprejemu paketa.
- Ne pišeš alt teksta iz naslova članka, če slike nisi pogledal.
- Ne prevajaš slovenskega alt teksta v EN in HR. Vsak jezik opisuje sliko po svoje, naravno.
- Ne izbiraš »manj slabe« slike, da bi se izognil ponovitvi.

## Stroški

Vsak zagon porabi plačljiv OpenAI in Gemini klic za sliko. Pred tretjim poskusom vprašaj Igorja, ali naj nadaljuješ.
