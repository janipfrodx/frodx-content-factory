# Preizkusi image-run - navodilo za Janija

Ta preizkus je izpuščen iz avtomatske izvedbe, ker vsak tek porabi plačljiv OpenAI in Gemini klic za sliko. Navodilo je samostojno - ne rabiš prebrati načrta, da ga izvedeš.

Preveri se troje: da sliki sploh prideta do skilla, da ju skill **izmeri, preden ju pogleda**, in da po tvoji zamenjavi izbire v mapi teka res leži tista slika, ki si jo izbral.

## Preden začneš

Stanje workflowa `lHc3NdejxehMyc9O` (`Generiraj sliko (Content Factory)`), preverjeno v živo 16. 9. 2026: **ni aktiven** (`active: false`), 8 vozlišč, zadnjič spremenjen 15. 8. 2026, trigger se imenuje `Trigger`.

Ker ni aktiven, produkcijski webhook `https://frodxai.app.n8n.cloud/webhook/generate-image` klica ne sprejme. Skill ga zato kliče prek orodja `execute_workflow` z `executionMode: "manual"` - to je pot, ki jo preizkušaš, in `"manual"` je za ta workflow dovoljen tudi takrat, ko klic dejansko porabi OpenAI in Gemini.

Telo gre gnezdeno pod `inputs.webhookData.body`:

```json
{
  "prompt_openai": "<GPT-Image prompt iz frodx-key-visual>",
  "prompt_gemini": "<Nano Banana prompt iz frodx-key-visual>",
  "size": "1536x1024"
}
```

Vozlišči, ki vrneta sliki, sta `OpenAI Image` (model `gpt-image-1`) in `Gemini Image` (model `models/gemini-3-pro-image`, "Nano Banana Pro").

Če hočeš workflow preizkusiti brez skilla, odpri workflow v n8n UI, klikni "Listen for test event" na vozlišču `Trigger` in v dveh minutah pošlji zahtevo na testni URL:

```bash
curl -X POST https://frodxai.app.n8n.cloud/webhook-test/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt_openai": "<prompt>", "prompt_gemini": "<prompt>", "size": "1536x1024"}'
```

## Kako sliki prideta do skilla - preberi, preden očitaš napako

Stanje preverjeno 16. 9. 2026. Workflow obe sliki naloži v shrambo aplikacije (gostitelj
`umvjwjzdrtamfrcqhopa.supabase.co`) in v odgovoru vrne javna URL-ja:

```json
{"openai": {"url": "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/<uuid>.png"},
 "gemini": {"url": "..."}}
```

Skill oba URL-ja sam prenese s `curl` v `images/openai.png` in `images/gemini.png`. Ročni prenos prek n8n UI ni
več potreben. `get_execution` binarnih bajtov ne vrne (instanca teče v načinu `filesystem-v2` in vrne referenco
na pot na disku, ne slike) - to skillu ni več ovira, ker slik od tam ne potrebuje.

Če skill poskuša sliki dobiti prek `get_execution`, te prosi, da ju ročno preneseš iz n8n UI, ali poroča, da
»slike ni bilo mogoče generirati«, je to napaka skilla - zapiši jo. Generirani sta bili.

Celoten razdelek je v `SKILL.md`, »Kako sliki dejansko prideta do tebe«.

## Preizkus 1: živ tek

Vzemi `languages.sl.content` iz `tests/fixtures/package_valid.json` (repo `frodx-content-factory`). Naslov kolumne je `meta.title`: "Zakaj lojalnostni programi kaznujejo zveste kupce".

1. Pokliči `frodx-key-visual` s tem naslovom in besedilom, da dobiš `prompt_openai` in `prompt_gemini`.
2. Pusti skillu, da pokliče workflow prek `execute_workflow` in sam prenese sliki iz vrnjenih URL-jev.
3. Od tod naprej dela skill sam: izmeri, odloči, kopira, napiše alt tekste in zapiše `state.json`.

Preveri:

- [ ] `frodx-key-visual` vrne dva ločena prompta
- [ ] klic prek `execute_workflow` dejansko sproži izvedbo (če ne, poskusi z `triggerNodeName: "Trigger"` in to zapiši kot najdbo)
- [ ] skill sliki prenese s `curl` iz URL-jev v odgovoru workflowa - **ne** poskuša brati bajtov prek `get_execution` in te ne prosi za ročni prenos iz n8n UI
- [ ] skill **izmeri obe sliki, preden ju pokaže**, in izpiše dimenzije

  ```bash
  python3 plugins/content-factory/skills/frodx-publish-send/scripts/dimenzije.py \
    runs/<slug>/images/openai.png runs/<slug>/images/gemini.png
  ```

- [ ] kandidatka pod **1200x630** je zavrnjena, tudi če je lepša; če nobena ne doseže praga, skill ne izbira, ampak pove, da si najbrž dobil pomanjšan predogled
- [ ] izbrana slika je v `images/izbrana.png` - **ena sama datoteka in ena sama pripona**, nobene `izbrana.jpg` poleg nje
- [ ] alt teksti so trije, vsak en stavek do 160 znakov, noben se ne začne z »Slika prikazuje«, »Image of« ali »Fotografija«, in nobeden ni prevod slovenskega
- [ ] `_run.image` ima vseh pet polj: `chosen`, `attempts`, `dimensions` (izmerjene, ne ugibane), `rubric` in `reason`
- [ ] `rubric` ima šest povedi: `koncept`, `robustnost`, `thumbnail`, `anti_slop`, `kompozicija`, `brand_fit` - povedi o **izbrani** sliki, ne ocene v številkah
- [ ] `_run.step` = 5 in `_run.status` = `awaiting_approval`
- [ ] zapis v `state.json` je nastal **takoj ob nastanku rezultata**, ne šele ko si potrdil - preveri datoteko, preden karkoli odgovoriš

**Strošek:** en plačljiv OpenAI in en Gemini klic. Za ta preizkus zadošča en tek brez ponovitev.

## Preizkus 2: zavrnitev obeh slik

Povej skillu, da sta obe sliki neustrezni - na primer, da ena prikazuje izmišljeno številko na zaslonu ali grafu (merilo 1 iz `references/image-decision.md`).

Preveri:

- [ ] skill popravi **oba** prompta v isti smeri glede na povedano pomanjkljivost
- [ ] skill znova pokliče workflow s popravljenima promptoma (2. poskus)
- [ ] po **drugi** ponovitvi skill ne poskusi tretjič sam, ampak vpraša Igorja, ali naj nadaljuje
- [ ] `_run.image.attempts` šteje poskuse pravilno

**Strošek:** vsaka ponovitev porabi nov par klicev. Za preizkus meje zadostujeta dve ponovitvi (skupno največ trije pari slik).

## Preizkus 3: zamenjava izbire

To je najtišja napaka v verigi, zato ima svoj preizkus. Ko ti skill pokaže obe sliki in svojo izbiro, **izberi drugo, kot jo je predlagal**.

Preveri:

- [ ] skill **najprej znova prekopira** izbrano sliko čez `images/izbrana.png` in šele potem popravi `_run.image`
- [ ] `images/izbrana.png` je po tem res tista slika, ki si jo izbral ti - odpri datoteko in poglej, ne verjemi zapisu
- [ ] `_run.image` je popravljen **v celoti**, tudi `rubric` in `reason`, ne le `chosen`
- [ ] alt teksti ustrezajo novi sliki, ne stari

Gate v `frodx-publish-send` meri samo dimenzije, zato zamenjane slike ne bi opazil. Če ta preizkus pade, gre v objavo zavrnjena slika z alt tekstom, napisanim za drugo.

## Zapis rezultatov

<!-- Dopolni po vsakem izvedenem preizkusu: datum, kdo je izvedel, kateri preizkus, izid (prestal/ni prestal) in morebitne opombe. -->
