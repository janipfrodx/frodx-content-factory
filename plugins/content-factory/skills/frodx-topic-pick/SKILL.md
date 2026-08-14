---
name: frodx-topic-pick
description: Pick the next FrodX content topic from the AEO topic queue on OneDrive. Reads the aeo-themes.xlsx sheet, ranks the open topics by how much they would move AI visibility, and proposes at most three with reasoning so Igor can choose. Use when starting a content run without a given topic, or when Igor asks "kaj naj pišem", "katere teme imamo", "predlagaj temo". Writes the chosen topic into the run state and marks the row as picked.
metadata:
  version: 0.1.0
---

# Izbira teme

Iz vrste tem na SharePointu izbere kandidate in Igorju predlaga največ tri.

## Postopek

1. Preberi `references/excel-contract.md` za lokacijo in stolpce.
2. Preberi Excel prek Microsoft 365 konektorja. Vzemi samo vrstice s `status = new`.
3. Če ni nobene, povej to in končaj. **Ne izmišljaj tem.**
4. Preberi `references/scoring.md` in rangiraj.
5. Predlagaj **največ tri** teme. Za vsako povej:
   - temo, zapisano kot pogled, ne kot kategorijo
   - `target_prompt`, ki ga zapira
   - priporočen format
   - zakaj ravno ta, v enem ali dveh stavkih
   - kaj govori proti njej, če kaj govori
6. Igor izbere. Če noče nobene, ponudi naslednje tri ali končaj.
7. Do te točke `state.json` še ne obstaja - tek ustvari dirigent (`frodx-content-factory`, razdelek »Zagon«) z `python3 scripts/init_run.py "<izbrana tema>" runs`, potem ko je tema znana. Ko dirigent to naredi in ti pove pot do `state.json`, zapiši vanj:
   - `_run.brief` = `{topic, target_prompt, format, rationale}`
   - `_run.topic_source` = `{excel_row_id, picked_at}` - `excel_row_id` je vrednost stolpca `id` izbrane vrstice, `picked_at` je ISO čas Igorjeve izbire
   - `_run.step` = 1, `_run.status` = `in_progress`

   Dirigent koraka 1 ne postavlja pod ponovno potrditev - glej `frodx-content-factory/SKILL.md`, razdelek »Koraki«, kjer je ta izjema izrecno zapisana. Igorjeva izbira v točki 6 zgoraj je gate za ta korak, zato `_run.status` pojdi naravnost na `in_progress`, ne na `awaiting_approval`.
8. V Excelu nastavi izbrani vrstici `status = picked` in `run_slug` na slug teka (isti slug, ki ga je izpisal `init_run.py`).

## Kaj ne delaš

- Ne predlagaš več kot treh tem. Če je dobrih kandidatov več, izberi tri najmočnejše in povej, da si ostale zadržal.
- Ne spreminjaš vrstic, ki jih Igor ni izbral.
- Ne izbiraš namesto Igorja. Predlog ni odločitev.
- Ne pišeš vsebine. To je naloga naslednjega koraka.
