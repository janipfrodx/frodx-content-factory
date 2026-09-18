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
| `active` | `false`, `triggerCount: 0` |

**Kopije se ne aktivira nikoli.** Bot `FrodXContentPublisher` ima en sam registriran webhook in ta
pripada produkciji. Aktivacija kopije bi ga prevzela in Igorjeve potrditve gumbov bi obtičale.

Iz istega razloga se v testnih sporočilih **ne pritiska inline gumbov**: pritisk pošlje
`callback_query` na produkcijski webhook z `run_id`, ki ga produkcija ne pozna. Odobritev se
simulira z ročnim tekom od `Telegram Callback Trigger` s pripeto vsebino.

Pot webhooka se s produkcijo ne prekriva: n8n je ob podvojitvi dal nov UUID.
