---
name: frodx-topic-pick
description: Pick the next FrodX content topic straight from the HubSpot AEO portal. Reads tracked prompts with their measured AI visibility plus the portal's content recommendations, ranks the gaps a column can actually close, and proposes at most three with reasoning so Igor can choose. Use when starting a content run without a given topic, or when Igor asks "kaj naj pišem", "katere teme imamo", "predlagaj temo". Records the chosen topic so it is never proposed twice.
metadata:
  version: 0.2.0
---

# Izbira teme

Iz HubSpot AEO portala pobere kandidate in Igorju predlaga največ tri.

## Postopek

1. Preberi `references/aeo-source.md`. Tam so klici, pomen polj in pogodba o tabeli zgodovine.
2. **Kandidati:** `get_aeo_metrics` z `include: ["PROMPTS"]`, `maxPrompts: 100`. Obdrži prompte z
   `visibility < 66`.
3. **Kontekst:** `manage_aeo_recommendations` LIST, `businessUnitId: 0`, `status: "NEW"`.
4. **Zgodovina:** `get_data_table_rows` nad `AEO-Picks`. Izloči vsak prompt, katerega `id` je že med
   `prompt_id`.
5. Če po tem ni nobenega kandidata, povej to in končaj. **Ne izmišljaj tem.**
6. Preberi `references/scoring.md` in rangiraj.
7. Predlagaj **največ tri** teme. Za vsako povej:
   - temo, zapisano kot stališče, ne kot kategorijo
   - `target_prompt` - dobesedno besedilo prompta iz HubSpota
   - vidnost in kaj pomeni (npr. »0 od treh asistentov nas omenja«)
   - koliko virov AI na to vprašanje navaja
   - priporočen format, in **če ta ni `kolumna`, izrecno povej, da bo veriga naredila kolumno** in
     kaj to pomeni za AEO učinek
   - če za ta prompt obstaja priporočilo za kanal, ki ni `OWNED_CONTENT`, to povej; kateri so, je v
     `references/aeo-source.md`
   - zakaj ravno ta, v enem ali dveh stavkih, in kaj govori proti njej
   - če je prompt iskalni po ponudnikih, povej, da ga kolumna premakne le posredno
8. Igor izbere. Če noče nobene, ponudi naslednje tri ali končaj.
9. Do te točke `state.json` še ne obstaja - tek ustvari dirigent (`frodx-content-factory`, razdelek
   »Zagon«) z `python3 scripts/init_run.py "<izbrana tema>" runs`, potem ko je tema znana. Ko ti
   dirigent pove pot do `state.json`, zapiši vanj:
   - `_run.brief` = `{topic, target_prompt, format, rationale}`
   - `_run.topic_source` = `{hubspot_prompt_id, hubspot_recommendation_id, visibility,
     citation_count, picked_at}`; `hubspot_recommendation_id` je `null`, kadar priporočila ni
   - `_run.step` = 1, `_run.status` = `in_progress`

   Dirigent koraka 1 ne postavlja pod ponovno potrditev - glej `frodx-content-factory/SKILL.md`,
   razdelek »Koraki«. Igorjeva izbira v točki 8 je gate za ta korak.
10. **Zapiši izbiro** v `AEO-Picks` z `add_data_table_rows`: `prompt_id`, `recommendation_id`
    (prazen niz, če ga ni), `topic`, `target_prompt`, `run_slug`, `picked_at`. Povej Igorju, da je
    zapisana.

    Če klic ne uspe, **tega ne zamolči**: povej, kaj se je zgodilo, in dodaj zadolžitev v
    `_run.open_tasks` (glej `frodx-content-factory/references/state-schema.md`). Nezapisana izbira
    pomeni, da bo ista tema spet med predlogi.

## Kaj ne delaš

- Ne predlagaš več kot treh tem. Če je dobrih kandidatov več, izberi tri najmočnejše in povej, da si
  ostale zadržal.
- Ne kličeš `START_ACTION` na priporočilu in ne ustvarjaš novih promptov. Glej `aeo-source.md`,
  razdelek »Česa ne kličeš«.
- Ne brišeš in ne spreminjaš vrstic v `AEO-Picks`. Tabela se samo dopolnjuje.
- Ne izbiraš namesto Igorja. Predlog ni odločitev.
- Ne pišeš vsebine. To je naloga naslednjega koraka.
