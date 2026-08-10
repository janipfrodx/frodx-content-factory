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
| `skill_versions` | verzije skillov, ki so tek obdelali |

## Pravila

- Vsak korak prebere celoten `state.json`, spremeni samo svojo rezino in zapiše nazaj.
- Korak nikoli ne zapolni polj, ki pripadajo poznejšemu koraku, tudi če bi jih znal.
- Ob prekinitvi je `state.json` edini vir resnice. Kar ni v njem, se ni zgodilo.
- Slike ostanejo binarne v `images/`. V `state.json` gre samo alt tekst.
