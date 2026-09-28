---
name: frodx-newsletter
description: Generira celotno FrodX "GameChanger" izdajo novičnika - slovenski original plus hrvaška in angleška transkreacija - pripravljeno za Janijev HubSpot uvoz prek docx. Uporabi vedno, ko Igor reče "naredi newsletter", "nova izdaja novičnika", "pripravi GameChanger", "novičnik za ta teden", "newsletter iz teh kolumn/URL-jev", "transkreiraj newsletter v HR/EN", "zgradi docx za Janija" ali ko pošlje URL-je kolumn/vsebin in hoče iz njih sestaviti izdajo. Pokrije ves postopek od intake vsebin prek SI originala (subject, preheader, hook, bloki, CTA) in samoevalvacije po sedmih vratih do HR in EN transkreacije, samoevalvacije vsake različice, docx builda po determinističnem table-per-block formatu ter scorecarda in handoffa. NE uporabljaj za samostojno kolumno (igor-column-writer), čisto jezikovno transkreacijo brez sestave izdaje (frodx-transcreation), pogodbe (frodx-contract-writer) ali key visual (frodx-key-visual).
---

# FrodX Newsletter (GameChanger)

Verzija 2.3 (31. 7. 2026) – glej `CHANGELOG.md`.

Iz Igorjevih vsebin (kolumne, novice, napovedi dogodkov) sestavi celotno trojezično izdajo novičnika in jo pripravi za Janijev HubSpot uvoz. SI je vir resnice; HR in EN sta nativni transkreaciji, ne prevoda.

Cilj ni surov prvi osnutek. Cilj je osnutek, ki je **že prestal sedem vrat samoevalvacije**, s scorecardom in jasno označbo, kaj ostaja Igorju v pregled. Manj čakanja, manj krogov korekcij, bolj predvidljiva kvaliteta.

## Kdaj se uporabi kateri skill (meje)

- **Sestava cele izdaje novičnika (ta skill):** subject, preheader, hook, bloki, CTA, vse tri jezike, docx za Janija.
- **Samostojna kolumna iz teme/brief-a** → `igor-column-writer`.
- **Samo prevod/transkreacija enega teksta brez sestave izdaje** → `frodx-transcreation`. Ta skill si za jezikovni transfer izposodi njegova pravila (glej `references/playbook.md`, razdelek Transkreacija).
- **Key visual / naslovna slika** → `frodx-key-visual`.

## Postopek (ena veriga)

### 1. Intake
Igor pošlje gradivo za izdajo. Tipično: 1–3 URL-ji kolumn/vsebin, morda napoved dogodka (webinar), morda novica o stranki/partnerju, morda slike.

- Vsebine z URL-jev preberi z `web_fetch` (bash **ne more** odpreti zunanjih URL-jev - glej `references/image-compositing.md`, razdelek Omrežje).
- Določi **tip izdaje** (monotematska kolumna / večbločna 2–3 vsebine / napoved dogodka / case study / čista AI-tema). Tip izbere hook in strukturo - glej `references/playbook.md`, razdelek Tipologija izdaj.
- Če je gradivo dvoumno (koliko blokov, kateri je glavni, ali gre webinar noter), vprašaj **eno** kratko vprašanje, sicer sklepaj iz gradiva in nadaljuj.

### 2. SI original
Napiši slovenski original po `references/playbook.md`: subject + preheader (po arhetipu), hook (oblični vstop + premostitev), 1–3 bloki (vsak: naslov, telo, 1 slika, 1 CTA), razpršeni CTA – od tega natanko en **pain link** (CTA, ki izkazuje problem, ne branosti; `references/measurement.md`) – podpis in noga. Glas in hišna pravila so kanonično v skillu - `references/playbook.md` (razdelek Glas) za novičnik, globlji uredniški glas pa v `frodx-transcreation` (`voice-and-style.md`, `forbidden-phrases.md`). Avtoriteta je skill, ne projektna navodila in ne userPreferences.

### 3. Samoevalvacija SI
Zaženi vseh **sedem vrat** iz `references/self-eval-rubric.md`. Trdna vrata (struktura, pravopis, glas/žargon, subject/preheader) popravi sam in tiho. Mehka vrata (hook, FrodX edinstvenost) dvigni in označi preostalo tveganje. Za hitre mehanske ulove poženi `scripts/eval_check.py` (na besedilnem osnutku z `--text`; na končnem docx brez zastavice - korak 6).

### 4. HR in EN transkreacija
Za vsako vsebinsko postavko izpelji nativno HR in EN različico po `references/playbook.md` (razdelek Transkreacija) in po `frodx-transcreation`, če je nameščen. Ključno: progresivno krčenje kazala SI→HR→EN, lokalizacija dogodkov (webinar SI 10:00 / HR 13:00), zamenjava podpisnika/noge po trgu, HR množina (NE dvojina), EN = mednarodna poslovna angleščina za CEE bralca (brez težkih idiomov).

### 5. Samoevalvacija HR in EN
Za vsako jezikovno različico ponovno zaženi sedem vrat - zdaj se aktivira tudi **Vrata 6 (transkreacija)**. Kalke popravi (npr. "Budite dobro" → "Sve najbolje"), dvojino popravi v množino, lokalizacijo preveri. Ker nisi rojeni govorec, mehko nativnost **dvigni in označi** za prvo pošiljko na nov trg, ne razglasi za rešeno.

### 6. docx build za Janija
Zgradi tri docx datoteke (SI/HR/EN) **točno po shemi iz `references/docx-pipeline.md`** (rekonstruirana iz Janijevih delujočih vzorcev). Železna pravila: **VELIKI ključi**; hook, TOC, closing, signoff in PS so **tabele** (ne proza); vsaka slika je **vdelana** v celico `IMAGE` (ne ime datoteke); **ena CTA na blok**, brez inline povezav v telesu; `BLOCK_ID` v obliki `block-01`. Vsebino izdaje vpiši v `EDITIONS` znotraj `scripts/build_newsletter.py` in zaženi `python3 scripts/build_newsletter.py`. Nato vsako datoteko preveri s `scripts/eval_check.py <docx>` (pokriva shemo in uredniške ulove). Slike pripravi po `references/image-compositing.md` (WebP → PNG, razmerje ohrani).

### 7. Scorecard in handoff
Za vsako različico vrni kompakten scorecard (format v `references/self-eval-rubric.md`). Eksplicitno izpostavi, **kar ostaja Igorju**: resničnost dejstev, živi URL-ji, odprtost webinarja, rojeni pregled HR/EN pri prvi pošiljki, ton novic o strankah. Predaj docx datoteke prek `present_files`. Ob dostavi pripravi še **vrstico za arhiv** (`references/archive.md`): vsi uredniški stolpci izpolnjeni, rezultati prazni, z opomnikom, da Igor v tednu po sendu dopiše odmev (številka + kanali) – edino metriko, ki je HubSpot ne vidi.

## Poštena ločnica (vgrajena v vsako izdajo)

Samoevalvacija ni zunanji ocenjevalec. Model, ki preverja sebe, ima slepe pege. Zato:

- **Popravim sam, tiho:** strukturne, pravopisne, glasovne, žargonske napake; kalke; dvojino; lokalizacijo ur in podpisnika.
- **Dvignem in označim (nikoli ne razglasim za rešeno sam):** ali hook res prime, ali os med bloki drži, mehka nativnost HR/EN, ton javne formulacije o strankah/partnerjih.
- **Ne morem preveriti iz svojega okolja → vedno označim:** ali je novica točna, ali je webinar termin odprt, ali živi URL dela. (Opomba: registracijske strani, ki se v mojem okolju kažejo kot "zaprte", so za prave uporabnike pogosto odprte - moj pogled je lahko zastarel; tega ne razglasim za napako, le označim za Igorjev pregled.)

## Reference

- `references/playbook.md` - kako napisati vsak del: subject/preheader arhetipi, hook formula in tipologija, struktura blokov, knjižnica CTA fraz, tipologija izdaj, transkreacijska pravila SI→HR→EN.
- `references/self-eval-rubric.md` - sedem vrat z merljivimi pragovi, zanka, scorecard format, kaj ostane Igorju.
- `references/docx-pipeline.md` - **prava shema** Janijevega uvoznika (8 tabel po vrsti, VELIKI ključi, vdelane slike, `BODY_P*`/`BULLET_*`/`EVENT_*`, lokalizirane vrednosti, `SEGMENT_REF` konvencija), build in validacija.
- `references/measurement.md` - **definicija uspeha in merjenje**: prospecting vrata, hierarhija metrik, pain link, kampanjski ID-ji, MCP recepti in omejitve, stanje baz.
- `references/archive.md` - shema arhiva poslanih izdaj z rezultati (polnjenje čaka na vir podatkov).
- `references/image-compositing.md` - kompozitiranje logotipov (cairosvg + Pillow), omrežna omejitev, kako Igor dostavi slike.

## Skripte

- `scripts/build_newsletter.py` - zgradi tri docx (SI/HR/EN) po pravi shemi; vsebino vpišeš v `EDITIONS`, slike **vdela** (python-docx). Zaženi: `python3 scripts/build_newsletter.py`.
- `scripts/eval_check.py` - preverja **docx** po pravi shemi (VELIKI ključi, tabele, vdelane slike, `block-0N`, ena CTA/blok, brez inline povezav) + uredniški ulovi (ritem, fraze, žargon, %, em dash, datum). Zaženi: `python3 scripts/eval_check.py <docx>` (na besedilnem osnutku `--text`). Vsako opozorilo je nasvet, ne trdi blok - končni urednik je Igor.
