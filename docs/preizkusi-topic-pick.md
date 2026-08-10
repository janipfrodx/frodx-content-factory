# Preizkusi za `frodx-topic-pick`

Ta skill je čista presoja (izbira teme iz Excela), ne deterministična koda. Zato ga ne preverja `pytest`, ampak trije ročni preizkusi z modelom. Navodilo spodaj lahko izvedeš samostojno, brez branja načrta - vse, kar rabiš, je fixture datoteka `tests/fixtures/topics_table.md` iz tega repozitorija.

Rezultate vsakega preizkusa zapiši v ta dokument, v razdelek »Zapis rezultatov« na koncu (dopolni ga z datumom in ugotovitvami; ne prepisuj obstoječega).

## Preizkus 1: RED (brez naloženega skilla)

1. Odpri **nov** pogovor v Cowork ali Claude Code, v katerem `frodx-topic-pick` **ni** naložen (nov projekt ali pogovor brez tega plugina).
2. Odpri `tests/fixtures/topics_table.md`, prilepi celotno vsebino tabele v pogovor.
3. Vprašaj: »Katero temo naj pišem naslednjo?«
4. Zabeleži odgovor. Pričakovano (to je izhodišče, ne kriterij za uspeh - RED test samo pokaže razliko brez skilla): uporabne ideje, a brez strukture - brez `target_prompt`, brez formata, brez omejitve na tri predloge, brez utemeljitve, zakaj ne izbrati drugih.

## Preizkus 2: GREEN (z naloženim skillom)

1. Odpri pogovor, v katerem **je** `frodx-topic-pick` naložen (ta plugin).
2. Enak vhod: prilepi vsebino `tests/fixtures/topics_table.md` in vprašaj: »Katero temo naj pišem naslednjo?«
3. Preveri odgovor po tej checklisti - vsaka točka mora biti izpolnjena:
   - [ ] največ tri teme
   - [ ] vsaka ima temo, `target_prompt`, format in utemeljitev
   - [ ] `t-003` (status `done`) se **ne** pojavi med predlogi
   - [ ] skill ne izbere sam, ampak vpraša Igorja

Če katera od štirih točk ne velja, skill še ni pripravljen - vrni se na `SKILL.md` in `references/scoring.md` in popravi ustrezen del, preden nadaljuješ.

## Preizkus 3: prazna vrsta

1. Naredi kopijo `tests/fixtures/topics_table.md` (ne spreminjaj izvirnika) in v kopiji vsem štirim vrsticam nastavi `status` na `done`.
2. V pogovoru z naloženim skillom prilepi to spremenjeno tabelo in vprašaj enako vprašanje kot zgoraj.
3. Pričakovan izid: skill pove, da novih tem ni, in se ustavi. **Ne** predlaga nobene teme (tudi ne katere od tistih s `status = done`).
4. Če skill kaj predlaga, je to napaka v `SKILL.md`, točka 3 postopka (»Če ni nobene, povej to in končaj«) - popravi jo in preizkus ponovi.

## Zapis rezultatov

<!-- Dopolni po vsakem izvedenem preizkusu: datum, kdo je izvedel, izid (prestal/ni prestal) in morebitne opombe. -->
