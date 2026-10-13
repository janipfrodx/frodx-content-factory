# FrodX Content Factory

Cowork plugin z verigo skillov za produkcijo vsebine FrodX: kolumna za frodx.com s socialnimi objavami, naslovno sliko in meta podatki, ali novičnik FrodX GameChanger v treh jezikih (SI, HR, EN), ki konča kot osnutek v Newsletter Hubu, ali Nikino tedensko zgodbo o HubSpot novosti za blog in LinkedIn.

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

V Coworku napiši `/frodx-content-factory` in povej, kaj rabiš. Skill izbere pravo vejo: »nova kolumna« vodi skozi sedem korakov do objave na frodx.com, »pripravi novičnik« pa skozi šest korakov do osnutka v Newsletter Hubu. »Nova Nikina zgodba« pa od HubSpotovega tedenskega maila skozi Nikin pregled v Docu do razporeda na HubSpot blogu in LinkedInu. Med koraki čaka na tvojo potrditev.

## Lastništvo vsebine

Skilli `igor-column-writer`, `frodx-transcreation`, `frodx-key-visual`, `frodx-newsletter` in `nika-update-writer` so Igorjevi. Vendorirani so nespremenjeni - glej `plugins/content-factory/VENDOR.md`. Ne urejaj jih neposredno.

## Testi

    python3 -m pytest tests/ -v

## Različice

0.10.2: veja nika: zgodba gre po pisanju takoj v kritiko (GPT in Gemini); Igor jo prvič vidi po kritiki, en gate namesto dveh.

0.10.1: veja nika: najzgodnejši čas bloga je zdaj + 15 minut, zaokroženo na četrt ure (urnik.py); povezave na osnutke v koraku 11 v sporočilu pred vprašanjem; po razporedu LinkedIn po dejanskem stanju cf-nika-linkedin.

0.10.0: veja nika do konca po poti kolumne: transkreacija v EN in HR, meta podatki (kampanja, oznake, naslovnice), osnutki in razpored na HubSpot blogu prek cf-nika-publish, LinkedIn objava prek cf-nika-linkedin; nadaljevanje po osnutkih v novem chatu.

0.9.0: veja nika gre skozi kritiko do Nikinega pregleda v Docu »Nikine zgodbe« in nazaj, paket nika_story v1.1, kratka LinkedIn objava.

0.8.1: veja nika po suhem teku: korak 1 išče po zadevi in pošiljatelju v enem klicu, hub v tabeli je označen kot ocena; korak 2 jemlje izdajo, datum in navedke dobesedno iz besedila članka, ne iz povzetka.

0.8.0: veja nika (Nikina tedenska zgodba o HubSpot novosti): vendoriran nika-update-writer 1.1.1, init_run --veja nika, preverba paketa nika_story v1.0. Predaja cf-deliver-nika in aplikacija še nista zgrajeni.

0.7.1: HR novičnika napiše in pregleda GPT-6.1 Sol v n8n (cf-transkreacija-hr) po Igorjevem paketu; EN in kolumna nespremenjena.
