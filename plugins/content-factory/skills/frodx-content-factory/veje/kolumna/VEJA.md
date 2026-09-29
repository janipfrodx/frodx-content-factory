# Veja kolumna

Kolumna ali blog za frodx.com v treh jezikih, s socialnimi objavami, naslovno sliko in meta podatki. Paket gre v aplikacijo za objave (PROD 2).

Poti `references/...`, `topic-pick/`, `publishing-meta/` in `vendor/` so relativne na mapo te veje (`veje/kolumna/`). Pot `scripts/init_run.py` je relativna na mapo debla (`plugins/content-factory/skills/frodx-content-factory/`).

Trije skilli te veje niso samostojni. Ko besedilo spodaj reče »pokliči X«, preberi to datoteko in jo izvedi:

| Ime v besedilu | Datoteka |
|---|---|
| `frodx-topic-pick` | `topic-pick/SKILL.md` |
| `frodx-publishing-meta` | `publishing-meta/SKILL.md` |
| `igor-column-writer` | `vendor/igor-column-writer/SKILL.md` |

## Sprožilci

Igor hoče novo kolumno ali blog za frodx.com. Primeri: »nova kolumna«, »napiši blog«, »nova vsebina za blog«, »zaženi tovarno za kolumno« ali samo tema, ki jo želi napisano.

Ne sem: vse, kar omenja newsletter, novičnik, NL ali GameChanger. To je veja novičnik.

## Paket

`state.json` ima od koraka 1 obliko paketa za aplikacijo za objave (`meta`, `universal`, `social_posts`, `languages.sl/en/hr`) in blok `_run`. Kdo zapolni katero polje, je v `references/state-schema.md`.

## Koraki

### Zagon

1. Če Igor ni povedal teme, pokliči `frodx-topic-pick`. Ta prebere HubSpot AEO portal in predlaga teme.
2. Ko je tema izbrana, ustvari tek:

```bash
python3 scripts/init_run.py --veja kolumna "<naslov teme>" runs
```

Pot `scripts/init_run.py` je relativna na mapo tega skilla (`plugins/content-factory/skills/frodx-content-factory/`); `runs` (in kasneje `outbox/`) nastane relativno na CWD ob zagonu ukaza.

Skripta izpiše pot do `state.json`. Če pove, da tek že obstaja, vprašaj Igorja, ali nadaljuje obstoječega ali začne novega z drugačnim naslovom.

3. Preberi `references/state-schema.md`, da veš, kdo zapolni katero polje.

### Vrstni red in gate-i

**Korak 1 (`frodx-topic-pick`) v to generično pravilo ni zajet.** Gate koraka 1 je Igorjeva izbira teme, ki se zgodi znotraj `frodx-topic-pick` samega - ta skill Igorja vpraša »katero temo pišemo« sam, in šele po njegovi izbiri zapiše `_run.status = in_progress` (ne `awaiting_approval`). Ko se `frodx-topic-pick` vrne z izbrano temo, ne vprašaj Igorja znova in ne prepiši `_run.status` nazaj na `awaiting_approval` - pojdi naravnost naprej, kot je opisano spodaj.

**Tudi korak 7 (`frodx-publish-send`) ni v celoti zajet v generično pravilo.** Ne vprašuje za potrditev po sebi - to je zadnji korak, ki samo validira in preda paket. Nastavi `_run.status` na `sent`, NE na `awaiting_approval`. Dry-run ne obstaja več - korak 7 preda prek `cf-deliver-draft`.

Vrstni red je zato pri koraku 1 obrnjen glede na korake 2-7: `frodx-topic-pick` teče **pred** `init_run.py` (»Zagon« zgoraj, točka 1 pred točko 2), ker je naslov teme, ki jo Igor izbere, vhod za slug, ki ga `init_run.py` ustvari. `state.json` ob teku `frodx-topic-pick` torej **še ne obstaja** - ustvari ga dirigent (ti) takoj po Igorjevi izbiri, s `python3 scripts/init_run.py "<izbrana tema>" runs`, preden `frodx-topic-pick` vanj zapiše `_run.brief` in `_run.topic_source`. Vsi ostali koraki (2-7) tečejo **po** `init_run.py` in pišejo v že obstoječ `state.json`.

| Korak | Skill | Kaj vprašaš Igorja |
|---|---|---|
| 1 | `frodx-topic-pick` | katero temo pišemo |
| 2 | `igor-column-writer` | je kolumna v redu |
| 3 | `frodx-critique-loop` | je popravljena verzija v redu |
| 4 | `frodx-transcreation` + `frodx-transcreation-check` | sta EN in HR v redu |
| 5 | `frodx-image-run` | so slike v redu |
| 6 | `frodx-publishing-meta` | so meta podatki v redu |
| 7 | `frodx-publish-send` | (brez vprašanja, samo pošlje) |

## Pisec in preslikava

Korak 2 je Igorjev skill in sme prekiniti z vprašanji o hooku, tezi in številkah. To je pričakovano - pusti ga.

**Socialne objave v koraku 2: štiri objave nastanejo, dve gresta naprej.** Po izhodu kolumne izrecno naroči
`igor-column-writer` **štiri** socialne objave po standardu iz njegovega
`references/social-posts.md` - vsaka z drugim vzvodom, vsaka s samooceno. Štiri je odločitev te
verige z 18. 9. 2026 in zoži njegov splošni razpon 3-5; standard sam se ne spreminja.

Vse štiri zapiši v `state.json` pod `_run.social_candidates` **takoj, ko nastanejo**, še preden
Igorja karkoli vprašaš:

```json
"social_candidates": [
  {"text": "<objava 1>", "lever": "<vzvod>", "score": 8, "chosen": false},
  {"text": "<objava 2>", "lever": "...", "score": 7, "chosen": false},
  {"text": "<objava 3>", "lever": "...", "score": 9, "chosen": false},
  {"text": "<objava 4>", "lever": "...", "score": 6, "chosen": false}
]
```

`score` je Igorjeva samoocena iz njegovega standarda. `chosen` ob nastanku pri vseh štirih `false`;
po Igorjevi potrditvi ga postavi na `true` pri tistih dveh, ki gresta naprej. Tako je iz `state.json`
razvidno ne le, med čim se je izbiralo, ampak tudi kaj je bilo izbrano.

Nato **sam predlagaj dve najboljši** in za vsako povej, zakaj. Ne ponavljaj Igorjeve samoocene kot
svoje utemeljitve - njegova ocena je vhod, tvoja presoja je izbira. Merila so ista kot v njegovem
standardu: drugačnost vzvoda, odprta zanka, tretja oseba, brez povezave v besedilu.

Igorju predlog predstavi kot gate: potrdi ali zamenjaj. Če zamenja, spoštuj to brez prepričevanja -
ti predlagaš, on odloči. Šele po njegovem odgovoru zapiši izbrani dve v `social_posts[]`:

```json
"social_posts": [
  {"text": "<izbrana objava>", "publish_date": "", "image_url": "", "image_alt": ""},
  {"text": "<izbrana objava>", "publish_date": "", "image_url": "", "image_alt": ""}
]
```

`image_url` in `image_alt` pustiš prazna - zapolni ju korak 5, faza B. Gate v koraku 7 ju zahteva
neprazna, zato paket, ki bi šel v oddajo pred korakom 5, tam pade. To je namerno.

Zavrnjenih dveh ne brišeš iz `_run.social_candidates`; ostaneta z `"chosen": false`. Zapis, med čim
se je izbiralo, je enako koristen kot izbira.

Korak 2 in del koraka 4 (Igorjeva vendorirana skilla `igor-column-writer` in `frodx-transcreation`) ne pišeta sama v `state.json` - vrneta besedilo v pogovoru, ti ga prepišeš v ustrezno rezino. Natančna preslikava (kaj gre v `meta.title`, `languages.sl.content`, `social_posts[]`, `languages.en/hr.content`) je v `references/igor-output-mapping.md`. Preberi jo pred prvim zagonom teh dveh korakov. `frodx-transcreation-check`, ki v koraku 4 teče za `frodx-transcreation`, je izjema - piše sam: `languages.<jezik>.content` (po popravku), `_run.transcreation_check`, `_run.transcreation_audit` in `_run.open_tasks`.

## Skupni koraki

Korak 4 kliči dvakrat: SL→EN in SL→HR.

Po obeh transkreacijah in **pred Igorjevim gateom** pokliči `frodx-transcreation-check`, prav tako
dvakrat - za `hr` in za `en`. Ta skill da prevod v pregled GPT-ju in Geminiju, popravke naroči nazaj
`frodx-transcreation` in zapiše izid v `_run.transcreation_check`. Korak 4 se s tem ne razdeli na dva
koraka; gate ostane en sam, po preverbi.

Za preverbo za vsak jezik teče še Igorjev `frodx-transcreation-audit`, **enkrat na jezik**, kot
zadnji korak - postopek je v `frodx-transcreation-check/SKILL.md`, točka 6. Vendorirani
`frodx-transcreation` ima na vrhu »Obvezno izročilo« na audit; izpolni ga ta točka, zato audita
po `frodx-transcreation` ne kličeš sam in ga ne kličeš ob ponovnih klicih transkreacije v zanki
preverbe. Končna verzija audita je besedilo jezika. Igorju ob gateu povej oceno in sodbo audita za
oba jezika in mesta, ki jih je varovalo vrnilo.

Zadolžitev za hrvaški native pregled se odslej zapiše v `_run.open_tasks` **vedno**, tudi kadar sta
oba ocenjevalca rekla `OBJAVLJIVO` - zapiše jo `frodx-transcreation-check` sam. Igorju ob gateu
izrecno povej, da **priporočaš še native pregled**; dva modela nista Hrvat. To je Janijeva odločitev
z 18. 9. 2026 in ni stvar presoje v posameznem teku.

Zadolžitve ne odstranjuj, da bi bil izpis gatea v koraku 7 čist. Odstrani jo šele, ko človek potrdi,
da je pregled opravljen.

Vhodi in cilji skupnih skillov so pri tej veji privzeti, kot jih opisuje vsak skill:

- `frodx-critique-loop`: vhod `languages.sl.content`, prompt `frodx-critique-loop/references/critique-prompt.md`, zapis nazaj v `languages.sl.content`.
- `frodx-transcreation-check`: vir `languages.sl.content`, prevod `languages.<jezik>.content`, popravek skozi `frodx-transcreation`.
- `frodx-image-run`: fazi A in B.
- `frodx-publish-send`: postopek za kolumno.

## Preverba paketa

`python3 frodx-publish-send/scripts/validate_package.py <state.json>` (pot relativna na `plugins/content-factory/skills/`): binarni kontrakt paketa (vsa polja, taksonomija iz `publishing-meta/references/hubspot-taxonomy.md`, slike, dolgi pomišljaj, podpis). Kršitve in pristojni koraki so v `frodx-publish-send/SKILL.md`.

## Oddaja

n8n `cf-deliver-draft` (`9jbBZ832E6NquY4I`) prek `execute_workflow`. Izidi (`created`, `duplicate`, `rejected`, `misconfigured`, `retry`) in zapis v `_run.delivery` so v `frodx-publish-send/SKILL.md`.

## Posebnosti

### Terminologija in AEO ciljni prompt

`frodx-transcreation/references/terminology.md` privzeto zahteva »SAP Engagement Cloud« in odsvetuje »Emarsys« kot samostojno ime izdelka - z izjemo, ki jo dopušča sam: »unless the source context explicitly requires reference to the former name«.

**AEO ciljni prompt je tak primer.** Če `_run.brief.target_prompt` vsebuje »Emarsys« (npr. »Emarsys vs HubSpot«), kolumna brez te besede ne odgovarja na vprašanje, zaradi katerega je nastala. Takrat velja: »Emarsys« stoji v naslovu in tam, kjer se govori o izvoru platforme ali o tem, kaj bralec išče; **povsod drugje** »SAP Engagement Cloud«. Tako je bilo izvedeno v teku 14.-15. 8. 2026.

Vendoriranega `terminology.md` zaradi tega ne spreminjaj (`tests/test_vendor_integrity.py` bi padel). Izjema je zapisana kot čakajoča točka za Igorja v `plugins/content-factory/VENDOR.md`.

### Kdaj se ustaviš (poleg splošnih pravil debla)

- HubSpot nima nobenega prompta, ki ne bi bil že obdelan - povej in končaj. Ne izmišljaj tem.
- Korak 7 javi kršitve - povej, katera polja manjkajo, in ponudi vrnitev na pristojni korak. Ne popravljaj paketa mimo skilla, ki je za polje odgovoren.
