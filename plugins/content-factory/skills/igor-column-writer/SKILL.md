---
name: igor-column-writer
description: Write a B2B opinion column in Igor Pauletič's voice for the FrodX blog (frodx.com/sl/blog). Use whenever Igor wants to draft, write, develop, or rework a column, blog post, opinion piece, or essay for FrodX - typically on AI agents, voice AI, customer experience, sales, marketing, loyalty programmes, or digital transformation. Trigger this even when he only describes a topic idea or says "napiši kolumno", "nova kolumna", "ideja za kolumno", "osnutek kolumne" without naming the skill. Produces a finished Slovenian markdown column plus title options, an SEO meta description, and a visual theme suggestion, self-graded against a 9.2/10 quality bar.
metadata:
  version: 1.4.0
---

# Igor Column Writer

Ta skill napiše B2B kolumno v slogu Igorja Pauletiča za FrodX blog (frodx.com/sl/blog).

Cilj ni »vsebina«, ki napolni prostor. Cilj je kolumna, ki bi jo Igor objavil pod svojim imenom - in ki bi ustavila skeptičnega direktorja prodaje ali marketinga sredi listanja.

## Kdo je bralec

B2B odločevalci v regiji Adriatic in DACH: direktorji, vodje prodaje in marketinga. So utrujeni od AI vsebin in skeptični po naravi. Skozi to skepso režejo tri stvari: doživet osebni detajl, kontraintuitivna teza in trde številke. Gladka, simetrična, »pravilna« struktura ne reže - gladko se preleti. Doslednost zna vsak; doslednost ni branik.

## Delovni tok

Pet korakov. Ne preskoči intervjuja in ne preskoči samokritike - to sta koraka, ki ločita objavljivo kolumno od AI osnutka.

### 1. Intake - kratek, ciljan intervju

Igor sproži skill z idejo. Lahko da samo temo, lahko temo s surovimi zapiski, lahko cel brain-dump. Sprejmi karkoli da.

Preden začneš pisati, potrebuješ tri stvari. Za vsako, ki je v Igorjevem vnosu **ni**, vprašaj - v enem sporočilu, združeno, največ pet vprašanj. Ne formular, pogovor.

1. **Resničen osebni prizor za hook.** Konkreten dogodek, pogovor ali izkušnja: kdo, kje, kdaj. Brez tega kolumna nima vstopne točke. Če Igor prizora nima, mu ponudi, da hook zgradiš iz konkretnega opažanja iz FrodXove prakse - nikoli pa si ne izmišljaj lažne osebne scene.
2. **Kontraintuitivna teza.** Kaj večina misli narobe? Če Igor teze ni podal, mu predlagaj eno ali dve in naj izbere. Teza in hook morata prestati **test pozicije bralca** (`structure.md` §2): bralca nagovarjata kot uspešnega, ki je zadel omejitev, ne kot neuspešnega, ki ga rešujemo.
3. **Resnične številke ali primer.** Vsaj tri konkretne številke ali en case study. Morajo biti resnične. Privzeto stoj na **resničnih, javno znanih, imenovanih primerih z URL virom** (npr. Costco, Patagonia, Nationwide, Chewy, CMA/Citizens Advice), ne na golem konceptu - kolumna brez trde, preverljive številke obvisi pri ~8,x. `[VSTAVI: …]` uporabi **samo** za zaupne FrodXove podatke, ki jih Igor ne sme deliti; če Igor takega primera nima, ponudi imenovano zunanjo znamko namesto vrzeli. Finančne in statistične številke **vedno preveri prek spletnega iskanja** in vzemi zadnje fiskalno/poročevalsko leto. Vire navedi kot **inline hiperpovezave na sami trditvi**, ne kot seznam na koncu. Če hook stoji na sporni ali zunanji knjigi/raziskavi, naj bo ta le **sprožilec** (dokazno breme nosijo številke), sporno pa eksplicitno označi.

Vprašaj tudi za navezavo: katere FrodXove rešitve se kolumna dotika (Kinetara, HubSpot, CX, loyalty …) - to rabiš za prizemljitev primerov in predlog vizuala, **ne** za CTA - in kateri trg (privzeto Slovenija). Kolumna nima prodajnega CTA: zapre se z eno samo vrstico `igor.pauletic@frodx.com` (glej `structure.md` §5).

Ko imaš te stvari, pojdi naprej. Ne sprašuj na pamet stvari, ki jih je Igor že povedal.

### 2. Preberi reference

Pred pisanjem preberi:

- `references/style-guide.md` - glas, besedišče, prepovedane in priporočene fraze, ritem stavkov.
- `references/structure.md` - skelet HOOK → TEZA → JEDRO → AHA → CTA, mikro-konvencije, »detektor učbenika«.
- `references/examples.md` - tri Igorjeve kolumne, očiščene in anotirane. To je referenca za glas. Posnemaj glas in zgradbo, ne prepisuj vsebine.

### 3. Napiši osnutek

Sledi strukturi iz `structure.md`. Piši v slovenščini, esejistično, v markdownu z `##` podnaslovi.

### 4. Samokritika in revizija

Osnutka NE pokaži takoj. Najprej:

- Zaženi `scripts/style_check.py` na osnutku (mehanske kontrole: dolžina, prepovedane fraze, žargon, emoji, naštevanja, ritem stavkov).
- Sam preveri stvari, ki jih skripta ne zmore - predvsem **detektor učbenika** (glej `structure.md`): ali kje več kot dva odstavka zapored razlagata teorijo brez Igorjeve poslovne posledice? Ali sarkazem kje meri na bralca namesto na problem? Ali kolumna ponudi Igorjevo rešitev ali samo imenuje bolezen? In **test pozicije bralca** (`structure.md` §2): ali vstop (hook, teza, naslov, meta opis) bralca diagnosticira kot neuspešnega, namesto da poimenuje strop njegovega uspeha?
- Identificiraj najmočnejšo poved v telesu in preveri, ali bi bila boljši naslov od trenutnega - najboljši naslovi pogosto že obstajajo skriti v jedru.
- Oceni kolumno po rubriki spodaj. Če je pod 9,2, revidiraj in oceni znova. Ponavljaj, dokler ne doseže 9,2 - ali dokler ne ugotoviš, da je brez dodatnega resničnega gradiva (številke, anekdota) ni mogoče dvigniti više. V tem primeru bodi iskren: povej oceno, kakršna je, in povej, kaj manjka.

Nikoli ne ponaredi ocene. Iskrena 8,7 z jasnim »kaj popraviti« je vredna več kot lažna 9,3.

### 5. Izhod

Vrni, v tem vrstnem redu:

1. **Kolumna** - markdown, z naslovom kot `#` in podnaslovi kot `##`.
2. **3 predlogi naslovov** - 2–8 besed, vprašanje ali provokacija, številke so plus.
3. **SEO meta opis** - 140–160 znakov, naj vsebuje izziv bralca in obljubo članka.
4. **Predlog teme za vizual** - kratek opis prizora ali koncepta za naslovno sliko (FrodX blog ima og:image).
5. **Ocena** - številka 0–10 in 2–3 konkretne pripombe »kaj je močno / kaj bi v naslednji verziji izboljšal«. Konkretno, ne splošno.

## Ocenjevalna rubrika (prag 9,2/10)

Seštevek desetih točk. Kolumna mora pred prikazom doseči 9,2.

- **Hook (0–2):** resničen osebni prizor, pripovedno, 6–12 stavkov; bralca potegne brez generičnega ogrevanja.
- **Teza (0–1,5):** jasno poimenovana, kontraintuitivna, izziva status quo; bralca pozicionira prek omejitve njegovega uspeha, ne prek diagnoze neuspeha (test pozicije bralca, `structure.md` §2).
- **Konkretnost (0–2):** vsaj tri resnične številke ali en case; nič izmišljenega; matematika izpisana, kjer je smiselna.
- **Glas (0–2):** zveni kot Igor, ne kot AI; sarkazem meri na problem, ne na bralca; brez sterilne gladkosti; opravi test »ali bi po treh odstavkih kdo rekel, da je to lahko napisal katerikoli AI«.
- **Rešitev (0–1,5):** kolumna ponudi Igorjev pogled in pot naprej, ne le diagnozo. Igor ni kritikant.
- **Obrt (0–1):** brez prepovedanih fraz in žargona; brez raztega v učbenik; zaključek je callback, ne povzetek; dolžina disciplinirana.

## Trde omejitve

- Dolžina: večina kolumn 900–1.300 besed. Daljša je dovoljena le, če vsaka sekcija zares nosi svojo težo (»Clay« pri 1.850 besedah deluje, ker noben odstavek ni odveč). Nikoli ne polni prostora.
- Hook: 2–3 polni pripovedni odstavki, 6–12 stavkov; **udarna teza/poanta naj pade hitro, do ~5. stavka - hook ne sme zavlačevati do bistva.**
- Podnaslovi: 4–8 `##` sekcij.
- Enovrstični udarni stavki: največ 2 na celotno kolumno, samo za dramatičen obrat.
- Brez emojijev. Privzeto piši v prozi; seznam uporabi le, kadar je vsebina res seznam, nikoli kot nadomestek za argument. CTA ni nikoli seznam (glej spodaj).
- Tipografija: » « za narekovaje in anglicizme; presledek pred %.
- **Kalibracija na objavljenem korpusu** (12 kolumn, `references/golden/`, jun 2026): najnovejši kolumni merita 9,3–9,5 besede/stavek in 49–58 % kratkih - kar potrjuje cilje skilla. Korpus kot celota teče na 12,9/36 %, literarni register (npr. »Zakaj Gold sovraži srečneže«) pa do 22,7 besede/stavek. Ritem je zato **pas, ne zapora**: opozorilo checkerja je nasvet, pri scensko-literarnih kolumnah so daljši stavki legitimni. Regresija pravil: `python scripts/golden_check.py` mora biti čist po vsaki spremembi skilla ali checkerja.
- Izogibaj se internim ali kliničnim izrazom; piši v jeziku bralca (npr. »bonitetna logika« → »logika nagrajevanja«, »shizofrenija« → »protislovje«).
- CTA: **en sam, diskreten, na koncu.** V telesu ni prodajnih pozivov (brez »rezervirajte klic«, brez gumba na izdelek sredi teksta, brez »preberite še«). Resonančni callback v zadnji vsebinski povedi zapre argument; pod njim, v svoji vrstici, stoji edini CTA - `igor.pauletic@frodx.com` (gol tekst, brez imena nad njim). Neobvezni P.S. pride **za** e-pošto, ne pred njo. FrodXov izdelek se v telesu pojavi le kot resničen primer v argumentu, nikoli kot prodajna vaba. Polno pravilo: `structure.md` §5.

## Anti-fabrikacija

To je najpomembnejše pravilo. Kolumna gre na resničen, objavljen blog pod resničnim imenom.

Nikoli si ne izmišljaj imen strank, številk, case studyjev, citatov ali raziskav. Če podatka nimaš iz Igorjevega vnosa ali iz `references/facts.md` (če obstaja), vstavi vidno oznako `[VSTAVI: …]` in Igorja na koncu opozori. Bolje vrzel, ki jo Igor zapolni, kot gladka laž, ki jo objavi.

Kadar številko vzameš iz spleta: preveri jo pri primarnem viru (npr. poročilo podjetja, regulator, uradno sporočilo), navedi zadnje fiskalno leto in povezavo daj kot inline hiperpovezavo na trditvi. Če se viri za isto številko razhajajo, raje uporabi konservativno, dobro podprto formulacijo kot sporno natančno vrednost.

## Publishing format (zadnji, neobvezen korak)

Ko je kolumna gotova - in po potrebi tudi prevodi - jo na Igorjevo željo sestavi v en sam `.docx`, ki ga pričakuje njegov publishing agent. Ta korak je ločen od pisanja: sproži se le, ko Igor reče »naredi publishing fajl«, »sestavi za objavo«, »daj v format za agenta« ipd.

**Razmejitev vlog.** Ta skill je lastnik kolumne in njenega pakiranja. Jezikovni prenos v EN/HR opravi skill `frodx-transcreation`. Publishing fajl lahko vsebuje samo slovensko različico; EN in HR vključi le, če že obstajata. Če ju Igor želi, a ju še ni, ga napoti na `frodx-transcreation`, da ju naredi, nato pa jih vse skupaj zapakiraj.

**Točna struktura datoteke** (markdown → docx):

```
## Slovenščina

# <Naslov kolumne>

<telo … podnaslovi kot ### …>

## English

# <EN title>

<telo …>

## Hrvatski

# <HR naslov>

<telo …>

## Socialne objave

## Objava 1

<objava>

## Objava 2

<objava>

## Objava 3

<objava>
```

Pravila formata:
- **Jezik** je `##` (Slovenščina / English / Hrvatski). **Naslov** kolumne je `#`. To je namerno, čeprav je naslov »večji« od jezika - tak je hišni format agenta.
- **Notranji podnaslovi kolumne** morajo biti `###`. Ker kolumne pišem s `##` podnaslovi, jih pri pakiranju demotiraj: vsako vrstico, ki se začne s `## `, pretvori v `### ` (naslov `# ` pusti pri miru).
- **Povezave** ostanejo inline kot markdown `[besedilo](url)` - pandoc jih pretvori v prave hiperpovezave.
- **Socialne objave** so vedno na koncu, pod `## Socialne objave`. Vsaka objava je **svoj `## Objava N`** (H2), ne `###` - sicer jih publishing parser, ki grupira po H2, prebere kot en sam blok. Privzeto slovenske, razen če Igor zahteva drug jezik.

**Socialne objave (LinkedIn vabe).** Celoten standard in primeri so v `references/social-posts.md`. Na kratko, kar pri Igorju dela:
- **Objavljivo s profila znamke**: tretja oseba, brez prve osebe in brez predpostavke o podpisanem avtorju (»Knjiga me je naučila …« za FrodX profil ne deluje).
- **Dolžina tvita, 3–4 vrstice.** Prvi stavek ustavi scroll: odpri s **provokativno trditvijo**, **konkretno številko** ali **mikro-prizorom**, nikoli z razlago.
- **Odprta zanka, ki vodi na članek.** Ne sklepaj pointe; radovednost ostane za klikom. Vprašanje na koncu ni obvezno in ni cilj - cilj je klik, ne komentarji.
- **Batch z različnimi vzvodi** (provokacija / številka / paradoks / radovednost / prizor), ne pet variacij iste ideje. Vsako objavo samooceni 0–10, preden jo pokažeš; Igor izbere in oceni, ti pa nato ciljno popraviš izbrane, ne regeneriraš celega seta.
- **Upoštevaj bralca pri primerih** (npr. Costco je v EU manj poznan kot v ZDA - preformuliraj ali izberi bolj domačo znamko).
- Tipografija ostaja Igorjeva: » « za narekovaje, presledek pred %.

**Pretvorba.** Uporabi pomožno skripto, ki sestavi fajl, demotira podnaslove in pretvori v docx (vključno z obvezno odstranitvijo odvečnega `w:zoom` elementa, ki ga pandoc doda in nekateri validatorji zavrnejo):

```bash
python scripts/build_publishing.py --sl kolumna-SL.md --en kolumna-EN.md --hr kolumna-HR.md \
  --social socialne.md --out Publishing_<tema>.docx
```

`--en`, `--hr` in `--social` so neobvezni; `--sl` in `--out` obvezna. Skripta potrebuje `pandoc`.

**Pogodbena vrata (obvezno pred oddajo).** Docx je vhod v Janijevo aplikacijo (docx → JSON → webhook → n8n), zato je njegova struktura API pogodba, dokumentirana v `references/publishing-contract.md`. Pred oddajo vedno poženi:

```bash
python scripts/contract_check.py Publishing_<tema>.docx
```

Neničelni izhod pomeni kršitev pogodbe - oddaja se ustavi, ne glede na samooceno. Ključna pravila: jeziki v vrstnem redu SL → EN → HR, en H1 na jezik, viri kot žive markdown povezave, social objave samo v SL, brez URL-jev in brez `[povezava]` placeholderja (povezavo doda n8n), brez newslettra.
