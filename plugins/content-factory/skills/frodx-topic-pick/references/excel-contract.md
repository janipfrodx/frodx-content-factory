# Excel s temami

Lokacija: **Janijev OneDrive, mapa `Content Factory`, datoteka `aeo-themes.xlsx`.**
Graph drive: `b!C6GvL-B8YUGFU1yFtNnX-srmZdzZI-ZJjHxZ5NKU8QtzFRkd4G3VRo_E5_L9PsI5`,
item: `01LR5CWKD447UVA2VK3ZHJQPZGOSEP2VP5`. Do nje se pride prek Microsoft 365 konektorja.

Prejšnji zapis je navajal `TEST473, Dokumenti/00 Projekti/FrodX/Content Factory/aeo-teme.xlsx`.
Ta pot ne obstaja - preverjeno 14. 8. 2026: knjižnica na TEST473 se imenuje `Dokumenti v skupni rabi`,
mapa je `00 Projekti/Frodx` (mali x) in podmape `Content Factory` v njej ni. Jani je datoteko ustvaril
v svojem OneDrive; zgornja pot je dejansko stanje.

Datoteko naj bi polnila ločena rutina `frodx-aeo-watch`, ki še ne obstaja. Do takrat se polni ročno
iz HubSpot AEO (Marketing -> AEO -> Recommendations -> zavihek "Owned content", vrstice s CHANNEL = Blog).
Ta skill jo samo bere in označuje izbrane vrstice.

## Pisanje prek konektorja NI mogoče - potrjeno v živem teku

Preverjeno 14. 8. 2026: v Claude Code sta `sharepoint_update_file` in `sharepoint_upload_file` vrnila
`permission_error: This tool is not available` - konektor je bil na voljo samo za branje.

Potrjeno v živem teku 14.-15. 8. 2026 v Cowork seji: Microsoft 365 konektor tam ponuja samo
`sharepoint_search`, `sharepoint_folder_search`, `read_resource`, `outlook_*`, `teams_*`, `get_me`,
`chat_message_search` - **nobenega orodja za pisanje.** Vrstica `aeo-001` je bila izbrana in obdelana
skozi vso verigo, v datoteki pa je ostala `status = new`, `run_slug` prazen.

**Zato velja do nadaljnjega:** korak "Pisanje" spodaj ni izvedljiv avtomatsko. Igorju (ali Janiju)
povej, naj vrstico označi ročno, in v `_run.topic_source.writeback_status` zapiši, da označevanje ni
bilo izvedeno, s kratkim razlogom. **Tega koraka nikoli ne preskoči tiho** - neoznačena vrstica pomeni,
da bo ista tema predlagana ob vsakem naslednjem teku in da vrsta tem trajno stoji.

### Dogovorjena rešitev (Janijeva odločitev 17. 8. 2026, izvedba še ni narejena)

Vrsta se preseli iz Excela v **n8n Data Table**, z dvema kratkima workflowoma:

1. **zapis priporočil** - ko Claude pobere priporočila iz HubSpot AEO, jih pošlje temu workflowu, ki jih shrani v Data Table (nadomesti ročno polnjenje Excela in bodočo rutino `frodx-aeo-watch`);
2. **označitev izbrane teme** - ko je tema izbrana, klic v ta workflow nastavi `status = picked` in `run_slug`.

Ob gradnji ne pozabi tretjega dela: **branje vrste**. n8n MCP zna v Data Table samo vstavljati vrstice
(`add_data_table_rows`); orodja za branje ali posodabljanje vrstic **ni** (preverjeno 17. 8. 2026 - na
voljo so le `search_data_tables`, `create_data_table`, `rename_data_table`,
`add/delete/rename_data_table_column`, `add_data_table_rows`). Branje in posodobitev vrstice morata
torej oba teči skozi workflow z Data Table vozliščem, ne prek MCP-ja neposredno.

Dokler to ne stoji, ta datoteka in ročno označevanje ostaneta v veljavi.

| Stolpec | Tip | Opis |
|---|---|---|
| `id` | text | unikaten ključ vrstice |
| `date_added` | date | kdaj je rutina temo zapisala |
| `topic` | text | predlagana tema |
| `target_prompt` | text | zgrešeni prompt, na katerega tema odgovarja |
| `channel` | text | LinkedIn / Reddit / Owned content |
| `format` | text | kolumna / vodnik / primerjava / FAQ |
| `source_recommendation` | text | dobesedno priporočilo iz AEO |
| `visibility_signal` | text | kvantitativni signal iz dashboarda, če obstaja |
| `status` | text | `new` / `picked` / `done` / `skipped` |
| `run_slug` | text | zapiše ta skill ob izbiri |

## Branje

Uporabi Microsoft 365 konektor. Upoštevaj samo vrstice s `status = new`.

## Pisanje

Ob izbiri nastavi izbrani vrstici `status = picked` in `run_slug = <slug teka>`. Ostalih vrstic ne spreminjaj.

## Prazna datoteka

Če ni nobene vrstice s `status = new`, povej Igorju, da novih tem ni, in končaj. Ne izmišljaj tem in ne posegaj po vrsticah s `status = done`.
