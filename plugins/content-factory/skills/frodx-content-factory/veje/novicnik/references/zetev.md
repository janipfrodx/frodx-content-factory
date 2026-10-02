# Žetev popravkov prevoda

Igorjevi potrjeni popravki HR in EN izdaj novičnika. Prevajalec jih dobi kot vhod, audit jih ne sme izničiti, varovalo jih preveri. Tako se popravek, ki ga je Igor enkrat naredil, ne ponovi.

## Tabela

n8n Data Table `CF-Zetev`, projekt `Content Factory` (`projectId: "FucXmQlDiWLVsRHW"`), ID `HXcjPS5C50RF7uMI`.

| Stolpec | Vsebina |
|---|---|
| `jezik` | `hr` ali `en` |
| `prej` | oblika, ki jo je Igor popravil, dobesedno, kot je stala v prevodu |
| `potem` | Igorjeva oblika |
| `razlog` | ena vrstica: zakaj (kalk, besedni red, izraz, register) |
| `veja` | `novicnik` |
| `run_slug` | tek, v katerem je popravek nastal |
| `datum` | ISO datum vpisa |

## Branje

V koraku 4, pred prevodom: `get_data_table_rows` nad `CF-Zetev`. Odgovor zapiši, kot je, v `runs/<slug>/prevod/zetev.json`. Če je tabela prazna, zapiši `[]`. `scripts/prevod_vhod.py` iz tega vzame vrstice za jezik.

## Pisanje

Na gate-u koraka 4, po Igorjevih popravkih: `add_data_table_rows`, ena vrstica na par. Po zapisu tabelo preberi nazaj in preveri, da so vrstice tam.

## Pravila

- Tabela se samo dopolnjuje. Vrstic ne brišeš in ne spreminjaš.
- Vpišeš samo par, ki ga je Igor na gate-u izrecno potrdil za žetev.
- V žetev gre samo splošen par (izraz, kalk, besedni red, register), ne enkratna vsebinska sprememba (dejstvo, številka, ime).
- `prej` je dovolj dolg, da ni del drugih besed: raje fraza kot ena kratka beseda.
- Vendorirani »Harvested corrections« v `croatian.md` in »Znane HR korekcije« v pisčevi rubriki ostanejo, kot so. Tabela je dodatek.
