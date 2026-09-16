# Ocenjevanje in rangiranje tem

Presoja izhaja iz skilla `aeo-topic-brief`, ki je isto delal nad mail-brifom iz AEO poročila. Logika
je ista, vhod je drug: prompti in priporočila neposredno iz portala, kot jih opisuje
`references/aeo-source.md`.

## Kaj šteje kot dobra tema

Vsa štiri merila morajo veljati:

- **Naslavlja konkreten `target_prompt`.** To ni več presoja - prompt je dobesedno besedilo iz
  HubSpota. Zaostriti je treba **temo**, ne prompta: iz vprašanja naredi stališče, ki nanj dejansko
  odgovarja.
- **Odgovor bi bil citirljiv za AI iskalnik**: jasen, strukturiran, samostojen. Vprašanje iz
  `target_prompt` postane naslov razdelka z direktnim odgovorom v prvem stavku.
- **Vezana na FrodX ekspertizo**: HubSpot, SAP Engagement Cloud / Emarsys, Open Loyalty, CloudTalk.
  Za primerjave z orodji, ki jih FrodX ne implementira, pišeš kot **nevtralen integrator**, ne kot
  zagovornik ene platforme.
- **Realen obseg** za en kos vsebine.

## Ali kolumna ta prompt sploh lahko premakne

To je pomembnejše od vseh števil. Prompti so dveh vrst:

- **Razlagalni** - »Kako težka je migracija na HubSpot?«, »Ali je bolje razviti lasten loyalty
  program ali uporabiti platformo?«, »Kako pripraviti načrt in specifikacijo?«. AI nanje odgovarja z
  razlago in citira članke. **Kolumna jih premakne.**
- **Iskalni po ponudnikih** - »Kateri partnerji v Sloveniji…«, »Kdo ima največ izkušenj…«, »Koga naj
  primerjamo?«. AI nanje odgovarja s seznamom podjetij in citira imenike, strani agencij in
  listicle. **Kolumna jih premakne le posredno**; premakne jih prisotnost v teh seznamih.

Iskalnih promptov **ne izloči** - uvrsti jih nižje in ob predlogu povej, zakaj. Odločitev je
Igorjeva, ne tvoja.

Praktičen znak, po katerem prompt prepoznaš: visok `averageCompetitorsMentioned` (3 in več) skoraj
vedno pomeni iskalni prompt, ker je AI naštel podjetja. Pri razlagalnih je ta številka nizka.

## Formati

| Signal v `target_prompt` | format |
| --- | --- |
| Konkretno vprašanje z več podvprašanji | `FAQ` |
| »kako narediti X« | `vodnik` |
| »kaj je bolje, X ali Y«, »X proti Y« | `primerjava` |
| Široka ali mnenjska teza | `kolumna` |

Kadar za prompt obstaja priporočilo z `actionChannel: "OWNED_CONTENT"`, je njegov `contentType`
namig, ne odločitev: `COMPARISON` kaže na primerjavo, `GUIDE` na vodnik, `LISTICLE_COMPARISON` na
primerjalni pregled. Če se s tem, kar bereš iz oblike prompta, ne ujema, povej svoj format in zakaj.

### Veriga zna izdelati samo kolumno

Korak 2 verige je `igor-column-writer`. Drugih producentov vsebine veriga nima - `vodnik`,
`primerjava` in `FAQ` bodo v praksi izvedeni kot mnenjska kolumna.

To je pomembno **pri izbiri teme, ne pri pisanju**. Za AEO se najbolj citira strukturiran FAQ ali
vodnik z definicijskim odgovorom v prvem stavku; kolumna to doseže slabše. Zato:

- Kadar format ni `kolumna`, to Igorju **izrecno povej**: »to je primerjava; veriga bo naredila
  kolumno - AEO učinek bo zato manjši«.
- Med enako močnimi kandidati daj prednost tistemu, ki kot kolumna izgubi najmanj.
- Ne prekvalificiraj teme v `kolumna`, da bi bila neskladnost videti manjša, in je ne izpusti tiho.

Isto velja za kanal: če ima prompt priporočilo za YouTube, LinkedIn ali Reddit, to povej. Veriga zna
samo kolumno in socialne objave ob njej.

## Rangiranje

Po vrsti, brez izjem:

1. **`visibility` naraščajoče.** 0 pred 33.
2. **`citationCount` padajoče.** Koliko virov AI na to vprašanje sploh navede. Visoka številka
   pomeni, da je vprašanje citatno gosto in da prostor dobiva nekdo drug.
3. **`buyingJourneyPhase`**: `DECISION` pred `EVALUATION` pred `CONSIDERATION` pred `AWARENESS`.

`averageCompetitorsMentioned` se **ne** uporablja za dvig na lestvici. V praksi je pokazatelj
iskalnega prompta (glej zgoraj), zato bi rangiranje po njem navzdol na vrh potisnilo natanko tiste
prompte, ki jih kolumna ne more premakniti. Navedi ga kot kontekst (»AI na to vprašanje povprečno
našteje 5,3 konkurenta«), ne kot razlog za vrstni red.

**Nobene od teh mer ne pretvarjaj v točke in jih ne seštevaj v skupno oceno.** Uteži za to nihče ni
definiral; izmišljena formula bi dala videz natančnosti, ki je ni. To pravilo velja od 10. 8. 2026
in se s spremembo vira ni spremenilo.

V utemeljitvi vsakega predloga povej, katera vidnost in kateri podatek o citatih sta temo pripeljala
na to mesto.

## Kaj pove `priority` in `score` na priporočilu

Kadar priporočilo obstaja, ju navedi kot kontekst. Nista pa merilo za vrstni red kandidatov: nosi ju
le del promptov, zato bi rangiranje po njiju primerjalo dva neprimerljiva razreda.

## Pogoste napake

- **Tema kot kategorija** namesto kot stališče. Zaostri jo, preden jo predlagaš.
- **Predlagaš vse kandidate namesto rangiranja.** Rangiraj in izberi največ tri, tudi če jih je malo.
- **Izmišljaš številke.** Vsak podatek o vidnosti, citatih ali konkurentih mora priti iz klica. Če
  ga v odgovoru ni, ga v besedilu ni.
- **Trdiš, da priporočilo pripada promptu, ko ima `promptId: 0`.** Glej `aeo-source.md`.
- **Izbiraš namesto Igorja.** Predlog ni odločitev.
