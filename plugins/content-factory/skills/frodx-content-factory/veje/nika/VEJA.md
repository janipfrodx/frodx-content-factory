# Veja nika

Nikina tedenska zgodba o eni HubSpot novosti v eni dejavnosti: do 450 besed. Isto zgodbo gre na blog frodx.com v SL, HR in EN; na LinkedIn gre kratka objava (SL na Nikin profil, EN na stran FrodX) z naslovnico in povezavo na blog v prvem komentarju. Igor novost izbere in zgodbo pripravi s teboj. Nika zgodbo pregleda v Docu »Nikine zgodbe« pred transkreacijo.

Poti `scripts/` in `vendor/` so relativne na mapo te veje (`veje/nika/`). V ukazih so zapisane relativno na mapo debla (`plugins/content-factory/skills/frodx-content-factory/`).

Pisec je `vendor/nika-update-writer/SKILL.md` (Igorjev `nika-update-writer` v1.1.1). Ni samostojen skill: ne »zaženeš« ga, ampak prebereš njegova navodila in reference ter izvedeš **samo korake, ki jih predpiše ta veja**. Kjer se veja in pisec razlikujeta, velja veja.

## Sprožilci

Igor hoče novo Nikino zgodbo o HubSpot novosti. Vejo prepoznaš po pomenu, ne po točni frazi. Primeri: »nova Nikina zgodba«, »HubSpot novost za Niko«, »tedenski update za Niko«, »prišel je HubSpot mail z novostmi«, »katero novost vzamemo ta teden«.

Korak 6 se sproži z »nadaljuj Niko«, »Nika je pregledala« ali »Nika je potrdila« (razdelek »Nadaljevanje«).

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

Gate je pri korakih 1-4 in 6; korak 5 teče brez vprašanja. Tek nastane ob gate-u koraka 1, ko je novost potrjena:

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

### Korak 1

- Igor prilepi novost (iz maila »Weekly Product Updates Roundup« ali od drugod). Status (`beta`, `scheduled`, `live`) prepiši iz prilepljenega; če ga ni, vprašaj.
- Hub oceni iz naslova in ga označi z »(ocena)«; potrdi ga članek v koraku 2.
- Nabiralnika ne bereš.
- Povezav v prilepljenem (`app.hubspot.com/product-updates/...`) ne odpiraš, ker vodijo na prijavo. Opis iz maila je samo namig za izbor, ne vir.
- Ta korak nadomesti pisčeva koraka 1 (Nika prilepi strani) in 2 (do sedem kandidatov).

### Korak 2

- Vir dejstev je samo članek na `knowledge.hubspot.com` ali drug javni zapis na `hubspot.com`. **Brez članka ni zgodbe**: povej Igorju in mu ponudi drugo novost iz tabele.
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
- Prejšnje zgodbe v `runs/<tek>/prev/` so zadnje tri objave z oznako rubrike »HubSpot z Niko« (SL), ki jih dobiš prek HubSpot konektorja, vsaka kot `.md`. Dokler oznaka ne obstaja (H2), ostane mapa prazna. Primere iz `vendor/nika-update-writer/references/primeri/` `check.py` primerja sam.
- Napaka `check.py`, nerazvrščena trditev ali nova zmožnost brez URL-ja ustavi paket. Opozorila `check.py` zapiši v `warnings`.
- Pri oceni pod 9,0 zgodbo enkrat revidiraj in povej, kaj manjka. Na gate-u Igor odloči, ali gre naprej.
- Presoja, ki je ne pokrije nobeno načelo in je Igor ne poda, ima `origin: skill`. Dilemo zapiši kot vprašanje za Niko v `preveri`, ne kot njeno odločitev.
- Vsaka oznaka `[PREVERI: ...]` v besedilu ima svojo vrstico v `preveri`. Odprta oznaka ustavi korak 6.
- Besedilo nima vrstice `---`, ker bi `check.py` preveril samo del za njo.

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
- `frodx-transcreation` in `frodx-transcreation-check` tečeta v koraku 7 (faza B).
- `frodx-image-run` ne teče: naslovnice so fiksne (`assets/`).
- `frodx-publish-send` ne teče: oddaja Niki in objava sta v razdelkih »Oddaja Niki« in »Objava«.
- Kritika popravljeno besedilo vpiše z `python3 veje/nika/scripts/besedilo.py vpis <state.json> sl <datoteka>`.

## Preverba paketa

```bash
python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --faza niki --telo outbox/<run_slug>.json
python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --faza objava
```

Prvi ukaz teče pred oddajo Niki, drugi pred korakom 10 (objava). Preverba pregleda:
- `type` `nika_story` in `version` `1.1`; vsa polja `story` (`title`, `blog_md`, `linkedin_text`, `meta_description`); natanko dva alternativna naslova; meta opis 140-160 znakov;
- `story.linkedin_text` je kratka objava (1-4 vrstice, brez povezave in naslova), ne zgodba; prvega komentarja paket ne nosi;
- `source` z `kb_urls` na `knowledge.hubspot.com` ali `hubspot.com`; dejavnost iz `vertikale.md`; izvor presoje;
- kategorijo vsake trditve ter URL in navedek vsake nove; da ima vsaka oznaka `[PREVERI` vrstico v `preveri`;
- `check.py --blog` brez napake; da v besedilu ni vrstice `---` in ni dolgega pomišljaja; da paket ne nosi `_run`;
- faza `objava` še: prevodi EN in HR (`languages`), meta podatki (kampanja, oznake, naslovnice) proti `hubspot-taxonomy.md` in urnik objave (`schedule`).

`--telo` zapiše telo za oddajo samo, kadar kršitev ni. Ocena pod 9,0 je opozorilo. Vsaka kršitev pove pristojni korak.

## Oddaja Niki

1. `python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --faza niki --telo outbox/<run_slug>.json`; kršitev ustavi oddajo.
2. `python3 veje/nika/scripts/zavihek.py runs/<tek>/state.json > runs/<tek>/zavihek.md`.
3. Claude Docs konektor: v Doc »Nikine zgodbe« (`https://claude.ai/code/artifact/f307990d-76ae-4e30-b9b2-9635fc39d412`, doc id `f307990d-76ae-4e30-b9b2-9635fc39d412`) dodaj zavihek z imenom `<run_slug>` in vsebino `zavihek.md`; red zavihkov je `b<run_slug>`, da se zavihki razvrstijo po datumu za »Pregled« (`a0`). Id zavihka (`file` id iz odgovora Docsa ob ustvarjanju) takoj zapiši v `_run.tab_id` v `state.json`. Če zavihek s tem imenom že obstaja (ponovna oddaja po »Zavrni«), zamenjaj njegovo vsebino in ne dodaj drugega; `_run.tab_id` ostane isti. Docs podpira spustni seznam v celicah tabele: tri celice odločitve dobijo `{"type":"dropdown","enum":"<id>"}` brez `index` (izbere Nika), in sicer »Odločitev« `832fa5b7-c46c` (Potrdi, Zavrni), »Bi se tako odločila« `d37fd622-c7ec` (da, ne, drugače) in »Razlog zavrnitve« `f74ea3fe-404a` (presoja, dejstvo, novost, slog); vrednosti so v `zavihek.py --celice`. Komentar ostane prazna besedilna celica. V zavihku »Pregled« dodaj vrstico (naslov, dejavnost, današnji datum, »čaka Niko«, povezava na zavihek) ali ob ponovni oddaji obstoječi nastavi stanje »čaka Niko«. Stanje posodobiš še v »Nadaljevanje« (»potrjeno« / »zavrnjeno«) in v koraku 12 (»razporejeno«).
4. `execute_workflow` na `cf-deliver-nika` (`o8L8DsTaqQT3wi9B`), `executionMode: "manual"`, `triggerNodeName: "Trigger"`, `inputs.webhookData.body`: `run_slug`, `doc_url` (povezava na Doc »Nikine zgodbe« iz koraka 3), `tab_id` (`_run.tab_id`), `title`, `activity`, `paket_json` (telo iz `outbox/<run_slug>.json` kot niz). Izid prebereš z `get_workflow_execution`, `includeData: true` in `nodeNames: ["Izid"]`, nikoli cele izvedbe; vozlišče `Izid` vrne `{izid, sporocilo, run_slug}`.
5. Igorju povej izid: `created` ali `resubmitted` - Nika je dobila sporočilo v Teams kanalu; `notify_failed` - daj mu povezavo na zavihek, da jo pošlje sam; `duplicate` - zgodba je že čez Nikin pregled; `rejected` - povej `sporocilo`.
6. Igorju povej, da nadaljuje, ko Nika napiše v kanal: »nadaljuj Niko«.

Med Nikinim pregledom v zavihek ne pišeš.

## Nadaljevanje

Sprožilci: »nadaljuj Niko«, »Nika je pregledala«, »Nika je potrdila«.

1. Če chat nima teka: `get_data_table_rows` na `CF-Teki` (`qXM8KuxMDyNQ9C0y`), vrstice z `veja = nika` in `stanje = caka_niko`; vprašaj, katero. Ustvari `runs/<run_slug>/state.json` = `paket_json` izbrane vrstice + `"_run": {"veja": "nika", "slug": "<run_slug>", "step": 6, "status": "in_progress", "approvals": {}, "open_tasks": [], "skill_versions": {}}`. `_run.tab_id` vzemi iz stolpca `tab_id` iste vrstice. `init_run.py` se tu ne kliče (naredi slug z današnjim datumom).
2. Preberi zavihek prek Claude Docs konektorja (zavihek je `_run.tab_id`; če `_run` ni na voljo, ga vzemi iz vrstice `CF-Teki` za ta `run_slug`, prebrane z `get_data_table_rows`): `export` zavihka s `format: "markdown"` (base64 v `data.bytes_b64`), dekodiraj in zapiši v `runs/<tek>/zavihek.md` brez sprememb. Neizbran spustni seznam se izvozi kot prazna celica; nespremenjen izvoz ima 0 spremenjenih povedi.
3. `python3 veje/nika/scripts/iz_zavihka.py runs/<tek>/zavihek.md runs/<tek>/state.json`. NAPAKA (manjka razdelek, neznana vrednost): povej Igorju dobesedno in ga prosi, naj Niko prosi za popravek v zavihku.
4. Odločitev prazna: Nika še ni končala; povej Igorju in končaj.
5. »Zavrni«: povej razlog in komentar. V zavihku »Pregled« nastavi stanje »zavrnjeno«. Z Igorjem predelaj zgodbo (korak 3 ali 4). Pred ponovno oddajo iz `state.json` izbriši `_run.nika_izvirnik` (da ga `iz_zavihka.py` ob naslednjem branju znova zapiše iz novega zavihka in se spremembe ne štejejo proti staremu izvirniku), osveži zavihek (tabela odločitve prazna) in ponovi »Oddaja Niki«, ki stanje v »Pregled« znova nastavi na »čaka Niko«; `cf-deliver-nika` vrne `resubmitted`, ker je vrstica še v `caka_niko`.
6. »Potrdi«: `check.py --blog` in preverba paketa v fazi `niki`. Odprta oznaka `[PREVERI` v besedilu ali kršitev ustavi tek; neodkljukane oznake iz `odprte` naštej Igorju.
7. Gate: pokaži Nikine spremembe (število spremenjenih povedi in povedi same), njeno sodbo in komentar. Po Igorjevem da v zavihku »Pregled« nastavi stanje »potrjeno« in tek gre na korak 7.

## Posebnosti

- Dolgi pomišljaj je prepovedan; namesto njega razmaknjen vezaj ( - ).
- Primeri v zgodbah so izmišljeni in anonimni; podjetja nikoli ne imenuješ.
- Številk ne izmišljaš: številka iz vira ima povezavo, ilustrativna je označena kot primer.
- Nika ne piše vnosa in ne dobi obrazca. Pisčevega `references/obrazec.md` ne uporabljaš.
- `nacela.md` in `glas.md` sta Igorjeva (vendor) in se ne urejata. Nikini odgovori prideta vanju skozi Igorjev vir.
- Obstojni točki sta zavihek (besedilo) in `CF-Teki` (paket ob oddaji).
