# Privzete vrednosti po jeziku

Pošiljatelj (`FROM_NAME`, `FROM_EMAIL`, `REPLY_TO`), segment (`SEGMENT_REF`), noga (`FOOTER_REF`), pozdrav (`GREETING`), podpis (`SIGNOFF_PHRASE`, `SIGNOFF_NAME`) in ura webinarja se vzamejo iz Igorjeve `vendor/frodx-newsletter/references/docx-pipeline.md`, razdelek META in SIGNOFF. Tovarna jih ne kopira, da ostane en vir: ko Igor spremeni svojo shemo, velja nova.

Dve izjemi, ker paket ni docx:

- **`TIMEZONE` se ne prenese.** Igorjeva shema za HR predpisuje `Europe/Zagreb`, aplikacija Newsletter Hub pa vedno uporablja `Europe/Ljubljana` (konstanta `TIMEZONE`). Zamik je isti, zato velja aplikacija.
- **`SEND_DATETIME` se ne prenese.** Čas pošiljanja nastavi Igor v aplikaciji.
