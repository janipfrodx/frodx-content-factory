# Excel s temami

Lokacija: SharePoint spletišče TEST473, `Dokumenti/00 Projekti/FrodX/Content Factory/aeo-teme.xlsx`.

Datoteko polni ločena rutina `frodx-aeo-watch`. Ta skill jo samo bere in označuje izbrane vrstice.

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
