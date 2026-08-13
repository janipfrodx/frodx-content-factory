# FrodX Content Factory

Cowork plugin z verigo skillov za produkcijo kolumn in socialnih objav.

## Namestitev v Claude Cowork

1. *Customize → Plugins → Add marketplace*
2. Vnesi `https://github.com/janipfrodx/frodx-content-factory`
3. Namesti plugin **content-factory**
4. Ob spremembi klikni *Update* na marketplaceu

## Uporaba

V Coworku napiši `/frodx-content-factory` ali »nova kolumna«. Skill te vodi skozi sedem korakov in med njimi čaka na tvojo potrditev.

## Lastništvo vsebine

Skilli `igor-column-writer`, `frodx-transcreation`, `frodx-key-visual` in `frodx-newsletter` so Igorjevi. Vendorirani so nespremenjeni - glej `plugins/content-factory/VENDOR.md`. Ne urejaj jih neposredno.

## Testi

    python3 -m pytest tests/ -v
