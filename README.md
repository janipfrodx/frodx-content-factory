# FrodX Content Factory

Cowork plugin z verigo skillov za produkcijo kolumn in socialnih objav.

## Namestitev v Claude Cowork

1. *Customize → Plugins → Add marketplace*
2. Vnesi `https://github.com/janipfrodx/frodx-content-factory`
3. Namesti plugin **content-factory**
4. Ob spremembi klikni *Update* na marketplaceu

### Pred vsakim tekom: preveri, da Cowork ni na stari kopiji

Cowork dela s **sinhronizirano kopijo** plugina (`/root/.claude/plugins/synced/content-factory/…`), ne s tem repom. Popravek v repu pride v Cowork šele po `git push` **in** kliku *Update*.

To ni teoretično. V teku 14.-15. 8. 2026 je Cowork iskal vir tem na poti, ki je bila v repu **že popravljena** (commit `7afdda6`, 14. 8.), a sinhronizirana kopija je bila starejša. Napaka je bila zato prijavljena kot vrzel v skillu, čeprav je bila v resnici zastarela kopija. Vir tem je od 16. 9. 2026 HubSpot AEO in ne datoteka, a pouk o zastareli kopiji velja naprej.

Urejanje datotek v `synced/` ne spremeni ničesar trajno - naslednji *Update* jih povozi.

### Pri vsaki spremembi: dvigni verzijo

Cowork gumb *Update* je omogočen samo, če se `version` v `.claude-plugin/marketplace.json` in
`plugins/content-factory/.claude-plugin/plugin.json` razlikuje od nameščene. Če ostane enaka, je
gumb siv, čeprav je v repu novejša koda. Pri vsakem commitu, ki spremeni kaj v `plugins/`, dvigni
obe verziji za isto številko.

## Uporaba

V Coworku napiši `/frodx-content-factory` ali »nova kolumna«. Skill te vodi skozi sedem korakov in med njimi čaka na tvojo potrditev.

## Lastništvo vsebine

Skilli `igor-column-writer`, `frodx-transcreation`, `frodx-key-visual` in `frodx-newsletter` so Igorjevi. Vendorirani so nespremenjeni - glej `plugins/content-factory/VENDOR.md`. Ne urejaj jih neposredno.

## Testi

    python3 -m pytest tests/ -v
