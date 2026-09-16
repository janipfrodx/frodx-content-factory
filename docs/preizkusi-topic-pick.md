# Ročni preizkusi: frodx-topic-pick

Ta skill je čista presoja, ne deterministična koda, zato ga `pytest` ne preverja. Preveriti ga je
treba v Coworku, na živih podatkih. Vsi trije preizkusi so brezplačni - vsi klici so bralni.

## 1. GREEN: predlog treh tem

1. V Coworku odpri sejo s pluginom `content-factory`.
2. Vprašaj: »Katero temo naj pišem naslednjo?«
3. Preveri:
   - [ ] predlagane so **največ tri** teme
   - [ ] vsaka nosi dobesedno besedilo prompta iz HubSpota, ne parafraze
   - [ ] vsaka nosi vidnost in podatek o citatih, in obe številki se ujemata z
         `get_aeo_metrics` odgovorom
   - [ ] kjer format ni `kolumna`, je izrecno povedano, da bo veriga naredila kolumno
   - [ ] nobena tema ni izmišljena in nobena številka ni zaokrožena »na občutek«

## 2. RED: prazna vrsta

1. Pokliči `get_data_table_rows` nad `AEO-Picks` in si zapiši, koliko vrstic je v tabeli.
2. Vprašaj isto vprašanje kot zgoraj, a v pogovoru povej, da so vsi prompti z vidnostjo pod 66 že
   obdelani.
3. Preveri:
   - [ ] skill pove, da novih tem ni, in konča
   - [ ] **ne** predlaga teme iz svojega znanja
   - [ ] ne predlaga prompta, ki je že v `AEO-Picks`

## 3. Zapis izbire

1. Izberi eno od predlaganih tem in pusti, da veriga ustvari tek.
2. Preveri:
   - [ ] v `AEO-Picks` je nova vrstica z `prompt_id`, `topic`, `run_slug` in `picked_at`
   - [ ] `_run.topic_source` v `state.json` nosi isti `hubspot_prompt_id`
   - [ ] če je zapis padel, je to povedano in je zadolžitev v `_run.open_tasks` - nikoli tiho
         preskočeno

Po preizkusu vrstico iz `AEO-Picks` zbriši v n8n vmesniku, če je bil tek samo preizkus.
