# Veja nika

Nikina tedenska zgodba o eni HubSpot novosti v eni dejavnosti: do 450 besed. Isto zgodbo gre na blog frodx.com v SL, HR in EN; na LinkedIn gre kratka objava (SL na Nikin profil, EN na stran FrodX) z naslovnico in povezavo na blog v prvem komentarju. Igor novost izbere in zgodbo pripravi s teboj. Nika zgodbo pregleda v Docu »Nikine zgodbe« pred transkreacijo.

Poti `scripts/` in `vendor/` so relativne na mapo te veje (`veje/nika/`). V ukazih so zapisane relativno na mapo debla (`plugins/content-factory/skills/frodx-content-factory/`).

Pisec je `vendor/nika-update-writer/SKILL.md` (Igorjev `nika-update-writer` v1.1.1). Ni samostojen skill: ne »zaženeš« ga, ampak prebereš njegova navodila in reference ter izvedeš **samo korake, ki jih predpiše ta veja**. Kjer se veja in pisec razlikujeta, velja veja.

## Sprožilci

Igor hoče novo Nikino zgodbo o HubSpot novosti. Vejo prepoznaš po pomenu, ne po točni frazi. Primeri: »nova Nikina zgodba«, »HubSpot novost za Niko«, »tedenski update za Niko«, »prišel je HubSpot mail z novostmi«, ali Igor prilepi novost iz HubSpot maila.

Korak 6 se sproži z »nadaljuj Niko«, »Nika je pregledala« ali »Nika je potrdila« (razdelek »Nadaljevanje«). Isti sprožilci v novem chatu nadaljujejo tudi tek, ki ima osnutke v HubSpotu (korak 11).

Ne sem: Igorjeva kolumna ali blog brez omembe Nike (veja kolumna) in novičnik (veja novičnik).

## Paket

`state.json` je od začetka telo paketa tipa `nika_story` v1.1 in blok `_run`. `_run` se pred oddajo odreže. Pogodba je `tests/fixtures/nika_story_body.json` v repozitoriju.

| Polje | Kdo ga zapolni |
|---|---|
| `source` | korak 1 (`update_title`, `status`, `mail_date`) in korak 2 (`kb_urls`) |
| `activity`, `dilemma` | korak 2; `activity` je ime dejavnosti dobesedno iz prvega stolpca `vendor/nika-update-writer/references/vertikale.md` |
| `story`, `judgment`, `claims`, `preveri`, `warnings`, `score`, `formulas` | korak 3 |
| `languages` | korak 7 (prevodi EN, HR) |
| `meta` | korak 8 (kampanja, oznake, naslovnice) |
| `schedule` | korak 9 (urnik objave) |

- `judgment.origin` je `nacelo` (presoja iz `vendor/nika-update-writer/references/nacela.md`, `principle` navede načelo), `igor` (Igorjev vnos iz `_run.vnos`) ali `skill` (ni ne načela ne vnosa).
- `claims[].category` je `nova` (z `url` na `knowledge.hubspot.com` ali `hubspot.com` in z `quote` iz vira), `obstojeci` ali `priporocilo`.
- `source.status` je `beta`, `scheduled` ali `live`. `source.mail_date` je `YYYY-MM-DD` ali prazen, če je Igor mail prilepil brez datuma.

## Koraki

Gate je pri korakih 1-4, 6-9 in 11; koraki 5, 10 in 12 tečejo brez vprašanja. Tek nastane ob gate-u koraka 1, ko je novost potrjena:

```bash
python3 scripts/init_run.py --veja nika "<naslov novosti>" runs
```

| Korak | Kaj teče | Gate: kaj vprašaš Igorja |
|---|---|---|
| 1 Novost | Igor prilepi novost iz maila (naslov, opis, status). Pravila so v podrazdelku »Korak 1«. | **da**: je to novost, ki jo pišemo. Nato `init_run.py`, iz prilepljenega izpolni `source` in `_run.kandidat` |
| 2 Kartica | Javni članek na `knowledge.hubspot.com` po naslovu novosti, prebran z `web_fetch`. Kartica po `vendor/nika-update-writer/references/vir.md`, predlog dejavnosti in dileme (`vendor/nika-update-writer/references/vertikale.md`). Pravila so v podrazdelku »Korak 2«. | **da**: kartica, dejavnost, dilema; Igor sme dodati svoj vnos |
| 3 Zgodba | Pisec, njegovi koraki 6-8, presoja po njegovem koraku 5: z Igorjevim vnosom ali brez njega iz `nacela.md`. `check.py --blog`, razvrstitev trditev, ocena po `vendor/nika-update-writer/references/rubrika.md`; LinkedIn je kratka objava. Pravila so v podrazdelku »Korak 3«. | **da**: Igor prebere zgodbo za blog, kratko LinkedIn objavo, trditve, oznake `[PREVERI]` in oceno |
| 4 Kritika | `frodx-critique-loop`, vhod po razdelku »Skupni koraki«; nato znova `check.py --blog` | **da**: popravljena zgodba |
| 5 Oddaja Niki | Zavihek v Docu in `cf-deliver-nika`, razdelek »Oddaja Niki« | brez vprašanja, Igorju poveš izid |
| 6 Nadaljevanje | Razdelek »Nadaljevanje« | **da**: Nikine spremembe in odločitev |
| 7 Transkreacija | razdelek »Transkreacija« | **da**: EN in HR (+ ocena audita za oba jezika) |
| 8 Meta | `python3 veje/nika/scripts/meta.py runs/<tek>/state.json` | **da**: kampanja, oznake, naslovnice, naslovi in meta opisi v treh jezikih |
| 9 Datumi | pojavno vprašanje, razdelek »Objava« | **da**: datum in ura bloga, dan LinkedIna |
| 10 Osnutki | `cf-nika-publish` `pripravi`, razdelek »Objava« | brez vprašanja |
| 11 Pregled osnutkov | sporočilo s tremi povezavami na osnutke, nato pojavno vprašanje z zavihki SL, HR, EN, razdelek »Objava« | **da**: »Da, razporedi« ali »Ne, treba je popraviti« za vsak jezik |
| 12 Razpored | `cf-nika-publish` `razporedi`, razdelek »Objava« | brez vprašanja, Igorju izid |

### Korak 1

- Igor prilepi novost (iz maila »Weekly Product Updates Roundup« ali od drugod). Status (`beta`, `scheduled`, `live`) prepiši iz prilepljenega; če ga ni, vprašaj.
- Hub oceni iz naslova in ga označi z »(ocena)«; potrdi ga članek v koraku 2.
- Nabiralnika ne bereš.
- Povezav v prilepljenem (`app.hubspot.com/product-updates/...`) ne odpiraš, ker vodijo na prijavo. Opis iz maila je samo namig za izbor, ne vir.
- Ta korak nadomesti pisčeva koraka 1 (Nika prilepi strani) in 2 (do sedem kandidatov).

### Korak 2

- Vir dejstev je samo članek na `knowledge.hubspot.com` ali drug javni zapis na `hubspot.com`. **Brez članka ni zgodbe**: povej Igorju; če hoče, prilepi drugo novost.
- Partnerski blogi so samo kazalec, da članek obstaja; v kartici dobijo `[PREVERI]`.
- Velja samo URL, ki v rezultatu `web_fetch` stoji dobesedno. URL-ja ne sestavljaš iz naslova.
- Izdajo, status, datum in navedke za `claims[].quote` prepišeš dobesedno iz besedila članka. Če orodje namesto besedila vrne povzetek, povzetek ni vir: kar v besedilu ne stoji, je »vir ne pove«.
- Dejavnost naj ne ponovi dejavnosti zadnjih treh zgodb (prejšnje zgodbe so v podrazdelku »Korak 3«). Odloči Igor.
- Igorjev vnos zapiši dobesedno v `_run.vnos`; pisec ga v koraku 3 uporabi namesto načela.
- Kartica ostane v pogovoru. V `state.json` pred vprašanjem zapišeš `activity`, `dilemma`, `source.kb_urls` in `_run.vnos`.

### Korak 3

- Zgodbo za blog zapiši v `runs/<tek>/zgodba-blog.md`, nato poženi:

  ```bash
  python3 veje/nika/vendor/nika-update-writer/scripts/check.py runs/<tek>/zgodba-blog.md --blog --prev runs/<tek>/prev
  ```

- `story.linkedin_text` je kratka objava po standardu kolumne `veje/kolumna/vendor/igor-column-writer/references/social-posts.md` (3-4 kratke vrstice, brez povezave in brez oznake zanjo), v Nikinem glasu, o isti novosti. Pisčevega pravila »isto besedilo za blog in LinkedIn« ne uporabiš. Preveri jo `preveri_paket.py`.
- Prejšnje zgodbe v `runs/<tek>/prev/` so zadnje tri objave z oznako rubrike »HubSpot z Niko« (SL), ki jih dobiš prek HubSpot konektorja, vsaka kot `.md`. Če je objav s to oznako manj kot tri, ima mapa toliko zgodb, kolikor jih je (morda nobene). Primere iz `vendor/nika-update-writer/references/primeri/` `check.py` primerja sam.
- Napaka `check.py`, nerazvrščena trditev ali nova zmožnost brez URL-ja ustavi paket. Opozorila `check.py` zapiši v `warnings`.
- Pri oceni pod 9,0 zgodbo enkrat revidiraj in povej, kaj manjka. Na gate-u Igor odloči, ali gre naprej.
- Presoja, ki je ne pokrije nobeno načelo in je Igor ne poda, ima `origin: skill`. Dilemo zapiši kot vprašanje za Niko v `preveri`, ne kot njeno odločitev.
- Vsaka oznaka `[PREVERI: ...]` v besedilu ima svojo vrstico v `preveri`. Odprta oznaka ustavi korak 6.
- Besedilo nima vrstice `---`, ker bi `check.py` preveril samo del za njo.

### Korak 8

- Skripta vpiše `meta` (kampanja, oznake, naslovnice z URL-ji in alt teksti) iz razdelka »Rubrika HubSpot z Niko« v `veje/kolumna/publishing-meta/references/hubspot-taxonomy.md` in iz `veje/nika/assets/naslovnice.json`.
- `MANJKA` pomeni človekov korak (H2 oznake, H3 kampanja, H4 naslovnice): povej ga Igorju in ne nadaljuj. Vrednosti ne izmišljaš.
- Pillar povezav Nikina zgodba nima.
- Gate: Igor pregleda kampanjo, oznake in naslovnice ter naslove in meta opise v SL, HR in EN. Po njegovem da gre tek na korak 9 (razdelek »Objava«).

## Pisec in preslikava

| Pisec (`SKILL.md`) | Veja |
|---|---|
| 1 Zajem, 2 Izbor | korak 1 (Igor prilepi novost) |
| 3 Kartica, 4 Izbira | korak 2 |
| 5 Nikin vnos ali načela | korak 3, brez Nikinega obrazca: Igorjev vnos ali `nacela.md` |
| 6 Zgodba, 7 Kontrola | korak 3 |
| 8 Paket | korak 3, v polja `state.json` (spodaj) |
| 9 Pregled, distribucija, objava | koraki 5-12 te veje |

Pisčev paket (korak 8) v `state.json`:

| Pisec | Polje |
|---|---|
| zgodba za blog | `story.blog_md`; naslov iz vrstice `# ` tudi v `story.title` |
| zgodba za LinkedIn | `story.linkedin_text` (kratka objava, korak 3) |
| dva alternativna naslova | `story.alt_titles` |
| meta opis (140-160 znakov) | `story.meta_description` |
| trditve po kategorijah | `claims` |
| seznam `[PREVERI: ...]` | `preveri` (`text`, `where`) |
| ocena s pripombami | `score` (`total`, `items` po petih postavkah rubrike) |
| opozorila `check.py` | `warnings` |
| uporabljene formule | `formulas` |

Pisčev predlog seznama pogovorov, kjer je zgodba uporabna, gre v pogovor, ne v paket.

## Skupni koraki

- `frodx-critique-loop` teče v koraku 4, vhod je v njegovem razdelku »Vhod po veji« (Nika).
- `frodx-transcreation` in `frodx-transcreation-check` tečeta v koraku 7 (razdelek »Transkreacija«).
- `frodx-image-run` ne teče: naslovnice so fiksne (`assets/`).
- `frodx-publish-send` ne teče: oddaja Niki in objava sta v razdelkih »Oddaja Niki« in »Objava«.
- Kritika popravljeno besedilo vpiše z `python3 veje/nika/scripts/besedilo.py vpis <state.json> sl <datoteka>`.

## Preverba paketa

```bash
python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --faza niki --telo outbox/<run_slug>.json
python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --faza objava --telo outbox/<run_slug>.json
```

Prvi ukaz teče pred oddajo Niki, drugi pred korakom 10 (objava); njegovo telo je `paket_json` za `pripravi` in prepiše telo iz oddaje Niki. Preverba pregleda:
- `type` `nika_story` in `version` `1.1`; vsa polja `story` (`title`, `blog_md`, `linkedin_text`, `meta_description`); natanko dva alternativna naslova; meta opis 140-160 znakov;
- `story.linkedin_text` je kratka objava (1-4 vrstice, brez povezave in naslova), ne zgodba; prvega komentarja paket ne nosi;
- `source` z `kb_urls` na `knowledge.hubspot.com` ali `hubspot.com`; dejavnost iz `vertikale.md`; izvor presoje;
- kategorijo vsake trditve ter URL in navedek vsake nove; da ima vsaka oznaka `[PREVERI` vrstico v `preveri`;
- `check.py --blog` brez napake; da v besedilu ni vrstice `---` in ni dolgega pomišljaja; da paket ne nosi `_run`;
- faza `objava` še: prevodi EN in HR (`languages`), meta podatki (kampanja, oznake, naslovnice) proti `hubspot-taxonomy.md` in urnik objave (`schedule`; zamik `publish_at` mora biti zamik `Europe/Ljubljana` na tisti dan, poleti +02:00, pozimi +01:00).

`--telo` zapiše telo za oddajo samo, kadar kršitev ni. Ocena pod 9,0 je opozorilo. Vsaka kršitev pove pristojni korak.

## Oddaja Niki

1. `python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --faza niki --telo outbox/<run_slug>.json`; kršitev ustavi oddajo.
2. `python3 veje/nika/scripts/zavihek.py runs/<tek>/state.json > runs/<tek>/zavihek.md`.
3. Claude Docs konektor: v Doc »Nikine zgodbe« (`https://claude.ai/code/artifact/f307990d-76ae-4e30-b9b2-9635fc39d412`, doc id `f307990d-76ae-4e30-b9b2-9635fc39d412`) dodaj zavihek z imenom `<run_slug>` in vsebino `zavihek.md`; red zavihkov je `b<run_slug>`, da se zavihki razvrstijo po datumu za »Pregled« (`a0`). Id zavihka (`file` id iz odgovora Docsa ob ustvarjanju) takoj zapiši v `_run.tab_id` v `state.json`. Če zavihek s tem imenom že obstaja (ponovna oddaja po »Zavrni«), zamenjaj njegovo vsebino in ne dodaj drugega; `_run.tab_id` ostane isti. Docs podpira spustni seznam v celicah tabele: tri celice odločitve dobijo `{"type":"dropdown","enum":"<id>"}` brez `index` (izbere Nika), in sicer »Odločitev« `832fa5b7-c46c` (Potrdi, Zavrni), »Bi se tako odločila« `d37fd622-c7ec` (da, ne, drugače) in »Razlog zavrnitve« `f74ea3fe-404a` (presoja, dejstvo, novost, slog); vrednosti izpiše `python3 veje/nika/scripts/zavihek.py runs/<tek>/state.json --celice`. Komentar ostane prazna besedilna celica. V zavihku »Pregled« (id `71a36976-ec9a`) dodaj vrstico (naslov, dejavnost, današnji datum, »čaka Niko«, ime zavihka `<run_slug>`) ali ob ponovni oddaji obstoječi nastavi stanje »čaka Niko«. Zadnja celica vrstice je ime zavihka `<run_slug>` kot navadno besedilo, brez omembe in brez povezave. Stanje posodobiš še v »Nadaljevanje« (»potrjeno« / »zavrnjeno«) in v koraku 12 (»razporejeno«).
4. `execute_workflow` na `cf-deliver-nika`. Telo webhooka gre gnezdeno pod `inputs.webhookData.body`:

   ```json
   {
     "workflowId": "o8L8DsTaqQT3wi9B",
     "executionMode": "manual",
     "triggerNodeName": "Trigger",
     "inputs": {
       "webhookData": {
         "method": "POST",
         "body": {
           "run_slug": "<run_slug>",
           "doc_url": "https://claude.ai/code/artifact/f307990d-76ae-4e30-b9b2-9635fc39d412",
           "tab_id": "<_run.tab_id>",
           "title": "<story.title>",
           "activity": "<activity>",
           "paket_json": "<telo iz outbox/<run_slug>.json kot niz>"
         }
       }
     }
   }
   ```

   `doc_url` je povezava na Doc »Nikine zgodbe« iz koraka 3, `tab_id` (`_run.tab_id`) je id zavihka, `paket_json` je telo iz `outbox/<run_slug>.json` kot niz, ne objekt. `execute_workflow` vrne samo `executionId`. Počakaj, da se izvedba konča: `get_workflow_execution` z `includeData: false` kliči, dokler `status` ni `success` ali `error`; šele nato prebereš izid. Dokler prejšnja izvedba teče, `cf-deliver-nika` ne kličeš znova. Izid prebereš z `get_workflow_execution`, `includeData: true` in `nodeNames: ["Izid"]`, nikoli cele izvedbe; vozlišče `Izid` vrne `{izid, sporocilo, run_slug}`. Če `execute_workflow` vrne napako ali izhod `get_workflow_execution` nima vozlišča `Izid`, povej Igorju, kaj je vrnil, in oddaje ne javi kot uspešne.
5. Igorju povej izid: `created` ali `resubmitted` - Nika je dobila sporočilo v Teams kanalu; `notify_failed` - daj mu povezavo na zavihek, da jo pošlje sam; `duplicate` - zgodba je že čez Nikin pregled; `rejected` - povej `sporocilo`.
6. Igorju povej, da nadaljuje, ko Nika napiše v kanal: »nadaljuj Niko«.

Med Nikinim pregledom v zavihek ne pišeš.

## Nadaljevanje

Sprožilci: »nadaljuj Niko«, »Nika je pregledala«, »Nika je potrdila«.

1. Če chat nima teka: `get_data_table_rows` na `CF-Teki` z `dataTableId: "qXM8KuxMDyNQ9C0y"`, `projectId: "FucXmQlDiWLVsRHW"`, `filter: {"filters":[{"columnName":"veja","value":"nika"},{"columnName":"stanje","value":"caka_niko"}]}` in še enkrat z istima `dataTableId` in `projectId` ter `filter: {"filters":[{"columnName":"veja","value":"nika"},{"columnName":"stanje","value":"osnutek"}]}`. Naštej vrstice obeh stanj in vprašaj, katero. Vrstica v stanju `razporejeno` je končana: če jo Igor omeni, mu povej `publish_at` in `linkedin_date` iz vrstice in ne nadaljuj. `init_run.py` se tu ne kliče (naredi slug z današnjim datumom). `_run.tab_id` vzemi iz stolpca `tab_id` izbrane vrstice.
   - `caka_niko`: ustvari `runs/<run_slug>/state.json` = `paket_json` izbrane vrstice + `"_run": {"veja": "nika", "slug": "<run_slug>", "step": 6, "status": "in_progress", "approvals": {}, "open_tasks": [], "skill_versions": {}}` in nadaljuj s točko 2.
   - `osnutek`: osnutki v HubSpotu že obstajajo, `paket_json` je paket za objavo iz koraka 10. Ustvari `runs/<run_slug>/state.json` = `paket_json` + `"_run": {"veja": "nika", "slug": "<run_slug>", "step": 11, "status": "in_progress", "approvals": {}, "open_tasks": [], "skill_versions": {}}`. `_run.hubspot_posts` sestavi iz stolpca `hubspot_post_ids` (`{sl, en, hr}`): za vsak jezik `id`, `editor_url` `https://app.hubspot.com/blog/4964185/editor/<id>/content` in `url` (`blog_url_sl`, `blog_url_en`, za HR prazen). `story.linkedin_text` nastavi na `li_sl_text`, `languages.en.linkedin_text` na `li_en_text`. Nadaljuj s korakom 11 (razdelek »Objava«); točke 2-7 tega razdelka odpadejo.
2. Preberi zavihek prek Claude Docs konektorja. Zavihek je `_run.tab_id`; če `_run` ni na voljo, ga vzemi iz stolpca `tab_id` vrstice `CF-Teki` za ta `run_slug`: `get_data_table_rows` z `dataTableId: "qXM8KuxMDyNQ9C0y"`, `projectId: "FucXmQlDiWLVsRHW"`, `filter: {"filters":[{"columnName":"run_slug","value":"<run_slug>"}]}`.
   - `read` s `container {"kind":"project","id":"f307990d-76ae-4e30-b9b2-9635fc39d412"}` in `ref {"object":"file","id":"<_run.tab_id>"}` vrne vozlišče telesa. Nato znova `read` z `ref {"object":"node","id":"<id iz content.id>"}`, brez payloada.
   - `xml` iz odgovora zapiši **dobesedno** v `runs/<tek>/zavihek.xml`. Če ima odgovor `next`, nadaljuj z `read` in payloadom `{"kind":"view", ...next}`; vsak naslednji kos shrani kot `zavihek-2.xml`, `zavihek-3.xml` in tako naprej.
   - Poženi `python3 veje/nika/scripts/xml_v_zavihek.py runs/<tek>/zavihek-nika.md runs/<tek>/zavihek.xml [runs/<tek>/zavihek-2.xml ...]`. Skripta preveri vsak odstavek proti Docsu in zapiše markdown zavihka. Ob NAPAKA zavihek enkrat preberi znova; če pade drugič, povej Igorju, kaj je skripta vrnila.
   - Neizbran spustni seznam je prazna celica; nespremenjen zavihek ima 0 spremenjenih povedi.
3. `python3 veje/nika/scripts/iz_zavihka.py runs/<tek>/zavihek-nika.md runs/<tek>/state.json`. NAPAKA (manjka razdelek, neznana vrednost): povej Igorju dobesedno in ga prosi, naj Niko prosi za popravek v zavihku.
4. Odločitev prazna: Nika še ni končala; povej Igorju in končaj.
5. »Zavrni«: povej razlog in komentar. V zavihku »Pregled« nastavi stanje »zavrnjeno«. Z Igorjem predelaj zgodbo (korak 3 ali 4). Pred ponovno oddajo iz `state.json` izbriši `_run.nika_izvirnik` (da ga `iz_zavihka.py` ob naslednjem branju znova zapiše iz novega zavihka in se spremembe ne štejejo proti staremu izvirniku), osveži zavihek (tabela odločitve prazna) in ponovi »Oddaja Niki«, ki stanje v »Pregled« znova nastavi na »čaka Niko«; `cf-deliver-nika` vrne `resubmitted`, ker je vrstica še v `caka_niko`.
6. »Potrdi«: najprej osveži datoteko bloga z `python3 veje/nika/scripts/besedilo.py izpis runs/<tek>/state.json sl > runs/<tek>/zgodba-blog.md`, nato `python3 veje/nika/vendor/nika-update-writer/scripts/check.py runs/<tek>/zgodba-blog.md --blog --prev runs/<tek>/prev` in preverba paketa v fazi `niki`. Odprta oznaka `[PREVERI` v besedilu ali kršitev ustavi tek; neodkljukane oznake iz `odprte` naštej Igorju.
7. Gate: pokaži Nikine spremembe (število spremenjenih povedi in povedi same), njeno sodbo in komentar. Po Igorjevem da v zavihku »Pregled« nastavi stanje »potrjeno«; tek gre na korak 7 (razdelek »Transkreacija«).

## Transkreacija

Po pravilih veje kolumna, razdelek »Skupni koraki« (`veje/kolumna/VEJA.md`), z razliko v poljih:

1. `frodx-transcreation` dvakrat: SL→EN in SL→HR. Vhod je `besedilo.py izpis <state.json> sl`; izhod vpišeš z `besedilo.py vpis <state.json> <jezik> <datoteka>` (prva vrstica `# <naslov>`).
2. `frodx-transcreation-check` za `en` in `hr`, z auditom na koncu, kot pri kolumni; vhod v njegovem »Vhod po veji« (Nika). Zadolžitev za HR native pregled zapiše v `_run.open_tasks` sam.
3. `story.meta_description` prevedi v `languages.<jezik>.meta_description` (največ 160 znakov).
4. `story.linkedin_text` prevedi samo v EN, v `languages.en.linkedin_text`, po istem standardu kratke objave. HR LinkedIn objave ni.
5. Gate: oba prevoda, oceni audita, EN LinkedIn objava; povej, da priporočaš HR native pregled. Po Igorjevem da gre tek na korak 8 (`meta.py`, razdelek »Koraki«).

## Objava

Po koraku 8. `state.json` ima vse tri jezike in `meta`; HubSpot osnutke in razpored naredi `cf-nika-publish` (`ZhBP6iFc2JlVhrvt`). Workflow ne objavljaš in ga ne aktiviraš: kličeš ga samo z `execute_workflow`.

9. Poženi `python3 veje/nika/scripts/urnik.py`; izpiše najzgodnejši čas bloga (zdaj + 15 minut, zaokroženo navzgor na četrt ure) kot `publish_at` in predlagani `linkedin_date`. Vprašaj Igorja za datum in uro bloga ter dan LinkedIna (ena objava na Nikin profil, ena na stran FrodX, obe ob 7.30). Prva ponujena možnost v vprašanju je ta `publish_at`, izpisan človeško (npr. »danes ob 11.00«), z `linkedin_date` iz istega izpisa. Prejšnjega časa od izpisanega `publish_at` ne sprejmeš: če ga Igor vpiše, povej najzgodnejši čas in vprašaj znova. Igor sme vpisati poljuben kasnejši čas; vsi časi so na četrt ure. LinkedIn ne sme pred blogom; na dan bloga mora biti blog do 7.30. Zapiši `schedule.publish_at` (ISO z zamikom `Europe/Ljubljana` na tisti dan: poleti +02:00, pozimi +01:00) in `schedule.linkedin_date`.
10. `python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --faza objava --telo outbox/<run_slug>.json`; kršitev ustavi tek. Nato `execute_workflow` na `cf-nika-publish` (`ZhBP6iFc2JlVhrvt`) z `{mode: "pripravi", run_slug, paket_json}`, po istem vzorcu kot pri »Oddaja Niki«:

   ```json
   {
     "workflowId": "ZhBP6iFc2JlVhrvt",
     "executionMode": "manual",
     "triggerNodeName": "Trigger",
     "inputs": {
       "webhookData": {
         "method": "POST",
         "body": {
           "mode": "pripravi",
           "run_slug": "<run_slug>",
           "paket_json": "<telo iz outbox/<run_slug>.json kot niz>"
         }
       }
     }
   }
   ```

   `paket_json` je telo iz `outbox/<run_slug>.json` kot niz, ne objekt. `execute_workflow` vrne samo `executionId`. Počakaj, da se izvedba konča: `get_workflow_execution` z `includeData: false` kliči, dokler `status` ni `success` ali `error`; šele nato prebereš izid. Dokler prejšnja izvedba za isti `run_slug` teče, `pripravi` in `razporedi` ne kličeš znova. Izid prebereš z `get_workflow_execution`, `includeData: true` in `nodeNames: ["Izid"]`, nikoli cele izvedbe; vozlišče `Izid` vrne `{izid, sporocilo, posts}`, kjer je `posts` `{sl, en, hr}` z `id`, `editor_url` in `url` za vsak jezik. Če `execute_workflow` vrne napako ali izhod `get_workflow_execution` nima vozlišča `Izid`, povej Igorju, kaj je vrnil, in izida ne javi kot uspešnega. `created`: osnutki so narejeni. `exists`: osnutki že obstajajo, `posts` so isti kot prvič, uporabi jih. `rejected`: povej `sporocilo` in ne nadaljuj; sporočilo »prejšnji pripravi za ta tek še teče ali je padel« pomeni, da mora Jani preveriti osnutke v HubSpotu in izprazniti `hubspot_post_ids`, preden ponoviš. Ob `created` in `exists` vrnjeni `posts` zapiši v `_run.hubspot_posts` v `state.json`, da jih lahko uporabiš znova (`pripravi` jih ob ponovnem klicu vrne kot `exists`).
11. Najprej navadno sporočilo (ne vprašanje; pojavno vprašanje povezav ne naredi klikljivih) s: tremi klikljivimi markdown povezavami na osnutke (`[SL osnutek](editor_url)`, `[HR osnutek](editor_url)`, `[EN osnutek](editor_url)`, iz `_run.hubspot_posts`), LinkedIn objavama dobesedno (SL `story.linkedin_text`, EN `languages.en.linkedin_text`, kot ju v koraku 12 dobi n8n) in urnikom (`schedule.publish_at`, `schedule.linkedin_date`, človeško). Nato pojavno vprašanje z zavihkom na jezik (SL, HR, EN) in izbiro »Da, razporedi« / »Ne, treba je popraviti«, brez URL-jev v besedilu vprašanja (lahko »SL osnutek iz sporočila zgoraj«). Ob »Ne« Igor pove, kaj; popraviš:
    - blog prek HubSpot konektorja: najprej `GET_POST`, `<div id="ifb-feedback-...">` ostane nespremenjen, en `UPDATE` naenkrat, isti popravek vpišeš v paket (`besedilo.py vpis`). Če konektor nima pravice, Igor popravi v urejevalniku in reče »popravljeno«.
    - LinkedIn objavo neposredno v `story.linkedin_text` oziroma `languages.en.linkedin_text` v `state.json` (`besedilo.py` piše samo `blog_md`); ostati mora kratka objava.
    - datum: posodobi `schedule` v `state.json` po pravilih koraka 9 in `urnik.py` poženi znova (čas teče); prejšnjega časa od novega najzgodnejšega ne sprejmeš. Datum v InstantFeedback widgetu v telesu objave ostane tisti iz koraka 10 (kozmetično).

    Po vsakem popravku znova poženi `python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --faza objava --telo outbox/<run_slug>.json` (preveri tudi kratko objavo in urnik); kršitev popraviš, preden greš naprej. Vprašanje ponoviš samo za jezike, ki še niso »Da«; če se je spremenila LinkedIn objava ali urnik, najprej znova pošlji sporočilo s povezavami, objavama in urnikom. Nič se ne razporedi, dokler niso vsi trije »Da«.
12. `execute_workflow` na `cf-nika-publish` z istim vzorcem kot v koraku 10 in telesom `{mode: "razporedi", run_slug, li_sl_text: story.linkedin_text, li_en_text: languages.en.linkedin_text, publish_at: schedule.publish_at, linkedin_date: schedule.linkedin_date}` (končne vrednosti iz `state.json` po morebitnih popravkih v koraku 11); `workflowId`, `executionMode`, `triggerNodeName` in `method` so isti. Počakaj, da se izvedba konča: `get_workflow_execution` z `includeData: false` kliči, dokler `status` ni `success` ali `error`; šele nato prebereš izid. Dokler prejšnja izvedba za isti `run_slug` teče, `razporedi` ne kličeš znova. Izid se bere iz vozlišča `Izid` z `{izid, sporocilo}` (`includeData: true`, `nodeNames: ["Izid"]`). Workflow datuma preveri po istih pravilih kot preverba paketa, ju zapiše v `CF-Teki` in razporedi z njima.
    - `scheduled`: povej Igorju datum bloga in dan LinkedIna in v zavihku »Pregled« nastavi stanje »razporejeno«.
    - `exists`: razpored že obstaja, povej in stanje v »Pregled« nastavi na »razporejeno«.
    - `schedule_failed`: povej sporočilo HubSpota; vrstica ostane `osnutek`, Igor ponovi.
    - `rejected`: povej `sporocilo`. Če sporočilo pravi, da je HubSpot razpored uspel, vrstica v CF-Teki pa ni posodobljena, `razporedi` ne ponavljaš (ni preverjeno, kako HubSpot sprejme ponovni razpored že razporejene objave): povej Igorju, da je blog razporejen, LinkedIn pa ne bo objavljen, dokler Jani v `CF-Teki` ne nastavi vrstice na `razporejeno` z `li_sl_text`, `li_en_text` in `li_sl_status`/`li_en_status` `scheduled`. Če pravi, da `publish_at` ni več v prihodnosti, z Igorjem izberi nov datum po koraku 9 (`urnik.py` poženi znova), znova poženi preverbo v fazi `objava` in ponovi `razporedi`.

    Pred sporočilom Igorju ob `scheduled` ali `exists` preveri, ali je `cf-nika-linkedin` (`cC1okNFo5bwsLq5D`) aktiven: n8n MCP `search_workflows` s `query: "cf-nika-linkedin"`, polje `active` zadetka z id `cC1okNFo5bwsLq5D`.
    - `active: true`: povej, da LinkedIn objavi `cf-nika-linkedin` dne `linkedin_date` ob 7.30 (SL na Nikin profil, EN na stran FrodX, s prvim komentarjem).
    - `active: false`, zadetka ni ali klic pade: povej, da je blog razporejen, LinkedIn objavi pa NE bosta objavljeni, dokler Jani ne aktivira `cf-nika-linkedin`; besedili čakata v `CF-Teki`. Nikoli ne trdi, da LinkedIn objavi sam, brez tega preverjanja.

## Posebnosti

- Dolgi pomišljaj je prepovedan; namesto njega razmaknjen vezaj ( - ).
- Primeri v zgodbah so izmišljeni in anonimni; podjetja nikoli ne imenuješ.
- Številk ne izmišljaš: številka iz vira ima povezavo, ilustrativna je označena kot primer.
- Nika ne piše vnosa in ne dobi obrazca. Pisčevega `references/obrazec.md` ne uporabljaš.
- `nacela.md` in `glas.md` sta Igorjeva (vendor) in se ne urejata. Nikini odgovori prideta vanju skozi Igorjev vir.
- Obstojne točke so zavihek (besedilo), `CF-Teki` ob oddaji Niki (paket) in `CF-Teki` po koraku 10 (paket za objavo, ID-ji osnutkov, LinkedIn besedili). Od obeh točk v `CF-Teki` se tek nadaljuje v novem chatu (razdelek »Nadaljevanje«).
