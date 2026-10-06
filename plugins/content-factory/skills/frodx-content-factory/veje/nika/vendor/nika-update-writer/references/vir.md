# Vir, kartica novosti in tri kategorije trditev

## Kartica novosti (nastane pred Nikinim vnosom)

Samo iz prilepljenega vira ali javne dokumentacije s povezavo. Nič po spominu.

```
Novost:       <ime v izvirniku>
Hub / orodje: <hub, orodje, podatkovni vir>
Status:       <private beta | public beta | live | in development | vir ne pove>
Izdaja:       <npr. Marketing Hub Professional, Enterprise | vse, tudi brezplačna | vir ne pove>
Datum:        <datum objave ali lansiranja; datum posodobitve članka ni datum lansiranja>
Cena:         <v enoti vira, npr. HubSpot krediti na enoto | ni posebne cene | vir ne pove>
Kaj omogoča:  <vsaka zmožnost, kot jo vir navaja; brez sklepanja>
Kje v UI:     <menijska pot iz vira | vir ne pove>
Poročila:     <samo metrike, ki jih vir navaja>
Vir ne pove:  <hramba; jeziki; pravice; pripis konverzij ...>
Povezave:     <URL za vsako vrstico zgoraj; Knowledge Base ima prednost pred partnerskim blogom>
```

»Kaj omogoča« je edini vir za trditve o zmožnostih. Kar ni v njej, ni v zgodbi.

## Pravila za dejstva o produktu
- Status točno in v pravem času: »v razvoju« pomeni prihodnjik (»bo lahko«), ne »zdaj« ali »odslej«; beta je beta.
- Paket in izdaja točno, kot v viru.
- Strošek v enoti, ki jo navaja vir (HubSpot krediti), ne preračunan v evre. Če vir enote ali števila ne navaja, zgodba pove samo, da se porabljajo krediti, in poveže na HubSpotov katalog; število ostane `[PREVERI]`.
- Kar vir ne pove, se zapiše kot vrzel (»kaj se z njo zgodi potem, dokumentacija ne pove«).
- Metrike poročil samo tiste, ki jih vir navaja.
- Partnerski blog ali povzetek je začasen vir; v kartici in v paketu dobi `[PREVERI: izvirni URL]`.

## Tri kategorije trditev

| Kategorija | Pogoj | Kako se zapiše v zgodbi |
|---|---|---|
| Nova zmožnost | V kartici, vrstica »Kaj omogoča«, s povezavo | Kot zmožnost novosti, povezava ob trditvi |
| Obstoječa zmožnost HubSpota | Potrjena v dokumentaciji ali s preizkusom | Kot nekaj, kar HubSpot »omogoča že dolgo« |
| Nikino procesno priporočilo | Njena odločitev, rutina, kombinacija zgornjih dveh s človeško odgovornostjo | V prvi osebi, kot njena odločitev, nikoli kot zmožnost orodja |

Trditev, ki ne sodi nikamor, ustavi paket.

## Anti-fabrikacija
- Iskanje po zgodovini ene stranke ni analiza vseh eskalacij. Spletno iskanje o podjetju ni iskanje o posamezniku.
- »Vidna 30 dni« ni »shranjena 30 dni«.
- Oznaka `[PREVERI: kaj natančno; kje]` organizira pregled, ne naredi trditve resnične. Zgodba z odprto oznako se ne objavi; oznako odstrani Nika.

## Kje se preverja
Knowledge Base (knowledge.hubspot.com), HubSpot Product Updates, katalog produktov in storitev (krediti), preizkus na peskovniku; DPO, kadar gre za osebne podatke.
