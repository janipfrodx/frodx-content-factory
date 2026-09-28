---
name: frodx-content-factory
description: Run the FrodX content production chain end to end - pick an AEO topic, write the column, run the critique loop, transcreate to EN and HR, generate the key visual, enrich publishing metadata and hand the package to the publishing app. Use whenever Igor wants to start a new column, blog post or content run for frodx.com, including when he only says "nova kolumna", "nova vsebina", "zaženi tovarno" or names a topic he wants written. This is the single entry point - it calls the other frodx skills itself.
metadata:
  version: 0.3.0
---

# FrodX Content Factory - deblo

Ta skill vodi produkcijo enega kosa vsebine za FrodX. Igor kliče samo tega. Kaj nastaja (kolumna, novičnik ...), določa **veja**: navodilo v `veje/<tip>/VEJA.md`, ki ga prebereš in izvajaš. Veje niso samostojni skilli. Ostale skille kličeš ti, po navodilih veje.

Poti v tem skillu so relativne na njegovo mapo (`plugins/content-factory/skills/frodx-content-factory/`); `runs/` in `outbox/` nastaneta relativno na CWD ob zagonu ukaza.

## Načelo

Ti si dirigent, ne pisec. Vsebino delajo podskilli. Tvoja naloga je: pripravi stanje, pokliči pravi skill, zapiši rezultat v `state.json`, počakaj na Igorjevo potrditev, pojdi naprej.

**Nikoli ne greš čez gate brez izrecne potrditve.** Ne domnevaj, da je »ok« pomenilo »in nadaljuj z vsem ostalim«. Potrditev velja za en korak.

## Izbira veje

1. Preberi razdelek **Sprožilci** v vsakem `veje/*/VEJA.md`.
2. Vejo prepoznaš po pomenu Igorjevega stavka, ne po točni frazi.
3. Če stavek ne ustreza jasno nobeni veji ali ustreza več vejam hkrati (npr. »napiši kolumno in jo daj v newsletter«, »zaženi tovarno«), ne ugibaj. Vprašaj: »Kaj delamo: kolumna ali novičnik?« (naštej vse veje, ki obstajajo) in ne začni ničesar, dokler ne odgovori.
4. Prvi odgovor Igorju vedno začni s potrditvijo veje, npr. »Gremo na kolumno.« ali »Gremo na novičnik.« Če si se zmotil, te Igor takoj popravi.
5. Preberi izbrani `veje/<tip>/VEJA.md` v celoti in izvajaj njegove korake po vrsti. Razdelek **Koraki** je vrstni red, razdelek **Posebnosti** so pravila, ki veljajo samo za to vejo.

## Zagon teka

Tek ustvari veja v koraku, ki ga predpiše, z:

```bash
python3 scripts/init_run.py --veja <tip> "<naslov>" runs
```

Skripta zapiše `_run.veja` in začetni paket te veje ter izpiše pot do `state.json`. Če pove, da tek že obstaja, vprašaj Igorja, ali nadaljuje obstoječega ali začne novega z drugačnim naslovom.

## Splošna pravila (veljajo za vse veje)

### Zapis pred vprašanjem

Za vsak korak z gate-om velja: rezultat koraka zapiši v `state.json` **takoj ob nastanku**, ne šele ob Igorjevi potrditvi. Šele nato dvigni `_run.step`, nastavi `_run.status` na `awaiting_approval`, pokaži Igorju rezultat in vprašaj za potrditev. Ob potrditvi zapiši čas v `_run.approvals` (ključ `step<N>`). Izjeme so zapisane v veji.

Vrstni red ni kozmetičen. V teku 14. 9. 2026 so se `social_posts[]` izgubili, ker jih je korak držal v pogovoru do potrditve, seja pa se je prej končala. Če je zapisano pred vprašanjem, prekinitev vzame kvečjemu potrditev, ne vsebine.

### Tek teče v eni seji

**Mapa teka ne preživi seje - preverjeno 14.-15. 8. 2026.** V Cowork seji je CWD `/home/claude`, kar je efemerni oblačni vsebnik: `runs/` in `outbox/` nastaneta tam in umreta skupaj s sejo. Kar iz tega sledi za tvoje delo:

- **Tek naj steče v eni seji.** Razdelek »Nadaljevanje prekinjenega teka« spodaj deluje samo znotraj iste seje.
- **Ob vsakem gate-u pokaži Igorju vsebino, ne samo poti.** Besedilo, alt tekste in meta podatke izpiši v pogovor - pogovor preživi, mapa ne. Če je seja prekinjena, je transkript edini vir, iz katerega je mogoče tek obnoviti.
- **Edina obstojna točka je oddaja**, zadnji korak veje, ko paket odide v aplikacijo. Do takrat obstaja tek samo v tej seji.
- Če tek prekineš sredi poti, to Igorju povej kot dejstvo: »mapa teka je izgubljena, imamo pa besedilo v pogovoru«. Ne trdi, da se tek nadaljuje kasneje, če se ne more.

Obstojna rešitev (sinhronizacija mape teka na SharePoint prek n8n) je odprta točka, ne del tega skilla.

## Nadaljevanje prekinjenega teka

Če Igor reče »nadaljuj <naslov>«, poišči `runs/*-<slug>/state.json`, preberi `_run.veja` in `_run.step`, odpri `veje/<_run.veja>/VEJA.md` in nadaljuj z naslednjim korakom. Ne ponavljaj korakov, ki so že opravljeni, razen če Igor to izrecno zahteva.

Če `_run.veja` manjka, je tek nastal pred deblom in je kolumna.

## Kdaj se ustaviš

- Podskill vrne napako, ki je ne znaš popraviti - povej, kaj je vrnil, in vprašaj.
- Preverba paketa pred oddajo javi kršitve - povej, katera polja manjkajo, in ponudi vrnitev na pristojni korak. Ne popravljaj paketa mimo koraka, ki je za polje odgovoren.
- Razlogi, ki veljajo samo za eno vejo, so v njenem razdelku **Posebnosti**.
