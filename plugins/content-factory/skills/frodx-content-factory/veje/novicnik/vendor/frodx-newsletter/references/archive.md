# GameChanger – arhiv poslanih izdaj

> Spomin izdaj z rezultati. Namen: po ~10 zapisih lestvica arhetipov in tem na FrodXovi bazi namesto ugibanja. **Status: shema pripravljena, polnjenje blokirano** – open/CTR po izdaji prek MCP nista dosegljiva (glej `measurement.md`, razdelek MCP). Vir: Igorjev CSV izvoz (Marketing > Email > Analyze) ali re-avtoriziran konektor.

## Shema (ena vrstica = ena jezikovna izdaja)

| Stolpec | Vir | Primer |
|---|---|---|
| `datum` | META `SEND_DATETIME` | 2026-07-23 |
| `package_id` | META | nl-2026-07-ai-vidnost |
| `jezik` | META | si |
| `subject` | META | … |
| `subject_arhetip` | playbook B (1–4) | 1_dvotaktni |
| `hook_arhetip` | HOOK tabela | B_prizor |
| `tip_izdaje` | playbook A | večbločna |
| `bloki` | BLOCK_TITLE seznam | kolumna+podcast+breeze |
| `pain_link_cilj` | CTA_URL pain kandidata | /sl/breeze-prompti |
| `sent / opens / clicks / replies / unsubs` | HubSpot izvoz | 3721 / 1180 / 96 / 4 / 2 |
| `vrata_vstopi` | SQL na `fx_prospecting_agent_status` | 0 |
| `opomba` | ročno | poletni termin |

## Polnjenje

1. Ob vsaki izdaji Claude pripravi vrstico z izpolnjenimi uredniškimi stolpci kot del handoffa (SKILL.md, korak 7); rezultati ostanejo prazni.
2. Rezultate dopišem, ko Igor pošlje izvoz – lahko v svežnju za več izdaj naenkrat.
3. Retrogradno: ob prvem izvozu označim tudi pretekle izdaje (arhetip, tip) iz besedil in izpeljem prvo lestvico: 5 najboljših / 5 najslabših po open in po reply, z branjem odstopanj, ne s testi značilnosti.

## Prvi zapis (retroaktivno, vir: Outlook)

| polje | vrednost |
|---|---|
| datum | 2024-12-19 (četrtek, 7.53) |
| jezik | si |
| subject | Kaj jedo Japonci za božič in koliko zasluži prodajnik v FrodXu? (61 znakov) |
| subject_arhetip | izven obstoječih štirih: dvojno vprašanje z nenavadnim parom |
| hook_arhetip | E (retroaktivno; izdaja je vir arhetipa) |
| tip_izdaje | kratka večbločna: podcast (RASTezanja ep. 21) + zaposlitveni oglas + referral prošnja |
| pain_link_cilj | ni ga – vse CTA bralne/socialne, nič komercialnega |
| rezultati | odgovori ≥15 ob osnovni črti 1–2 na izdajo (7–15×); kanali: največ LinkedIn sporočila, nato SMS in telefon, manjšina mail; opens/clicks manjkajo do izvoza |
| opomba | decembrski termin; osebni ton nadpovprečen (žena, Božiček); božični okvir odprt v hooku in zaprt v zaključku |

Datoteko arhiva vodi Igor (predlog: `GameChanger-arhiv.xlsx` na SharePointu ob ostalih newsletter datotekah); ta dokument je samo shema, da je vsak zapis primerljiv.
