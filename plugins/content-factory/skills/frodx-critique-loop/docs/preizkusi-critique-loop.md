# Preizkusi critique loop - navodilo za Janija

Ta korak (Step 6 in Step 7 iz načrta implementacije) je bil izpuščen iz avtomatske izvedbe, ker vsak klic porabi plačljiv OpenAI in Gemini klic. To navodilo je samostojno - ne rabiš prebrati načrta, da ga izvedeš.

## Preden začneš

Workflow `GZmnPGOcVANH2sfy` (`Kritiziraj besedilo (Content Factory)`) trenutno **ni aktiven** (`active: false`). Produkcijski webhook (`https://frodxai.app.n8n.cloud/webhook/critique-text`) zato ne bo sprejel klica, dokler ga ne aktiviraš. Za ročni preizkus imaš dve možnosti:

- **A: test webhook.** Odpri workflow v n8n UI, klikni "Listen for test event" na vozlišču `Trigger`, nato v 2 minutah pošlji zahtevo na `https://frodxai.app.n8n.cloud/webhook-test/critique-text`. Izvedba pristane v Executions kot testna.
- **B: aktiviraj workflow** in pošlji na produkcijski URL. Priporočeno samo, če nameravaš workflow pustiti aktiven tudi za pravo rabo v verigi.

## Step 6: Živ preizkus z eno zanko

Vzemi `languages.sl.content` iz `tests/fixtures/package_valid.json` (v repu `frodx-content-factory`). Trenutna vrednost je:

```
Prvi odstavek slovenske kolumne.

igor.pauletic@frodx.com
```

Telo zahteve (odpri `plugins/content-factory/skills/frodx-critique-loop/references/critique-prompt.md` in njegovo celotno vsebino prilepi kot vrednost `critiquePrompt` - spodaj je zaradi dolžine skrajšano na `...`):

```json
{
  "text": "Prvi odstavek slovenske kolumne.\n\nigor.pauletic@frodx.com",
  "context": "Programi zvestobe | ciljani prompt: testni klic - preverjanje critique loopa",
  "language": "sl",
  "critiquePrompt": "... (celotna vsebina references/critique-prompt.md) ..."
}
```

Primer s `curl` (test webhook, možnost A zgoraj):

```bash
curl -X POST https://frodxai.app.n8n.cloud/webhook-test/critique-text \
  -H "Content-Type: application/json" \
  -d @telo.json
```

kjer je `telo.json` datoteka z zgornjim JSON-om (s polno vsebino `critique-prompt.md` v `critiquePrompt`).

Preveri:
- [ ] `get_execution` vrne neprazna izhoda iz `OpenAI Critique` in `Gemini Critique`
- [ ] `critiquePrompt` iz telesa je res prišel do modelov (kritika naj sledi obliki iz prompta: sodba v prvi vrstici, potem pripombe)
- [ ] `critique/round-1.json` nastane in ima vseh šest ključev

**Opomba o stroških:** vsak krog porabi plačljiv OpenAI in Gemini klic. Za preizkus zadošča ena zanka na kratkem besedilu.

## Step 7: Preizkus meje treh krogov

Pošlji namerno slabo besedilo (npr. tri odstavke splošnih trditev brez številk in brez hooka). Preveri, da se skill ustavi po tretjem krogu in Igorju pokaže odprte pripombe namesto da nadaljuje.

Primer slabega besedila za `text` (namenoma brez konkretnega hooka, brez številk, generično - da oba ocenjevalca skoraj zagotovo rečeta `ZA POPRAVEK`):

```
Digitalna transformacija je danes pomembna za vsako podjetje. Podjetja, ki se ne prilagodijo, bodo v prihodnosti imela težave. Zato je pomembno, da vodstvo razmisli o tem vprašanju.

Tehnologija se hitro spreminja in podjetja morajo biti pripravljena. Konkurenca ne počaka, zato je treba ukrepati pravočasno. Vsak vodja bi moral to vzeti resno.

igor.pauletic@frodx.com
```

Pošlji ga skozi celotno zanko (do tri kroge, isti webhook in obliko telesa kot v Step 6, s tem besedilom kot `text` v krogu 1 in z besedilom iz `critique/round-N.json` popravki za naslednje kroge - glej `SKILL.md`, razdelek "Postopek", točka 4).

Preveri:
- [ ] po tretjem krogu se zanka ustavi sama, brez napake
- [ ] nastanejo `critique/round-1.json`, `critique/round-2.json` in `critique/round-3.json`, vsak z vsemi šestimi ključi
- [ ] Igor je ob koncu pokazan zadnjo verzijo besedila in odprte pripombe iz zadnjega kroga - ne nadaljevanje v krog 4
