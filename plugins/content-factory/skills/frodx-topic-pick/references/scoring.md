# Ocenjevanje in rangiranje tem

Ta datoteka je prirejena iz `aeo-topic-brief` (skill, ki isto presojo dela nad mail-brifom iz HubSpot AEO poročila, ne nad Excelom). Logika presoje je prenesena nespremenjena; polja so preslikana na stolpce iz `references/excel-contract.md`. Kjer vir uporablja podatek, ki ga Excel nima (izračunane sezname `new_prompts`/`disappeared_prompts`, `visibility_direction`, `opportunities` po kanalih), je to spodaj izrecno povedano - ne nadomeščaj manjkajočega s izmišljenimi števili.

## Kaj šteje kot dobra tema

Vsa štiri merila morajo veljati (vir: `aeo-topic-brief`, razdelek »Good-topic criteria«):

- **Naslavlja konkreten `target_prompt`**, ne splošne teme. Če je vrstica v Excelu zapisana kot kategorija (»O programih zvestobe«), to ni dovolj - preden temo predlagaš Igorju, jo zaostri v stališče, ki dejansko odgovarja na `target_prompt` te vrstice.

  **Izpeljava, ko je `target_prompt` prazen.** Rutina `frodx-aeo-watch` tega stolpca (še) ne polni - preverjeno 14. 8. 2026: prazen je bil v vseh 11 vrsticah. Prompt zato smeš izpeljati iz stolpca `topic`, kadar je ta zapisan kot vprašanje ali primerjava (»How to…«, »What Is…«, »X vs Y«). Pod dvema pogojema:
  - izpeljani prompt **izrecno označi kot izpeljavo** v `_run.brief.rationale` (npr. »`target_prompt` izpeljan iz `topic`, ker je stolpec prazen«), nikoli ga ne predstavi kot podatek iz vira;
  - če `topic` ni v obliki, iz katere je prompt razviden (gola kategorija), izpeljave **ne ugibaj** - to vrstico predlagaj samo, če Igor prompt pove sam, sicer jo izpusti in povej, zakaj.
- **Odgovor bi bil citirljiv za AI iskalnik**: jasen, strukturiran, samostojen - vprašanje iz `target_prompt` postane naslov razdelka z direktnim odgovorom v prvem stavku.
- **Vezana na FrodX ekspertizo**: HubSpot, SAP Engagement Cloud / Emarsys, Open Loyalty, CloudTalk. Za primerjave, ki vključujejo orodja, ki jih FrodX ne implementira, pisati kot **nevtralen integrator**, ne kot zagovornik ene platforme.
- **Realen obseg** za en kos vsebine.

**Igorjev prag** (vir: isti razdelek, »Igor's bar«): tema mora biti dovolj zaostrena, da iz nje nastane dober kos vsebine. Če tema, kot jo je zapisala rutina `frodx-aeo-watch` v stolpcu `topic`, bere kot kategorija, jo pred predlogom zaostri - ne prenašaj je nespremenjene samo zato, ker že stoji v Excelu.

## Formati

Vir: `aeo-topic-brief`, razdelek »Format rules«. Pravilo je nespremenjeno; le da tu Excel že prinaša predlog v stolpcu `format`.

| Signal v `target_prompt` | format |
|---|---|
| Konkretno vprašanje z več podvprašanji | `FAQ` |
| »kako narediti X« | `vodnik` |
| »kaj je bolje, X ali Y«, »X proti Y« | `primerjava` |
| Široka / mnenjska / miselno-vodilna teza | `kolumna` |

Stolpec `format` v Excelu je **namig, ne odločitev** - enako kot je bil v viru `rec_format` namig, ne prevlada nad obliko prompta. Preveri, ali oblika `target_prompt` ustreza vrednosti v `format`; če se ne ujema, v predlogu Igorju povej svoj format in navedi zakaj.

### Veriga zna izdelati samo kolumno

Korak 2 verige je `igor-column-writer`. Drugih producentov vsebine veriga **nima** - `vodnik`, `primerjava` in `FAQ` bodo v praksi izvedeni kot mnenjska kolumna. Preverjeno 14. 8. 2026: v vrsti tem je bilo 10 od 11 vrstic označenih kot `vodnik`, `primerjava` ali `FAQ`.

To je pomembno **pri izbiri teme, ne pri pisanju**. Za AEO se najbolj citira strukturiran FAQ ali vodnik z definicijskim odgovorom v prvem stavku; kolumna to doseže slabše. Zato:

- Kadar predlagana vrstica ni `kolumna`, to v predlogu Igorju **izrecno povej**: »ta vrstica je FAQ; veriga bo naredila kolumno - AEO učinek bo zato manjši«.
- Med enako močnimi kandidati daj prednost tistemu, ki kot kolumna izgubi najmanj. Vrstica, ki hoče definicijski FAQ (»What Is X«), izgubi največ.
- Odločitev, ali se tako vrstico vseeno piše, je Igorjeva. Ne izpusti je tiho in ne prekvalificiraj je v `kolumna`, da bi bila neskladnost videti manjša.

## Pravila o jezikih - se NE prenašajo

Vir vsebuje razdelek »Language targeting« (privzeto `sl/en/hr`, oženje samo za tržno vezane teme). Ta skill ga izpusti namenoma:

- `references/excel-contract.md` nima stolpca za jezike, in `_run.brief` (izhod tega skilla) tudi ne vsebuje polja `languages` (glej `state-schema.md`).
- Veriga korakov (dirigent, korak 4) transkreira SL→EN in SL→HR **vedno**, za vsak tek - to ni odločitev, ki bi jo ta skill sprejemal na nivoju teme.

Če je tema izrazito vezana na en trg (npr. slovenska specifika), to omeni v `rationale`, a ne dodajaj polja za jezike, ki ga izhodna shema ne predvideva.

## Prioriteta in rangiranje

### Kateri signal je merodajen

`visibility_signal` je prosto besedilo in v praksi nosi **dva signala hkrati**, ki si nasprotujeta. Preverjeno v datoteki 14. 8. 2026, vseh 11 vrstic v obliki `citation lift +X%, priority HIGH|MEDIUM|LOW`:

| priority | citation lift v teh vrsticah |
|---|---|
| HIGH (3 vrstice) | +0,7 % / +1,4 % / +1,7 % |
| MEDIUM (6 vrstic) | +4,4 % do +11,9 % |
| LOW (2 vrstici) | +8,6 % / +11,6 % |

Torej: **višja prioriteta pomeni nižji citation lift.** Rangiranje po enem ali po drugem signalu da skoraj obrnjen vrstni red, zato izbira signala ne sme biti prepuščena presoji.

**Pravilo (Janijeva odločitev, 15. 8. 2026):**

1. **`priority` je primarni signal.** Rangiraj `HIGH` pred `MEDIUM` pred `LOW`.
2. **`citation lift` je sekundarni** - loči samo vrstice z **enako** prioriteto.
3. Nobene od teh dveh mer ne pretvarjaj v točke in ne seštevaj ju v skupno oceno. Uteži za to nihče ni definiral; izmišljena formula bi dala videz natančnosti, ki je ni.
4. V `_run.brief.rationale` povej, katera prioriteta in kateri lift sta vrstico pripeljala na vrh.

Definicij za nobenega od signalov HubSpot AEO ne dokumentira - ne veva, na kaj je `citation lift` odstotek in kako AEO določi `priority`. Če definicija kdaj pride, se to pravilo ponovno pretehta; do takrat velja zgornji vrstni red in se ne domneva, kaj naj bi merili.

### Preslikava iz izvornega skilla

Vir: `aeo-topic-brief`, razdelek »Prioritization by trend«. Tam se je prioriteta računala iz `new_prompts` / `disappeared_prompts` / `visibility_direction` / `has_previous` - te izračunane sezname Excel nima. Namesto njih ima vsaka vrstica `visibility_signal` (prosto besedilo iz dashboarda) in `date_added`. Logika prioritete je enaka, preslikava je tale:

- **Vrstica z `visibility_signal`, ki opisuje svež, nepokrit prompt** (npr. besedilo v pomenu »nov prompt, brez pokritosti«) - to je ustreznik `new_prompts`: najvišja prioriteta, gap je svež.
- **Vrstica z `visibility_signal`, ki opisuje prompt, ki vztraja kljub prejšnjim poskusom** (npr. besedilo v pomenu »vztrajajoč prompt, N. teden«) - trenutni pristop ne prime. Če Excel oz. `source_recommendation` razkriva, kateri format/kanal je bil že poskušen, v predlogu Igorju priporoči **drugačen** format ali kot, ne ponovitve.
- **`source_recommendation`** je ustreznik `top_recommendation` iz vira - dobesedno priporočilo iz AEO poročila. Vtkaj ga v `rationale`, enako kot je vir zahteval vtkanje `top_recommendation` in `opportunities`.
- **`channel`** pove, kateri kanal (LinkedIn / Reddit / Owned content) je AEO za to vrstico priporočil. Excel nima agregata po kanalih na ravni celotnega poročila (v viru je bil to `opportunities: {linkedin, reddit, owned_content}`, številke za vse tri kanale hkrati) - tega tu ni in si ga ne izmišljuj. `channel` je zato informacija o tej eni vrstici, ne signal za prerazporejanje uteži med kandidati.
- **`date_added`** je informativen znak, ne pravilo s pragom: starejša vrstica je čakala dlje, kar lahko omeniš, a to ni razlog za avtomatično prednost - ne izmišljuj si števila dni, po katerem tema »zapada«.
- `visibility_signal`, ki nakazuje, da je prompt izginil s seznama manjkajočih (ustreznik `disappeared_prompts` - pristop je torej deloval), se v praksi ne bo pojavil med kandidati, ker take vrstice dobijo `status = done` in jih ta skill ne bere (glej `excel-contract.md`, razdelek Branje). Če pa bi kdaj vseeno naletel na tak signal pri vrstici s `status = new`, to pomeni: format/kot, ki je pri sorodnem promptu deloval, je vreden ponovitve pri trenutnem kandidatu - enako kot v viru.

## Pogoste napake (vir: »Common mistakes«, prilagojeno)

- **Tema kot kategorija** namesto kot stališče - glej zgoraj, zaostri pred predlogom.
- **Predlagaš vse kandidate namesto rangiranja.** Vir: »Covering all missing_prompts« - enako velja tu: rangiraj in izberi največ tri, ne izpuščaj rangiranja samo zato, ker je kandidatov malo.
- **Izmišljaš številke, ki jih Excel ne daje** (točke vidnosti, deleže citiranja, dneve do zapadlosti). Vir prepoveduje izmišljanje metrik iz mail-brifa; tu enako velja za vse, česar `excel-contract.md` ne navaja.
- **Izbiraš namesto Igorja.** Ni v izvornem skillu (tam ni bilo izbire osebe), a velja tu - glej `SKILL.md`, razdelek »Kaj ne delaš«.
