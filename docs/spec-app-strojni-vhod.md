# Specifikacija: strojni vhod v aplikacijo `frodx-content-app`

Stanje 17. 8. 2026. Namenjeno izvedbi v Lovableu. Nič od tega še ni zgrajeno.

Aplikacija: `frodx-content-app`, Lovable projekt `90b43584-6783-4de3-aca2-e95435c76de7`,
Supabase projekt `umvjwjzdrtamfrcqhopa`.

## Stanje 17. 8. 2026

Kje smo, da se ta specifikacija bere v pravem kontekstu.

**Veriga skillov stoji.** Naloge 1 do 11 iz načrta so zaključene. Po prvem živem teku 14. do 15. 8.
so popravljene napake iz poročila (kritika, izbira teme, `open_tasks` kot opozorilo, terminologija).
63 testov prehaja.

**Sedem commitov ni pushanih.** Dokler ne gre `git push` in klik *Update* na marketplaceu, Cowork
teče po stari sinhronizirani kopiji plugina. To je v prvem teku že enkrat povzročilo lažno prijavo
napake.

**Dostavna pot je razjasnjena in odločena.** Aplikacija ostane v verigi. Podrobno v
`docs/popravki-po-teku-2026-08-15.md`, razdelek »Dopolnitev 17. 8. 2026«. Na kratko:

- `PROD 2 - FrodX Content Publishing Pipeline` (`3lK6pjOfOAa0BxDm`) je že celotna dostavna pot do
  HubSpota, Telegrama in socialnih omrežij. **Ostane v produkciji nedotaknjen**, dokler nov ni
  pripravljen za produkcijo (Janijeva odločitev).
- Slike ne sprejema kot datoteko, ampak kot **`featured_image_url`**. Base64 v `frodx-publish-send`
  je bil rešitev za problem, ki ga dostavna pot nikoli ni imela.
- Aplikacija že zna naložiti sliko in narediti javni URL, validirati paket, in podpisati ter oddati
  na webhook. Manjka samo strojni vhod, kar je predmet tega dokumenta.
- Aplikacija se ne podvaja s Telegramom: aplikacija je **pred** `frodx-publish`, Telegram potrjuje
  osnutke **za njim**.

**Odprto in na kom je.**

| kaj | na kom | stanje |
| --- | --- | --- |
| `git push` + *Update* na marketplaceu | Jani | čaka njegovo dovoljenje |
| host `umvjwjzdrtamfrcqhopa.supabase.co` na egress allowlist | Andrej (lastnik organizacije) | **prošnja poslana 17. 8. 2026**, čaka odgovor |
| gradnja dveh poti in tabele v aplikaciji | ni dodeljeno | specifikacija je ta dokument, gradnja še ni začeta |
| dopolnitev `cf-generate-image` in nov `cf-deliver-draft` | ni dodeljeno | glej razdelek »Kaj mora narediti n8n« |
| popravek `frodx-image-run` in `frodx-publish-send` | ni dodeljeno | šele ko je pot do slik odločena |
| RLS Supabase projekta aplikacije | ni preverjeno | do projekta ni dostopa prek Supabase konektorja, ker ga upravlja Lovable |
| podpis se v `PROD 2` doda dvakrat | odprto od prej | ne dotikamo se, ker je workflow v produkciji |

## Zakaj

Aplikacija danes vse, kar potrebuje veriga, **že zna**: naloži sliko v `content-images` in vrne javni
URL (`uploadFeaturedImage`), validira paket (`contentJsonSchema`), Igor v čarovniku nastavi datum
objave bloga in datume socialnih objav, nato `dispatchToN8n` podpiše HMAC in odda na
`https://frodxai.app.n8n.cloud/webhook/frodx-publish`.

Manjka eno: vse to so `createServerFn` z `requireSupabaseAuth`, torej jih kliče **prijavljen
brskalnik**. Klicalca brez seje ni. Zato Igor danes datoteke nalaga ročno.

Ta specifikacija doda strojni vhod: dve ozki HTTP poti, ki jih kliče n8n, in tabelo osnutkov, iz
katere se čarovnik odpre na koraku 3. Vse ostalo ostane nedotaknjeno.

Ozadje o tem, zakaj slika ne more potovati skozi Clauda in kako je zasnovana celotna pot, je v
`docs/popravki-po-teku-2026-08-15.md`, razdelek »Dopolnitev 17. 8. 2026«.

## Kaj se ne spremeni

- `dispatchToN8n` - podpisovanje in oddaja delujeta pravilno, se ne dotika
- `Step3EditForm`, `Step4Schedule`, `Step5Confirm` - logika ostane
- `Step1Upload`, `Step2Processing` - ročna pot prek docxa ostane na voljo
- `contentJsonSchema` in `languageSchema` v `src/lib/content-schema.ts` - oblika se ne spreminja
- n8n workflow `PROD 2 - FrodX Content Publishing Pipeline` (`3lK6pjOfOAa0BxDm`) - ostane v
  produkciji, dokler ni nov pripravljen za produkcijo

## Način izvedbe

Ti dve poti **ne smeta biti `createServerFn`.** `src/lib/api/example.functions.ts` pravi, da gre
strežniška logika prek `createServerFn` namesto prek Supabase Edge Functions, in za vse, kar kliče
brskalnik, to velja naprej. Tu je klicalec n8n brez seje in brez odjemalskega bundla, zato potrebuje
navadno HTTP pot - strežniško pot TanStack Starta v `src/routes/api/`. Mehanizem naj izbere izvajalec
po različici, ki je v projektu; zahteva je le, da je pot dosegljiva z golim `POST` iz zunanjega
sistema.

Nalaganje v shrambo naj **ponovno uporabi obstoječo logiko** iz `uploadFeaturedImage`
(`src/lib/content.functions.ts`): `supabaseAdmin.storage.from("content-images").upload(...)` z
imenom `${crypto.randomUUID()}.${ext}`, nato `getPublicUrl`. Ne piši nove.

## Avtentikacija

Nova skrivnost v Lovable Cloud → Secrets: **`INGEST_API_KEY`**. Ista vrednost se shrani v n8n kot
credential tipa Header Auth.

Obe poti zahtevata glavo:

```
x-api-key: <INGEST_API_KEY>
```

- primerjava naj bo konstantnočasovna (`crypto.timingSafeEqual` nad enako dolgima bufferjema)
- manjkajoča ali napačna glava → `401` z telesom `{"error":"unauthorized"}`
- če `INGEST_API_KEY` v okolju ni nastavljen, pot vrne `503` in v dnevnik zapiše razlog; **nikoli ne
  sme pasti v način brez preverjanja**

Brez seje Supabase, brez `requireSupabaseAuth`. Pisanje gre prek `supabaseAdmin` (`service_role`),
kar je isti vzorec kot v obstoječih funkcijah.

## Pot 1: `POST /api/images`

Naloži eno sliko in vrne javni URL. Kliče se **dvakrat na tek**, za obe kandidatki, še preden je
izbrana - Claude potrebuje URL-ja, da sliki sploh pogleda in se odloči.

Telo (`application/json`):

```json
{
  "image_base64": "<gola base64 vsebina, brez data: predpone>",
  "filename": "openai.png",
  "mime_type": "image/png"
}
```

Validacija (z `zod`, enake meje kot obstoječi `uploadFeaturedImage`):

| polje | pravilo |
| --- | --- |
| `image_base64` | `min(1).max(14_000_000)` |
| `filename` | `min(1).max(255)` |
| `mime_type` | `^image/(png\|jpe?g\|webp\|gif\|avif)$` |

Odgovori:

| status | telo | kdaj |
| --- | --- | --- |
| `200` | `{"url": "...", "path": "<uuid>.png"}` | naloženo |
| `400` | `{"error":"validation","detail":[...]}` | telo ne ustreza shemi |
| `401` | `{"error":"unauthorized"}` | ključ manjka ali je napačen |
| `502` | `{"error":"storage","detail":"<sporočilo>"}` | shramba je zavrnila nalaganje |

Zavržena kandidatka ostane v bucketu. To je namenoma: je dokaz, med čim se je izbiralo. Brisanja ta
specifikacija ne predpisuje.

## Pot 2: `POST /api/drafts`

Ustvari osnutek iz gotovega paketa. Slika je takrat že naložena, zato se tu prenaša **samo njen URL**.

Telo (`application/json`):

```json
{
  "content": { "meta": {}, "universal": {}, "social_posts": [], "languages": {} },
  "featured_image_url": "https://umvjwjzdrtamfrcqhopa.supabase.co/storage/v1/object/public/content-images/<uuid>.png",
  "run_slug": "2026-08-17-zakaj-lojalnostni-programi-kaznujejo-zveste",
  "source": "content-factory"
}
```

Validacija:

- `content` skozi **obstoječi** `contentJsonSchema` iz `src/lib/content-schema.ts`
- `featured_image_url`: `https`, in **host se mora ujemati z lastno shrambo projekta**
  (`umvjwjzdrtamfrcqhopa.supabase.co`). Poljubnih zunanjih URL-jev se ne sprejema.
- `run_slug`: `min(1).max(120)`, `^[a-z0-9-]+$`
- `source`: neobvezno, privzeto `"content-factory"`

Odgovori:

| status | telo | kdaj |
| --- | --- | --- |
| `201` | `{"draft_id":"<uuid>","edit_url":"https://<app>/draft/<uuid>"}` | osnutek ustvarjen |
| `409` | `{"error":"duplicate","draft_id":"<uuid>","edit_url":"..."}` | `run_slug` že obstaja |
| `400` | `{"error":"validation","detail":[...]}` | shema ali URL nista v redu |
| `401` | `{"error":"unauthorized"}` | ključ manjka ali je napačen |

`409` naj vrne **id obstoječega osnutka**, ne le napake - klicalec mora znati nadaljevati brez
podvajanja.

**Alt tekstov aplikacija ne sme prepisovati.** `content.languages.<jezik>.featured_image_alt` pridejo
izpolnjeni iz verige, kjer jih je napisal Claude, ki je sliko dejansko videl. Za osnutke iz te poti se
`generateImageAlts` **ne kliče**. Prazna polja ostanejo prazna in jih dopolni Igor.

`content.social_posts[].publish_date` prav tako pride prazen. Datume nastavi Igor v koraku 4.

## Tabela `content_drafts`

Nova migracija v `supabase/migrations/`:

| stolpec | tip | opombe |
| --- | --- | --- |
| `id` | `uuid` | PK, `default gen_random_uuid()` |
| `run_slug` | `text` | `not null`, **`unique`** - nosilec idempotence |
| `content` | `jsonb` | `not null`, celoten paket |
| `featured_image_url` | `text` | `not null` |
| `source` | `text` | `not null default 'content-factory'` |
| `status` | `text` | `not null default 'new'`, dovoljeno `new` / `dispatched` |
| `created_at` | `timestamptz` | `not null default now()` |
| `dispatched_at` | `timestamptz` | `null` |
| `dispatch_result` | `text` | `null`, vrednost, ki jo vrne `dispatchToN8n` |

Indeks na `status, created_at desc` za seznam osnutkov.

RLS vklopljen. Politike:

- prijavljeni uporabniki aplikacije: `select` in `update` (isti vzorec kot obstoječa avtentikacija)
- `anon`: nič
- vstavljanje samo prek `service_role`, torej iz `/api/drafts`

## Pot do osnutka v čarovniku

Nova pot pod obstoječo avtentikacijo, npr. `src/routes/_authenticated/draft/$draftId.tsx`:

1. prebere vrstico po `id`
2. napolni stanje čarovnika s `content` in `featured_image_url`
3. odpre **korak 3** (`Step3EditForm`); koraka 1 in 2 se preskočita, ker parsanja ni treba
4. od tam naprej je pot enaka kot danes: korak 4 datumi, korak 5 potrditev in `dispatchToN8n`

Seznam osnutkov s statusom `new` naj bo dosegljiv z domače strani, da Igor vidi, kaj ga čaka.

Po **uspešnem** `dispatchToN8n` (rezultat `accepted`) se vrstica označi: `status = 'dispatched'`,
`dispatched_at = now()`, `dispatch_result` = vrnjeni rezultat. Tako se isti osnutek ne odda dvakrat.
Pri `duplicate`, `rejected`, `missing_key` ali `error` vrstica ostane `new`, da je poskus mogoče
ponoviti.

## Kaj mora narediti n8n

Ni predmet te specifikacije in še ni zgrajeno, a brez tega ti poti nimata klicalca. Zapisano tu, da se
slika ne razgubi.

**`cf-generate-image`** je obstoječi `lHc3NdejxehMyc9O` (`Generiraj sliko (Content Factory)`), webhook
`generate-image`, trenutno `active: false`. Dopolniti ga je treba tako, da po generiranju obeh slik
vsako pošlje na `POST /api/images` (credential tipa Header Auth z `INGEST_API_KEY`) in Claudu vrne oba
javna URL-ja. Danes vrača `filesystem-v2` reference in pomanjšan base64, kar je oboje neuporabno.

**`cf-deliver-draft`** je nov kratek workflow. Prejme od Clauda paket in izbrani `featured_image_url`,
pokliče `POST /api/drafts` in vrne `draft_id` ter `edit_url`. Namen ni tehnični, ampak varnostni:
`INGEST_API_KEY` ostane v n8n credentialu in nikoli ne pride v Claudov kontekst. Isto velja za
`HMAC_SECRET`, ki ostane v aplikaciji.

Claude v celotni verigi nosi **samo nize**: URL slike, besedilo, presojo. Nikoli bajtov, nikoli
skrivnosti.

## Vrstni red gradnje

Prve tri točke so neodvisne od tega, kako Claude sliki vidi, zato jih odgovor Andreja ne blokira.

1. dve poti in tabela osnutkov v aplikaciji (ta dokument)
2. dopolnitev `cf-generate-image` z nalaganjem na `/api/images`
3. nov `cf-deliver-draft`
4. `frodx-publish-send`: neha sestavljati base64, pošilja `featured_image_url` prek `cf-deliver-draft`
5. `frodx-image-run`: zapiše dejansko pot do slik, ko je odločena. Danes ta skill kot trajno rešitev
   navaja SharePoint, kar bo treba popraviti, in ne opozarja, da `web_fetch` slik ne podpira, zato ga
   bo naslednja seja poskusila po nepotrebnem.
6. dry-run celotne verige, nato prvi živi tek
7. šele ko nova pot dela: pregled, ali `PROD 2` še potrebuje kaj, in dvojni podpis v njem

## Kaj namenoma ni v tem obsegu

- brisanje zavrženih slik iz bucketa
- kakršnokoli spreminjanje `dispatchToN8n` ali `PROD 2`
- MCP strežnik za aplikacijo - Claudu ne bi nič olajšal, sliko bi bilo še vedno treba prenesti kot
  base64 skozi kontekst, kar je dokazano pokvarjeno, dal pa bi mu pisalni dostop do cele aplikacije
- avtomatsko izbiranje datuma objave; datum ostane Igorjeva odločitev

## Kako se preveri

Po izvedbi, z resnično majhno PNG sliko:

```bash
# 1. nalozi sliko
curl -sS -X POST https://<app>/api/images \
  -H "x-api-key: $INGEST_API_KEY" -H "content-type: application/json" \
  -d "{\"image_base64\":\"$(base64 -i test.png)\",\"filename\":\"test.png\",\"mime_type\":\"image/png\"}"

# 2. brez ključa mora biti 401
curl -sS -o /dev/null -w '%{http_code}\n' -X POST https://<app>/api/images \
  -H "content-type: application/json" -d '{}'

# 3. ustvari osnutek (paket iz tests/fixtures/package_valid.json v tem repu)
curl -sS -X POST https://<app>/api/drafts \
  -H "x-api-key: $INGEST_API_KEY" -H "content-type: application/json" \
  -d @body.json

# 4. isti run_slug drugic mora biti 409 z istim draft_id
```

Nato v brskalniku: `edit_url` odpre čarovnik na koraku 3, besedila in slika so na mestu, korak 4
sprejme datume, korak 5 odda in vrstica dobi `status = 'dispatched'`.

Za korak 3 se lahko uporabi `tests/fixtures/package_valid.json` iz tega repa - je resničen paket v
obliki, ki jo veriga izdela.

## Pogoj zunaj aplikacije

Ta izbira **ne vpliva na nič v tej specifikaciji**: javni URL slike je potreben v vsakem primeru, ker
ga zahteva vozlišče `Download Featured Image` v `PROD 2`. Gre le za to, kako Claude kandidatki
**vidi**, preden izbere.

Preverjeno v Coworku 17. 8. 2026:

| pot | izid |
| --- | --- |
| `web_fetch` na slikovni URL | **ne deluje.** Orodje vrne `Image content is not supported`; podpira le besedilne in HTML vsebine |
| `bash_tool` + `curl` na javni URL | **blokirano.** Egress allowlist za `bash_tool` obsega samo pakirne vire (npm, pypi, crates, GitHub, Ubuntu). `frodx.com` in `*.supabase.co` sta zunaj njega. Vrnjeni 403 je proxyjev, ne Supabaseov |
| `read_resource` na `file:///{driveId}/{itemId}` (Microsoft 365) | **deluje.** MCP konektorji niso omejeni z istim allowlistom |

Ostaneta torej dve trajni poti:

1. **Lastnik organizacije doda host `umvjwjzdrtamfrcqhopa.supabase.co`** v nastavitve network egressa.
   Nato Cowork sliko prenese s `curl` in jo prebere z `Read`. Manj dela: n8n nalaga samo v aplikacijo.
   Prosi za ta en host, **ne za `*.supabase.co`**.
2. **Microsoft 365.** n8n naloži obe sliki tudi na SharePoint in vrne `driveId` in `itemId`. Edina že
   dokazana pot, a zahteva OneDrive/SharePoint credential v n8n (verjetno tudi registracijo aplikacije
   v Azure, torej najbrž prav tako administratorja) in dodatna vozlišča v workflowu.

**Vmesna pot, ki ne potrebuje nikogar:** ko `/api/images` obstaja, dobi človek dva javna URL-ja. Sliki
odpre v brskalniku in ju povleče v Coworkov pogovor - naložena slika je Claudu vidna. To je bistveno
manj dela od današnjega obhoda, kjer je treba sliki iskati v n8n izvedbi. Veriga je s tem uporabna
takoj, trajna rešitev pa lahko pride pozneje.
