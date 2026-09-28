# GameChanger – merjenje in definicija uspeha

> Vir resnice za to, KAJ novičnik meri in ZAKAJ. Uredniška pravila so v `playbook.md`; to je poslovna plast nad njimi. Podatki preverjeni neposredno v FrodX HubSpot portalu prek MCP, 31. 7. 2026.

---

## Definicija uspeha (Igor, julij 2026)

Narava FrodX posla: nakupa ni mogoče pripisati enemu kliku v mailu. Uspeh izdaje ni open rate in ni CTR. Uspeh je **aktivnost, ki posameznika pripelje do izkazanega interesa za prospecting agenta** – konkretno do vstopa v vrata `fx_prospecting_agent_status` (vrednosti: `review` → `include`).

**Hierarhija metrik (od najmočnejše):**
1. vstop kontakta v prospecting vrata (`review`/`include`)
2. odgovor na mail (`hs_email_last_reply_date` / geslo iz zaključka)
3. klik na pain link (glej spodaj)
4. skupni CTR izdaje
5. open rate – higiena, ne cilj

**Osnovna črta (SI, Igorjev podatek, jul 2026):** običajna izdaja dobi 1–2 odgovora. Izstopajoča izdaja (KFC, 19. 12. 2024) jih je dobila ≥15 – večinoma **mimo maila**: največ LinkedIn sporočila, nato SMS in telefon, manjšina po mailu. HubSpot (`hs_email_last_reply_date`) vidi samo mail delež, zato je metrika #2 brez ročnega štetja sistematično prenizka. Edini senzor za odmev čez kanale je Igor: v tednu po sendu vpiše skupni odmev (številka + kanali) v arhiv. Posledica za vrata: najmočnejši signali (SMS direktorja) so najmanj avtomatizabilni – vstop v vrata zanje ostane ročen.

Subject in hook se še vedno pišeta za odprtje, a scorecard in odločitve o vsebini se ravnajo po tej hierarhiji, ne po točki 5.

---

## Pain link (uredniško pravilo)

Klik na kolumno dokazuje **branost**. Klik na stran rešitve, demo, posvet ali prijavo dokazuje **problem**. Samo drugi tip klika lahko kdaj napolni prospecting vrata.

Pravilo: vsaka izdaja ima **natanko en pain link** – eno CTA, katere cilj izkazuje problem. Preostale CTA so bralne. Pri monotematski izdaji brez problemskega URL-ja pain signal nosi zaključek (odgovor z geslom) ali PS; to eksplicitno označim v scorecardu. `eval_check.py` šteje pain kandidate in opozori pri 0 ali >1.

---

## Kaj HubSpot meri sam – UTM NE dodajaj

Klik v marketinškem mailu gre prek HubSpotovega redirecta; seja dobi vir »Email marketing« in se pripiše kampanji, na katero je mail pripet. Tagiranje `CTA_URL` z UTM parametri **ni potrebno in ga ne uvajaj** (preverjeno: SI kampanja je brez UTM zabeležila 3 526 sej). Edina Janijeva obveznost: vsak novi mail pripeti na pravo kampanjo.

**A/B testiranje subjectov: opuščeno** (Igor, julij 2026). Baza je premajhna – za zaznavo razlike 5 odstotnih točk pri open rate bi rabili ~1 300 naslovov na vejo. Namesto testov: retrogradni arhiv (`archive.md`).

---

## Kampanje – fiksni CRM ID-ji

| Kampanja | campaignCrmObjectId |
|---|---|
| SI - GC - Newsletter | 435835742825 |
| HR - FX - Newsletter | 435835743362 |
| EN - FX - Newsletter | 435835568808 |

---

## Stanje CRM – snapshot 31. 7. 2026

**Baze po jeziku** (`hs_language` × `hs_marketable_status`):

| Jezik | Vsi | Marketinški (dosegljivi) | Seje jun 25–jul 26 | Seje/mark. kontakt |
|---|---|---|---|---|
| SI | 9 372 | 3 785 | 3 526 | 0,93 |
| HR | 1 875 | 741 | 434 | 0,59 |
| EN | 2 260 | **143** | 95 | 0,66 |

Sklep: HR in EN na kontakt dosegata 63 % oz. 71 % slovenske učinkovitosti – razlika je v velikosti baze, ne v pisanju. **Trojezičnost je Igorjeva fiksna odločitev (julij 2026): SI/HR/EN ostanejo v vsakem primeru. Vprašanja ukinjanja ne odpiraj več.**

EN anomalija: 94 % EN kontaktov ni marketinških (pri SI/HR 40 %). Dvig statusa ni zastonj – HubSpot zaračunava po marketinških kontaktih (tier), zato je to Igorjeva cenovna odločitev, ne tehnični popravek.

**Prospecting vrata:** 140 kontaktov (116 `include`, 24 `review`); SI 121, HR 19, EN 0; lifecycle pretežno MQL. Vseh 140 ima original in latest source **OFFLINE** – nihče ni prišel prek novičnika ali druge sledene inbound poti. Nativni HubSpot Prospecting Agent (`hs_prospecting_agent_enrollment_status`): 0 aktivno vključenih; množici se ne prekrivata. Marketing → vrata povezava ne obstaja (spec za Janija je bil predan 31. 7. 2026). Dokler je ni, poročam promet, ne interesa – tega ne razglašam za uspeh.

---

## MCP – kaj deluje in kaj ne (stanje 31. 7. 2026)

**Deluje** – recepti, ki so bili preverjeni in tečejo:

Baze po jeziku in statusu:
```sql
SELECT hs_language, hs_marketable_status, COUNT(*) FROM CONTACT
GROUP BY hs_language, hs_marketable_status
```

Vrata – kdo je noter in od kod:
```sql
SELECT hs_language, lifecyclestage, COUNT(*) FROM CONTACT
WHERE fx_prospecting_agent_status IN ('include','review')
GROUP BY hs_language, lifecyclestage
```
```sql
SELECT hs_analytics_source, COUNT(*) FROM CONTACT
WHERE fx_prospecting_agent_status IN ('include','review')
GROUP BY hs_analytics_source
```

Kampanjska analitika (seje, novi/vplivani kontakti): `read_campaign_data`, operation `GET_ANALYTICS`, z ID-ji iz tabele zgoraj.

Preverjena imena lastnosti za angažma (za poizvedbe in Janijeve workflowe): `hs_email_last_click_date`, `hs_email_last_open_date`, `hs_email_last_reply_date`, `hs_email_click`, `hs_email_open`, `hs_email_replied`, `hs_email_delivered`, `hs_analytics_num_page_views`, `hs_analytics_last_url`, `hs_analytics_last_visit_timestamp`, `zoom_webinar_registration_count`, `zoom_webinar_attendance_count`, `num_conversion_events`.

**Ne deluje – ne poskušaj znova, dokler Igor ne javi spremembe:**
- `MARKETING_EMAIL` objekt: `Missing required scopes` → open rate in CTR po izdaji prek MCP nista dosegljiva. Nadomestek: Igorjev izvoz iz Marketing > Email > Analyze (CSV) ali re-avtorizacija konektorja.
- Workflowi: ne berem in ne pišem (avtomatizacij ne morem zgraditi, samo specificirati).
- Seznami: naštevanja ni; `SEGMENT_REF` konvencija ostane nespremenjena.

---

## Mesečno poročilo (recept)

Ko Jani vzpostavi marketing → vrata povezavo, na Igorjevo zahtevo (»mesečno poročilo novičnika«) izdelam:
1. vstopi v vrata ta mesec: SQL na `fx_prospecting_agent_status` + `last_lead_status_change_date`/datum spremembe, presek z `hs_email_last_click_date` v mesecu;
2. kampanjske seje po jeziku (`GET_ANALYTICS`, mesečni razpon);
3. odgovori: kontakti s `hs_email_last_reply_date` v mesecu;
4. open/CTR po izdaji iz arhiva (`archive.md`), če je vir na voljo.
Poročilo primerja z prejšnjim mesecem in izpostavi eno akcijo, ne dvajsetih.
