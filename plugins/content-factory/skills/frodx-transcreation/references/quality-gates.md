# Quality Gates

Use this checklist silently before returning final copy.

## Native-copy gate

The copy passes only if:

- A native business reader would believe it was originally written in the target language.
- The rhythm follows English or Croatian, not Slovenian.
- The wording does not expose literal transfer from Slovenian.
- Idioms are recreated, not explained.
- CTA phrasing is natural for the target culture and medium.

## Igor/FrodX gate

The copy passes only if:

- It sounds experienced, direct, practical, and commercially aware.
- It does not sound like generic B2B content.
- It avoids empty strategic language.
- It preserves first-person authority when the source uses it.
- It keeps a slightly provocative edge where the source has tension.
- It does not become too polite, too enthusiastic, or too academic.

## Accuracy gate

The copy passes only if:

- All names, numbers, dates, product names, and claims are preserved accurately.
- No unsupported statistics, industries, promises, features, or guarantees are added.
- Product terminology follows `terminology.md`.
- Claims about finance and DORA compliance are used only when supported by the source/context.
- Offers, proposals, and commercial terms preserve scope and obligations.

## Anti-cliche gate

Remove or rewrite:

- Generic B2B openings.
- Inflated adjectives.
- Empty benefits.
- Repetitive three-part AI lists.
- "Not only... but also" patterns unless they are genuinely the most natural option.
- Formal summary endings.
- Any phrase listed in `forbidden-phrases.md` or its direct equivalent.

## Language-specific gate

English:

- Avoid Central-European English.
- Avoid consultant noun stacks when simpler verbs work better.
- Use contractions where natural in personal/editorial formats.
- Avoid over-polished SaaS copy.

Croatian:

- Avoid Slovenian calques.
- Avoid Serbian-sounding vocabulary where Croatian-native options are available.
- Avoid unnecessary English hybrids.
- Choose klijent, korisnik, or kupac based on relationship and context.
- Keep Croatian business tone natural, not bureaucratic.

## Typography gate

The copy passes only if (see `typography.md`):

- Percent spacing matches the language (EN 70%, HR/SL 70 %).
- Decimals and thousands match the language (EN 8.5 / 10,000; HR/SL 8,5 / 10.000).
- Quotation marks and apostrophes are typographic, one style per piece, correct for the language.
- No em dash (—). The FrodX-house dash is a spaced hyphen " - " on the blog and an en dash (–) in newsletters; currency format is respected.

## Cold tell-sweep (zadnja, OBVEZNA vrata)

Ostala vrata zgoraj so vzporedna - vsako lovi svojo kategorijo. Ta so drugačna: zadnji, ciljani prelet celotnega besedila, ki išče **samo eno stvar** - "cold tells", drobne sledi, ki izdajo, da je besedilo prevedeno iz slovenščine in ne napisano izvirno. Splošna native-copy vrata to spregledajo, ker berejo »ali zveni v redu«; ta sweep bere »ali bi rojeni pisec to napisal točno tako, ali samo zato, ker je izvirnik tako rekel«.

**Postopek.** Po vseh drugih vratih preberi osnutek še enkrat, stavek za stavkom, in za vsak stavek vprašaj: *če bi rojeni EN/HR poslovni pisec pisal to misel iz nič, brez slovenskega izvirnika pred sabo - bi jo napisal tako?* Vsak stavek, ki preživi le zato, ker je izvirnik tak, je cold tell. Prepiši ga. Sweep ni branje za smisel (to si že naredil); je lov na sledi prevoda.

**Katalog tellov (kaj iščeš):**

1. **Skladenjski kalk** - slovenski besedni red ohranjen tam, kjer bi cilj preuredil. SL pogosto postavi okoliščino ali glagol naprej; EN hoče poanto spredaj (SVO), HR ima svoj naravni red. »Že leta opažam, da …« ni EN »For years I have been observing that …«, ampak »I've watched this for years: …«.
2. **Leksikalni kalk** - dobesedna preslikava slovenske kolokacije ali idioma, ki v cilju ne obstaja. HR je še posebej dovzeten za slovensko obarvano besedišče. Idiom poustvari, ne prevedi.
3. **Diskurzni vezni tell** - slovenski povezovalci, prevedeni dobesedno: »In zato« → trd »And therefore«; »Tako pač je« → »That's just how it is«; »Skratka« → strojni »In short«. Rojeni pisec zvezo pogosto izpusti ali drugače zasuka.
4. **Registrski tell** - slovenske brezosebne, pasivne in samostalniške konstrukcije, prenesene v cilj, kjer bi bil Igorjev EN/HR oseben in glagolski. »Pri tem je treba upoštevati …« ni »It should be taken into account that …«, ampak »Watch one thing: …«. Nominalizacije razbij v glagole.
5. **Ritmični tell** - slovnično pravilen stavek s slovensko kadenco: predolg, enakomeren, brez Igorjevega kratkega udarca za poanto. Če zaporedje »teče preveč gladko in enakomerno«, je to prevedeni ritem - vrini kratko poved.
6. **Format/typo tell** - decimalke in tisočice po jeziku (EN 8.5 / 10,000; HR/SL 8,5 / 10.000), %, narekovaji; pomišljaj nikoli - (en dash v novičnikih, razmaknjen vezaj na blogu). Mehanski del ujame `transcreation_check.py`; tu preveri, česar skripta ne vidi.
7. **HR posebej** - slovenska **dvojina**, ki se prikrade v hrvaščino (HR pozna le množino: »dva izdelka sta« → »dva proizvoda su«); srbske oblike (saradnja, hiljada, uslov …); slovensko-hrvaški lažni prijatelji.

**Pravilo:** najmanj en namenski prelet samo za telle, po vseh drugih vratih. Ko najdeš tell, ga prepiši in po potrebi prelet ponovi. Ker nisi rojeni govorec, pri prvi pošiljki na nov trg mehko nativnost (telle, ki bi jih ujel samo rojeni govorec) **dvigni in označi** za Igorjev pregled, ne razglasi za rešeno.
