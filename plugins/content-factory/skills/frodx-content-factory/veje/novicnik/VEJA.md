# Veja novičnik

Izdaja novičnika FrodX GameChanger v treh jezikih (`si`, `en`, `hr`), 1-3 bloki, s slikami blokov. Osnutek gre v Newsletter Hub, kjer ga Igor pregleda, doda manjkajoče slike, nastavi čas in razporedi. Docx ne nastane.

Poti `references/`, `scripts/` in `vendor/` so relativne na mapo te veje (`veje/novicnik/`). V ukazih so zapisane relativno na mapo debla (`plugins/content-factory/skills/frodx-content-factory/`).

Pisec je `vendor/frodx-newsletter/SKILL.md` (Igorjev `frodx-newsletter` v2.3, pravila zamrznjena do v3.0). Ni samostojen skill: ne »zaženeš« ga, ampak prebereš njegova navodila in reference ter izvedeš **samo korake, ki jih predpiše ta veja**.

## Sprožilci

Igor hoče novo izdajo novičnika. Veja se prepozna po pomenu, ne po točni frazi. Primeri: »delava nov newsletter«, »dejva naredit nov NL«, »pripravi novičnik«, »nov GameChanger«, »naredi newsletter iz teh treh kolumn«.

Ne sem: nova kolumna ali blog brez omembe novičnika. To je veja kolumna.

## Paket

`state.json` je od začetka telo `POST /api/drafts` Newsletter Huba (`run_slug`, `editions[]` za `si`, `en`, `hr`) in blok `_run`. Pogodba je `tests/fixtures/newsletter_draft_body.json` v repozitoriju. Kdo zapolni katero polje, je v `references/state-schema.md`.

- Paket ne nosi `send_datetime`, `timezone` ali kazala (TOC). Aplikacija ju nima oziroma ju nastavi Igor; časovni pas je vedno `Europe/Ljubljana`.
- `status` izdaje je `ready_to_send` ali `draft`, kot ga napiše pisec.
- Privzete vrednosti po jeziku: `references/privzete-vrednosti.md`.

## Koraki

Tek ustvari takoj, ko je veja potrjena, pred korakom 1:

```bash
python3 scripts/init_run.py --veja novicnik "<tema izdaje ali 'novicnik'>" runs
```

| Korak | Kaj teče | Gate: kaj vprašaš Igorja |
|---|---|---|
| 1 Gradivo | Igor poda 1-3 URL-je kolumn ali vsebin, po želji webinar, novico in slike. Pisec, njegov korak 1 (Intake): vsebine z URL-jev prebereš z `web_fetch`, določiš tip izdaje. Igorjevo pravilo je natanko en pain link na izdajo (CTA na rešitev, demo, posvet ali prijavo; `self-eval-rubric.md`). Če v gradivu takega URL-ja ni, ga pri gate-u vprašaš. URL-ja ne izmišljaš. Zapiši `_run.gradivo`, `_run.tip_izdaje` in Igorjeve odločitve v `_run.gradivo_odlocitve`. | kateri bloki gredo noter, v kakšnem vrstnem redu in kateri CTA je pain link |
| 2 SI izdaja | Pisec, njegova koraka 2-3 (SI original po `playbook.md`, sedem vrat po `self-eval-rubric.md`). Tu se ustaviš: HR in EN še ne nastaneta. | je SI izdaja v redu |
| 3 Kritika | `frodx-critique-loop` na SI izdaji (glej Skupni koraki) | je popravljena verzija v redu |
| 4 HR in EN | Pisec, njegova koraka 4-5 (transkreacija iz **popravljene** SI, sedem vrat z vrati 6). Nato `frodx-transcreation-check` za `hr` in za `en`. Na koncu, enkrat na jezik, Igorjev `frodx-transcreation-audit` (točka 6 v `frodx-transcreation-check/SKILL.md`). | sta HR in EN v redu (+ ocena audita za oba jezika, priporočilo za native pregled HR) |
| 5 Slike | `frodx-image-run`, Faza C | so slike v redu (odloča blok za blokom) |
| 6 Oddaja | preverba paketa, `cf-deliver-newsletter`, nato Igorjev scorecard in arhivska vrstica v pogovor | brez vprašanja o vsebini; odprte zadolžitve prebereš na glas in vprašaš, ali oddaja kljub temu (`frodx-publish-send`) |

**Pisčev korak 6 (docx build za Janija) se ne izvede nikoli.** Ne piši v `EDITIONS` znotraj `build_newsletter.py`, ne poganjaj ga in ne kliči `present_files`. Pisčev korak 7 (scorecard, kaj ostaja Igorju, vrstica za arhiv po `archive.md`) izvedeš ob oddaji, v pogovor, brez docxov.

Pisec v koraku 1 sme vprašati eno kratko vprašanje o gradivu. To je pričakovano - pusti ga.

## Pisec in preslikava

Pisec vsebino izdaje oblikuje v obliki `EDITIONS` iz `vendor/frodx-newsletter/scripts/build_newsletter.py` (META ključi, hook, bloki, closing, signoff, PS). Skripte ne urejaš in ne poganjaš; oblika je samo dogovor, kako pisec vrne vsebino.

Po koraku 2 zapiši SI v JSON datoteko (pari `("KLJUČ", vrednost)` kot seznami `["KLJUČ", vrednost]`):

```json
{"si": {"meta": [["PACKAGE_ID", "nl-2026-10-..."], ["LANGUAGE", "si"], ...],
        "hook_archetype": "B_prizor", "hook": ["..."],
        "blocks": [{"id": "block-01", "type": "column", "img_file": "", "img_alt": "",
                    "title": "...", "body": ["..."], "bullets": [], "cta_label": "...", "cta_url": "https://..."}],
        "closing_type": "bookend", "closing": ["..."], "signoff_phrase": "...", "signoff_name": "Igor", "ps": "..."}}
```

in jo vpiši:

```bash
python3 veje/novicnik/scripts/iz_editions.py <state.json> <editions.json>
```

Po koraku 4 enako za `hr` in `en` v eni datoteki. Skripta preslika `EDITIONS` v izdaje paketa (tabela v specu), izpusti TOC, `SEND_DATETIME` in `TIMEZONE`, trajanje webinarja pretvori v celo število minut in ob manjkajočem polju glasno pade.

**Varovalka:** skripta HR in EN zavrne, dokler v `_run.approvals` ni `step3` (Igor je potrdil kritiko SI). Če HR in EN vseeno nastaneta pred kritiko, ju zavrži in napiši znova iz popravljene SI. Ne prevajaš besedila, ki se bo še spremenilo.

Ob vsakem gate-u Igorju pokaži izdajo z `python3 veje/novicnik/scripts/izdaja_besedilo.py izpis <state.json> <jezik>`, ne JSON-a.

## Skupni koraki

- **`frodx-critique-loop`** (korak 3), razdelek »Vhod po veji« v skillu:
  - vhod: `izdaja_besedilo.py izpis <state.json> si`;
  - prompt: `references/critique-prompt.md` (začasen, sestavljen iz Igorjeve rubrike);
  - zapis: `izdaja_besedilo.py vpis <state.json> si <besedilo.txt>`.
- **`frodx-transcreation-check`** (korak 4), za `hr` in za `en`, razdelek »Vhod po veji« v skillu:
  - izvirnik: `izpis ... si`, prevod: `izpis ... <jezik>`;
  - popravek na besedilu izdaje po pisčevih pravilih transkreacije, vpis z `vpis ... <jezik>`, ne s ponovnim klicem `frodx-transcreation`;
  - zadolžitev za native HR pregled gre v `_run.open_tasks` vedno, kot pri kolumni. Igorju ob gate-u povej, da priporočaš native pregled.
  - audit na koncu, enkrat na jezik, po razdelku »Vhod po veji« v skillu: oznake izdaje ostanejo nespremenjene, vpis samo z `vpis ... <jezik>`. Igorju ob gate-u povej oceno in sodbo audita za oba jezika.
- **`frodx-image-run`** (korak 5): samo Faza C. Fazi A in B ne tečeta.
- **`frodx-publish-send`** (korak 6): razdelek »Veja novičnik« v skillu.

## Preverba paketa

```bash
python3 veje/novicnik/scripts/preveri_paket.py <state.json> --telo outbox/<run_slug>.json
```

Preveri: trije jeziki, vsak natanko enkrat; 1-3 bloki z enakim `block_id` in `type` v vseh jezikih; `webinar` ima `event` (datum, ura, trajanje), drugi bloki `null`; vsak blok ima naslov, telo in CTA z `https://`; slika bloka mora biti v shrambi `content-images`; ni dolgega pomišljaja (razen v `delivery.segment_ref`); ni vzorčnih vrednosti iz Igorjeve predloge; v SI in HR nedeljivi presledek pred %, v EN % brez presledka; ni `send_datetime` in ni `_run`. Blok brez slike je opozorilo, ne kršitev. Vsaka kršitev pove pristojni korak.

## Oddaja

n8n `cf-deliver-newsletter` (`Wd1gVtK77b29ePrJ`) prek `execute_workflow`, `executionMode: "manual"`. Workflow ostane neaktiven. Izidi (`created`, `duplicate`, `rejected`, `misconfigured`, `retry`) in zapis v `_run.delivery` so v `frodx-publish-send/SKILL.md`, razdelek »Veja novičnik«. Igor dobi `edit_url`.

Po oddaji v pogovor izpiši pisčev scorecard za vse tri jezike, kaj ostaja Igorju (resničnost dejstev, živi URL-ji, odprtost webinarja, native pregled HR in EN, ton novic o strankah) in vrstico za arhiv po `vendor/frodx-newsletter/references/archive.md`.

## Posebnosti

- Jezikovna koda slovenščine je v tej veji `si`, ne `sl`.
- Webinar ima po jezikih lahko različno uro (Igorjevo pravilo: SI 10:00, HR 13:00). To ni napaka.
- Igorjeva rubrika dovoli en dash (–) kot premor v stavku. Dolgi pomišljaj ne sme nikamor, razen v `SEGMENT_REF`, kot v Igorjevem vzorcu.
- `scripts/eval_check.py` pisca je pomoč, ne gate: vedno vrne exit 0.
- Blok `announcement` o resnični stranki ali partnerju: ton javne formulacije vedno označi Igorju.
- Igorja **ne** kliči za potrditev kakršnekoli n8n spremembe. Ta veja ne spreminja workflowov.
