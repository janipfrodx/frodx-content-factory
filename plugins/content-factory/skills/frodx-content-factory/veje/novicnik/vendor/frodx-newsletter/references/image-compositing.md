# FrodX Newsletter - slike in kompozitiranje

## Omrežna omejitev (pomembno)

bash v tem okolju **ne more** odpreti zunanjih URL-jev - dosegljivi so samo paketni registri (npm, pip, …). Posledice:

- Vsebine s `frodx.com` ali drugih strani beri z **`web_fetch`**, ne z bash/curl.
- URL-ji slik, ki jih vrne `web_fetch`, se **ne dajo prenesti** v peskovnik. Zato mora Igor slike **naložiti neposredno** (upload), šele nato jih lahko obdelam in kompozitiram.
- Registracijske strani webinarjev, ki se v mojem okolju kažejo kot "zaprte", so za prave uporabnike pogosto odprte - moj pogled je lahko zastarel/cachiran. Tega ne razglasim za napako, le označim za Igorjev pregled.

## Vdelava, format in razmerje

- **Slike so VDELANE v docx**, ne ločene datoteke. Janijev uvoznik ne uvaža slik po imenu - vsak blok ima vrstico `IMAGE` z dejansko vdelano sliko (python-docx `add_picture`), `IMAGE_FILE` pa nosi le ime za referenco.
- **WebP najprej pretvori v PNG** (PIL: `Image.open("x.webp").convert("RGB").save("x.png")`), sicer parsanje dimenzij ni zanesljivo.
- **Razmerje ohrani.** Slika gre v originalnem razmerju (kvadrat ali vsaj 16:9); build skalira **samo navzdol** (max širina ~520 px), nikoli ne obreže. Webinar/blok naslovnice pripravi v kvadratu ali 16:9, ne v ozkem traku.

## Kompozitiranje logotipa na fotografijo

Tipičen primer: logotip partnerja (npr. Kinetara) na fotografijo (npr. WOOP! Graz bowling) za blok sliko.

Orodja: **cairosvg** (SVG → PNG s prosojnostjo) + **Pillow** `alpha_composite`.

```bash
pip install cairosvg pillow --break-system-packages
```

Postopek:
1. Če je logotip SVG, ga z `cairosvg` rasteriziraj v PNG s prosojnostjo (alfa kanal ohranjen).
2. Po potrebi prebarvaj (npr. črn → bel) in podloži s prosojno temno ploščico za kontrast nad fotografijo.
3. Z Pillow `Image.alpha_composite` zloži logotip na fotografijo na izbrano pozicijo.
4. Shrani PNG; build ga **vdela** v celico `IMAGE` ustreznega bloka (vrstica `IMAGE_FILE` nosi le ime datoteke za referenco).

```python
from PIL import Image
import cairosvg, io

# SVG logo -> PNG z alfo
png_bytes = cairosvg.svg2png(url="logo.svg", output_width=600)
logo = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

# (po potrebi) prebarvanje črn->bel in temna prosojna ploščica
# ...

photo = Image.open("woop_graz.jpg").convert("RGBA")
# pozicioniraj logo (npr. spodaj desno z odmikom)
photo.alpha_composite(logo, (x, y))
photo.convert("RGB").save("b2.png", "PNG")
```

## Ton novic o partnerjih (označi Igorju)

Javna formulacija o strankah/partnerjih je Igorjeva presoja, ne moja. Primer: Avstrija je **prva zastavica Kinetare na tem trgu** (»zapičili smo zastavico tudi v Avstriji«), NE njihov prvi trg sploh - Kinetara ima veliko regionalnih strank. Tak framing vedno dvignem v Igorjev pregled.
