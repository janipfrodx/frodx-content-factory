# Veja nika

Nikina tedenska zgodba o eni HubSpot novosti v eni dejavnosti: do 450 besed. Isto besedilo gre na blog frodx.com (s povezavami na vir v besedilu) in na Nikin LinkedIn (povezava v prvem komentarju). Igor novost izbere in zgodbo pripravi s teboj. Nika jo samo potrdi ali zavrne v aplikaciji.

Poti `scripts/` in `vendor/` so relativne na mapo te veje (`veje/nika/`). V ukazih so zapisane relativno na mapo debla (`plugins/content-factory/skills/frodx-content-factory/`).

Pisec je `vendor/nika-update-writer/SKILL.md` (Igorjev `nika-update-writer` v1.1.1). Ni samostojen skill: ne »zaženeš« ga, ampak prebereš njegova navodila in reference ter izvedeš **samo korake, ki jih predpiše ta veja**. Kjer se veja in pisec razlikujeta, velja veja.

## Sprožilci

Igor hoče novo Nikino zgodbo o HubSpot novosti. Vejo prepoznaš po pomenu, ne po točni frazi. Primeri: »nova Nikina zgodba«, »HubSpot novost za Niko«, »tedenski update za Niko«, »prišel je HubSpot mail z novostmi«, »katero novost vzamemo ta teden«.

Ne sem: Igorjeva kolumna ali blog brez omembe Nike (veja kolumna) in novičnik (veja novičnik).

## Paket

`state.json` je od začetka telo `POST /api/drafts` tipa `nika_story` v1.0 in blok `_run`. `_run` se pred oddajo odreže. Pogodba je `tests/fixtures/nika_story_body.json` v repozitoriju.

| Polje | Kdo ga zapolni |
|---|---|
| `source` | korak 1 (`update_title`, `status`, `mail_date`) in korak 2 (`kb_urls`) |
| `activity`, `dilemma` | korak 2; `activity` je ime dejavnosti dobesedno iz prvega stolpca `vendor/nika-update-writer/references/vertikale.md` |
| `story`, `judgment`, `claims`, `preveri`, `warnings`, `score`, `formulas` | korak 3 |

- `judgment.origin` je `nacelo` (presoja iz `vendor/nika-update-writer/references/nacela.md`, `principle` navede načelo), `igor` (Igorjev vnos iz `_run.vnos`) ali `skill` (ni ne načela ne vnosa).
- `claims[].category` je `nova` (z `url` na `knowledge.hubspot.com` ali `hubspot.com` in z `quote` iz vira), `obstojeci` ali `priporocilo`.
- `source.status` je `beta`, `scheduled` ali `live`. `source.mail_date` je `YYYY-MM-DD` ali prazen, če je Igor mail prilepil brez datuma.

## Koraki

Gate je pri vsakem koraku. Tek nastane ob gate-u koraka 1, ko je novost izbrana:

```bash
python3 scripts/init_run.py --veja nika "<naslov novosti iz maila>" runs
```

| Korak | Kaj teče | Gate: kaj vprašaš Igorja |
|---|---|---|
| 1 Kandidati | M365 konektor: zadnji mail pošiljatelja `noreply@notifications.hubspot.com` z zadevo »Weekly Product Updates Roundup« iz zadnjih 14 dni. Tabela do 10 vrstic: novost, hub, status, predlagana dejavnost (`vendor/nika-update-writer/references/vertikale.md`), oznaka »tehnično« ali »poslovni učinek«. Pravila so v podrazdelku »Korak 1«. | **da**: katero novost vzamemo. Nato `init_run.py`, izbrano vrstico zapiši v `_run.kandidat`, iz maila pa izpolni `source` |
| 2 Kartica | Javni članek na `knowledge.hubspot.com` po naslovu novosti, prebran z `web_fetch`. Kartica po `vendor/nika-update-writer/references/vir.md`, predlog dejavnosti in dileme. Pravila so v podrazdelku »Korak 2«. | **da**: kartica, dejavnost, dilema; Igor sme dodati svoj vnos |
| 3 Zgodba | Pisec, njegovi koraki 6-8, presoja po njegovem koraku 5: z Igorjevim vnosom ali brez njega iz `nacela.md`. `check.py` v obeh načinih, razvrstitev trditev, ocena po `vendor/nika-update-writer/references/rubrika.md`. Pravila so v podrazdelku »Korak 3«. | **da**: Igor prebere zgodbo za blog, LinkedIn besedilo, trditve, oznake `[PREVERI]` in oceno |
| 4 Oddaja | Preverba paketa, nato razdelek »Oddaja« | **da**, ena potrditev |

### Korak 1

- Konektor bere samo maile pošiljatelja `noreply@notifications.hubspot.com` z zadevo »Weekly Product Updates Roundup«. Nobenega drugega iskanja po Igorjevem nabiralniku, tudi ne za boljšo presojo (ISO 27001).
- Če maila ni ali konektor ni povezan, to povej in prosi Igorja, naj mail prilepi ali posreduje.
- Povezav v mailu (`app.hubspot.com/product-updates/...`) ne odpiraš, ker vodijo na prijavo. Opis iz maila je samo namig za izbor, ne vir.
- Mail ima bete (»Trending Betas«) in novosti »Scheduled for release«; novosti »Live« v njem ni. Status za `source.status` prepiši iz razdelka maila (`beta` ali `scheduled`).
- Ta korak nadomesti pisčev korak 1 (Nika prilepi strani) in njegov korak 2 (do sedem kandidatov).

### Korak 2

- Vir dejstev je samo članek na `knowledge.hubspot.com` ali drug javni zapis na `hubspot.com`. **Brez članka ni zgodbe**: povej Igorju in mu ponudi drugo novost iz tabele.
- Partnerski blogi so samo kazalec, da članek obstaja; v kartici dobijo `[PREVERI]`.
- Velja samo URL, ki v rezultatu `web_fetch` stoji dobesedno. URL-ja ne sestavljaš iz naslova.
- Dejavnost naj ne ponovi dejavnosti zadnjih treh zgodb (prejšnje zgodbe so v podrazdelku »Korak 3«). Odloči Igor.
- Igorjev vnos zapiši dobesedno v `_run.vnos`; pisec ga v koraku 3 uporabi namesto načela.

### Korak 3

- Zgodbo zapiši v `runs/<tek>/zgodba-blog.md` in `runs/<tek>/zgodba-linkedin.md`, nato poženi:

  ```bash
  python3 veje/nika/vendor/nika-update-writer/scripts/check.py runs/<tek>/zgodba-blog.md --blog --prev runs/<tek>/prev
  python3 veje/nika/vendor/nika-update-writer/scripts/check.py runs/<tek>/zgodba-linkedin.md --linkedin --prev runs/<tek>/prev
  ```

- Prejšnje zgodbe v `runs/<tek>/prev/` so zadnje tri Nikine objave, ki jih dobiš prek HubSpot konektorja, vsaka kot `.md`. Dokler Nika kot avtorica v HubSpotu ne obstaja, ostane mapa prazna. Primere iz `vendor/nika-update-writer/references/primeri/` `check.py` primerja sam.
- Napaka `check.py`, nerazvrščena trditev ali nova zmožnost brez URL-ja ustavi paket. Opozorila `check.py` zapiši v `warnings`.
- Pri oceni pod 9,0 zgodbo enkrat revidiraj in povej, kaj manjka. Na gate-u Igor odloči, ali gre naprej.
- Presoja, ki je ne pokrije nobeno načelo in je Igor ne poda, ima `origin: skill`. Dilemo zapiši kot vprašanje za Niko v `preveri`, ne kot njeno odločitev.
- Vsaka oznaka `[PREVERI: ...]` v besedilu ima svojo vrstico v `preveri`. Aplikacija Niki zaklene Potrdi, dokler je katera odprta.
- Besedilo nima vrstice `---`, ker bi `check.py` preveril samo del za njo.

## Pisec in preslikava

| Pisec (`SKILL.md`) | Veja |
|---|---|
| 1 Zajem, 2 Izbor | korak 1 (mail namesto prilepljenih strani) |
| 3 Kartica, 4 Izbira | korak 2 |
| 5 Nikin vnos ali načela | korak 3, brez Nikinega obrazca: Igorjev vnos ali `nacela.md` |
| 6 Zgodba, 7 Kontrola | korak 3 |
| 8 Paket | korak 3, v polja `state.json` (spodaj) |
| 9 Pregled, distribucija, objava | aplikacija in n8n, ne Cowork |

Pisčev paket (korak 8) v `state.json`:

| Pisec | Polje |
|---|---|
| zgodba za blog | `story.blog_md`; naslov iz vrstice `# ` tudi v `story.title` |
| zgodba za LinkedIn | `story.linkedin_text` |
| povezava v prvem komentarju | `story.first_comment` |
| dva alternativna naslova | `story.alt_titles` |
| meta opis (140-160 znakov) | `story.meta_description` |
| trditve po kategorijah | `claims` |
| seznam `[PREVERI: ...]` | `preveri` (`text`, `where`) |
| ocena s pripombami | `score` (`total`, `items` po petih postavkah rubrike) |
| opozorila `check.py` | `warnings` |
| uporabljene formule | `formulas` |

Pisčev predlog seznama pogovorov, kjer je zgodba uporabna, gre v pogovor, ne v paket.

## Skupni koraki

Ta veja skupnih korakov ne kliče:
- `frodx-critique-loop` ne teče, ker ima pisec rubriko in `check.py`. Kritiko dodamo po pilotu, če jo Igor hoče.
- `frodx-transcreation-check` ne teče, ker je zgodba samo v SI.
- `frodx-image-run` ne teče, ker naslovne slike v pilotu ni.
- `frodx-publish-send` ne teče; oddaja je v razdelku »Oddaja«.

## Preverba paketa

```bash
python3 veje/nika/scripts/preveri_paket.py runs/<tek>/state.json --telo outbox/<run_slug>.json
```

Preverba pregleda:
- `type` `nika_story` in `version` `1.0`; vsa polja `story`; natanko dva alternativna naslova; meta opis 140-160 znakov; prvi komentar s povezavo na vir;
- `source` z `kb_urls` na `knowledge.hubspot.com` ali `hubspot.com`; dejavnost iz `vertikale.md`; izvor presoje;
- kategorijo vsake trditve ter URL in navedek vsake nove; da ima vsaka oznaka `[PREVERI` vrstico v `preveri`;
- `check.py --blog` in `--linkedin` brez napake; da v besedilu ni vrstice `---` in ni dolgega pomišljaja; da paket ne nosi `_run`.

Ocena pod 9,0 je opozorilo. Vsaka kršitev pove pristojni korak.

## Oddaja

n8n `cf-deliver-nika` še ne obstaja; zgradi se, ko Igor potrdi predračun. Do takrat korak 4 konča s preverbo paketa: telo stoji v `outbox/<run_slug>.json`. Igorju povej, da predaja v aplikacijo še ni zgrajena, in mu zgodbo za blog ter LinkedIn besedilo izpiši v pogovor, ker mapa teka ne preživi seje.

## Posebnosti

- Dolgi pomišljaj je prepovedan; namesto njega razmaknjen vezaj ( - ).
- Primeri v zgodbah so izmišljeni in anonimni; podjetja nikoli ne imenuješ.
- Številk ne izmišljaš: številka iz vira ima povezavo, ilustrativna je označena kot primer.
- Nika ne piše vnosa in ne dobi obrazca. Pisčevega `references/obrazec.md` ne uporabljaš.
- `nacela.md` in `glas.md` sta Igorjeva (vendor) in se ne urejata. Nikini odgovori prideta vanju skozi Igorjev vir.
- Tek teče v eni seji; obstojna točka je oddaja.
