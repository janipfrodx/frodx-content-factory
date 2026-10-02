# Veja novičnik

Izdaja novičnika FrodX GameChanger v treh jezikih (`si`, `en`, `hr`), 1-3 bloki, s slikami blokov. Osnutek gre v Newsletter Hub, kjer ga Igor pregleda, doda manjkajoče slike, nastavi čas in razporedi. Docx ne nastane.

Poti `references/`, `scripts/` in `vendor/` so relativne na mapo te veje (`veje/novicnik/`). V ukazih so zapisane relativno na mapo debla (`plugins/content-factory/skills/frodx-content-factory/`).

Pisec je `vendor/frodx-newsletter/SKILL.md` (Igorjev `frodx-newsletter` v2.3, pravila zamrznjena do v3.0). Ni samostojen skill: ne »zaženeš« ga, ampak prebereš njegova navodila in reference ter izvedeš **samo korake, ki jih predpiše ta veja**.

## Sprožilci

Igor hoče novo izdajo novičnika. Veja se prepozna po pomenu, ne po točni frazi. Primeri: »delava nov newsletter«, »dejva naredit nov NL«, »pripravi novičnik«, »nov GameChanger«, »naredi newsletter iz teh treh kolumn«.

Ne sem: nova kolumna ali blog brez omembe novičnika. To je veja kolumna.

## Paket

`state.json` je od začetka telo `POST /api/drafts` Newsletter Huba (`run_slug`, `editions[]` za `si`, `en`, `hr`) in blok `_run`. Pogodba je `tests/fixtures/newsletter_draft_body.json` v repozitoriju. Kdo zapolni katero polje, je v `references/state-schema.md`.

- Paket ne nosi `send_datetime`, `timezone` ali kazala (TOC). Aplikacija ju nima oziroma ju nastavi Igor; časovni pas je vedno `Europe/Ljubljana`.
- `status` izdaje je `ready_to_send` ali `draft`, kot ga napiše pisec.
- Privzete vrednosti po jeziku: `references/privzete-vrednosti.md`.

## Koraki

Tek ustvari takoj, ko je veja potrjena, pred korakom 1:

```bash
python3 scripts/init_run.py --veja novicnik "<tema izdaje ali 'novicnik'>" runs
```

Gate-i so samo pri korakih 1, 3, 4 in 6. Koraka 2 in 5 tečeta brez vprašanja; rezultat se tudi tam zapiše v `state.json` takoj ob nastanku.

| Korak | Kaj teče | Gate: kaj vprašaš Igorja |
|---|---|---|
| 1 Gradivo | Igor poda 1-3 URL-je kolumn ali vsebin, po želji webinar, novico in slike. Pisec, njegov korak 1 (Intake): vsebine z URL-jev prebereš z `web_fetch`, določiš tip izdaje. Nato pripraviš vse iz podrazdelka »Korak 1« spodaj. Igorjevo pravilo je natanko en pain link na izdajo (CTA na rešitev, demo, posvet ali prijavo; `self-eval-rubric.md`). Če v gradivu takega URL-ja ni, ga pri gate-u vprašaš. URL-ja ne izmišljaš. Zapiši `_run.gradivo`, `_run.tip_izdaje`, vse odločitve pa v `_run.gradivo_odlocitve` in `_run.block_images`. | **da**, en gate za vse: kateri bloki in v kakšnem vrstnem redu, pain link, način po bloku in jeziku, slika po bloku in jeziku, hook in zgodba za blok kolumne |
| 2 SI izdaja | Pisec, njegova koraka 2-3 (SI original po `playbook.md` z izbranim hookom in zgodbo, sedem vrat po `self-eval-rubric.md`). HR in EN še ne nastaneta. | **ne**: takoj korak 3 |
| 3 Kritika | `frodx-critique-loop` na SI izdaji, največ dva kroga (glej Skupni koraki) | **da**: je SI izdaja v redu. Igor jo vidi prvič, že popravljeno po kritiki |
| 4 HR in EN | Pisec, njegova koraka 4-5, z vhodom iz `scripts/prevod_vhod.py` (podrazdelek »Korak 4« spodaj). Nato enkrat na jezik Igorjev `frodx-transcreation-audit` (točka 6 v `frodx-transcreation-check/SKILL.md`), brez GPT/Gemini preverbe. Nato Igorjev pregled in žetev. | **da**: Igorjevi popravki HR in EN, ocena audita za oba jezika, kateri popravki gredo v žetev |
| 5 Slike | `frodx-image-run`, Faza C, podrazdelek »Korak 5 veje«: izvede odločitve iz koraka 1 | **ne**: takoj korak 6 |
| 6 Oddaja | preverba paketa, nato v enem sporočilu kršitve, opozorila in odprte zadolžitve: odprte zadolžitve prebereš na glas in vprašaš, ali oddaja kljub temu (`frodx-publish-send`). Nato `cf-deliver-newsletter`, navodilo za Hub, Igorjev scorecard in arhivska vrstica v pogovor | **da**, ena potrditev |

**Pisčev korak 6 (docx build za Janija) se ne izvede nikoli.** Ne piši v `EDITIONS` znotraj `build_newsletter.py`, ne poganjaj ga in ne kliči `present_files`. Pisčev korak 7 (scorecard, kaj ostaja Igorju, vrstica za arhiv po `archive.md`) izvedeš ob oddaji, v pogovor, brez docxov.

Pisec v koraku 1 sme vprašati eno kratko vprašanje o gradivu. To je pričakovano - pusti ga.

### Korak 1: kaj pripraviš pred gate-om

Igorju pokažeš vse v enem sporočilu, po točkah a-e. Igor lahko odgovori v več sporočilih; gate je zaprt, ko je odločeno vse. Šele nato zapiši `_run.approvals.step1`.

**a) Jezikovne različice.** Za vsak URL s frodx.com poišči HR in EN različico iste strani, po vrsti:
1. preklopnik jezikov v rezultatu `web_fetch` strani: povezavi iste strani na `/hr/` in `/en/`. Povezav hreflang iz glave strani `web_fetch` ne vrne, zato jih ne iščeš;
2. če preklopnika ni: HubSpot konektor. Konektor različic ne poveže sam. Z `LIST_BLOG_POSTS` (pri straneh s seznamom strani) poišči objavo v jeziku `hr` oziroma `en`, katere slug ustreza SI slugu po pomenu. To je predlog, ne dejstvo: Igorju povej, da si ga našel po slugu;
3. če ju ne najdeš: vprašaj Igorja. URL-ja ne ugibaš in ne sestavljaš iz SI naslova. Poti niso enotne: domača stran je `/hr/homepage`, a `/en/home-page`.

Vsak najden URL preberi z `web_fetch`: stran se mora naložiti in biti v pravem jeziku, sicer različica ni najdena. Rezultat `web_fetch` obdela manjši model, zato velja samo URL, ki v rezultatu stoji dobesedno. Igorju na gate-u za vsak URL povej, od kod je (preklopnik, konektor).

**b) Tabela blokov po jezikih.** Za vsak blok in vsak jezik (`hr`, `en`) določi način:
- `transkreacija` (privzeto): blok ima isto vsebino kot v SI in nastane s transkreacijo SI bloka. Če ima vsebina bloka objavljeno različico v tem jeziku (točka a), je njen URL **referenca**;
- `lokalni_vir`: blok je v tem jeziku vsebinsko drug in v SI nima izvirnika (npr. HR radionica namesto SI webinarja). URL je stran tega trga; če je Igor gradivo prilepil v pogovor, ostane prazen.

Hook, zaključek, podpis in PS so vedno transkreacija, brez reference. V vseh jezikih ostane isto število blokov z istim `block_id` in `type` (pogodba paketa). Če Igor hoče v enem jeziku drugačno število blokov, mu to povej na tem gate-u: paket tega ne dopušča.

**c) Slike.** `frodx-image-run`, Faza C, podrazdelek »Korak 1 veje«: za vsak blok in jezik preberi og:image strani tega jezika, ga uvozi in Igorju poročaj, kaj si našel.

**d) Hook in zgodba za blok kolumne.** Po protokolu kandidatov v `vendor/frodx-newsletter/references/playbook.md` (razdelek »Pet hook arhetipov«) predlagaj 2-3 kandidate za hook, vsakega z arhetipom, in enega priporoči. Arhetip E velja Igorjevo pravilo rotacije (največ 1× na 4-6 izdaj); E ni privzet. Pri kandidatu E Igor vrne svoj resničen stavek reakcije; tega si ne izmisliš. Če ima izdaja blok `column`, vprašaj, katero osebno zgodbo ali izkušnjo Igor da vanj.

**e) Pain link** po pravilu iz tabele.

Odločitve zapiši v `_run.gradivo_odlocitve` (`bloki`, `pain_link`, `opombe`, `hook`, `zgodba_kolumne`, `jeziki`; oblika v `references/state-schema.md`) in v `_run.block_images`, preden vprašaš.

### Korak 4: HR in EN

Točke a-d tečejo za vsak jezik (`hr`, nato `en`; točka b enkrat na tek), točka e enkrat za oba jezika, točki f-g spet za vsak jezik, točka h enkrat za oba:

a. **Viri.** Za vsak blok z neprazno `url` v `_run.gradivo_odlocitve.jeziki.<jezik>` stran preberi z `web_fetch` in glavno besedilo (brez menijev in noge) zapiši v `runs/<slug>/prevod/viri/<jezik>-<block_id>.txt`. Pri `lokalni_vir` brez URL-ja zapiši tja gradivo, ki ga je Igor dal v pogovoru.

b. **Žetev.** Enkrat na tek, pred prvim jezikom: `get_data_table_rows` nad `CF-Zetev` (`references/zetev.md`), odgovor zapiši v `runs/<slug>/prevod/zetev.json`. Branje po straneh in oblika odgovora sta v `references/zetev.md`; prazna tabela je `{"rows": [], "count": 0}`.

c. **Vhod prevajalca.**

```bash
python3 veje/novicnik/scripts/prevod_vhod.py <state.json> <jezik>
```

Ob `MANJKA:` se vrni na korak, ki ga izpis imenuje. Ob `NAPAKA:` je `prevod/zetev.json` ali `state.json` pokvarjen: CF-Zetev preberi znova po `references/zetev.md` in skripto poženi še enkrat; če napaka ostane, izpis pokaži Igorju in se ustavi. Skripta zapiše `prevod/<jezik>-vhod.json` in žetev za varovalo (`transcreation-check/<jezik>-round-zetev.json`).

d. **Prevod.** Pisec, njegova koraka 4-5, iz `prevod/<jezik>-vhod.json`:
- blok `transkreacija`: transkreacija SI bloka. Referenca ni vir besedila. Zgodba, dolžina in struktura bloka pridejo iz SI. Iz reference vzameš že potrjene izraze, naslove, terminologijo in formulacije, da se blok ne razlikuje od strani, na katero vodi CTA;
- blok `lokalni_vir`: napišeš ga iz vira, v tonu in osi te izdaje; hook ga mora povezati tako kot v SI. Pisčeva preverba »ali os med bloki drži« velja tudi za ta jezik;
- nobena oblika iz stolpca `prej` v žetvi se ne pojavi; uporabiš obliko iz `potem`;
- CTA bloka v tem jeziku je URL iz `_run.gradivo_odlocitve.jeziki.<jezik>.<block_id>.url`, kadar ni prazen; sicer ostane URL SI bloka.

e. **Vpis.** HR in EN v eni datoteki z `iz_editions.py` (glej »Pisec in preslikava«).

f. **Preverba žetve.** Izpis jezika (`izdaja_besedilo.py izpis <state.json> <jezik>`) zapiši v `prevod/<jezik>-izpis.txt` in poženi iz `plugins/content-factory/skills/`:

```bash
python3 frodx-transcreation-check/scripts/preveri_iznicenje.py <mapa teka>/transcreation-check <jezik> /dev/null <mapa teka>/prevod/<jezik>-izpis.txt
```

Vsaka vrstica `IZNIČENO:` je oblika iz žetve, ki je v prevodu. Zamenjaj jo z obliko `potem` in vpiši z `izdaja_besedilo.py vpis`. Varovalo primerja podnize: če je najdena oblika samo del druge besede, je ne menjaj in to povej Igorju na gate-u.

g. **Audit.** `frodx-transcreation-check`, točka 6, po »Vhod po veji« za novičnik.

h. **Gate.** Igorju pokaži HR in EN z `izdaja_besedilo.py izpis` ter oceno in sodbo audita za oba jezika. Igor pove popravke; vneseš jih z `izdaja_besedilo.py vpis`. Iz njegovih popravkov izlušči kandidate za žetev po pravilih v `references/zetev.md` (samo splošni pari) in jih pokaži kot seznam `prej → potem (razlog)`. Igor izrecno potrdi, kateri gredo v žetev. Potrjene pare vpiši z `add_data_table_rows` v `CF-Zetev`, tabelo preberi nazaj in jih zapiši v `_run.zetev`. Nato `_run.approvals.step4`.

Če Igor nima popravkov, ni kandidatov in ni vprašanja o žetvi: `_run.zetev` ostane `[]`, zapiši `_run.approvals.step4` in pojdi na korak 5.

## Pisec in preslikava

Pisec vsebino izdaje oblikuje v obliki `EDITIONS` iz `vendor/frodx-newsletter/scripts/build_newsletter.py` (META ključi, hook, bloki, closing, signoff, PS). Skripte ne urejaš in ne poganjaš; oblika je samo dogovor, kako pisec vrne vsebino.

Po koraku 2 zapiši SI v JSON datoteko (pari `("KLJUČ", vrednost)` kot seznami `["KLJUČ", vrednost]`):

```json
{"si": {"meta": [["PACKAGE_ID", "nl-2026-10-..."], ["LANGUAGE", "si"], ...],
        "hook_archetype": "B_prizor", "hook": ["..."],
        "blocks": [{"id": "block-01", "type": "column", "img_file": "", "img_alt": "",
                    "title": "...", "body": ["..."], "bullets": [], "cta_label": "...", "cta_url": "https://..."}],
        "closing_type": "bookend", "closing": ["..."], "signoff_phrase": "...", "signoff_name": "Igor", "ps": "..."}}
```

in jo vpiši:

```bash
python3 veje/novicnik/scripts/iz_editions.py <state.json> <editions.json>
```

Po koraku 4 enako za `hr` in `en` v eni datoteki. Skripta preslika `EDITIONS` v izdaje paketa (tabela v specu), izpusti TOC, `SEND_DATETIME` in `TIMEZONE`, trajanje webinarja pretvori v celo število minut in ob manjkajočem polju glasno pade.

**Varovalka:** skripta HR in EN zavrne, dokler v `_run.approvals` ni `step3` (Igor je potrdil kritiko SI). Če HR in EN vseeno nastaneta pred kritiko, ju zavrži in napiši znova iz popravljene SI. Ne prevajaš besedila, ki se bo še spremenilo.

Ob vsakem gate-u Igorju pokaži izdajo z `python3 veje/novicnik/scripts/izdaja_besedilo.py izpis <state.json> <jezik>`, ne JSON-a.

## Skupni koraki

- **`frodx-critique-loop`** (korak 3), razdelek »Vhod po veji« v skillu, največ dva kroga:
  - vhod: `izdaja_besedilo.py izpis <state.json> si`;
  - prompt: `references/critique-prompt.md` (začasen, sestavljen iz Igorjeve rubrike);
  - zapis: `izdaja_besedilo.py vpis <state.json> si <besedilo.txt>`.
- **`frodx-transcreation-check`** (korak 4), za `hr` in za `en`, razdelek »Vhod po veji« v skillu. Za novičnik teče samo točka 6 (Igorjev audit), enkrat na jezik; zanka GPT/Gemini (točke 1-5) ne teče:
  - izvirnik: `izpis ... si`, prevod: `izpis ... <jezik>`;
  - vhod audita je žetev iz `transcreation-check/<jezik>-round-zetev.json` (zapiše jo `prevod_vhod.py`), varovalo jo preveri;
  - oznake izdaje ostanejo nespremenjene, vpis samo z `vpis ... <jezik>`. Igorju ob gate-u povej oceno in sodbo audita za oba jezika;
  - zadolžitev za native HR pregled se pri novičniku ne zapiše v `_run.open_tasks`: native pregled je Igorjev pregled na gate-u koraka 4.
- **`frodx-image-run`** (korak 1 in korak 5): samo Faza C. Fazi A in B ne tečeta.
- **`frodx-publish-send`** (korak 6): razdelek »Veja novičnik« v skillu.

## Preverba paketa

```bash
python3 veje/novicnik/scripts/preveri_paket.py <state.json> --telo outbox/<run_slug>.json
```

Preveri: trije jeziki, vsak natanko enkrat; 1-3 bloki z enakim `block_id` in `type` v vseh jezikih; `webinar` ima `event` (datum, ura, trajanje), drugi bloki `null`; vsak blok ima naslov, telo in CTA z `https://`; slika bloka mora biti v shrambi `content-images`; ni dolgega pomišljaja (razen v `delivery.segment_ref`); ni vzorčnih vrednosti iz Igorjeve predloge; v SI in HR nedeljivi presledek pred %, v EN % brez presledka; ni `send_datetime` in ni `_run`. Blok brez slike je opozorilo, ne kršitev. Vsaka kršitev pove pristojni korak.

## Oddaja

n8n `cf-deliver-newsletter` (`Wd1gVtK77b29ePrJ`) prek `execute_workflow`, `executionMode: "manual"`. Workflow ostane neaktiven. Izidi (`created`, `duplicate`, `rejected`, `misconfigured`, `retry`) in zapis v `_run.delivery` so v `frodx-publish-send/SKILL.md`, razdelek »Veja novičnik«.

Ob `created` Igorju napiši navodilo iz `frodx-publish-send` (»Osnutek je v Hubu ...«): kje doda manjkajoče slike z gumbom pri bloku, da nastavi čas in da šele »Razporedi« ustvari maile v HubSpotu. Seznam blokov brez slike vzemi iz `_run.block_images` (`vir` `brez` ali `prilozena`).

Po oddaji v pogovor izpiši pisčev scorecard za vse tri jezike, kaj ostaja Igorju (resničnost dejstev, živi URL-ji, odprtost webinarja, ton novic o strankah) in vrstico za arhiv po `vendor/frodx-newsletter/references/archive.md`.

## Posebnosti

- Jezikovna koda slovenščine je v tej veji `si`, ne `sl`.
- Webinar ima po jezikih lahko različno uro (Igorjevo pravilo: SI 10:00, HR 13:00). To ni napaka.
- Igorjeva rubrika dovoli en dash (–) kot premor v stavku. Dolgi pomišljaj ne sme nikamor, razen v `SEGMENT_REF`, kot v Igorjevem vzorcu.
- `scripts/eval_check.py` pisca je pomoč, ne gate: vedno vrne exit 0.
- Blok `announcement` o resnični stranki ali partnerju: ton javne formulacije vedno označi Igorju.
- Igorja **ne** kliči za potrditev kakršnekoli n8n spremembe. Ta veja ne gradi in ne spreminja workflowov: v teku 1. 10. 2026 je gradnja workflowa za slike po oddaji porabila 12 minut in velik del konteksta, Igor pa ga ni potreboval.
- **Ne ustvarjaš, ne kloniraš in ne urejaš mailov v HubSpotu.** Če Igor to zahteva, mu povej, da bi nastala dva izvora iste izdaje (Hub osnutek in HubSpot mail) in s tem tveganje dvojnega pošiljanja, in ga napoti na Hub: »Razporedi« maile ustvari sam.
- Ne objavljaš in ne urejaš HubSpot strani, tudi ne og:image. Napačen og:image na strani zapiši v `_run.open_tasks` za Janija.
- Ne nalagaš slik prek brskalnika in ne sestavljaš base64. Priložena slika gre v Hub z gumbom pri bloku.
- **Po oddaji** tek ne teče več. Kar Igor prinese po oddaji (slike, popravki besedila), uredi v Hubu; ti mu poveš, kje.
