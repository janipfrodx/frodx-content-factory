# Iz Igorjevega izhoda v state.json

`igor-column-writer` (korak 2) in `frodx-transcreation` (korak 4) sta vendorirana skilla in
ne vesta ničesar o `state.json` - vrneta samo besedilo/markdown v pogovoru. Prepis v ustrezno
rezino `state.json` je naloga dirigenta (tebe), po vsakem od teh dveh korakov. Spodaj je natančna
preslikava, izpeljana iz dejanskega besedila obeh skillov (`igor-column-writer/SKILL.md`,
`frodx-transcreation/SKILL.md`, `igor-column-writer/references/publishing-contract.md`,
`igor-column-writer/references/social-posts.md`) - ne ugibaj drugačne sintakse.

Ne urejaj vendoriranih skillov. To je samo navodilo, kako dirigent bere njihov izhod.

## Korak 2 - `igor-column-writer`

Osnovni delovni tok skilla (razdelek »5. Izhod« v njegovem `SKILL.md`) vrne, v tem vrstnem redu,
**v pogovoru, ne v datoteko**:

1. Kolumna - markdown, naslov kot `#`, podnaslovi kot `##`.
2. 3 predlogi naslovov (2-8 besed).
3. SEO meta opis (140-160 znakov).
4. Predlog teme za vizual.
5. Ocena (0-10) in 2-3 konkretne pripombe.

Preslikava v `state.json`:

- **`meta.title`** - naslov, ki ga Igor izbere med tremi predlogi (postavka 2) ali med pisanjem
  spremeni (skill sam preveri, ali je najmočnejša poved v telesu boljši naslov - glej njegov
  razdelek »4. Samokritika in revizija«). Zapiši dokončno različico, kot jo Igor potrdi.
- **`languages.sl.content`** - celotno kolumno (postavka 1), skupaj z `#` naslovom. Zapiši
  natanko to, kar skill vrne - ne preoblikuj markdowna.
- **Postavka 3 (SEO meta opis) in postavka 4 (predlog vizuala) se NE zapišeta neposredno.**
  `languages.sl.meta_description` po `references/state-schema.md` pripada koraku 6
  (`frodx-publishing-meta`), ne koraku 2 - Igorjev predlog iz postavke 3 je lahko izhodišče za
  korak 6, ni pa dokončno polje. Predlog vizuala (postavka 4) ni polje v `state.json` - je vhod
  za korak 5 (`frodx-image-run`), če ga takrat še potrebuješ; prenesi ga naprej v pogovoru, ne
  v state.
- **Postavka 5 (ocena)** se ne zapiše v `state.json`. Namenjena je Igorju pri tem koraku.

**Socialne objave (`social_posts[]`) - odprta točka.** `references/state-schema.md` pripiše
`social_posts[]` korak 2, vendar osnovnih pet postavk »Izhoda« zgoraj socialnih objav NE
vsebuje. Standard za socialne objave (`igor-column-writer/references/social-posts.md`: batch
3-5, vsaka z drugim vzvodom, samoocena 0-10, Igor izbere) je v vendoriranem skillu opisan v
okviru ločenega, neobveznega koraka »Publishing format«, ki se sproži šele, ko Igor izrecno
reče »naredi publishing fajl« ali podobno - ne avtomatsko ob osnovnem teku skilla.

Ker ta veriga socialne objave potrebuje že v koraku 2 (ne šele ob morebitnem docx pakiranju),
moraš dirigent po izhodu kolumne **izrecno prositi** za nabor socialnih objav po standardu iz
`references/social-posts.md` (batch 3-5, različni vzvodi, samoocena), počakati na Igorjevo
izbiro, in šele izbrano/potrjeno besedilo zapisati v `social_posts[]` kot seznam
`{"text": "<besedilo objave>"}` (brez `publish_date` - tega ta veriga ne zapolni, glej
`schema/content-json.schema.json`). To je zahteva te verige, ni avtomatika osnovnega skilla -
ne domnevaj, da jih igor-column-writer vrne sam, brez da bi jih posebej naročil.

Socialne objave so **samo slovenske** (`publishing-contract.md` §3: »Samo SL«) - `frodx-transcreation`
jih v koraku 4 ne prevaja.

## Korak 4 - `frodx-transcreation`

Skill se pokliče dvakrat (SL→EN, SL→HR - glej `frodx-content-factory/SKILL.md`, »Korak 4 kliči
dvakrat«). Njegov delovni tok (`frodx-transcreation/SKILL.md`, korak 8) pravi: »Return the final
transcreated text only« - vrne **samo končno prevedeno/transkreirano besedilo**, brez ločenega
naslova, brez meta opisa, brez predstavitvenega besedila (»Here is the translation« je izrecno
prepovedano).

Preslikava v `state.json`:

- **`languages.en.content`** - celoten rezultat klica SL→EN, natanko kot ga skill vrne (vključno
  z `#` naslovom in `##` podnaslovi, ki jih transkreacija ohrani v isti obliki kot vhodni SL
  markdown).
- **`languages.hr.content`** - enako za rezultat klica SL→HR.
- `meta.title` se ne prepisuje za EN/HR - v `state.json` je samo eno polje `meta.title` (glej
  `state-schema.md`); prevedeni naslovi ostanejo del `languages.en.content` /
  `languages.hr.content` kot `#` vrstica.
- `social_posts[]` se v tem koraku ne dotika - te ostanejo samo slovenske (glej zgoraj).
