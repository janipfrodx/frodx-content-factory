---
name: nika-update-writer
description: Napiše Nikino tedensko zgodbo o eni HubSpot novosti (Product updates) v eni dejavnosti - do 450 besed, eno besedilo za blog frodx.com (s povezavami na vir v besedilu) in LinkedIn (povezava v prvem komentarju) - v Nikinem slogu in z Nikino strokovno presojo kot hrbtenico. Uporabi vedno, ko Nika ali Igor reče "nova HubSpot zgodba", "zgodba o novosti", "kaj je novega v HubSpotu ta teden", "napiši za Niko", "tedenski update", "HubSpot novost za blog", prilepi seznam ali stran iz HubSpot Product updates ali vpraša, katero novost vzeti. Pokrije ves tok od izbora kandidatov in kartice novosti z URL-ji prek Nikinega vnosa (obrazec ali diktat) do zgodbe, razvrstitve trditev, kontrole s check.py in paketa za pregled. NE uporabljaj za Igorjeve kolumne (igor-column-writer), prevode (frodx-transcreation), newsletter (frodx-newsletter) ali Nikine maile in tickete (my-writing-style).
metadata:
  version: 1.1.1
  supersedes: 1.1.0
---

# Nika Update Writer

Tedenska zgodba o eni HubSpot novosti v eni dejavnosti, pod imenom Nike Bratuž (HubSpot team lead, glavna arhitektka HubSpot rešitev pri FrodX). Merodajen dokument je »Nikina tedenska zgodba o HubSpot novosti« v1.2 (1. 10. 2026); spremembe v1.1.0 so navedene na koncu in imajo prednost pred dokumentom, kjer se razlikujeta.

## Avtoriteta za glas

Glas določa Nika, ne ta skill. Če je v okolju nameščen Nikin skill `my-writing-style`, velja njegov razdelek »Blog« skupaj s »Splošno« in »Dejstva o produktu«; ob kakršni koli razliki z `references/glas.md` velja njen skill. `references/glas.md` je povzetek istih pravil za okolja, kjer njenega skilla ni, in hrani korekcijsko žetev. Ta skill skrbi za postopek: vir, presojo, trditve, kontrolo.

## Na čem stoji

HubSpotov seznam novosti je samo sprožilec. Vsebina zgodbe je Nikina odločitev: kaj zaradi novosti v procesu spremeni, kaj obdrži in zakaj, in kdaj bi se odločila drugače. Brez njenega vnosa skill napiše pravilno in generično besedilo, ki ga iz iste objave napiše vsak partner. Zato:

- **Presoja izhaja iz Nikinega vnosa ali iz njenih načel** (`references/nacela.md`). Paket navede, iz katerega načela; presoja brez načela in brez vnosa je skillova, se tako označi in rubrika jo omeji (`references/rubrika.md`). Brez Nikine potrditve ni objave.
- **Vsako dejstvo o produktu ima URL.** Kartica brez povezave je nepopolna; na blogu je povezava v besedilu ob trditvi, na LinkedInu v prvem komentarju.
- **Utemeljenost je pogoj, ne točke.** Vsaka trditev o tem, kaj se da narediti, sodi v eno od treh kategorij (`references/vir.md`). Nerazvrščena trditev ustavi paket.
- **En izhod, do 450 besed telesa, ciljno okoli 400.** Naslov in podnaslovi ne štejejo. Isto besedilo za blog in LinkedIn.
- **Kartica novosti nastane pred Nikinim vnosom**, da odloča na podlagi polnega opisa.
- **Prazno neobvezno polje pomeni izpustitev**, ne domneve.

## Delovni tok (en teden)

Nikin čas: okoli 10 minut za vnos ali 5 do 7 minut diktata, 15 do 20 za pregled. Vse teče v pogovoru; faza 2 (n8n) pride po pilotu petih zgodb.

### 1. Zajem
Nika prilepi **celotne strani** novosti iz Product updates ali članke iz Knowledge Base, ne samo seznama. Če je prilepila samo seznam, jo prosi za polne strani kandidatov; odrezan vir pomeni oznake namesto presoje.

### 2. Izbor
Tabela največ sedmih kandidatov: novost, hub, status, izdaja, vpliv, predlagana dejavnost (po `references/vertikale.md`). Kozmetika, preimenovanja menijev in »in development« brez opisa izpadejo. Če ni ničesar, do česar bi Nika lahko imela presojo, predlagaj, da teden izpade.

### 3. Kartica novosti
Za kandidate, ki jih Nika označi, napiši kartico po `references/vir.md`, z URL-jem za vsako vrstico, ki ga ima. **Samo iz vira, nič po spominu.** Če je na voljo spletni dostop, poišči javni članek v Knowledge Base ali javni zapis posodobitve in ga dodaj kot povezavo; partnerski blog je začasen vir z oznako `[PREVERI]`. Kartica gre Niki pred obrazcem.

### 4. Izbira
Nika izbere eno novost, eno dejavnost in eno dilemo (kje v tej dejavnosti novost trči ob proces, odgovornost ali rok). Dnevnik pokaže zaporedje dejavnosti, ne predpisuje ga.

### 5. Nikin vnos ali načela
Če Nika sodeluje v tem koraku, ji daj obrazec iz `references/obrazec.md` ali jo povabi, naj odgovore posname in prilepi transkript; iz transkripta izpolni obrazec in ji ga pokaži pred pisanjem. Če zgodba nastaja brez njenega vnosa (Nika dobi samo tekst v potrditev), presojo izpelji iz `references/nacela.md` in v paketu navedi načelo; dilemo, ki je nobeno načelo ne pokrije, zapiši kot vprašanje za Niko, ne kot njeno odločitev.

### 6. Zgodba
Preberi `my-writing-style` (če obstaja), `references/glas.md`, `references/struktura.md`, `references/nacela.md`, kartico, kartico dejavnosti in vnos. Iz transkripta ohrani Nikine povedi in besede, kjer zdržijo pravila; skill ureja, ne prepisuje. Primeri v `references/primeri/` kažejo obliko in register, ne vrstnega reda formul: uvodne formule iz zadnje zgodbe se ne ponovijo.

### 7. Kontrola
1. Zaženi `python3 scripts/check.py <datoteka> --blog --prev <mapa prejšnjih zgodb>` in `--linkedin`. Napaka ustavi paket; opozorilo zahteva odločitev.
2. Razvrsti vsako trditev o zmožnosti v kategorijo (nova / obstoječi HubSpot / Nikino priporočilo) in zapiši seznam s povezavo za vsako novo zmožnost. Nerazvrščena trditev ustavi paket.
3. Oceni po `references/rubrika.md`. Pod 9,0 revidiraj in povej, kaj manjka.

### 8. Paket
Vrni: zgodbo v obliki za blog (naslov, podnaslovi, povezave v besedilu, e-naslov) in za LinkedIn (brez njih, povezava v prvem komentarju), dva alternativna naslova, meta opis (140 do 160 znakov), seznam trditev po kategorijah s povezavami, seznam `[PREVERI: ...]`, oceno s pripombami, predlog seznama pogovorov, kjer je zgodba uporabna.

### 9. Pregled, distribucija, objava
Nika dobi tekst, ob trditvah povezave in eno vrstico, iz katerega načela izhaja presoja; odgovori s potrditvijo, popravkom ali zavrnitvijo. Vsak popravek gre v korekcijsko žetev (`glas.md`), vsak odgovor o presoji v `nacela.md`. Datum izbere človek. Dnevnik: `assets/dnevnik-template.md`.

## Vrata pred objavo
Brez objave, dokler ni Nikine presoje, dokler je katera koli trditev nerazvrščena, dejstvo o produktu brez povezave ali oznaka nerazrešena, in dokler check.py vrne napako.

## Korekcijska žetev
Vsak Nikin popravek, ki se ponovi dvakrat, postane pravilo v `references/glas.md`; če velja tudi zunaj teh zgodb, ga predlagaj Niki za njen `my-writing-style`. Prva žetev je iz njenih prepisov obeh primerov (5. 10. 2026).

## Reference
- `references/glas.md` - povzetek Nikinih pravil za blog in korekcijska žetev
- `references/struktura.md` - sestavine, oblika za blog in LinkedIn, formule, proračun besed
- `references/vir.md` - kartica novosti z URL-ji, tri kategorije trditev, pravila za dejstva o produktu
- `references/vertikale.md` - deset kartic dejavnosti in tabela tip novosti / dejavnost
- `references/nacela.md` - Nikina načela, iz katerih se izpelje presoja, s stopnjo potrditve
- `references/obrazec.md` - obrazec in diktat
- `references/rubrika.md` - pogoj utemeljenosti in pet postavk
- `references/primeri/` - Nikina prepisa obeh pilotnih zgodb in zgodba Deal Progression, ki jo je odobrila
- `scripts/check.py` - deterministična kontrola
- `assets/dnevnik-template.md` - dnevnik objav in odzivov

## Spremembe v1.1.1 (6. 10. 2026)
Dodana `nacela.md` s prvim izrecno potrjenim načelom in šestimi, potrjenimi z objavo; korak 5 ima pot brez Nikinega vnosa (presoja iz načel). Korekcijska žetev, runda 2: brez aforističnih povedi, ena misel na poved pri omejitvah, ugovor sme izreči imenovana vloga. Tretji primer: Deal Progression (odobren 6. 10.). `check.py` opozori na povedi do pet besed.

## Spremembe v1.1.0 (5. 10. 2026)
Glas preide na Nikin `my-writing-style`; začetna kartica glasu po Igorjevem opisu in Jepsonov lok sta umaknjena. Meja 450 besed telesa namesto 400, do štirje podnaslovi. Obvezne povezave na vir; »prvi komentar« velja samo za LinkedIn. Prepovedani retorični vložki in uvod s »Kljub« sta napaki v check.py; ponovljene formule iz prejšnje zgodbe so opozorilo. Primera sta Nikina prepisa z dvema popravkoma skilla (uvod, krediti), ki čakata njeno potrditev. Diktat je enakovreden obrazcu. Presoja, ki jo Nika samo potrdi, je v rubriki omejena na 2 od 3.
