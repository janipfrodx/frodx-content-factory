# FrodX Newsletter - Samoevalvacijska rubrika

> **Namen:** preden Igorju pokažem osnutek, ga sam ocenim po teh sedmih vratih, popravim vse, kar pade pod prag, in pokažem že popravljeno verzijo z razčlembo. Cilj: manj Igorjevega čakanja in krogov korekcij, bolj predvidljiva kvaliteta.
>
> **Kdaj se izvede:** vsakič, avtomatsko, pred prvim prikazom osnutka - za vsako jezikovno različico posebej.

---

## Kako rubrika deluje (zanka)

1. Napišem osnutek (iz URL-jev / vsebine).
2. Zaženem vseh 7 vrat spodaj.
3. **Trdna vrata (objektivna):** vse padce popravim sam, tiho, in v razčlembi navedem, kaj sem popravil.
4. **Mehka vrata (presoja):** popravim, kar lahko, preostalo tveganje pa **označim Igorju**, ne razglasim za rešeno.
5. Pokažem že popravljen osnutek + kompakten scorecard (tabela na koncu).
6. Igor kvečjemu korigira preostalo.

**Pravilo iskrenosti:** samoevalvacija ni zunanji ocenjevalec. Model, ki preverja sebe, ima slepe pege. Zato so vrata označena kot trdna (objektivno merljiva, zanesljivo popravim) ali mehka (stvar čuta - dvignem kvaliteto, a ne garantiram zadnje pol točke). Mehka vrata vedno spremlja opozorilo, kje je smiseln Igorjev ali rojeni pregled.

Za hitre mehanske ulove (dolžina stavkov, prepovedane fraze, presledek pred %, štetje blokov) poženi `scripts/eval_check.py`. Skripta je pomoč, ne razsodnik - ujame, kar je strojno preverljivo, ostalo presodim sam.

---

## Vrata 1 - HOOK (mehko + delno trdno)

| Kriterij | Prag | Tip |
|---|---|---|
| Oblični vstop | Prvi 1–2 stavka NE govorita o temi/produktu; so zgodba, prizor, dejstvo ali citat | trdno |
| Premostitveni stavek | Eksplicitna premostitev od sidra k FrodX vsebini je prisotna | trdno |
| Arhetip | Določen eden od 4 (A statistika+pripoznava, B prizor, C kontrast/reframe, D univerzalna trditev+primeri) | trdno |
| Dolžina | 2–3 odstavki, 6–12 stavkov | trdno |
| Svežina sidra | Sidro NI dobesedno prepisano iz promovirane kolumne (sicer bralec dobi isti vstop dvakrat) | mehko |
| Pozicija bralca | Vstop bralca nagovarja prek omejitve njegovega uspeha, ne prek diagnoze neuspeha (»ne dosegate«, »vaš X ne dela« kot vstop = padec); neuspeh sme biti tretjeoseben ali Igorjev lasten | mehko |
| Moč | Sidro dejansko prime in se naravno poveže z vsemi bloki | mehko |

**Ob padcu:** prepišem hook. Če uvod takoj govori o produktu → nov oblični vstop. Če sidro prepisano iz kolumne → poiščem svež kot. Če premostitve ni → dodam jo. Če vstop diagnosticira bralčev neuspeh → prepišem prek omejitve uspeha: kaj že deluje + strop (s številko) + cena stropa.
**Označim Igorju:** če je os med bloki raztegnjena (vsebine so tematsko oddaljene), povem, da je strop omejen z izborom vsebin, ne s pisanjem.

---

## Vrata 2 - STRUKTURA (trdno, strojno preverljivo)

Shema docx je v `references/docx-pipeline.md` (rekonstruirana iz Janijevih delujočih vzorcev).

| Kriterij | Prag |
|---|---|
| Število blokov | 1–3 |
| VELIKI ključi | vsi ključi tabel VELIKE TISKANE (`SUBJECT`, `BLOCK_TITLE`, `BODY_P1` …) |
| Tabele, ne proza | hook, TOC, closing, signoff, PS so **TABELE** (ne proza zunaj tabel) |
| META polno | vseh 14 META ključev prisotnih (vključno `FROM_NAME`, `FROM_EMAIL`, `SEGMENT_REF`) |
| `BLOCK_ID` | oblika `block-01/02/03` (ne `b1`) |
| TOC ↔ bloki | TOC vrstic (brez glave) == blokov; vsak `BLOCK_ID` iz TOC obstaja; `TOC_TYPE` == `BLOCK_TYPE` |
| Slika na blok | točno 1, **vdelana** v celico `IMAGE` (ne ime datoteke); razmerje ohranjeno |
| CTA na blok | točno 1 (`CTA_LABEL` + `CTA_URL`); **brez inline povezav v telesu** |
| Telo | razbito na `BODY_P1, BODY_P2, …`; ≥1 odstavek |
| Webinar blok | ima `EVENT_DATE` / `EVENT_TIME` / `EVENT_DURATION_MIN` |
| Brez podvojitve | noben teaser podvojen čez dva bloka |
| Številke med jeziki | identične v SI/HR/EN |

**Ob padcu:** trdi STOP - popravim shemo, dokler se ne ujame. Po buildu poženi `scripts/eval_check.py <docx>`; shema mora biti zelena. Ta vrata ujamejo tip napake »blok prazen / manjka slika / mali ključi / hook kot proza«.

---

## Vrata 3 - FRODX EDINSTVENOST (mehko + delno trdno)

| Kriterij | Prag | Tip |
|---|---|---|
| Dokaz na trditev | vsaka ključna trditev podprta s številko ALI konkretnim primerom | trdno |
| Količina dokazov | ≥ 3 konkretne številke + ≥ 1 poslovni primer na izdajo | trdno |
| Pain link | natanko 1 CTA na izdajo cilja stran, ki izkazuje problem (rešitev, demo, posvet, prijava), ne zgolj branost; pri monotematski izdaji sme pain signal nositi zaključek/PS, kar označim; pri prelom izdaji (playbook: licenca za prelom) izjema z oznako v scorecardu | trdno (štetje) / mehko (izbira cilja) |
| Provokativna iskrenost | vsaj en pošten obrat, ki pove neprijetno resnico konstruktivno | mehko |
| Brez abstrakcije | nobene votle izjave brez dokaza | mehko |

**Ob padcu:** abstraktno izjavo zamenjam s številko/primerom ali jo črtam. Če dokazov ni v gradivu, **ne izmišljam** - označim `[VSTAVI: …]` in vprašam Igorja.

---

## Vrata 4 - JEZIK IN GLAS (trdno, skoraj v celoti merljivo)

| Kriterij | Prag |
|---|---|
| Ritem stavka | uredniški ritem (povprečje ~11 besed, ~48 % stavkov ≤ 8 besed); novičnik sme biti še malo bolj sekan kot kolumna - glej opombo spodaj |
| Aktivna oblika | brez trpnika, kjer ga je mogoče izogniti |
| Prepovedane fraze | nobene iz `forbidden-phrases.md` / playbook razdelka Glas (npr. »tu je trik«, »v današnjem digitalnem svetu«, »seveda«, »če sem iskren«) |
| Žargon | nobenega angleškega žargona (leverage, synergy, game changer …) |
| One-linerji | največ 2 na izdajo, samo za dramatični obrat |
| Krepki tisk | minimalen, največ 2× na sekcijo |

**Opomba o ritmu:** pravi uredniški ritem (kalibriran na 17 objavljenih Igorjevih kolumnah) je ~11 besed (mediana 9), s 48 % stavkov ≤ 8 besed. Za novičnik se ravnaj po tej kalibraciji, ne po starem »15–18«; kratki stavki po močni opazki ali neprijetni resnici so del glasu. Naravnost vedno premaga ujemanje s številko.
**Ob padcu:** dolge stavke razbijem, trpnik pretvorim v aktiv, prepovedane fraze in žargon zamenjam, odvečni bold in one-linerje obrežem.

---

## Vrata 5 - PRAVOPIS (trdno, preverljivo)

| Kriterij | Prag |
|---|---|
| Slovnica in ločila | brez napak |
| Presledek pred % | SI/HR nedeljivi presledek `92 %`; **EN brez presledka `92%`** |
| Narekovaji | pravilni za jezik (SI »…«, HR »…«, EN "…") |
| Datum | SI/HR `18. 6. 2026` ali ISO `2026-06-18`; EN ISO `2026-06-18` ali day-first `18 June 2026`. **NIKOLI** ameriški `June 18, 2026` ali `6/18/2026` |
| Decimalke / tisočice | **vrednost ista čez vse jezike, lokalizira se le ločilo** (SI/HR decimalna vejica `1,5` → EN decimalna pika `1.5`; tisočice SI/HR tanki presledek `1 250` → EN vejica `1,250`) |
| Pomišljaji | premor v stavku = **en dash `–` (U+2013), NE em dash ` - ` (U+2014)**; vezaj v zloženkah = `-` |

**Opomba o datumu (past pri EN):** EN transkreacija privzeto vleče ameriški `Month DD, YYYY`. Vedno preglej in pretvori v ISO ali day-first.

**Ob padcu:** popravim sam, tiho. To so vrata, kjer je samoevalvacija najbolj zanesljiva.

---

## Vrata 6 - TRANSKREACIJA (mehko; samo HR/EN)

| Kriterij | Prag | Tip |
|---|---|---|
| Nativnost | bere kot original, ne prevod; brez kalkov | mehko |
| Kalki | nobenih (npr. SI »Bodite dobro« → HR NE »Budite dobro«, ampak »Sve najbolje«) | delno trdno |
| HR slovnica | množina, NE dvojina (hrvaščina nima dvojine) | trdno |
| Lokalizacija dogodkov | termini/ure po trgu (npr. webinar SI 10:00 / HR 13:00) | trdno |
| Entiteta/podpisnik/noga | po trgu (Ljubljana/Zagreb; pravi podpisnik) | trdno |
| Številke | **vrednost/števke nespremenjene iz SI** (npr. 1,5 mio ostane 1,5 mio); lokalizira se le ločilo in format datuma po Vrata 5 (NIKOLI ameriški datum) | trdno |
| Gesla/CTA | lokalizirani (SI »cenik check« → HR »provjera cjenika« → EN »pricing check«) | trdno |
| Ilustrativne reference | ostanejo, če dokazujejo univerzalno mehaniko; lokalno vezane vsebinske postavke izpadejo | mehko |

**Ob padcu:** prepišem nativno, kalke zamenjam, dvojino popravim v množino.
**Označim Igorju (vedno pri HR/EN):** ker nisem rojeni govorec, mehka nativnost ostaja moja ocena po znanju, ne po čutu. Za prvo pravo pošiljko na nov trg priporočim enkraten pregled rojenega govorca; ko gre dvakrat brez pripomb, korak odpade.

Znane HR korekcije, ki jih zapomni: »Budite dobro« → »Sve najbolje«; »cjenik check« → »provjera cjenika«; »udvostruči pozive« → »udvostruči broj poziva«; besedni red »širom otvaramo vrata«.

---

## Vrata 7 - SUBJECT + PREHEADER (trdno + delno mehko)

| Kriterij | Prag |
|---|---|
| Subject arhetip | eden od 4: dvotaktni obrat / številka kot vaba / provokativno vprašanje / izposoja znanega imena |
| Pozicija bralca | subject NI diagnoza bralčevega neuspeha; provokacija meri na sistem, panogo ali status quo, ne na bralčevo nesposobnost |
| Subject dolžina | ≤ 2 enoti misli, kratko |
| Preheader nadaljuje | NE ponovi subjecta; doda številko/dokaz ALI konča z vprašanjem |
| Večbločna izdaja | preheader našteje vsebine (mini-kazalo) |
| Brez polnila | nevidni zero-width znaki niso del vsebine |

**Ob padcu:** regeneriram subject/preheader po arhetipu. Če preheader ponavlja subject → nov kot.

---

## SCORECARD (pokažem ob osnutku)

Za vsako jezikovno različico vrnem kompaktno tabelo:

```
Vrata                 | Status      | Popravljeno / opomba
----------------------|-------------|----------------------------------
1 Hook                | PASS / 9    | sidro sveže, premostitev ok
2 Struktura           | PASS        | TOC↔bloki ok, 1 slika+1 CTA/blok
3 FrodX edinstvenost  | PASS / 9    | 5 številk, 1 case
4 Jezik in glas       | PASS        | 2 predolga stavka razbita
5 Pravopis            | PASS        | presledek pred % popravljen
6 Transkreacija (HR)  | PASS / 9,5  | »Budite dobro«→»Sve najbolje«; ⚠ priporočam pregled rojenega govorca
7 Subject+preheader   | PASS        | dvotaktni obrat; preheader nadaljuje
----------------------|-------------|----------------------------------
SKUPNA OCENA: 9 / 10  | strop omejen z izborom vsebin (dve temi)
```

**Pomen statusov:**
- **PASS** - prag dosežen (po potrebi po mojem popravku).
- **PASS / N** - mehko vrata; dosežen prag + ocena kvalitete 0–10.
- **⚠** - preostalo tveganje, ki ga ne morem zanesljivo rešiti sam → Igorjev ali rojeni pregled.
- **STOP** - trdo vrata padlo, osnutka ne pokažem, dokler ni popravljeno.

---

## Kaj ostane Igorju (nikoli ne razglasim za rešeno sam)

- **Resničnost dejstev:** ali je trditev/novica točna, ali je webinar termin odprt, ali živi URL dela. Tega ne morem preveriti iz svojega okolja → vedno označim.
- **Mehka nativnost HR/EN:** dvignem, a za prvo pošiljko priporočim rojeni pregled.
- **Ali hook res prime / ali os med bloki drži:** dvignem in ocenim, a končna presoja je Igorjeva.
- **Ton novic o strankah/partnerjih:** ali je javna formulacija prava (npr. WOOP! Graz framing - Avstrija je prva zastavica Kinetare na tem trgu, NE njihov prvi trg sploh).

---

## Povzetek v enem stavku

> Vsak osnutek prestane 7 vrat (struktura, pravopis, glas, žargon, subject/preheader so trdna in jih popravim sam; hook, edinstvenost in nativnost so mehka - dvignem in označim preostalo tveganje), Igor pa dobi že popravljeno verzijo s scorecardom namesto surovega prvega osnutka.
