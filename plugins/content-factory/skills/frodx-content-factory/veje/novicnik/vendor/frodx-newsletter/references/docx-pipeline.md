# FrodX Newsletter - docx pipeline (za Janijev HubSpot uvoz)

Jani pretvori docx v HubSpot novičnik prek API-ja (Lovable uvoznik). Docx mora biti **deterministično strojno berljiv**. Ta dokument je pogodba med tem, kar napišem, in tem, kar Jani uvozi.

> **Vir resnice:** ta shema je rekonstruirana iz treh dejanskih docx, ki jih je Janijev uvoznik **uspešno obdelal** (`FrodX_Newsletter_TEST_si/hr/en`). Ne ugibaj formata - drži se te sheme. Če Jani uvoznik spremeni, ob naslednji izdaji znova preveri proti delujočemu vzorcu in posodobi ta dokument.

---

## Železna pravila (kar je uvoznik dejansko zahteval)

1. **Vsi ključi VELIKE TISKANE.** `SUBJECT`, `FROM_EMAIL`, `BLOCK_TITLE`, `BODY_P1` … Male črke → uvoznik polja ne najde.
2. **Vse strojno berljivo je v tabelah `ključ | vrednost`.** Tudi **hook, kazalo, zaključek, podpis in PS so TABELE**, ne proza. (Proza zunaj tabel = stari format → hook in bloki se uvozijo kot *prazni*.)
3. **Slike so VDELANE v celico.** Vsak blok ima vrstico `IMAGE` z **vdelano sliko** (python-docx `add_picture`) v desni celici. Uvoznik **NE** uvaža ločenih slikovnih datotek po imenu. `IMAGE_FILE` (ime datoteke) je ločena *tekstovna* vrstica; `IMAGE` nosi dejansko vdelano sliko.
4. **Ena povezava na blok.** Vsak blok ima točno en CTA (`CTA_LABEL` + `CTA_URL`). **Inline povezav v telesu NI** (delujoči vzorci jih nimajo). Če je sekundarna povezava pomembna (npr. YouTube video), naj **postane CTA** tega bloka - ne inline link.
5. **Vrstni red tabel je fiksen** (spodaj). Bloki gredo po vrsti; TOC se nanje sklicuje prek `BLOCK_ID`.

---

## Zaporedje tabel (točno to, po vrsti)

1. **META** (2 stolpca)
2. **HOOK** (2 stolpca)
3. **TOC** (3 stolpci, z glavo)
4. … **BLOCK** (2 stolpca) - ena tabela na blok, 1–3 blokov
5. **CLOSING** (2 stolpca)
6. **SIGNOFF** (2 stolpca)
7. **PS** (2 stolpca)

(Nad tabelami je lahko en kozmetičen naslov za človeka, npr. `FrodX Newsletter (SI)`; uvoznik ga ignorira.)

---

## 1) META - vseh 14 ključev (VELIKE)

| ključ | primer (SI) | opomba |
|---|---|---|
| `PACKAGE_ID` | `nl-2026-06-zaposlujete` | unikatni slug izdaje (po jeziku) |
| `EDITION_NAME` | `Ne kupujete CRM-ja. Zaposlujete.` | tematski naslov izdaje (sme biti `=` ali `≠` SUBJECT) |
| `LANGUAGE` | `si` | `si` / `hr` / `en` |
| `STATUS` | `ready_to_send` | ali `draft` |
| `SEGMENT_REF` | `SI_ALL - celotna slovenska newsletter baza (Jani mapira na HubSpot list ID)` | konvencija `SI_ALL/HR_ALL/EN_ALL` + opis; Jani mapira na pravi list - **številčnega ID-ja ne rabim od Igorja** |
| `SEND_DATETIME` | `2026-06-17T08:00:00` | ISO; **isti čas čez vse jezike**; Igor potrdi |
| `TIMEZONE` | `Europe/Ljubljana` | **HR = `Europe/Zagreb`**; SI in EN = `Europe/Ljubljana` |
| `FROM_NAME` | `Igor Pauletič` | **HR = `Igor Pauletić`** (hrvaški ć); SI/EN = `Pauletič` |
| `FROM_EMAIL` | `igor.pauletic@frodx.com` | |
| `REPLY_TO` | `igor.pauletic@frodx.com` | |
| `FOOTER_REF` | `FRODX_SI` | `FRODX_HR` / `FRODX_EN` |
| `SUBJECT` | … | po arhetipu (playbook B) |
| `PREHEADER` | … | nadaljuje subject (playbook C) |
| `GREETING` | `Pozdravljeni,` | **HR = `Pozdrav,`** · **EN = `Hello,`** |

---

## 2) HOOK - ključi

| ključ | opomba |
|---|---|
| `HOOK_ARCHETYPE` | `A_statistika` / `B_prizor` / `C_kontrast` / `D_univerzalna` |
| `HOOK_P1` | prvi odstavek; **začni z malo začetnico** - teče iz GREETING (»Pozdravljeni,« + prazna vrstica + »predstavljajte si …«) |
| `HOOK_P2` | drugi odstavek |
| `HOOK_P3` | (po potrebi) tretji odstavek |

Hook = 2–3 odstavki, vsak svoja vrstica `HOOK_P{n}`.

---

## 3) TOC - tristolpčna tabela z glavo

Prva vrstica je **glava**: `TOC_LABEL | TOC_TYPE | BLOCK_ID`. Nato ena vrstica na blok.

- `TOC_TYPE`: `column` / `webinar` / `announcement` - **ujema se z `BLOCK_TYPE`** tega bloka.
- `BLOCK_ID`: `block-01`, `block-02`, … (ujema se z bloki).
- Število vrstic (brez glave) **== število blokov**; noben teaser podvojen.

---

## 4) BLOCK - ena tabela na blok (vrstni red ključev kot spodaj)

| ključ | obvezno | opomba |
|---|---|---|
| `BLOCK_ID` | da | `block-01`, `block-02`, `block-03` (**NE** `b1`) |
| `BLOCK_TYPE` | da | `column` / `webinar` / `announcement` |
| `IMAGE_FILE` | da | ime datoteke (tekst), npr. `block-01_crm.png` |
| `IMAGE_ALT` | da | alt besedilo |
| `IMAGE` | da | **vdelana slika** v desni celici (ne ime datoteke!) |
| `BLOCK_TITLE` | da | naslov bloka |
| `BODY_P1`, `BODY_P2`, … | da (≥1) | telo, razbito **po odstavkih**, vsak svoja vrstica |
| `BULLET_1`, `BULLET_2`, … | ne | po želji alineje (npr. tri vprašanja) |
| `EVENT_DATE` | webinar | `2026-06-18` |
| `EVENT_TIME` | webinar | `10:00` (lokaliziraj: HR pogosto `13:00`) |
| `EVENT_DURATION_MIN` | webinar | `45` |
| `CTA_LABEL` | da | besedilo gumba |
| `CTA_URL` | da | ciljni URL - **en sam na blok** |

`EVENT_*` vrstice samo za `webinar` bloke; postavi jih **med** `BULLET_*` in `CTA_LABEL`.

---

## 5) CLOSING - ključi

| ključ | opomba |
|---|---|
| `CLOSING_TYPE` | npr. `bookend` (navezava na hook) |
| `CLOSING_P1` | navezava / zaokrožitev zgodbe iz hooka |
| `CLOSING_P2` | nizkofrikcijski **odgovor-z-geslom** (»odgovorite na ta mail z »… check««) |

---

## 6) SIGNOFF - ključi

| ključ | opomba |
|---|---|
| `SIGNOFF_PHRASE` | SI `Bodite dobro,` · HR `Sve najbolje,` · EN `Best,` |
| `SIGNOFF_NAME` | samo ime: `Igor` |

---

## 7) PS - ključ

| ključ | opomba |
|---|---|
| `PS_TEXT` | en odstavek; časovno omejen / dopolnilni nagovor |

---

## Slike (razmerje in vir)

- Slika gre v docx v **originalnem razmerju** (kvadrat ali vsaj 16:9), **nikoli obrezana**. Builder prebere naravne dimenzije in skalira **samo navzdol** (max širina ~520 px).
- **WebP najprej pretvori v PNG** (PIL), sicer parsanje dimenzij ni zanesljivo.
- Zunanjih slik (frodx.com, YouTube thumbnaili) peskovnik **ne more prenesti** - Igor jih naloži kot PNG/JPG. Za referenco YouTube naslovnice: `https://img.youtube.com/vi/[VIDEO_ID]/maxresdefault.jpg` (a v docx gre Igorjeva naložena datoteka).

---

## Build in validacija

```bash
pip install python-docx pillow --break-system-packages   # samo če manjka
# vsebino izdaje (SI/HR/EN) vpišeš v EDITIONS znotraj skripte:
python3 scripts/build_newsletter.py
# strukturna validacija (mora reči: All validations PASSED!):
python3 /mnt/skills/public/docx/scripts/office/validate.py /mnt/user-data/outputs/GameChanger_si.docx
# shema + uredniški ulovi na docx:
python3 scripts/eval_check.py /mnt/user-data/outputs/GameChanger_si.docx
```

Zgradi vse tri jezike, vsako datoteko validiraj in poženi `eval_check.py` na docx.

---

## Pogoste pasti (iz dejanskih krogov korekcij)

- **Mali ključi** → uvoznik polja ne najde. Vse VELIKE.
- **Hook / closing / PS kot proza** → uvozijo se prazni. Morajo biti **tabele**.
- **Slika kot ime datoteke** namesto vdelana → blok »prazen«. `IMAGE` mora vsebovati vdelano sliko.
- **Manjkajoča META polja** (`FROM_NAME` / `FROM_EMAIL` / `SEGMENT_REF`) → uvoznik javi napako.
- **`BLOCK_ID` v obliki `b1`** → uporabi `block-01`.
- **Inline povezave v telesu** → jih ni; sekundarno povezavo daj kot CTA bloka.
- **Em dash ` - ` v telesu** → uporabi en dash `–`. (En sam em dash je dopusten le v `SEGMENT_REF`, ker je tako v Janijevem delujočem vzorcu.)
