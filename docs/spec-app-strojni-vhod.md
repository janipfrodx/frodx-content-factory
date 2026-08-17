# Specifikacija: strojni vhod v aplikacijo `frodx-content-app`

Stanje 17. 8. 2026. Namenjeno izvedbi v Lovableu. Nič od tega še ni zgrajeno.

Aplikacija: `frodx-content-app`, Lovable projekt `90b43584-6783-4de3-aca2-e95435c76de7`,
Supabase projekt `umvjwjzdrtamfrcqhopa`.

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

Da Claude v Coworku kandidatki **vidi** z javnega URL-ja, mora biti domena
`umvjwjzdrtamfrcqhopa.supabase.co` na seznamu dovoljenih domen za Coworkovo orodje `bash_tool`.
Preverjeno 17. 8. 2026: klic na `frodx.com` je zavrnil egress proxy z 96-bajtnim besedilnim
sporočilom, ne s sliko. Če dovoljenja ni mogoče dobiti, ostane dokazana pot prek Microsoft 365
(`read_resource` na `file:///{driveId}/{itemId}`), ki pa zahteva OneDrive/SharePoint credential v n8n.
Ta izbira ne vpliva na nič v tej specifikaciji: javni URL slike je potreben v vsakem primeru, ker ga
zahteva vozlišče `Download Featured Image` v `PROD 2`.
