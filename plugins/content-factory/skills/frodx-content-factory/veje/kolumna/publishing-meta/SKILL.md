---
name: frodx-publishing-meta
description: Fill in all publishing metadata for a finished FrodX column - slugs, SEO titles, meta descriptions, topic clusters, the HubSpot campaign and the per-language tags, and the closing pillar page link in each language. Use after the text and image are final and before the package is sent, or when Igor asks for "meta podatki", "SEO", "kampanja", "tagi". Picks the campaign from a fixed list of ten and never invents HubSpot tag ids or pillar URLs.
metadata:
  version: 0.2.0
---

# Meta podatki za objavo

Zapolni vsa polja, ki jih HubSpot potrebuje in ki jih ne napiše nihče drug.

## Postopek

1. Preberi `state.json`. Če katerikoli jezik nima `content`, povej in končaj - meta podatkov ni mogoče delati na pol napisanem paketu.
2. Preberi `references/hubspot-taxonomy.md` v celoti. Vsebuje deset dovoljenih kampanj in tabelo tagov po parih (kampanja, jezik). Preberi tudi `references/pillar-pages.md` v celoti: pillar URL za vsak par (kampanja, jezik).
3. **Izberi kampanjo.** Beri vsebino kolumne, ne samo naslova. Ena kampanja za vse tri jezike, prepisana **dobesedno** z zgornjega seznama - vključno s predpono `Interest - `. Če se članek res enakovredno dotika dveh, izberi tisto, ki jo naslavlja hook. Če se članek ne ujema dobro z nobeno od desetih, izberi najbližjo in Igorju izrecno povej, da je bila izbira približek, ne pravi zadetek - nove kampanje ne izmišljaš, tudi če bi bolje pristajala.
4. **Nastavi tage.** Za vsak jezik poišči par (kampanja, jezik) v tabeli:
   - par obstaja → prepiši `tag_id`, `tag_name`, `tag_slug` dobesedno
   - para ni → vsa tri polja pustiš **prazna** (`""`)

   Tag ID-ja nikoli ne izmišljaš in ne prepisuješ iz drugega jezika, tudi če se zdi očitno, kaj bi moral biti. Ko končaš, povej Igorju, kateri jeziki so ostali brez taga in zakaj (sklic na razdelek »Znane vrzeli« v taksonomiji, če par tam nastopa).
5. **Pillar povezava.** Za vsak jezik poišči par (kampanja, jezik) v `references/pillar-pages.md`:
   - **URL obstaja** → v jeziku tega jezika napiši en stavek, ki pove, kaj bralec na pillar strani dobi v zvezi s temo te kolumne. Stavek je prilagojen članku, ne splošen. Vzorci iz objav pred junijem 2026:
     - »Več o tem, kako AI agenti premikajo vrednost iz CRM sistemov v sloj nad njimi.«
     - »Več o strategiji in implementaciji programa zvestobe z OpenLoyaltyjem.«
     - »See how lead scoring, nurturing and CRM handoff improve B2B sales.«
     - »Više o tome kako kroz omnichannel marketing graditi vlastite odnose s kupcima.«

     Pravila: en stavek; brez prodajnega poziva (»rezervirajte klic«, »pišite mi«); brez dolgega pomišljaja; brez dejstev ali številk, ki jih ni v kolumni; hrvaščina, ne srbščina.

     Vrstico zapiši kot **zadnjo vrstico** `languages.<jezik>.content`: prazna vrstica, nato `[stavek](pillar_url)`, URL dobesedno iz tabele. Stoji za podpisom in za morebitnim P.S. Če je zadnja vrstica že povezava na URL iz `pillar-pages.md` (ponovni zagon koraka 6), jo zamenjaj, ne dodaj druge.
   - **URL je prazen** → vrstice ne dodaš. Igorju povej, kateri jezik je ostal brez pillar povezave in zakaj (sklic na »Znane vrzeli« v `pillar-pages.md`). Pillar URL-ja ne izmišljaš in ne prepisuješ iz drugega jezika.

   Zakaj vrstica ne krši Igorjevega pravila: `vendor/igor-column-writer/references/structure.md` prepoveduje povezavo »preberite še« **v telesu kolumne**. Pillar vrstica stoji za podpisom, zunaj telesa, po dogovoru s sestanka z Andrejem in Niko (»pillar page link pod podpisom«). Vendoriranih datotek ne spreminjaš.
6. **Slug.** `universal.slug` iz slovenskega naslova (`meta.title`). Vsak jezik ima svoj `languages.<jezik>.slug` iz naslova/vsebine tega jezika. Pravila za oba:
   - male črke
   - šumnike in druge posebne znake prečrkuj (č→c, š→s, ž→z, ć→c, đ→dj) ali odstrani
   - vsako ločilo in presledek postane en vezaj `-`
   - brez vodilnih ali končnih vezajev, brez zaporednih vezajev
   - slug mora ustrezati vzorcu `^[a-z0-9]+(-[a-z0-9]+)*$` - to je trdna meja, gate iz koraka 7 ga preveri natanko po tem vzorcu
7. **`seo_title`.** Do 65 znakov (šteto z `len()`, presledki štejejo). Ni nujno enak naslovu kolumne - naslov kolumne dela za bralca, `seo_title` za iskalnik in AI motor. Naj vsebuje temo, ne ugank. Prazen `seo_title` gate zavrne.
8. **`meta_description`.** 140-160 znakov (šteto z `len()`), v jeziku tistega jezika. To je trdna meja, ne priporočilo - gate v koraku 7 pade, če je zunaj nje na katerikoli strani, tudi za en znak. Napiši, kaj bralec dobi, ne ponovi naslova. Preden zapišeš vrednost v `state.json`, dejansko preštej znake - ne ocenjuj na oko.
9. **`topic_cluster`.** 2-5 besed, v jeziku tistega jezika, tematska oznaka za članek (ni nujno enaka `campaign_name`). Če za `topic_cluster` v besedilu ni podlage, to povej Igorju namesto da si izmisliš oznako.
10. Zapiši vse v `state.json`, nastavi `_run.step` = 6, `_run.status` = `awaiting_approval`.
11. Pokaži Igorju tabelo: za vsak jezik naslov (`seo_title`), opis (`meta_description`) z dolžino v znakih, slug, kampanjo in tag ter pillar URL in stavek (ali »brez pillarja«). Dolžine izpiši, da vidi, kje je tesno.

## Kaj ne delaš

- Ne izmišljaš dejstev, ki jih v besedilu ni. Če za `topic_cluster` ni podlage, povej.
- Ne izbereš kampanje, ki je ni na seznamu desetih, tudi če bi se bolje prilegala. Če nobena ne paše, izberi najbližjo in to izrecno povej Igorju.
- Ne izmišljaš pillar URL-jev. Kjer je v `pillar-pages.md` prazno, vrstice ni.
- Ne pišeš `featured_image_alt` - to je delo koraka 5.
- Ne nastavljaš `publish_at`. Datum izbere Igor v aplikaciji.

## Zakaj to dela Claude in ne aplikacija

Do zdaj je ta polja pisal Gemini v aplikaciji na podlagi prvih 4000 znakov besedila. Ti imaš cel članek, kontekst briefa in ciljani prompt iz koraka 1. Ob uvedbi tega skilla se AI obogatitev v aplikaciji izklopi, da polj ne pišeta dva sistema.
