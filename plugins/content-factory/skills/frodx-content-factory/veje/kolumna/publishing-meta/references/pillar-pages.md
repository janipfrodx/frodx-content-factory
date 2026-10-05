# Pillar strani po kampanji in jeziku

Kanonični vir za pillar povezavo, ki jo korak 6 (`frodx-publishing-meta`) zapiše kot zadnjo vrstico kolumne, in za gate v koraku 7 (`validate_package.py`).

- `campaign_name` je prepisan dobesedno iz `hubspot-taxonomy.md`, s predpono `Interest - `.
- `pillar_url` je absoluten (`https://frodx.com/...`), brez `?hsLang` in brez parametrov.
- Prazen `pillar_url` pomeni, da za ta par pillarja ni: kolumna v tem jeziku ostane brez pillar povezave, gate opozori, oddaje ne blokira.
- V tabelo gre samo URL, ki ga je potrdila Urša. Pillar URL-ja se ne izmišlja in ne prepisuje iz drugega jezika.
- Vsak par (kampanja, jezik) ima natanko eno vrstico, tudi kadar je URL prazen. Test `tests/test_pillar_pages.py` to preverja.

| campaign_name | lang | pillar_url |
|---|---|---|
| Interest - AI agenti in Voice AI | sl |  |
| Interest - AI agenti in Voice AI | en |  |
| Interest - AI agenti in Voice AI | hr |  |
| Interest - Prodaja in lead management | sl |  |
| Interest - Prodaja in lead management | en |  |
| Interest - Prodaja in lead management | hr |  |
| Interest - Programi zvestobe | sl |  |
| Interest - Programi zvestobe | en |  |
| Interest - Programi zvestobe | hr |  |
| Interest - Loyalty programs | sl |  |
| Interest - Loyalty programs | en |  |
| Interest - Loyalty programs | hr |  |
| Interest - HubSpot inbound marketing | sl |  |
| Interest - HubSpot inbound marketing | en |  |
| Interest - HubSpot inbound marketing | hr |  |
| Interest - Emarsys omnichannel marketing | sl |  |
| Interest - Emarsys omnichannel marketing | en |  |
| Interest - Emarsys omnichannel marketing | hr |  |
| Interest - E-commerce in retail | sl |  |
| Interest - E-commerce in retail | en |  |
| Interest - E-commerce in retail | hr |  |
| Interest - Digitalna transformacija | sl |  |
| Interest - Digitalna transformacija | en |  |
| Interest - Digitalna transformacija | hr |  |
| Interest - CX Customer Experience | sl |  |
| Interest - CX Customer Experience | en |  |
| Interest - CX Customer Experience | hr |  |
| Interest - AI Support & Service Hub | sl |  |
| Interest - AI Support & Service Hub | en |  |
| Interest - AI Support & Service Hub | hr |  |

## Znane vrzeli

- **Vse vrstice (5. 10. 2026):** čakajo na Uršino potrditev. Osnutek s podlago je v specu `docs/superpowers/specs/2026-10-05-pillar-povezave-design.md` (zunanji repo `Razvoj Content.Factory`), del 1.
