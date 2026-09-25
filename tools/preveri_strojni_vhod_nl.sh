#!/usr/bin/env bash
# Preveri strojni vhod Newsletter Huba po objavi.
# Ustreza razdelku "Testiranje" v docs/superpowers/specs/2026-09-25-newsletter-strojni-vhod-design.md
# nadrejenega repozitorija.
#
# Uporaba:
#   INGEST_API_KEY='<kljuc>' bash tools/preveri_strojni_vhod_nl.sh <base_url>
#
# base_url je objavljeni URL Newsletter Huba (PUBLIC_APP_URL), brez zadnje posevnice.
# Kljuca skript nikamor ne izpise. Ob uspehu ustvari en osnutek (source = factory), ki ga je
# treba v aplikaciji pobrisati rocno.

set -uo pipefail

BASE="${1:-}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE="$REPO/tests/fixtures/newsletter_draft_body.json"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

[[ -n "$BASE" ]] || { echo "MANJKA: base_url (objavljeni URL Newsletter Huba)." >&2; exit 2; }
[[ -n "${INGEST_API_KEY:-}" ]] || { echo "MANJKA: spremenljivka INGEST_API_KEY ni nastavljena." >&2; exit 2; }
[[ -f "$FIXTURE" ]] || { echo "MANJKA: $FIXTURE" >&2; exit 2; }

echo "base_url: $BASE"
echo

pass=0; fail=0
check() { # opis, pricakovano, dobljeno
  if [[ "$2" == "$3" ]]; then
    echo "  OK     $1 ($3)"; pass=$((pass+1))
  else
    echo "  NAPAKA $1: pricakovano $2, dobljeno $3"; fail=$((fail+1))
  fi
}
post() { # telo_datoteka, [kljuc|napacen]
  local hdr=()
  case "${2:-}" in
    kljuc) hdr=(-H "x-api-key: $INGEST_API_KEY") ;;
    napacen) hdr=(-H "x-api-key: napacen-kljuc") ;;
  esac
  curl -sS -m 60 -w '\n%{http_code}' -X POST "$BASE/api/drafts" \
    ${hdr[@]+"${hdr[@]}"} -H 'content-type: application/json' --data-binary @"$1"
}
jget() { python3 -c 'import json,sys
try: print(json.load(sys.stdin).get(sys.argv[1],""))
except Exception: print("")' "$1"; }
variant() { # ime, python izraz nad b (telo)
  python3 - "$FIXTURE" "$SLUG" "$2" > "$TMP/$1.json" <<'PY'
import json, sys
b = json.load(open(sys.argv[1]))
b["run_slug"] = sys.argv[2]
exec(sys.argv[3])
json.dump(b, sys.stdout)
PY
}

SLUG="preveri-nl-$(date +%Y%m%d-%H%M%S)"

echo "1) brez kljuca"
printf '{}' > "$TMP/empty.json"
RESP="$(post "$TMP/empty.json")"
check "status" 401 "$(tail -n1 <<<"$RESP")"

echo "2) napacen kljuc + pokvarjeno telo (avtentikacija pred validacijo)"
printf 'to ni json' > "$TMP/broken.txt"
RESP="$(post "$TMP/broken.txt" napacen)"
check "status" 401 "$(tail -n1 <<<"$RESP")"

echo "3) samo dva jezika"
variant two 'b["editions"] = b["editions"][:2]'
check "status" 400 "$(tail -n1 <<<"$(post "$TMP/two.json" kljuc)")"

echo "4) stirje bloki"
variant four 'e = b["editions"][0]; e["blocks"] = [e["blocks"][0]] * 4'
check "status" 400 "$(tail -n1 <<<"$(post "$TMP/four.json" kljuc)")"

echo "5) webinar brez event"
variant webinar 'b["editions"][0]["blocks"][1]["event"] = None'
check "status" 400 "$(tail -n1 <<<"$(post "$TMP/webinar.json" kljuc)")"

echo "6) veljavno telo (blok-02 je brez slike), run_slug=$SLUG"
variant ok 'pass'
RESP="$(post "$TMP/ok.json" kljuc)"
CODE="$(tail -n1 <<<"$RESP")"; BODY="$(sed '$d' <<<"$RESP")"
check "status" 201 "$CODE"
DRAFT1="$(jget draft_id <<<"$BODY")"; EDIT1="$(jget edit_url <<<"$BODY")"
echo "  draft_id: ${DRAFT1:-<ni ga>}"
echo "  edit_url: ${EDIT1:-<ni ga>}"
[[ -n "$DRAFT1" ]] && pass=$((pass+1)) || { echo "  NAPAKA: ni draft_id. Telo: ${BODY:0:400}"; fail=$((fail+1)); }
[[ "$EDIT1" == "$BASE/draft/$DRAFT1" ]] && pass=$((pass+1)) || { echo "  NAPAKA: edit_url ni $BASE/draft/<id>"; fail=$((fail+1)); }

echo "7) isto telo drugic"
RESP="$(post "$TMP/ok.json" kljuc)"
check "status" 409 "$(tail -n1 <<<"$RESP")"
check "isti draft_id" "$DRAFT1" "$(sed '$d' <<<"$RESP" | jget draft_id)"

echo
echo "-----"
echo "OK: $pass   NAPAK: $fail"
[[ -n "${EDIT1:-}" ]] && echo "Odpri v brskalniku: $EDIT1  (osnutek nato pobrisi v aplikaciji)"
[[ $fail -gt 0 ]] && exit 1 || exit 0
