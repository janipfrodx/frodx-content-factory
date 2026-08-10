---
name: frodx-key-visual
description: Iz Igorjeve kolumne (ali samo teme/teze) izpelji vizualni koncept in vrni dva pripravljena prompta za generiranje key visuala - enega za Nano Banana (Gemini) in enega za ChatGPT/GPT-Image. Uporabi vedno, ko Igor reče "naredi key visual", "rabim naslovno sliko", "prompt za nano banana", "prompt za sliko kolumne", "vizual za blog", "og:image za kolumno", "scroll stopper za objavo" - ali ko ima gotovo kolumno in hoče naslovno sliko za FrodX blog (frodx.com/sl/blog) in LinkedIn. Par s skillom igor-column-writer (prevzame njegov "Predlog teme za vizual"). Paleto izbere glede na znamko teme (FrodX privzeto, Kinetara, InstantFeedback). NE generira slike sam - generirata jo zunanja modela; ta skill napiše prompta, ki ju Igor prilepi.
metadata:
  version: 1.6.0
---

# FrodX Key Visual

Ta skill iz kolumne izpelje **vizualni koncept** in napiše dva pripravljena prompta za generiranje naslovne slike: enega za **Nano Banana** (Gemini 2.5 Flash Image) in enega za **ChatGPT / GPT-Image**.

Cilj ni »slika k članku«. Cilj je key visual, ki ustavi skeptičnega direktorja sredi listanja po feedu - in se bere kot naslovnica resne poslovne revije, ne kot še en AI render.

Skill **ne** generira slike. Generirata jo zunanja modela. Skill napiše prompta, ki ju Igor prilepi v Gemini oz. ChatGPT.

## Kdo gleda

Isti bralec kot pri kolumnah: B2B odločevalci v Adriatic/DACH, siti AI vsebin. Generičen AI render (moder hologram, robotska roka, nevronski vrtinec, lebdeči UI) zanj ni scroll stopper - je signal »preskoči«. Skozi skepso reže uredniška fotografija z eno lateralno metaforo. Dve disciplini hkrati: koncept mora preživeti **thumbnail test** (~120 px, silhueta, en element) in imeti **visoko voltažo** - zadržan slog, glasna anomalija (obraz, nemogoča situacija, nemogoče merilo). Tiha duhovitost je za slike v članku, ne za feed; glej `references/visual-style.md`.

## Privzetki (ne sprašuj znova)

- **Slog:** konceptualna uredniška fotografija (register resnih poslovnih revij). Odklon na krepek grafični poster le, ko je teza strukturna/številčna - glej `references/visual-style.md`.
- **Format:** blog og:image, razmerje **1.91:1** (1200×630).
- **Tekst v sliki:** privzeto NE - vizual je čist, z negativnim prostorom za overlay naslova. **Izjema:** funkcionalni mikro-tekst, kadar je tekst *sama anomalija* (cenovna oznaka, številka, ena beseda na etiketi). Pravila: največ 2–3 kratke besede ali številke; jezikovno nevtralno ali delujoče čez SL/HR/EN; v promptu zapisano dobesedno v narekovajih; nikoli dekorativni napisi, naslovi ali logotipi; negativni prostor za overlay ostane.
- **Brez logotipov in vodnih žigov.**
- **Ljudje:** dovoljeni in pogosto zaželeni (obrazi ustavljajo scroll) - generična oseba, nikoli resnična/prepoznavna; pravila v `references/visual-style.md`.
- **Jezik promptov:** angleščina (modela tam delujeta bolje). Koncept in utemeljitev za Igorja v slovenščini.

## Delovni tok

Štirje koraki. Ne preskoči izpeljave koncepta - tam se loči scroll stopper od ilustracije teme.

### 1. Intake

Igor sproži skill s kolumno (markdown ali besedilo), s temo + tezo, ali z »Predlogom teme za vizual« iz `igor-column-writer`. Sprejmi karkoli.

Iz vnosa izlušči štiri stvari (kar manjka in se ne da izluščiti, vprašaj - združeno, v enem sporočilu, največ tri vprašanja):

1. **Teza** - kontraintuitivna trditev kolumne. To je tisto, kar mora vizual nositi.
2. **Čustveni sprožilec** - frustracija (#1) ali radovednost. Vizual mora ta občutek nositi, ne le ilustrirati teme.
3. **Konkreten motiv-kandidat** - objekt, prizor ali gesta iz kolumne, ki se da uprizoriti fizično. Če ima kolumna osebni hook v prvi osebi ali je vizual primarno za LinkedIn, presodi tudi varianto z **Igorjem v kadru** (prek referenčne fotografije - pravila v `references/visual-style.md`); ponudi jo kot opcijo, ne kot privzetek.
4. **Znamka in paleta** - ugotovi, na katero znamko družine FrodX meri tema (FrodX / Kinetara / InstantFeedback) in izberi pripadajočo paleto po `references/visual-style.md`. Vse tri so zaklenjene: FrodX #2465C9 + črna, InstantFeedback #00A4BD teal + #D564C4 magenta, Kinetara monokromno (črn/temen motiv na svetlem polju, brez barvnega poudarka).

Ne izmišljaj si blagovnih barv ali stranke. Koncept ne sme trditi številk - slika ne nosi dokaznega bremena, zato fabrikacija tu ni problem vsebine, je problem slogovne resničnosti znamke.

### 2. Preberi reference

- `references/visual-style.md` - privzeti slog, metoda izpeljave z mini primeri, **thumbnail test**, pravila za ljudi v kadru, **anti-slop seznam** (interni filter, ne za v prompt), kompozicija za 1.91:1, palete po znamkah, kdaj odkloniti na grafični poster.
- `references/prompt-recipes.md` - kako se piše prompt za Nano Banano (pogovorno) vs. za GPT-Image (strukturirano), izdelana primera, ravnanje z razmerjem in **playbook popravkov** za iteracijo.

### 3. Izpelji koncept

Iz teze najdi **lateralno fizično metaforo**, ne dobesedne ilustracije teme. Metoda in mini primeri (različne napetosti) so v `references/visual-style.md` - primeri so kalibracija metode, ne predloge motivov; izpelji svežega.

Naredi **2–3 koncepte**. Vsakega preveri skozi thumbnail test, test robustnosti in anti-slop filter, nato izberi najmočnejšega in v eni povedi povej, zakaj ustavi scroll. Preostala pusti kot rezervo (Igor lahko izbere drugega; na zahtevo napišeš prompta tudi zanj).

### 4. Napiši prompta, samokritika, izhod

Po `references/prompt-recipes.md` napiši oba prompta (Nano Banana + GPT-Image) za izbrani koncept. Oba v angleščini, isti motiv, kompozicija 1.91:1, negativni prostor, **kratka pozitivna omejitvena vrstica** (ne dolg »avoid« seznam - ta je interni filter; popravki gredo v iteracijo po playbooku).

Preden pokažeš: oceni po rubriki spodaj. Če je pod 9,0, popravi koncept ali prompt in oceni znova. Najpogostejši padci: koncept je dobeseden, pade na thumbnail testu, ali zdrkne v anti-slop klišeje.

## Izhodni format

Vrni točno v tem vrstnem redu, v slovenščini razen samih promptov:

```
## Vizualni koncept

**Izbrani koncept:** <ena poved: kaj vidimo + zakaj ustavi scroll>
**Metafora:** <kako motiv nosi tezo>
**Razpoloženje:** <frustracija / radovednost - in kako ga slika nosi>
**Thumbnail:** <ena poved: kaj se vidi pri 120 px>

### Prompt - Nano Banana (Gemini)
<angleški prompt, pogovorno-opisni>

### Prompt - ChatGPT / GPT-Image
<angleški prompt, strukturiran>

## Kako uporabiti
<2–3 stavki: kam prilepiti; v Gemini izberi razmerje v vmesniku, ne le v promptu; iteriraj en popravek na sporočilo po playbooku iz prompt-recipes.md; računaj na crop na 1200×630>

## Rezervna koncepta
1. <ena poved>
2. <ena poved>

## Ocena
<0–10 + 2–3 konkretne pripombe>
```

## Ocenjevalna rubrika (prag 9,0/10)

- **Moč koncepta (0–2):** lateralna metafora, ne dobesedna ilustracija; nosi tezo in napetost; en sam fokus; **voltaža za feed** - vsaj en močan vzvod (obraz / nemogoča situacija / nemogoče merilo / kričeča anomalija), ne le tiha duhovitost.
- **Robustnost (0–1):** anomalija je v tem, *kaj* je v kadru, ne v pozi/postavitvi; koncept preživi nenatančno generacijo. Koncept, ki potrebuje srečo pri izvedbi, ne more čez 9,0 skupaj.
- **Thumbnail test (0–1,5):** berljiv kot silhueta pri ~120 px; en element, en kontrast.
- **Anti-slop (0–2):** prestane interni filter; nič holograma/robota/vrtinca/lebdečega UI; bere se kot uredniška fotografija, ne stock.
- **Kompozicija (0–1,5):** en jasen fokus, namerni negativni prostor za overlay, 1.91:1, nadzorovana svetloba.
- **Brand fit (0–1):** paleta znamke pravilno izbrana in vključena; brez logotipov in teksta.
- **Kakovost prompta (0–1,5):** oba prompta popolna in pisana po logiki svojega modela; omejitve kratke in pozitivne; element, ki mora biti prazen, označen pri elementu samem.

## Trde omejitve

- Razmerje vedno **1.91:1**; negativni prostor na eni strani za overlay.
- **Nič teksta, logotipov, vodnih žigov** v sliki.
- Anti-slop seznam je interni filter - v prompt gre le kratka pozitivna omejitvena vrstica.
- Thumbnail test je obvezen pred izborom koncepta.
- Prompta v angleščini; vse ostalo za Igorja v slovenščini.
- Brez izmišljenih blagovnih barv - samo zaklenjene palete iz `references/visual-style.md`; Kinetara je namerno monokromna (brez barvnega poudarka).
