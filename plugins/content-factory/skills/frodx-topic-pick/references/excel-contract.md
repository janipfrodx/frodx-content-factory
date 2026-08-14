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

## OPOZORILO: pisanje prek konektorja ni nujno mogoče

Preverjeno 14. 8. 2026: v Claude Code sta `sharepoint_update_file` in `sharepoint_upload_file` vrnila
`permission_error: This tool is not available` - konektor je bil na voljo samo za branje. Korak
"Pisanje" spodaj (nastavi `status = picked`) bo ob isti omejitvi padel. Če se to zgodi, povej Igorju,
naj vrstico označi ročno, in NE tiho preskoči označevanja - sicer bo ista tema izbrana še enkrat.

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
