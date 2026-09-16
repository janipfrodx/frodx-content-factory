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

4. Pridobi sliki. **Preberi najprej razdelek »Kako sliki dejansko prideta do tebe« spodaj** - `get_execution` binarnih bajtov na tej n8n instanci ne vrne in poskus prepisa base64 na disk je bil preizkušen in ni deloval. Brez tega razdelka ta korak porabi dva plačljiva klica in obstane.
5. **Izmeri obe sliki, preden ju gledaš.** Tek 14. 9. 2026 je kot naslovno sliko oddal datoteko 784x522, ker tega ni nihče izmeril.

   ```bash
   python3 <plugin>/skills/frodx-publish-send/scripts/dimenzije.py \
     runs/<slug>/images/openai.png runs/<slug>/images/gemini.png
   ```

   `<plugin>` je `plugins/content-factory/`, torej ista mapa, iz katere teče ta skill. Poti do slik
   sta relativni na CWD, kjer je `init_run.py` ustvaril `runs/` - enako kot pri dirigentu.

   Kandidatka mora biti široka vsaj **1200 px** in visoka vsaj **630 px** (`frodx-key-visual/references/prompt-recipes.md`: og:image potrebuje crop na 1200x630). Slika, ki je ožja, ni kandidatka, tudi če je lepša. Če nobena ne doseže praga, ne izbiraj - to ni vprašanje okusa, ampak znak, da si dobil pomanjšan predogled namesto polne slike. Preveri, ali sta datoteki res iz vozlišč `OpenAI Image` in `Gemini Image`, in šele potem ponovi generacijo po točki 7.

6. Preberi `references/image-decision.md` in `frodx-key-visual/references/visual-style.md`. Poglej obe sliki in odloči.
7. Če zavrneš obe: popravi oba prompta v isti smeri in ponovi od točke 3. Največ dve ponovitvi.
8. Izbrano sliko kopiraj v `images/izbrana.png` (če je izvorna datoteka JPEG, ohrani pripono: `images/izbrana.jpg`).
9. Napiši alt tekst za vse tri jezike. Opiši, **kar je na sliki**, ne o čem je članek. Naslov uporabi samo za razdvoumljenje. En stavek, do 160 znakov, ciljno okoli 125. Ne začenjaj z »Slika prikazuje«, »Image of«, »Fotografija«.
10. Zapiši v `state.json`:
    - `languages.sl.featured_image_alt`, `languages.en.featured_image_alt`, `languages.hr.featured_image_alt`
    - `_run.image`:

    ```json
    {
      "chosen": "openai",
      "attempts": 1,
      "dimensions": {"openai": [1536, 1024], "gemini": [1536, 864]},
      "rubric": {
        "koncept": "<ena poved>",
        "robustnost": "<ena poved>",
        "thumbnail": "<ena poved>",
        "anti_slop": "<ena poved>",
        "kompozicija": "<ena poved>",
        "brand_fit": "<ena poved>"
      },
      "reason": "<en stavek>"
    }
    ```

    Šest polj `rubric` je šest meril iz rubrike v `frodx-key-visual/SKILL.md`. Sedmega, »Kakovost prompta«, tu ni: ocenjuje prompt, ne slike, in je bil opravljen že v točki 2. Piši poved o **izbrani** sliki, ne oceno v številkah - številčna rubrika velja za koncept pred generiranjem.
    - `_run.step` = 5, `_run.status` = `awaiting_approval`
11. Pokaži Igorju obe sliki, izmerjene dimenzije, svojo izbiro in rubriko. Če izbere drugo, spoštuj to in popravi `_run.image` v celoti, tudi `rubric` in `reason`.

## Kako sliki dejansko prideta do tebe

Stanje preverjeno 17. 8. 2026 neposredno v workflowu `lHc3NdejxehMyc9O`, ugotovitve iz živega teka 14.-15. 8. 2026.

**Kar ne deluje in se ne poskuša znova:**

- `get_execution` **ne vrne bajtov**. n8n Cloud instanca teče v načinu `filesystem-v2`, zato vrne referenco oblike `{"data": "filesystem-v2", "id": "filesystem-v2:workflows/…/binary_data/…"}`. To je pot na disku n8n instance, ne slika.
- **Prepis base64 na disk skozi kontekst ne deluje.** Workflow ima veji `Shrink OpenAI → B64 OpenAI` in `Shrink Gemini → B64 Gemini` (640×640 `maximumArea`, JPEG q60), ki v polji `openai_b64` in `gemini_b64` vrneta base64 - ta res pride skozi. Poskus 15. 8. 2026, da se ta niz (~45.000 znakov) prepiše v datoteko in dekodira, je dal 17 kB namesto ~35 kB in `OSError: broken data stream when reading image file`; ob prisilnem izrisu je bilo uporabnih okoli 2 % slike. Ponovni poskus je ista operacija z istim razlogom za odpoved - ne ponavljaj ga in ne poročaj, da »slike ni bilo mogoče generirati« (generirana je bila).

**Vmesni postopek, dokler nalaganje ni rešeno.** Ta korak edini v verigi ne more do konca brez človeka:

1. Iz izvedbe si zapiši ID in povej Igorju (ali Janiju), naj v n8n UI odpre to izvedbo in prenese sliki iz vozlišč `OpenAI Image` in `Gemini Image` - tam sta **polni** sliki, ne pomanjšani predogled.
2. Prosi ga, naj ju položi v mapo teka kot `images/openai.png` in `images/gemini.png`.
3. Šele ko datoteki obstajata, ju odpri in nadaljuj s točko 5. **Preden sliki vidiš, ne izbiraj in ne piši alt teksta.**

**Trajna rešitev, ko bo workflow dopolnjen.** Preverjeno 17. 8. 2026: Microsoft 365 konektor prek `read_resource` na URI `file:///{driveId}/{itemId}` vrne **sliko, ki jo res vidiš** - ne besedilnega izvlečka. Ko bo workflow sliko nalagal na SharePoint in vračal `driveId` in `itemId`, bo postopek tak:

```
read_resource("file:///{driveId}/{itemId}")
```

in slika je pred tabo, brez base64 in brez datoteke na disku. Takrat točke 1-3 vmesnega postopka odpadejo. Dokler workflow tega ne vrača, velja vmesni postopek zgoraj - sam nalaganja ne izvajaj in `driveId`/`itemId` si ne izmišljaj.

## Kaj ne delaš

- Ne nalagaš slike nikamor. URL naredi aplikacija ob sprejemu paketa.
- Ne pišeš alt teksta iz naslova članka, če slike nisi pogledal.
- Ne prevajaš slovenskega alt teksta v EN in HR. Vsak jezik opisuje sliko po svoje, naravno.
- Ne izbiraš »manj slabe« slike, da bi se izognil ponovitvi.

## Stroški

Vsak zagon porabi plačljiv OpenAI in Gemini klic za sliko. Pred tretjim poskusom vprašaj Igorja, ali naj nadaljuješ.

Ne zaganjaj workflowa znova zato, da bi »morda tokrat« prišel binarni izhod. V teku 14.-15. 8. 2026 sta bila zaradi tega porabljena **dva para** slik (izvedbi 183698 in 183742). Če sliki obstajata v prejšnji izvedbi, jih vzemi od tam - popravek workflowa velja šele za nove izvedbe, sliki iz stare izvedbe pa sta še vedno v n8n.
