# Igorjev paket za hrvaško transkreacijo

Igor Pauletič ga je pripravil 2. 10. 2026 (ChatGPT/Codex) in poslal Janiju 3. 10. 2026. Datoteke 00-05 so nespremenjene; ne urejaj jih. Sprememba gre skozi Igorja, test `tests/test_igor_hr_sol_vendor.py` jo zazna.

- `01-transkreacija-system.txt`: sistemski prompt pisca (SI -> HR).
- `02-pregled-system.txt`: sistemski prompt ločenega pregleda; vrne samo ugotovitve.
- `03-primer-vhoda.json`: oblika vhoda.
- `04-shema-transkreacije.json`, `05-shema-pregleda.json`: sheme izhodov.
- `00-navodila-za-Janija.txt`: Igorjev opis toka in pogoja za sprejem.

Prompta tečeta v n8n workflowu `cf-transkreacija-hr`; kodo vozlišča s prompti generira `tools/n8n_hr_sol.py`. Skripta `veje/novicnik/scripts/hr_sol.py` s kontrolno vsoto FNV-1a preveri, da sta prompta v n8n enaka tema tukaj.
