# LinkedIn: slika na objavi, link v prvem komentarju

Delo poteka v kopiji `ccAcIxMOEKlWkbg7` (`PROD - FrodX Content Publishing Pipeline copy`).
Produkcija je `3lK6pjOfOAa0BxDm` (`PROD - FrodX Content Publishing Pipeline`) - **ID je merodajen**,
starejši dokumenti v tem repozitoriju jo imenujejo »PROD 2«.

## Varnostno stanje kopije

Urejeno 18. 9. 2026. Pred tem je bila kopija čist klon produkcije in bi ob aktivaciji objavljala na
prave račune.

| Kaj | Stanje |
|---|---|
| `Daily 7:30 Publish Check` | onemogočen |
| 26 Telegram vozlišč | `chatId` preusmerjen z `-5299932503` (Igorjeva skupina) na `8773374711` (zasebni chat Jani + bot) |
| `Telegram Callback Trigger` | ostaja omogočen, ker se prek njega poganja ročni test |
| `Post LinkedIn Company` | onemogočen do živega testa |
| `LI Setup - Create Post via HTTP` | onemogočen do živega testa |
| `Facebook Graph API` | onemogočen - ta načrt Facebooka ne spreminja |
| data tabele | prevezane na `TEST-FrodX-Pipeline`, `TEST-FrodX-Social-Posts`, `TEST-FrodX-Idempotency` |
| 14 HubSpot pisalnih vozlišč (spodaj) | onemogočena |
| `active` | `false`, `triggerCount: 0` |

**Kopije se ne aktivira nikoli.** Bot `FrodXContentPublisher` ima en sam registriran webhook in ta
pripada produkciji. Aktivacija kopije bi ga prevzela in Igorjeve potrditve gumbov bi obtičale.

Iz istega razloga se v testnih sporočilih **ne pritiska inline gumbov**: pritisk pošlje
`callback_query` na produkcijski webhook z `run_id`, ki ga produkcija ne pozna. Odobritev se
simulira z ročnim tekom od `Telegram Callback Trigger` s pripeto vsebino.

Pot webhooka se s produkcijo ne prekriva: n8n je ob podvojitvi dal nov UUID.

## HubSpot: onemogočena pisalna vozlišča (dopolnjeno 18. 9. 2026)

Neodvisen pregled je odkril, da so poleg LinkedIn/Facebook v kopiji ostala omogočena tudi vsa
vozlišča, ki pišejo v pravi produkcijski HubSpot portal prek `api.hubapi.com`. Isti razred tveganja
kot objavna vozlišča - poln ročni tek bi na produkcijskem portalu ustvaril, planiral ali izbrisal
resnične blog zapise. Vseh 14 je zdaj `disabled: true`:

| Vozlišče | Endpoint | Metoda |
|---|---|---|
| `Schedule SL HubSpot Post` | `/cms/blogs/2026-03/posts/schedule` | POST |
| `Schedule EN HubSpot Post` | `/cms/blogs/2026-03/posts/schedule` | POST |
| `Schedule HR HubSpot Post` | `/cms/blogs/2026-03/posts/schedule` | POST |
| `Create SL HubSpot Draft` | `/cms/v3/blogs/posts` | POST |
| `Create EN HubSpot Variation` | `/cms/v3/blogs/posts/multi-language/create-language-variation` | POST |
| `Update EN HubSpot Variation` | `/cms/v3/blogs/posts/{id}` | PATCH |
| `Create HR HubSpot Variation` | `/cms/v3/blogs/posts/multi-language/create-language-variation` | POST |
| `Update HR HubSpot Variation` | `/cms/v3/blogs/posts/{id}` | PATCH |
| `Upload Featured Image to HubSpot` | `/files/v3/files` | POST |
| `Update SL with InstantFeedback` | `/cms/v3/blogs/posts/{id}` | PATCH |
| `Update HR with InstantFeedback` | `/cms/v3/blogs/posts/{id}` | PATCH |
| `Delete HubSpot Drafts (SL)` | `/cms/v3/blogs/posts/{id}` | DELETE |
| `Delete HubSpot Drafts (EN)` | `/cms/v3/blogs/posts/{id}` | DELETE |
| `Delete HubSpot Drafts (HR)` | `/cms/v3/blogs/posts/{id}` | DELETE |

`Download Featured Image` (GET, dinamični URL) ostaja omogočen - samo bere/prenaša datoteko, ne
spreminja stanja na noben produkcijski sistem.

Preverjenih je bilo vseh 17 vozlišč tipa `httpRequest` v kopiji; edina gostitelja sta
`api.hubapi.com` in `api.linkedin.com` (slednji je onemogočen že v prvotni varnostni pripravi).
Noben drug zunanji ponudnik v kopiji ne piše v produkcijo.

**Posledica za poznejše naloge:** ker so vsa HubSpot pisalna vozlišča onemogočena, poln ročni tek od
`Telegram Callback Trigger` naprej ne bo dobil pravega odgovora HubSpot API-ja na tej točki (ne bo
ustvarjenega osnutka, ne bo `id`-ja objave, ne bo planiranja). Izhod teh vozlišč je treba simulirati
s pripeto vsebino (`prepare_workflow_pin_data`), enako kot je za LinkedIn/Facebook objavo že
predvideno v prejšnjem razdelku - sicer se veriga po teh vozliščih prekine, ker naslednji koraki
pričakujejo polja iz HubSpot odgovora (npr. `id` objave).
