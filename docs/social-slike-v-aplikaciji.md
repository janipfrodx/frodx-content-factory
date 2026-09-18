# Socialne slike v aplikaciji

Stanje 18. 9. 2026. Spremembe v `frodx-content-app` za paket socialnih slik.

## Zakaj je bila sprememba nujna

`social_posts[]` sta do zdaj potovala skozi dve ozki grli, ki sta neznana polja **tiho** zavrgli:

1. zod shema v `src/lib/content-schema.ts` - neznanih ključev ne zavrne, odstrani jih;
2. `dispatchToN8n` v `src/lib/content.functions.ts` - socialne objave izrecno preslika na
   `{text, publish_date}`.

Paket bi torej prestal gate v Coworku in prispel v aplikacijo brez slik, brez ene same napake.

## Kaj je spremenjeno

| Datoteka | Sprememba |
|---|---|
| `src/lib/content-schema.ts` | `image_url` in `image_alt`, oba `z.string().default("")` |
| `src/lib/content.functions.ts` | `dispatchToN8n` preslika obe polji naprej |
| urejevalnik osnutka (`Step3EditForm.tsx`) | pogojni predogled slike in urejljiv alt tekst |
| `Step4Schedule.tsx` | ni bila v prvotnem seznamu treh datotek, a jo je Lovable agent spremenil - brez tega bi bila polji izbrisani tu, tik pred `dispatchToN8n`, ker ta korak `social_posts` v celoti sestavi na novo za razporejanje. Sprememba je posledica tipa, ki ga `ContentJson` po `.default("")` zahteva (`image_url`/`image_alt` sta v izhodnem tipu obvezna), zato je bila nujna, ne le priročna. |

## Zakaj sta polji v aplikaciji neobvezni, v gateu pa obvezni

Ista zod shema streže dvema potema: strojnemu vhodu iz Content Factory (ki sliki vedno ima) in
ročnemu docx uvozu (ki ju nima in ju nikoli ne bo imel). Če bi bili polji v aplikaciji obvezni, bi
ročni uvoz nehal delati.

Zahtevo nosi `validate_package.py` v Coworku, ker velja samo za pot, ki gre skozi verigo.

## Preverjeno v predogledu

Obstoječi osnutek "HubSpot ali Salesforce? Napačno vprašanje" (brez `image_url` na nobeni od treh
socialnih objav) se v Step 3 urejevalniku prikaže enako kot pred spremembo - brez slike, brez
praznega okvirja. To potrjuje, da `.default("")` deluje kot pričakovano za stare osnutke.

## Kaj ni bilo objavljeno

Sprememba je preverjena samo v Lovable predogledu (`preview_url`). Objava (Publish) v aplikaciji
ni bila sprožena - to je Janijevo dejanje.
