# Prompt recipes - Nano Banana vs. GPT-Image

Oba prompta opisujeta **isti motiv**. Razlikuje se forma, ker modela drugače poslušata. Oba sta v angleščini.

## Skupna pravila

- En motiv, en fokus, uredniška fotografija (razen pri grafičnem posterju).
- Razmerje: navedi **wide 1.91:1 landscape** v promptu, a vedi, da prompt ni jamstvo - glej »Razmerje in crop« spodaj.
- Negativni prostor na eni strani za overlay naslova - navedi stran.
- **Omejitve formuliraj pozitivno in kratko.** Generativni modeli nimajo pravega »negative« polja (GPT-Image vse bere kot en tekst) in dolgi »avoid« seznami znajo priklicati ravno naštete elemente. Privzeta omejitvena vrstica je ena sama:
  > Clean image with no text, no logos and no watermarks; grounded, realistic editorial photography.
  Daljši popravki pridejo šele v iteraciji, ciljano (glej »Playbook popravkov«).
- **Funkcionalni mikro-tekst** (kadar je dovoljen po SKILL.md): zapiši ga dobesedno v narekovajih pri elementu (»a small price tag reading exactly "€45"«) in hkrati prepovej vse ostalo besedilo (»no other text anywhere in the image«). GPT-Image je pri kratkih napisih zanesljivejši; pri Nano Banani po prvi generaciji preveri črkovanje in po potrebi popravi v iteraciji.

## Nano Banana (Gemini 2.5 Flash Image)

Posluša **pogovorno, opisno prozo** - kot da fotografu opisuješ prizor. Vodi z motivom in občutkom, ne s seznamom parametrov. Dve močni lastnosti, ki ju izkoristi:

- **Iterativno popravljanje:** naslednje sporočilo je en ciljan popravek (»make the light warmer«, »more empty space on the left«), model ohrani prizor.
- **Referenčna slika:** če ima Igor fotografijo lokacije, izdelka ali osebe v slogu, jo lahko priloži in zahteva »in this style« ali »place this object in …«. Omeni mu to možnost, kadar koncept stoji na specifičnem objektu (npr. dejanski Kinetara naprava/zaslon). Posebej: za varianto z **Igorjem v kadru** vedno prek njegove priložene fotografije (»place the person from the reference photo in this scene, keeping his face accurate«) - nikoli po opisu; deadpan in pravilo »v prizoru, ne komentira prizora« veljata enako.

Struktura (tekoča proza, ne bullet seznam):

> An editorial magazine-cover photograph of [SUBJECT + what it is doing / its state]. [Setting and atmosphere in one sentence.] Shot in the restrained, serious style of a business-magazine cover: single subject, quiet tension. [Light: one directional source, quality, mood.] [Palette: brand accent + neutral field.] Wide 1.91:1 landscape composition with generous empty negative space on the [left/right] for a title overlay. Photorealistic and clean, with no text, no logos and no watermarks.

### Izdelan primer (napetost »nagrada, ki kaznuje«; FrodX paleta)

> An editorial magazine-cover photograph of two identical takeaway coffee cups side by side on a pale counter, one of them casually marked down with a small elegant price tag, the other untouched. A cold, almost clinical retail setting, slightly out of focus behind. Shot in the restrained, serious style of a business-magazine cover: symmetrical, quiet, with one unsettling asymmetry. Soft directional daylight from the left, gentle shadows. Neutral pale field with a single deep blue (#2465C9) accent on the price tag. Wide 1.91:1 landscape composition with generous empty negative space on the right for a title overlay. Photorealistic and clean, with no text on the tag itself, no logos and no watermarks.

Opomba: če mora biti element brez napisa (kartonček, zaslon), to povej pri elementu samem (»no text on the tag itself«) - splošna omejitev na koncu ne zadošča vedno.

## ChatGPT / GPT-Image

Posluša **strukturirano**. Razbij v bloke; model jih zanesljivo upošteva. Brez imen živih fotografov in brez blagovnih znamk v sliki.

Struktura (bloki):

> **Subject:** [en motiv, stanje / gesta]
> **Setting:** [okolje, atmosfera]
> **Composition:** wide 1.91:1 landscape; single focal point on the [left/right] third; large empty negative space on the [opposite side] for a title overlay
> **Lighting:** [en usmerjen vir, kakovost, sence]
> **Color:** [poudarna barva znamke + nevtralno polje]
> **Camera:** editorial photography, [50mm / 35mm], [globinska ostrina]
> **Mood:** [napetost teze - utelešena, ne opisana]
> **Style:** serious business-magazine cover photograph, photorealistic, restrained
> **Output:** clean image with no text, no logos, no watermarks

### Izdelan primer (napetost »red, ki skriva nered«; s človekom; InstantFeedback paleta)

> **Subject:** a person seen from behind, carefully watering a single perfect artificial plant
> **Setting:** an otherwise empty, very tidy modern office, bright and slightly sterile
> **Composition:** wide 1.91:1 landscape; figure and plant on the right third; large empty pale wall on the left for a title overlay
> **Lighting:** soft, even daylight from a large window, minimal shadows
> **Color:** bright neutral field with a single teal (#00A4BD) accent on the watering can
> **Camera:** editorial photography, 35mm, medium depth of field
> **Mood:** quiet absurdity - diligent care for something that cannot grow
> **Style:** serious business-magazine cover photograph, photorealistic, restrained
> **Output:** clean image with no text, no logos, no watermarks; the person is generic and not recognizable

Primera sta namerno različna (objekt-anomalija vs. človek-gesta; dve znamki). Ne recikliraj njunih motivov - prompt izpelji iz svežega koncepta.

## Razmerje in crop

- V **Gemini** (Nano Banana) razmerje najzanesljiveje držiš z izbiro aspect ratio v vmesniku, ne le v promptu. Igorju to povej v »Kako uporabiti«.
- V **ChatGPT** zahtevaj »landscape«; GPT-Image privzeto generira 1536×1024 (3:2), ne 1.91:1.
- V obeh primerih bo za og:image verjetno potreben **crop na 1200×630** - koncept naj to prenese (fokus stran od robov, negativni prostor velikodušen).

## Playbook popravkov (iteracija)

Ko prvi izid ni pravi, popravljaj **ciljano, en popravek na sporočilo** (Nano Banana ohrani prizor; v ChatGPT ponovi cel prompt s spremenjenim blokom):

| Problem | Popravek |
|---|---|
| Pojavi se tekst/napis | »remove all text and lettering from the image« + pri elementu: »the [tag/screen] is blank« |
| Premalo praznine | »make the [left] side a plain empty wall, move the subject further [right]« |
| Preveč elementov / gneča | »simplify the scene: keep only [subject], remove everything else« |
| Plastičen render videz | »more natural photographic texture, subtle film grain, realistic materials« |
| Sci-fi / sij / hologrami se prikradejo | »no glowing or futuristic elements; ordinary, physical, present-day objects only« |
| Napačna barva poudarka | »change the [object] color to deep blue #2465C9, keep everything else unchanged« |
| Čudne roke | »reframe so the hands are not visible« ali poenostavi gesto |
| Stock poza / izraz ubije deadpan (kažoči prsti, nasmeh, poziranje) | »his expression is calm, serious and matter-of-fact, not smiling; no presenting gestures, hands relaxed« - izraz je nosilni element prizora, popravi ga pred vsem drugim |

Anti-slop popravki pridejo torej **šele tu**, ciljano in posamično - ne preventivno v osnovni prompt.
