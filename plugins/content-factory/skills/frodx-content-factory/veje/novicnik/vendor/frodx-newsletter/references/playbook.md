# FrodX Newsletter - Playbook

Kako napisati vsak del izdaje. Izpeljano iz analize 35 dejanskih slovenskih izdaj. Ta playbook nosi strukturo, specifično za novičnik; glas in hišna pravila so v razdelku Glas spodaj in v skillu `frodx-transcreation`.

---

## Glas (avtoriteta in hišna pravila)

**Avtoriteta glasu je skill, ne projektna navodila in ne userPreferences.** Globlji uredniški glas (kdo govori, ritem, prepovedane fraze, žargon, anti-AI pravila) je kanonično definiran v `frodx-transcreation/references/voice-and-style.md` in `forbidden-phrases.md` (isti Igorjev glas čez vse vsebine) ter v `igor-column-writer/references/style-guide.md`. Ko sta skilla nameščena, sta vir resnice; ta playbook ju ne podvaja, le povzame novičniku specifične razlike.

Nepogrešljiva hišna pravila, ki morajo držati v vsaki izdaji (tudi če zgornji referenci nista pri roki):

- **Pomišljaj: nikoli dolgi (—, U+2014).** V novičnikih je hišni pomišljaj **en dash (–, U+2013)** - ne razmaknjeni vezaj (ta je za blog in kolumne). `eval_check.py` dolgi pomišljaj ujame.
- **Prepovedane fraze čez vse jezike** in njihove ustreznice: »tu je trik« / »here's the trick« / »ovdje je trik«; prazni marketinški obrati (»v današnjem digitalnem svetu«, »ključno je poudariti« …); žargon (leverage, synergy, game changer …). Polni seznami so v `forbidden-phrases.md`.
- **Ritem** kot pri kolumni: povprečje ~11 besed, blizu polovica stavkov ≤8 besed. Ne ciljaj 15–18.
- **Glas:** samozavesten, neposreden, rahlo provokativen, argumentiran; sarkazem meri na problem, nikoli na bralca. Brez emojijev.
- **Pozicija bralca (success-constraint):** vstop, subject in bloki bralca nagovarjajo prek omejitve njegovega uspeha, ne prek diagnoze neuspeha; neuspeh sme biti tretjeoseben ali Igorjev, nikoli bralčeva vstopna diagnoza. Kanonična definicija s tremi testi in vzorci po FrodXovih rešitvah: `igor-column-writer/references/structure.md` §2 (test pozicije bralca).
- **Tipografija:** SI in HR narekovaji ter % po jeziku (glej `frodx-transcreation/references/typography.md`).

---

## A. Tipologija izdaj (najprej določi tip)

Tip izbere hook in strukturo:

| Tip | Bloki | Hook teži k | Opomba |
|---|---|---|---|
| Monotematska kolumna | 1 | prizor / definicijski reframe | cel prostor eni tezi |
| Večbločna (2–3 vsebine) | 2–3 | univerzalna trditev + primeri | preheader = mini-kazalo |
| Napoved dogodka (webinar) | 1–2 | statistika + pripoznava | lokaliziraj ure SI/HR |
| Case study | 1–2 | kontrast / pred-po | številke v ospredju |
| Čista AI-tema | 1–2 | provokativno vprašanje | konkreten primer obvezen |

Razpon med tipi je tisto, kar šteje - isti vzorec ne sme teči vsak teden.

---

## B. Subject - formule in arhetipi

Pet arhetipov (uporabi enega, max 2 enoti misli):

1. **Dvotaktni obrat:** `[provokativna trditev]. [kratek obrat, ki vrže uvid.]`
2. **Številka kot vaba:** konkretna številka, ki obljublja preobrat.
3. **Provokativno vprašanje:** vprašanje, ki obrne pričakovanje.
4. **Izposoja znanega imena:** znan akter + presenetljivo ravnanje.
5. **Nenavadni par** (samo ob hook arhetipu E): dvojno vprašanje, ki v en subject vpreže kuriozum in insider tease (»Kaj jedo Japonci za božič in koliko zasluži prodajnik v FrodXu?«); preheader ponudi prisilno izbiro med njima. Sme prekršiti pravilo kratkosti – dokaz: 61 znakov, ≥15 odgovorov.

Uporabne formule:
- `[Letnica/kontekst]: [provokativna trditev]. [Kratek obrat, ki vrže krivdo/uvid.]`
- `Ko sem [nepričakovano dejanje]. [Posledica brez razlage.]`
- `Kako veš, da [neprijetna resnica o nečem domačem]?`
- `Zakaj je tudi [znan akter] [presenetljivo ravnal]?`

Pravilo: subject obljublja **isti preobrat kot hook**, ne teme novičnika. Drugo pravilo: subject nikoli ne diagnosticira bralčevega neuspeha (»Vaš marketing ne dela« je padec); provokacija meri na sistem, panogo ali status quo.

---

## C. Preheader - formule

Preheader **nadaljuje** subject, nikoli ne ponovi:
- `[Konkretna številka], ki spremeni, kako gledaš na [temo].`
- `[Znan akter] je naredil X. Tu je, kaj to pomeni zate.`
- `Tri zgodbe in ena neprijetna lekcija.` (mini-kazalo za večbločno izdajo)

Pri večbločni izdaji preheader našteje vsebine. Brez nevidnih zero-width polnil.

---

## D. Hook (opener) - formula v 5 korakih

1. **Sidro:** slavno podjetje / statistika / oseben prizor s konkretnimi detajli ("petek, 16:47, vonj po kuhanem vinu").
2. **Razvoj:** 2–4 stavki, ki sidro razvijejo v napetost ali uvid.
3. **Premostitev:** eksplicitni stavek, ki pelje od sidra k FrodX vsebini.
4. **Teza:** kontraintuitivna trditev ali izziv statusa quo - bralca pozicionira prek omejitve njegovega uspeha, ne prek diagnoze neuspeha (glej razdelek Glas, pravilo Pozicija bralca).
5. **Napoved:** kaj bralca čaka v izdaji (mehko, ne kazalo).

Dolžina: 2–3 odstavki, 6–12 stavkov, pripovedno. V docx gre hook v **tabelo HOOK** (`HOOK_P1, HOOK_P2, HOOK_P3`), ne kot proza; `HOOK_P1` se začne z **malo začetnico**, ker teče iz `GREETING` (»Pozdravljeni,« + prazna vrstica + »predstavljajte si …«).

### Pet hook arhetipov (vstopni mehanizmi)
- **A - statistika + pripoznava:** številka, ki zaboli, nato priznanje.
- **B - prizor:** konkreten prizor s časom, krajem, detajlom.
- **C - kontrast / reframe:** `X ni Y. Je Z.` (definicijski one-liner; šteje v kvoto 2 one-linerjev).
- **D - univerzalna trditev + primeri:** trditev, ki velja širše, podprta z dvema-tremi primeri.
- **E - kuriozum z mostom** (dodan v 2.1 iz izdaje KFC/Japonska, 19. 12. 2024: ≥15 odgovorov ob osnovni črti 1–2 na izdajo, večina mimo maila): presenetljivo, preverljivo dejstvo iz sveta zunaj B2B, ki je **nosilno za tezo izdaje**, ne okras. Petstopenjska mehanika iz izvirnika: (1) sidro v znanem – bralec se najprej počuti pametnega (Coca-Cola in Božiček); (2) eskalacija v neznano (KFC kot japonska božična tradicija, kampanja 1974); (3) osebni lok preverjanja – »mislil sem, da je fake news, preveril sem vire« spremeni trivio v kredibilnost; (4) konkretna številka (3,6 mio družin, rezervacije tedne vnaprej); (5) komplicitna poanta, ki vabi odgovor (»Če me je naplahtal BBC, sem zdaj tudi jaz vas.«). Naravni subject par: dvojno vprašanje z nenavadnim parom (kuriozum + insider tease), preheader ponudi prisilno izbiro med njima. Pogoji: dejstvo preverljivo z virom, povedljivo v enem stavku (bralec ga lahko prenese naprej), sezonski sprožilec je bonus, okvir se sme vrniti v zaključku (callback). Optimiziran za **odgovore** (metrika #2), ne za klike. Rotacija: največ 1× na 4–6 izdaj, sicer novičnik zdrsne iz avtoritete v trivia servis.

**Protokol kandidatov za E:** kadar je E na vrsti, Claude ob izvornih URL-jih dostavi 2–3 kandidate: dejstvo + primarni vir + konkretna številka + most v enem stavku + skica komplicitne poante. Igor izbere in vrne **en resničen stavek svoje reakcije** (»tega res nisem vedel« / »poznam, a številka me je presenetila«) – ta stavek je surovina za osebni lok preverjanja (korak 3); Claude si prvoosebne nevere ne izmišlja. Kuriozum mora preživeti vse tri trge (SI/HR/EN), sicer se ob izbiri označi zamenjava za HR/EN. Anti-test izrabljenosti: če bi dejstvo lahko pristalo v motivacijskem LinkedIn postu (Kodak, Blockbuster, kuhana žaba – povrhu izmišljena), ga zavrzi.

---

## Licenca za prelom (relacijska izdaja)

Vsakih **6–8 izdaj** ena izdaja namerno prelomi predlogo. Precedens: KFC izdaja (19. 12. 2024, `archive.md`) je prekršila tri pravila – dolg subject, brez pain linka, brez kolumne – in dosegla ≥15 odgovorov ob osnovni črti 1–2. Naravni termini: december, sredina poletja, mejniki (obletnica, jubilejna številka).

Pravila preloma: glasovna, pravopisna in tipografska vrata ter docx shema veljajo **vedno**; strukturna pravila (tipologija, pain link, TOC, dolžina subjecta) so suspendirana z eksplicitno oznako **»prelom izdaja«** v scorecardu. Pričakovana opozorila `eval_check.py` (npr. pain link = 0) se ob tej oznaki zavestno ignorirajo. Cilj prelom izdaje niso kliki, ampak **odgovori in odnos** – meri se po odmevu čez kanale (mail + LinkedIn + SMS + telefon), ki ga Igor vpiše v arhiv.

Pravilo svežine: če izdaja promovira kolumno, hook **ne sme** dobesedno prepisati uvoda te kolumne - bralec ne sme dobiti istega vstopa dvakrat. Poišči svež kot na isto temo.

---

## E. Struktura bloka

Vsak blok ima točno: **naslov · telo · 1 slika · 1 CTA**. Telo 3–6 stavkov, gradi argument, ne LinkedIn fragmenti. V docx je telo razbito na odstavke `BODY_P1, BODY_P2, …` (en odstavek = ena vrstica tabele); po želji alineje `BULLET_1, …`.

**Brez inline povezav v telesu.** Janijev uvoznik jih ne pozna - vsak blok ima točno **eno** povezavo, in to je CTA (`CTA_LABEL` + `CTA_URL`). Če je sekundarna povezava pomembna (npr. YouTube video, druga stran), naj **postane CTA** tega bloka, ne link sredi besedila.

Pri večbločni izdaji: mini-kazalo (TOC) na vrhu, vsaka postavka kaže na svoj blok. Število TOC postavk == število blokov. Noben teaser ni podvojen čez dva bloka. (Shema docx: `references/docx-pipeline.md`.)

---

## F. CTA - struktura in knjižnica

- **Per-blok CTA:** `[Velelnik] [objekt]: [konkretna korist]` → "Preberite kolumno: 5 vprašanj za pošten prodajni načrt 2026"
- **Zaključni CTA:** nizkofrikcijski odgovor z geslom → "odgovorite na ta mail z »2026 reality check«"
- **Mehki CTA:** odnosni, ne transakcijski → "mi napišite. Rad delim, kaj pri nas deluje – in kaj ne."
- **P.S. CTA:** časovno omejen, komercialen → "okno je odprto še približno 10 dni."

Pravilo: **ena CTA na blok** (`CTA_LABEL` + `CTA_URL`), nikoli zid gumbov in **nobenih inline povezav v telesu**. Odgovor-z-geslom živi v zaključku (`CLOSING_P2`), časovno/komercialni dodatek v `PS_TEXT`. Tako čez izdajo nastanejo 2–3 razpršeni klici k dejanju, a vsak v svojem strukturnem polju.

**Pain link (od v2.0):** klik na kolumno dokazuje branost; klik na stran rešitve, demo, posvet ali prijavo dokazuje problem. Vsaka izdaja ima **natanko en pain link** – ena CTA cilja problemski cilj, preostale so bralne. Pri monotematski izdaji brez problemskega URL-ja pain signal nosi zaključek (odgovor z geslom) ali PS; to označim v scorecardu. Zakaj: uspeh izdaje se meri po vstopih v prospecting vrata, ne po odprtjih (`measurement.md`).

Knjižnica fraz po tipu bloka (iz 35 izdaj). Dva sloga soobstajata - **velelnik bralcu** in **prva oseba kot bralčev glas** (gumb govori v imenu bralca):

| Tip bloka | Velelnik bralcu | Prva oseba (bralčev glas) |
|---|---|---|
| Kolumna / blog | Preberi(te) kolumno · Preberi celotno zgodbo | Želim prebrati več! |
| Webinar / dogodek | Prijavi(te) se · Rezerviraj mesto | Grem zraven! · Računajte name |
| Case study | Poglej(te) primer · Preberi case | Pokaži mi, kako |
| Ponudba / produkt | Naroči predstavitev · Rezerviraj klic | Zanima me · Pošljite mi detajle |
| Odnosni / mehki | Napišite mi · Odgovorite na ta mail | - |

---

## G. Podpis in noga

Podpisnik in noga po trgu (glej Transkreacija). SI: Igor, FrodX Ljubljana. HR: Igor je zdaj podpisnik (Dejan ni več zaposlen), noga ostaja FRODX_HR (Zagreb). EN: po trgu/kontekstu.

---

## H. Transkreacija SI → HR → EN

SI je vir resnice. HR in EN nista prevoda, ampak nativni transkreaciji. Za globlja jezikovna pravila uporabi `frodx-transcreation` (če je nameščen); tu so pravila, specifična za novičnik.

**Kaj ostane fiksno čez vse jezike:** argument, struktura, številke, imena entitet, persuasivna logika.

**Kaj se prilagodi:**
- **Progresivno krčenje kazala SI → HR → EN.** EN izdaja je pogosto bolj zbita; lokalno vezane postavke (npr. SI/HR webinar) izpadejo ali se zamenjajo (npr. EN dobi Kinetara service announcement namesto webinarja).
- **Lokalizacija dogodkov:** ure in termini po trgu (webinar SI 10:00 Ljubljana / HR 13:00 Zagreb).
- **Podpisnik in noga** po trgu (glej zgoraj).
- **Gesla in CTA** lokalizirani: SI »cenik check« → HR »provjera cjenika« → EN »pricing check«.
- **Sidro hooka** se sme zamenjati za lokalno bolj prijemljivo (npr. SI Renault → EN McDonald's), univerzalno znana imena (Dončić, znane znamke) preživijo.
- **Datum in ločila:** vrednost ista, format lokaliziran. Datum SI/HR `18. 6. 2026` ali ISO; EN ISO ali `18 June 2026` - NIKOLI ameriški `June 18, 2026`. Decimalna vejica (SI/HR) → pika (EN). Pomišljaj povsod en dash `–`, ne em dash ` - `.

**HR varovalke:**
- Množina, NE dvojina (hrvaščina nima dvojine).
- Brez kalkov iz slovenščine: »Bodite dobro« → »Sve najbolje«, ne »Budite dobro«.
- Znane korekcije: »cjenik check« → »provjera cjenika«; »udvostruči pozive« → »udvostruči broj poziva«; besedni red »širom otvaramo vrata«.

**EN register (Igorjevo pravilo):** mednarodna poslovna angleščina za CEE bralca. Jasno, direktno, nativno - a brez težkih idiomov, naloženih frazalnih glagolov, športnih/kulturnih referenc. Stavek, ki ga londonski native občuduje, bralec v Zagrebu ali Varšavi pa prebere dvakrat, je padel.

**Anti-fabrikacija:** nikoli ne dodaj številke, imena ali trditve, ki je ni v SI originalu. Če manjka, označi `[VSTAVI: …]` in vprašaj Igorja.
