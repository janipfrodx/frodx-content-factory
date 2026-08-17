# FrodX Content Factory

Cowork plugin z verigo skillov za produkcijo kolumn in socialnih objav.

## Namestitev v Claude Cowork

1. *Customize → Plugins → Add marketplace*
2. Vnesi `https://github.com/janipfrodx/frodx-content-factory`
3. Namesti plugin **content-factory**
4. Ob spremembi klikni *Update* na marketplaceu

### Pred vsakim tekom: preveri, da Cowork ni na stari kopiji

Cowork dela s **sinhronizirano kopijo** plugina (`/root/.claude/plugins/synced/content-factory/…`), ne s tem repom. Popravek v repu pride v Cowork šele po `git push` **in** kliku *Update*.

To ni teoretično. V teku 14.-15. 8. 2026 je Cowork iskal Excel s temami na poti `TEST473 → Dokumenti/00 Projekti/FrodX/Content Factory/aeo-teme.xlsx` in ga ni našel - pot je bila v repu **že popravljena** (commit `7afdda6`, 14. 8.), a sinhronizirana kopija je bila starejša. Napaka je bila zato prijavljena kot vrzel v skillu, čeprav je bila v resnici zastarela kopija.

Urejanje datotek v `synced/` ne spremeni ničesar trajno - naslednji *Update* jih povozi.

## Uporaba

V Coworku napiši `/frodx-content-factory` ali »nova kolumna«. Skill te vodi skozi sedem korakov in med njimi čaka na tvojo potrditev.

## Lastništvo vsebine

Skilli `igor-column-writer`, `frodx-transcreation`, `frodx-key-visual` in `frodx-newsletter` so Igorjevi. Vendorirani so nespremenjeni - glej `plugins/content-factory/VENDOR.md`. Ne urejaj jih neposredno.

## Testi

    python3 -m pytest tests/ -v
