# Živi preizkusi preverbe prevoda

Datum: 24. 9. 2026. Workflow `eGHQGAbgeQhfCcZu` (`cf-transcreation-check`), `executionMode: "manual"`.
Modela: OpenAI `gpt-6-sol`, Gemini `models/gemini-3.1-pro-preview`. `checkPrompt` je
`references/transcreation-check-prompt.md` z `{{DANES}}` = `24. 9. 2026`.

## Pred preizkusi - dve napaki, odkriti ob prvem teku

Prvi tek preizkusa A (izvedba `209729`) je odkril dvoje:

1. `openai_error: "Authorization failed - please check your credentials"`. Ključ v credentialu
   `OpenAI API` (`R57o8BoYHtoylkoX`) ni več deloval; isti credential uporabljata kritika
   (`GZmnPGOcVANH2sfy`) in naslovna slika (`lHc3NdejxehMyc9O`). Jani je vstavil nov ključ.
   Hkrati je bil model v OpenAI vozliščih kritike in preverbe zamenjan z `gpt-6-astra` na `gpt-6-sol`.
2. `Shape` je namesto niza vrnil objekt. Gemini vrne `content = {parts: [{text}], role}`, OpenAI
   `output = [{type: "message", content: [{type: "output_text", text}]}]`; stara veriga
   `message.content ?? content ?? text ?? output` je pri obeh zadela objekt. `Shape` zdaj izlušči
   besedilo, prazen odgovor brez napake pa vrne kot `<model>_error`.

Spodnji trije preizkusi so tekli po obeh popravkih.

## Preizkus A - namerna napaka mora pasti

Izvedba `209744`. Vhod: `target_lang: "hr"`, drugi stavek prevoda je ostal slovenski:

```
Svaka akcija za nove kupce je kazen za zveste. Taj popust netko plaća.
```

OpenAI:

```
ZA POPRAVEK

1. Nepreveden slovenski izraz
   Navedek: "Svaka akcija za nove kupce je kazen za zveste."
   Popravek: Svaka akcija za nove kupce kazna je za vjerne kupce.
```

Gemini:

```
ZA POPRAVEK

1. Nepreveden del besedila (slovenizem)
   Navedek: "je kazen za zveste."
   Popravek: je kazna za vjerne.
```

`openai_error: null`, `gemini_error: null`.

Ugotovitev: oba ocenjevalca sta ujela napako in imenovala pravi stavek. Prompt je dovolj oster.

## Preizkus B - čist prevod mora iti skozi

Izvedba `209745`. Isti vhod, drugi stavek pravilno preveden:

```
Svaka akcija za nove kupce kazna je za vjerne. Taj popust netko plaća.
```

OpenAI:

```
OBJAVLJIVO

Brez najdb.
```

Gemini:

```
OBJAVLJIVO

Brez najdb.
```

`openai_error: null`, `gemini_error: null`.

Ugotovitev: brez lažnih pozitivov.

## Preizkus C - padlo vozlišče

Izvedba `209748`. Vhod preizkusa A. `Gemini Check` je bil začasno pokvarjen z neobstoječim modelom
(`models/ne-obstaja-preizkus-c`) namesto z odstranitvijo credentiala, ker je tako stanje mogoče
natančno povrniti; učinek je isti - vozlišče pade. Po teku je model vrnjen na
`models/gemini-3.1-pro-preview`, credential nedotaknjen.

```json
{
  "openai": "ZA POPRAVEK\n\n1. Nepreveden dio rečenice\n   Navedek: \"Svaka akcija za nove kupce je kazen za zveste.\"\n   Popravek: Svaka akcija za nove kupce kazna je za vjerne kupce.",
  "gemini": null,
  "openai_error": null,
  "gemini_error": "The resource you are requesting could not be found"
}
```

Ugotovitev: tek ne pade, `gemini` je `null`, `gemini_error` neprazen, `openai` neprazen.

## Kar ostane odprto

- `Normalize Input` ob praznem `checkPrompt` še vedno vstavi `PLACEHOLDER`. Skill prompt vedno
  pošlje, zato se v teh preizkusih ni pokazalo.
- Nov OpenAI ključ je Janijev osebni in je začasen.
