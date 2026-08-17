# state.json - struktura stanja

`state.json` **je paket v gradnji**, ne vmesni format. Od koraka 1 ima že ciljno strukturo. Vsak korak zapolni svojo rezino. Korak 7 samo validira in pošlje.

## Paketni del

| Ključ | Kdo zapolni |
|---|---|
| `meta.title` | korak 2 (naslov, ki ga Igor izbere) |
| `meta.exported_at` | korak 1 (ustvarjanje), korak 7 (osveži) |
| `meta.version` | vedno `"1.1"` |
| `universal.slug` | korak 6 |
| `social_posts[]` | korak 2 |
| `languages.<jezik>.content` | korak 2 (sl), korak 3 (popravki sl), korak 4 (en, hr) |
| `languages.<jezik>.slug` | korak 6 |
| `languages.<jezik>.seo_title` | korak 6 |
| `languages.<jezik>.meta_description` | korak 6 |
| `languages.<jezik>.topic_cluster` | korak 6 |
| `languages.<jezik>.campaign_name` | korak 6 |
| `languages.<jezik>.tag_id/tag_name/tag_slug` | korak 6 |
| `languages.<jezik>.featured_image_alt` | korak 5 |

## `_run` - samo za verigo

Ta blok se pred pošiljanjem odstrani.

| Ključ | Pomen |
|---|---|
| `slug` | ime teka |
| `step` | zadnji dokončan korak, 1-7 |
| `status` | `awaiting_topic`, `awaiting_approval`, `in_progress`, `ready`, `sent` |
| `topic_source` | `{excel_row_id, picked_at}` iz koraka 1 |
| `brief` | `{topic, target_prompt, format, rationale}` iz koraka 1 |
| `approvals` | `{step2: <ISO čas>, ...}` - kdaj je Igor kaj potrdil |
| `critique_rounds` | koliko krogov kritike je bilo |
| `open_tasks` | odprte zadolžitve, ki jih veriga ni opravila - glej spodaj |
| `skill_versions` | verzije skillov, ki so tek obdelali |

### `open_tasks` - odprte zadolžitve

Seznam. Vsak element:

```json
{
  "what": "hrvaška različica ni šla skozi native pregled",
  "who": "native govorec hrvaščine",
  "created_at": "2026-08-15T12:00:00.000Z",
  "step": 4
}
```

Kdaj se zapiše: kadar korak nadaljuje, čeprav nekaj v njem ni bilo opravljeno, in je to zavestna odločitev človeka - ne kadar korak pade. Znana dva primera:

- **korak 1:** vrstica v vrsti tem ni bila označena kot `picked`, ker je konektor bralni (`frodx-topic-pick`, točka 8);
- **korak 4:** hrvaščina brez native pregleda, če Igor ali Jani odloči, da tek gre naprej.

Pravila:

- Zadolžitve **ne odstranjuj sam.** Odstrani jo šele, ko človek potrdi, da je opravljena.
- Ločena datoteka v mapi teka (npr. `HR-NATIVE-PREGLED-CAKA.md`) je dovoljena kot **dodatek** s podrobnostmi, nikoli kot nadomestilo - taka datoteka ne potuje s paketom in je nihče ne prebere.
- Korak 7 seznam prebere in **opozori**, a oddaje ne blokira (Janijeva odločitev 17. 8. 2026). Glej `frodx-publish-send/SKILL.md`.
- `_run` se pred pošiljanjem odstrani, zato `open_tasks` v aplikacijo nikoli ne gre. Namenjen je verigi in človeku, ne prejemniku paketa.

## Pravila

- Vsak korak prebere celoten `state.json`, spremeni samo svojo rezino in zapiše nazaj.
- Korak nikoli ne zapolni polj, ki pripadajo poznejšemu koraku, tudi če bi jih znal.
- Ob prekinitvi je `state.json` edini vir resnice. Kar ni v njem, se ni zgodilo.
- Slike ostanejo binarne v `images/`. V `state.json` gre samo alt tekst.
