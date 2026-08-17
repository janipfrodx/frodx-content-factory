---
name: frodx-content-factory
description: Run the FrodX content production chain end to end - pick an AEO topic, write the column, run the critique loop, transcreate to EN and HR, generate the key visual, enrich publishing metadata and hand the package to the publishing app. Use whenever Igor wants to start a new column, blog post or content run for frodx.com, including when he only says "nova kolumna", "nova vsebina", "zaženi tovarno" or names a topic he wants written. This is the single entry point - it calls the other frodx skills itself.
metadata:
  version: 0.1.0
---

# FrodX Content Factory - dirigent

Ta skill vodi produkcijo ene kolumne skozi sedem korakov. Igor kliče samo tega; ostale skille kličeš ti.

## Načelo

Ti si dirigent, ne pisec. Vsebino delajo podskilli. Tvoja naloga je: pripravi stanje, pokliči pravi skill, zapiši rezultat v `state.json`, počakaj na Igorjevo potrditev, pojdi naprej.

**Nikoli ne greš čez gate brez izrecne potrditve.** Ne domnevaj, da je »ok« pomenilo »in nadaljuj z vsem ostalim«. Potrditev velja za en korak.

## Zagon

1. Če Igor ni povedal teme, pokliči `frodx-topic-pick`. Ta prebere Excel in predlaga teme.
2. Ko je tema izbrana, ustvari tek:

```bash
python3 scripts/init_run.py "<naslov teme>" runs
```

Pot `scripts/init_run.py` je relativna na mapo tega skilla (`plugins/content-factory/skills/frodx-content-factory/`); `runs` (in kasneje `outbox/`) nastane relativno na CWD ob zagonu ukaza.

**Mapa teka ne preživi seje - preverjeno 14.-15. 8. 2026.** V Cowork seji je CWD `/home/claude`, kar je efemerni oblačni vsebnik: `runs/` in `outbox/` nastaneta tam in umreta skupaj s sejo. Kar iz tega sledi za tvoje delo:

- **Tek naj steče v eni seji.** Razdelek »Nadaljevanje prekinjenega teka« spodaj deluje samo znotraj iste seje.
- **Ob vsakem gate-u pokaži Igorju vsebino, ne samo poti.** Besedilo kolumne, alt tekste in meta podatke izpiši v pogovor - pogovor preživi, mapa ne. Če je seja prekinjena, je transkript edini vir, iz katerega je mogoče tek obnoviti.
- **Edina obstojna točka je korak 7**, ko paket odide v aplikacijo. Do takrat obstaja tek samo v tej seji.
- Če tek prekineš sredi poti, to Igorju povej kot dejstvo: »mapa teka je izgubljena, imamo pa besedilo v pogovoru«. Ne trdi, da se tek nadaljuje kasneje, če se ne more.

Obstojna rešitev (sinhronizacija mape teka na SharePoint prek n8n) je odprta točka, ne del tega skilla.

Skripta izpiše pot do `state.json`. Če pove, da tek že obstaja, vprašaj Igorja, ali nadaljuje obstoječega ali začne novega z drugačnim naslovom.

3. Preberi `references/state-schema.md`, da veš, kdo zapolni katero polje.

## Koraki

Za korake 2-7 velja: po vsakem koraku zapiši rezultat v `state.json`, dvigni `_run.step`, nastavi `_run.status` na `awaiting_approval`, pokaži Igorju rezultat in vprašaj za potrditev. Ob potrditvi zapiši čas v `_run.approvals`.

**Korak 1 (`frodx-topic-pick`) v to generično pravilo ni zajet.** Gate koraka 1 je Igorjeva izbira teme, ki se zgodi znotraj `frodx-topic-pick` samega - ta skill Igorja vpraša »katero temo pišemo« sam, in šele po njegovi izbiri zapiše `_run.status = in_progress` (ne `awaiting_approval`). Ko se `frodx-topic-pick` vrne z izbrano temo, ne vprašaj Igorja znova in ne prepiši `_run.status` nazaj na `awaiting_approval` - pojdi naravnost naprej, kot je opisano spodaj.

**Tudi korak 7 (`frodx-publish-send`) ni v celoti zajet v generično pravilo.** Ne vprašuje za potrditev po sebi - to je zadnji korak, ki samo validira in preda paket. Nastavi `_run.status` na `ready` (dry-run) ali `sent` (živo pošiljanje), NE na `awaiting_approval`.

Vrstni red je zato pri koraku 1 obrnjen glede na korake 2-7: `frodx-topic-pick` teče **pred** `init_run.py` (»Zagon« zgoraj, točka 1 pred točko 2), ker je naslov teme, ki jo Igor izbere, vhod za slug, ki ga `init_run.py` ustvari. `state.json` ob teku `frodx-topic-pick` torej **še ne obstaja** - ustvari ga dirigent (ti) takoj po Igorjevi izbiri, s `python3 scripts/init_run.py "<izbrana tema>" runs`, preden `frodx-topic-pick` vanj zapiše `_run.brief` in `_run.topic_source`. Vsi ostali koraki (2-7) tečejo **po** `init_run.py` in pišejo v že obstoječ `state.json`.

| Korak | Skill | Kaj vprašaš Igorja |
|---|---|---|
| 1 | `frodx-topic-pick` | katero temo pišemo |
| 2 | `igor-column-writer` | je kolumna v redu |
| 3 | `frodx-critique-loop` | je popravljena verzija v redu |
| 4 | `frodx-transcreation` | sta EN in HR v redu |
| 5 | `frodx-image-run` | je slika v redu |
| 6 | `frodx-publishing-meta` | so meta podatki v redu |
| 7 | `frodx-publish-send` | (brez vprašanja, samo pošlje) |

Korak 2 je Igorjev skill in sme prekiniti z vprašanji o hooku, tezi in številkah. To je pričakovano - pusti ga.

Koraka 2 in 4 (Igorjeva vendorirana skilla) ne pišeta sama v `state.json` - vrneta besedilo v pogovoru, ti ga prepišeš v ustrezno rezino. Natančna preslikava (kaj gre v `meta.title`, `languages.sl.content`, `social_posts[]`, `languages.en/hr.content`) je v `references/igor-output-mapping.md`. Preberi jo pred prvim zagonom teh dveh korakov.

Korak 4 kliči dvakrat: SL→EN in SL→HR. Hrvaščina rabi native pregled; če Igor pove, da ga bo opravil nekdo drug, počakaj in tega ne obidi.

Če Igor (ali Jani) izrecno odloči, da tek gre naprej **brez** native pregleda, je to dovoljeno - a zadolžitev takrat zapiši v `_run.open_tasks` (oblika je v `references/state-schema.md`):

```json
{"what": "hrvaška različica ni šla skozi native pregled", "who": "native govorec hrvaščine",
 "created_at": "<ISO čas odločitve>", "step": 4}
```

Ločena datoteka v mapi teka s seznamom, kaj naj native govorec preveri, je koristen dodatek, ni pa nadomestilo: taka datoteka ne potuje s paketom in gate je ne vidi. Zapis v `_run.open_tasks` je tisti, ki ga korak 7 prebere in izpiše.

### Terminologija in AEO ciljni prompt

`frodx-transcreation/references/terminology.md` privzeto zahteva »SAP Engagement Cloud« in odsvetuje »Emarsys« kot samostojno ime izdelka - z izjemo, ki jo dopušča sam: »unless the source context explicitly requires reference to the former name«.

**AEO ciljni prompt je tak primer.** Če `_run.brief.target_prompt` vsebuje »Emarsys« (npr. »Emarsys vs HubSpot«), kolumna brez te besede ne odgovarja na vprašanje, zaradi katerega je nastala. Takrat velja: »Emarsys« stoji v naslovu in tam, kjer se govori o izvoru platforme ali o tem, kaj bralec išče; **povsod drugje** »SAP Engagement Cloud«. Tako je bilo izvedeno v teku 14.-15. 8. 2026.

Vendoriranega `terminology.md` zaradi tega ne spreminjaj (`tests/test_vendor_integrity.py` bi padel). Izjema je zapisana kot čakajoča točka za Igorja v `plugins/content-factory/VENDOR.md`.

## Nadaljevanje prekinjenega teka

Če Igor reče »nadaljuj kolumno X«, poišči `runs/*-<slug>/state.json`, preberi `_run.step` in nadaljuj z naslednjim korakom. Ne ponavljaj korakov, ki so že opravljeni, razen če Igor to izrecno zahteva.

## Kdaj se ustaviš

- Excel nima novih tem - povej in končaj. Ne izmišljaj tem.
- Podskill vrne napako, ki je ne znaš popraviti - povej, kaj je vrnil, in vprašaj.
- Korak 7 javi kršitve - povej, katera polja manjkajo, in ponudi vrnitev na pristojni korak. Ne popravljaj paketa mimo skilla, ki je za polje odgovoren.
