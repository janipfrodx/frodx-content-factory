# HubSpot taksonomija - kampanje in tagi

Kanonični vir za `campaign_name`, `tag_id`, `tag_name` in `tag_slug`.

## Kampanje

`campaign_name` sme biti **samo ena od teh desetih vrednosti**, prepisana dobesedno. To je edini seznam, ki ima GUID-e; kanonično živi v vozlišču `Extract Campaign GUID` v n8n workflowu `PROD 2 - FrodX Content Publishing Pipeline` (`3lK6pjOfOAa0BxDm`).

| campaign_name | hubspot_campaign_guid |
|---|---|
| Interest - AI agenti in Voice AI | 83ff3b4a-b380-4ed1-ab81-afb9a5704685 |
| Interest - Prodaja in lead management | aa75dc5d-6025-4d83-8870-0b86a9e1397d |
| Interest - Programi zvestobe | bdeff9f6-7f4a-4f7d-8d54-b8590f94b203 |
| Interest - Loyalty programs | 47259292-c3a6-4a9a-844d-cda7476a403a |
| Interest - HubSpot inbound marketing | fa865065-1306-4f2c-952c-ea67203dc015 |
| Interest - Emarsys omnichannel marketing | 6784cc33-24a0-4c0a-bf5f-bc3ca6feabfc |
| Interest - E-commerce in retail | 7549f0ea-1636-49fb-9c64-25b2f7629402 |
| Interest - Digitalna transformacija | 65e30f52-6459-4015-a244-af6d0663a52b |
| Interest - CX Customer Experience | d7d001a5-6f22-4cdb-9927-fd6862dfed3e |
| Interest - AI Support & Service Hub | fa41e141-7deb-412e-b72d-0f11c4e1249f |

Kampanja je ista za vse tri jezike.

**Kako izbrati:** beri vsebino članka, ne samo naslova. Izberi prevladujočo temo, ne obrobne omembe. Če se članek res enakovredno dotika dveh, izberi tisto, ki jo naslavlja hook.

## Tagi

Tag je odvisen od para (kampanja, jezik). Kjer para v tabeli ni, HubSpot taga danes nima - polja `tag_id`, `tag_name` in `tag_slug` za ta jezik ostanejo **prazna**. Tag ID-ja se nikoli ne izmišlja in ne izposoja iz drugega jezika.

| campaign_name | lang | tag_id | tag_name | tag_slug |
|---|---|---|---|---|
| Interest - AI agenti in Voice AI | sl | 191973014556 | AI agenti in voice AI | ai-agenti-in-voice-ai |
| Interest - AI agenti in Voice AI | en | 109945154884 | AI agents and voice AI | ai-agents-and-voice-ai |
| Interest - AI agenti in Voice AI | hr | 109945154882 | AI agents and voice AI | ai-agents-and-voice-ai |
| Interest - CX Customer Experience | sl | 207418884675 | CX Customer experience | cx-customer-experience |
| Interest - CX Customer Experience | en | 109945154887 | CX Customer Experience | cx-customer-experience |
| Interest - CX Customer Experience | hr | 106911727209 | CX Customer Experience | cx-customer-experience |
| Interest - Digitalna transformacija | sl | 209217440670 | Digitalna transformacija | digitalna-transformacija |
| Interest - E-commerce in retail | sl | 209217440615 | E-commerce in retail | e-commerce-in-retail |
| Interest - Emarsys omnichannel marketing | sl | 209208762680 | Emarsys omnichannel marketing | emarsys-omnichannel-marketing |
| Interest - Emarsys omnichannel marketing | en | 209208760856 | Emarsys omnichannel marketing | emarsys-omnichannel-marketing |
| Interest - HubSpot inbound marketing | sl | 209208760891 | HubSpot inbound marketing | hubspot-inbound-marketing |
| Interest - HubSpot inbound marketing | en | 209217440600 | HubSpot inbound marketing | hubspot-inbound-marketing |
| Interest - HubSpot inbound marketing | hr | 209208760896 | HubSpot inbound marketing | hubspot-inbound-marketing |
| Interest - Loyalty programs | en | 110457313465 | Loyalty programs | loyalty-programs |
| Interest - Loyalty programs | hr | 109978703639 | Loyalty programs | loyalty-programs |
| Interest - Programi zvestobe | sl | 207432704834 | Loyalty programi zvestobe | loyalty-programi-zvestobe |
| Interest - Prodaja in lead management | sl | 209208755742 | Prodaja in lead management | prodaja-in-lead-management |
| Interest - Prodaja in lead management | en | 110457313457 | Sales and Lead Management | sales-and-lead-management |
| Interest - Prodaja in lead management | hr | 109956645711 | Sales and Lead Management | sales-and-lead-management |

## Znane vrzeli

Te kombinacije danes taga nimajo. Objava v tem jeziku bo brez taga.

- Digitalna transformacija: en, hr
- E-commerce in retail: en, hr
- Programi zvestobe: en, hr (SL varianta je »Programi zvestobe«, EN/HR pa »Loyalty programs« - to sta ločeni kampanji, ne prevoda)
- Loyalty programs: sl
- Emarsys omnichannel marketing: hr
- AI Support & Service Hub: sl, en, hr

Če je vrzel moteča, se tag ustvari v HubSpotu in doda v to tabelo. Do takrat ostane prazno.

## Izvor podatkov

Kampanje in GUID-i: n8n `Extract Campaign GUID`. Tagi: `src/lib/tag-mapping.ts` v aplikaciji `frodx-content-app`, s popravkom predpone. Kampanje so bile v HubSpotu preimenovane iz `Blog -` v `Interest -`; `tag-mapping.ts` ima še stara imena, ta tabela nova.
