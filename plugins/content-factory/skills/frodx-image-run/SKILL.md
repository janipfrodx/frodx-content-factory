---
name: frodx-image-run
description: Produce every image a FrodX column needs, in two phases. Phase A is the key visual - get the two image prompts from frodx-key-visual, run them through the n8n image workflow, judge the two results and write alt text in all three languages. Phase B makes one image for each approved social post and writes its alt text in Slovenian only. Use after the column text is final and the social posts are chosen, or when Igor asks for "naslovna slika", "key visual", "slike za socialne objave", "generiraj sliko". Stores the chosen images in the run folder and their public URLs and alt texts in the run state.
metadata:
  version: 0.2.0
---

# Naslovna in socialne slike

Iz besedila kolumne naredi naslovno sliko z alt teksti v vseh treh jezikih, iz besedila vsake
potrjene socialne objave pa še po eno sliko s slovenskim alt tekstom.

## Postopek

Skill ima dve fazi. **Faza A** naredi naslovno sliko kolumne - dve kandidatki, OpenAI in Gemini,
1536x1024. **Faza B** naredi po eno sliko za vsako potrjeno socialno objavo - ena kandidatka,
samo OpenAI, 1024x1024. Fazi sta ločeni, ker gresta na različna workflowa in imata različni merili.

## Faza A - naslovna slika

1. Preberi `state.json`. Če je `languages.sl.content` prazen, povej in končaj.
2. Pokliči skill `frodx-key-visual` z naslovom in besedilom kolumne. Vrne dva prompta - enega za Nano Banana, enega za GPT-Image. Slik namenoma ne generira; to je tvoja naloga.
3. Kliči n8n workflow `lHc3NdejxehMyc9O` (`Generiraj sliko (Content Factory)`), webhook `generate-image`, prek orodja `execute_workflow`. Workflow trenutno **ni aktiven** (`active: false`), zato je `executionMode` `"manual"` - enako kot pri `frodx-critique-loop`, `"manual"` orodje izrecno dovoljuje tudi za klice, ki dejansko kličejo zunanje storitve (OpenAI, Gemini), ne samo za suha testiranja. Telo webhooka gre gnezdeno pod `inputs.webhookData.body`:

```json
{
  "workflowId": "lHc3NdejxehMyc9O",
  "executionMode": "manual",
  "triggerNodeName": "Trigger",
  "inputs": {
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

4. **Prenesi sliki na disk.** Workflow v odgovoru vrne javna URL-ja, ne bajtov:

   ```json
   {"openai": {"url": "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/<uuid>.png"},
    "gemini": {"url": "..."}}
   ```

   Oba prenesi v mapo teka:

   ```bash
   curl -sS -o runs/<slug>/images/openai.<pripona> "<openai.url>"
   curl -sS -o runs/<slug>/images/gemini.<pripona> "<gemini.url>"
   ```

   `<pripona>` vzemi iz konca URL-ja (`.png` ali `.jpg`). Gemini vrne `.jpg`, OpenAI `.png` -
   preverjeno v teku 24. 9. 2026. Datoteke ne preimenuj v drugo pripono, kot jo ima URL.

   URL-ja si **zapiši**, ne samo datotek - URL izbrane slike gre v točki 10 v `_run.image.url` in je edino, kar aplikacija o sliki potrebuje.

   Če `curl` vrne prazno ali napako, ne poskušaj brati bajtov iz izvedbe workflowa in ne kodiraj base64 skozi kontekst; oboje je bilo preizkušeno 15. 8. 2026 in ne deluje. Povej Janiju, da gostitelj shrambe ni dosegljiv, in počakaj.
5. **Izmeri obe sliki, preden ju gledaš.** Tek 14. 9. 2026 je kot naslovno sliko oddal datoteko 784x522, ker tega ni nihče izmeril.

   ```bash
   python3 <plugin>/skills/frodx-publish-send/scripts/dimenzije.py \
     runs/<slug>/images/openai.<pripona> runs/<slug>/images/gemini.<pripona>
   ```

   `<plugin>` je `plugins/content-factory/`, torej ista mapa, iz katere teče ta skill. Poti do slik
   sta relativni na CWD, kjer je `init_run.py` ustvaril `runs/` - enako kot pri dirigentu.

   Kandidatka mora biti široka vsaj **1200 px** in visoka vsaj **630 px** (`frodx-key-visual/references/prompt-recipes.md`: og:image potrebuje crop na 1200x630). Slika, ki je ožja, ni kandidatka, tudi če je lepša. Če nobena ne doseže praga, ne izbiraj - to ni vprašanje okusa, ampak znak, da si dobil pomanjšan predogled namesto polne slike. Preveri, ali sta datoteki res iz vozlišč `OpenAI Image` in `Gemini Image`, in šele potem ponovi generacijo po točki 7.

6. Preberi `references/image-decision.md` in `frodx-key-visual/references/visual-style.md`. Poglej obe sliki in odloči.
7. Če zavrneš obe: popravi oba prompta v isti smeri in ponovi od točke 3. Največ dve ponovitvi.
8. Izbrano sliko kopiraj v `images/izbrana.<pripona>`, s pripono izbrane slike. Ena sama datoteka in ena sama pripona, da je jasno, katero sliko si izbral. Korak 7 te datoteke ne pošilja - aplikaciji preda `_run.image.url`; datoteka na disku je le tvoj delovni izvod, ki ga meri gate.
9. Napiši alt tekst za vse tri jezike. Opiši, **kar je na sliki**, ne o čem je članek. Naslov uporabi samo za razdvoumljenje. En stavek, do 160 znakov, ciljno okoli 125. Ne začenjaj z »Slika prikazuje«, »Image of«, »Fotografija«.
10. Zapiši v `state.json`:
    - `languages.sl.featured_image_alt`, `languages.en.featured_image_alt`, `languages.hr.featured_image_alt`
    - `_run.image`:

    ```json
    {
      "chosen": "openai",
      "url": "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/<uuid>.png",
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

    `url` je javni URL **izbrane** kandidatke, prepisan iz odgovora workflowa v točki 4. Aplikacija drugega o sliki ne dobi, zato mora biti tu in mora biti tisti, ki ustreza `chosen`. Zavržena kandidatka ostane v shrambi; to ni napaka, ampak zapis, med čim se je izbiralo.
    - `_run.step` = 5, `_run.status` = `awaiting_approval`
11. Pokaži Igorju obe sliki, izmerjene dimenzije, svojo izbiro in rubriko. Če izbere drugo, spoštuj to: **najprej odstrani staro `images/izbrana.*` in znova prekopiraj izbrano sliko v `images/izbrana.<pripona>`**, šele potem popravi `_run.image` v celoti, tudi `chosen`, `url`, `rubric` in `reason`. Brez prve polovice gre v objavo zavrnjena slika - gate meri dimenzije datoteke in `_run.image.url` ločeno, da sta neusklajena, pa ne vidi.

## Faza B - slika za vsako socialno objavo

Teče po fazi A, ko je naslovna slika izbrana in `state.json` zapisan. Predmet so **vse** objave v
`social_posts[]` - korak 2 jih je zožil s štirih na tiste, ki jih je Igor potrdil, navadno dve. Za
vsako narediš eno sliko, torej vsaka objava stane en plačljiv klic.

Če jih ni dve, se **ne ustavljaj**: Igorju povej, koliko objav vidiš in koliko plačljivih klicev bo
to pomenilo, in nadaljuj po njegovem odgovoru. Meje ne zabija stroj - to bi Igorju vzelo odločitev v
konkretnem teku, ročna docx pot pa jih tako in tako pogosto vrne tri. Ustavi se samo pri **štirih
ali več**: to je znak, da korak 2 ni bil opravljen in bi delal slike za kandidatke, ki jih Igor ni
izbral. Slike ne izbirajo, katera objava gre v objavo.

12. Za vsako objavo `social_posts[i]` napiši prompt. Piši ga **iz besedila te objave**, ne iz
    kolumne in ne iz naslovne slike. Dve objavi z dvema različnima vzvodoma zaslužita dve različni
    sliki; dve različici istega motiva pomenita, da nisi bral objave.

    Slog vzemi iz `frodx-key-visual/references/visual-style.md` - isti FrodX videz kot naslovna
    slika. Prompt je angleški, brez besedila in logotipov na sliki, ker socialna omrežja besedilo
    na sliki slabo prikažejo v predogledu.

13. Za vsako objavo kliči n8n workflow `ZvoLqzl7zBr8X4WR` (webhook `social-image`) prek
    `execute_workflow`. Workflow ni aktiven, zato je `executionMode` `"manual"`:

    ```json
    {
      "workflowId": "ZvoLqzl7zBr8X4WR",
      "executionMode": "manual",
      "triggerNodeName": "Trigger",
      "inputs": {
        "webhookData": {
          "method": "POST",
          "body": {
            "prompt": "<prompt za to objavo>",
            "size": "1024x1024",
            "filename": "social-<slug>-<i>.png"
          }
        }
      }
    }
    ```

    **Ena kandidatka na objavo, samo OpenAI.** Gemini v tej fazi ne sodeluje - Janijeva odločitev
    18. 9. 2026. Primerjave ni, ker ni s čim primerjati; ocenjuješ eno sliko proti promptu.

    Odgovor je nespremenjeno telo `/api/images`, torej dve polji:

    ```json
    {"url": "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/<uuid>.png",
     "path": "<uuid>.png"}
    ```

    Rabiš `url`; `path` je pot v shrambi in ga nikamor ne zapisuješ.

14. Prenesi vse slike in jih izmeri - po eno datoteko na objavo, poimenovano po njenem indeksu
    (pri dveh objavah torej `social-0.png` in `social-1.png`):

    ```bash
    curl -sS -o runs/<slug>/images/social-0.png "<url objave 0>"
    curl -sS -o runs/<slug>/images/social-1.png "<url objave 1>"
    python3 <plugin>/skills/frodx-publish-send/scripts/dimenzije.py \
      runs/<slug>/images/social-0.png runs/<slug>/images/social-1.png
    ```

    Vsaka mora biti **1024x1024**. Manjša datoteka ni lepša slika, ampak pomanjšan predogled -
    tek 14. 9. 2026 je tako oddal 784x522 naslovno sliko. Če katera ne ustreza, ne izbiraj in ne
    popravljaj alt teksta; ponovi generacijo te ene objave.

15. Poglej vse slike. Za vsako odloči:
    - **sprejmeš:** slika ustreza objavi in ni videti kot generična zaloga;
    - **ponoviš:** popravi prompt in ponovi 13 za **to eno objavo**. Največ dve ponovitvi na objavo.
      Druge objave ne generiraš znova, ker je bila prva slaba.

16. Za vsako sprejeto sliko napiši slovenski alt tekst. Velja isto pravilo kot pri naslovni sliki:
    opiši, **kar je na sliki**, ne o čem je objava. En stavek, do 160 znakov, ciljno okoli 125. Ne
    začenjaj z »Slika prikazuje« ali »Fotografija«.

    Prevoda ni. Socialne objave so samo slovenske (`publishing-contract.md` §3), zato je tudi alt
    tekst samo slovenski - drugače kot naslovna slika, ki jih ima tri.

17. Zapiši v `state.json` **takoj**, ne šele ob Igorjevi potrditvi:

    - `social_posts[i].image_url` = javni URL sprejete slike te objave
    - `social_posts[i].image_alt` = alt tekst te objave
    - `_run.social_images`:

    ```json
    [
      {"index": 0, "url": "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/<uuid>.png",
       "prompt": "<prompt, kot je bil poslan>", "dimensions": [1024, 1024], "attempts": 1},
      {"index": 1, "url": "...", "prompt": "...", "dimensions": [1024, 1024], "attempts": 2}
    ]
    ```

    `index` je mesto objave v `social_posts[]`, ne zaporedna številka generacije. Če je vrstni red
    objav kdaj drugačen od vrstnega reda generiranja, je `index` tisti, ki drži.

18. Pokaži Igorju vsako objavo z njeno sliko skupaj - besedilo in slika drug ob drugem, ne ločena
    seznama. Na LinkedInu se vidita skupaj; oceniti ju je treba skupaj. Če katero sliko zavrne,
    ponovi 13 do 17 za tisto eno objavo in `state.json` prepiši v celoti za tisti `index`, tudi
    `_run.social_images`.

## Kako slike dejansko pridejo do tebe

Velja za obe fazi. Workflow faze A (`lHc3NdejxehMyc9O`, stanje preverjeno 16. 9. 2026) obe kandidatki
naloži v shrambo aplikacije in vrne javna URL-ja; workflow faze B (`ZvoLqzl7zBr8X4WR`) stori enako za
svojo eno sliko na objavo. Nalaganje opravi n8n s svojim credentialom; ključ nikoli ne pride v tvoj
kontekst.

Postopek je zato cel v točkah zgoraj - **3 do 5 za fazo A** in **13 do 15 za fazo B**: pokliči
workflow, prenesi slike s `curl`, izmeri jih z `dimenzije.py`, poglej jih in odloči.

**Kar se ne poskuša več:**

- `get_execution` binarnih bajtov na tej instanci ne vrne, ampak referenco na pot na disku n8n instance, ne sliko.
- Prepis base64 skozi kontekst na disk ne deluje. Poskus 15. 8. 2026 je dal 17 kB namesto 35 kB in
  `OSError: broken data stream when reading image file`.
- Ročni prenos datotek iz n8n UI. Bil je vmesna rešitev, dokler nalaganja ni bilo; zdaj je.

## Kaj ne delaš

- Ne nalagaš slike nikamor. URL naredi workflow, ko sliko naloži v shrambo; ti ga samo prevzameš iz
  odgovora - v fazi A v točki 4, v fazi B v točki 13.
- Ne pišeš alt teksta iz naslova članka, če slike nisi pogledal.
- Ne prevajaš slovenskega alt teksta v EN in HR. Vsak jezik opisuje sliko po svoje, naravno.
- Ne izbiraš »manj slabe« slike, da bi se izognil ponovitvi.
- Ne uporabljaš naslovne slike kot slike socialne objave. Naslovna je 1536x1024 in je narejena za
  og:image crop; socialna je kvadratna in nastaja iz besedila objave.
- Ne pišeš prompta socialne slike iz kolumne. Objava ima svoj vzvod - slika mora slediti njemu.
- Ne generiraš tretje slike »za izbiro«. Ena kandidatka na objavo je odločitev, ne omejitev orodja.

## Stroški

Tek stane obe fazi skupaj. **Faza A** porabi po en plačljiv OpenAI in en Gemini klic - dve kandidatki
za naslovno sliko. **Faza B** porabi po en plačljiv OpenAI klic na socialno objavo. Tek z dvema
objavama torej stane štiri slike. Pred tretjim poskusom naslovne slike vprašaj Igorja, ali naj
nadaljuješ.

Ne zaganjaj workflowa znova zato, da bi »morda tokrat« prišel binarni izhod. V teku 14.-15. 8. 2026 sta bila zaradi tega porabljena **dva para** slik (izvedbi 183698 in 183742). Če sta URL-ja iz prejšnje izvedbe še pri roki, ju uporabi - sliki v shrambi ostaneta in nov zagon zanju ni potreben.

Vsaka ponovitev v fazi B stane še en klic za tisto objavo. Pred tretjo ponovitvijo katerekoli objave
vprašaj Igorja, ali naj nadaljuješ.
