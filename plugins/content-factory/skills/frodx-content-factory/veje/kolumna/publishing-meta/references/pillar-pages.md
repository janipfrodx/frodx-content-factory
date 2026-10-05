# Pillar strani po kampanji in jeziku

Kanonični vir za pillar povezavo, ki jo korak 6 (`frodx-publishing-meta`) zapiše kot zadnjo vrstico kolumne, in za gate v koraku 7 (`validate_package.py`).

- `campaign_name` je prepisan dobesedno iz `hubspot-taxonomy.md`, s predpono `Interest - `.
- `pillar_url` je absoluten (`https://frodx.com/...`), brez `?hsLang` in brez parametrov.
- Prazen `pillar_url` pomeni, da za ta par pillarja ni: kolumna v tem jeziku ostane brez pillar povezave, gate opozori, oddaje ne blokira.
- V tabelo gre samo potrjen URL (potrdi Jani ali Urša), preverjen s curl: 200 brez preusmeritve. Pillar URL-ja se ne izmišlja in ne prepisuje iz drugega jezika.
- Vsak par (kampanja, jezik) ima natanko eno vrstico, tudi kadar je URL prazen. Test `tests/test_pillar_pages.py` to preverja.

| campaign_name | lang | pillar_url |
|---|---|---|
| Interest - AI agenti in Voice AI | sl | https://frodx.com/ai-agenti-voice-ai |
| Interest - AI agenti in Voice AI | en | https://frodx.com/en/ai-agenti-voice-ai |
| Interest - AI agenti in Voice AI | hr | https://frodx.com/hr/ai-agenti-voice-ai |
| Interest - Prodaja in lead management | sl | https://frodx.com/lead-management-prodajni-proces |
| Interest - Prodaja in lead management | en | https://frodx.com/en/lead-management-sales-process |
| Interest - Prodaja in lead management | hr | https://frodx.com/hr/lead-management-prodajni-proces |
| Interest - Programi zvestobe | sl | https://frodx.com/program-zvestobe-openloyalty |
| Interest - Programi zvestobe | en | https://frodx.com/en/loyalty-program-openloyalty |
| Interest - Programi zvestobe | hr | https://frodx.com/hr/program-lojalnosti-openloyalty |
| Interest - Loyalty programs | sl | https://frodx.com/program-zvestobe-openloyalty |
| Interest - Loyalty programs | en | https://frodx.com/en/loyalty-program-openloyalty |
| Interest - Loyalty programs | hr | https://frodx.com/hr/program-lojalnosti-openloyalty |
| Interest - HubSpot inbound marketing | sl | https://frodx.com/hubspot-inbound-marketing-vodic |
| Interest - HubSpot inbound marketing | en | https://frodx.com/en/hubspot-marketing-sales-guide |
| Interest - HubSpot inbound marketing | hr | https://frodx.com/hr/hubspot-inbound-marketing-vodic |
| Interest - Emarsys omnichannel marketing | sl | https://frodx.com/omnichannel-marketing-emarsys |
| Interest - Emarsys omnichannel marketing | en | https://frodx.com/en/omnichannel-marketing-emarsys |
| Interest - Emarsys omnichannel marketing | hr | https://frodx.com/hr/omnichannel-marketing-emarsys |
| Interest - E-commerce in retail | sl | https://frodx.com/ecommerce-strategija-shopify |
| Interest - E-commerce in retail | en | https://frodx.com/en/ecommerce-strategy-shopify |
| Interest - E-commerce in retail | hr | https://frodx.com/hr/ecommerce-strategija-shopify |
| Interest - Digitalna transformacija | sl | https://frodx.com/digitalna-transformacija-strategija |
| Interest - Digitalna transformacija | en | https://frodx.com/en/digital-transformation-strategy |
| Interest - Digitalna transformacija | hr | https://frodx.com/hr/digitalna-transformacija-strategija |
| Interest - CX Customer Experience | sl | https://frodx.com/customer-experience-cx-vodic |
| Interest - CX Customer Experience | en | https://frodx.com/en/customer-experience-cx-guide |
| Interest - CX Customer Experience | hr | https://frodx.com/hr/customer-experience-cx-vodic |
| Interest - AI Support & Service Hub | sl |  |
| Interest - AI Support & Service Hub | en |  |
| Interest - AI Support & Service Hub | hr |  |

## Znane vrzeli

- **Interest - AI Support & Service Hub (sl, en, hr):** pillar strani za to kampanjo ni. Kandidat `/resitve-za-stranke/omnichannel-kontaktni-center-in-hubspot` je storitvena stran, ne pillar (Jani, 5. 10. 2026). Vpiše se, ko pillar nastane.

## Izvor vrednosti

Potrdil Jani 5. 10. 2026, vsi URL-ji preverjeni s curl istega dne (200, brez preusmeritve). Šest kampanj je pillar povezave imelo v objavah februar-maj 2026; HubSpot inbound marketing in E-commerce in retail sta kandidata iz sitemapa s strukturo vodiča. Za AI agente je izbran `/ai-agenti-voice-ai` (vodič), ne `/ai-agenti-in-frodx` (storitvena stran).
