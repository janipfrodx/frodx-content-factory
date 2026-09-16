#!/usr/bin/env bash
# Preveri strojni vhod aplikacije frodx-content-app po objavi.
# Ustreza razdelku "Kako se preveri" v docs/spec-app-strojni-vhod.md.
#
# Uporaba:
#   INGEST_API_KEY='<kljuc>' bash tools/preveri_strojni_vhod.sh [base_url]
#
# Privzeti base_url je objavljena aplikacija. Kljuca skript nikamor ne izpise.
# Ob uspehu ustvari eno vrstico v content_drafts, ki jo je treba pobrisati rocno
# (ali pa jo v carovniku oddaj do konca).

set -uo pipefail

BASE="${1:-https://frodx-content-app.lovable.app}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE="$REPO/tests/fixtures/package_valid.json"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [[ -z "${INGEST_API_KEY:-}" ]]; then
  echo "MANJKA: spremenljivka INGEST_API_KEY ni nastavljena." >&2
  exit 2
fi
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
post() { # pot, telo_datoteka, [glava_kljuca]
  local url="$BASE$1" file="$2"
  if [[ "${3:-}" == "kljuc" ]]; then
    curl -sS -m 120 -w '\n%{http_code}' -X POST "$url" \
      -H "x-api-key: $INGEST_API_KEY" -H 'content-type: application/json' --data-binary @"$file"
  else
    curl -sS -m 120 -w '\n%{http_code}' -X POST "$url" \
      -H 'content-type: application/json' --data-binary @"$file"
  fi
}
jget() { python3 -c 'import json,sys
try: print(json.load(sys.stdin).get(sys.argv[1],""))
except Exception: print("")' "$1"; }

# Majhna prava PNG slika, 4x4 rdeca.
python3 - "$TMP/test.png" <<'PY'
import sys, zlib, struct
def chunk(t, d):
    c = t + d
    return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
w = h = 4
raw = b"".join(b"\x00" + b"\xff\x00\x00" * w for _ in range(h))
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(raw))
       + chunk(b"IEND", b""))
open(sys.argv[1], "wb").write(png)
PY

python3 - "$TMP/test.png" > "$TMP/img.json" <<'PY'
import base64, json, sys
b64 = base64.b64encode(open(sys.argv[1], "rb").read()).decode()
json.dump({"image_base64": b64, "filename": "test.png", "mime_type": "image/png"},
          open(sys.stdout.fileno(), "w"))
PY

# ---------- 1. /api/images s kljucem -> 200 ----------
echo "1) POST /api/images (s kljucem)"
RESP="$(post /api/images "$TMP/img.json" kljuc)"
CODE="$(tail -n1 <<<"$RESP")"; BODY="$(sed '$d' <<<"$RESP")"
check "status" 200 "$CODE"
IMG_URL="$(jget url <<<"$BODY")"
if [[ -n "$IMG_URL" ]]; then
  echo "  url:  $IMG_URL"
  echo "  path: $(jget path <<<"$BODY")"
  pass=$((pass+1))
else
  echo "  NAPAKA: v odgovoru ni polja url. Telo: ${BODY:0:400}"; fail=$((fail+1))
fi
echo

# ---------- 2. /api/images brez kljuca -> 401 ----------
echo "2) POST /api/images (brez kljuca)"
printf '{}' > "$TMP/empty.json"
RESP="$(post /api/images "$TMP/empty.json")"
check "status" 401 "$(tail -n1 <<<"$RESP")"
check "telo" '{"error":"unauthorized"}' "$(sed '$d' <<<"$RESP" | tr -d ' \n')"
echo

# ---------- 3. napacen kljuc + pokvarjeno telo -> 401, ne 400 ----------
echo "3) POST /api/drafts (napacen kljuc + pokvarjeno telo), avtentikacija pred validacijo"
printf 'to ni json' > "$TMP/broken.txt"
RESP="$(curl -sS -m 60 -w '\n%{http_code}' -X POST "$BASE/api/drafts" \
  -H 'x-api-key: napacen-kljuc' -H 'content-type: application/json' --data-binary @"$TMP/broken.txt")"
check "status" 401 "$(tail -n1 <<<"$RESP")"
echo

# ---------- 4. /api/drafts s kljucem -> 201 ----------
SLUG="preveri-$(date +%Y%m%d-%H%M%S)"
python3 - "$FIXTURE" "$IMG_URL" "$SLUG" > "$TMP/draft.json" <<'PY'
import json, sys
json.dump({"content": json.load(open(sys.argv[1])),
           "featured_image_url": sys.argv[2],
           "run_slug": sys.argv[3],
           "source": "content-factory"}, open(sys.stdout.fileno(), "w"))
PY
echo "4) POST /api/drafts (s kljucem, run_slug=$SLUG)"
RESP="$(post /api/drafts "$TMP/draft.json" kljuc)"
CODE="$(tail -n1 <<<"$RESP")"; BODY="$(sed '$d' <<<"$RESP")"
check "status" 201 "$CODE"
DRAFT1="$(jget draft_id <<<"$BODY")"; EDIT1="$(jget edit_url <<<"$BODY")"
echo "  draft_id: ${DRAFT1:-<ni ga>}"
echo "  edit_url: ${EDIT1:-<ni ga>}"
[[ -n "$DRAFT1" ]] && pass=$((pass+1)) || { echo "  NAPAKA: ni draft_id. Telo: ${BODY:0:400}"; fail=$((fail+1)); }
echo

# ---------- 5. isti run_slug drugic -> 409 z istim draft_id ----------
echo "5) POST /api/drafts (isti run_slug drugic)"
RESP="$(post /api/drafts "$TMP/draft.json" kljuc)"
CODE="$(tail -n1 <<<"$RESP")"; BODY="$(sed '$d' <<<"$RESP")"
check "status" 409 "$CODE"
check "isti draft_id" "$DRAFT1" "$(jget draft_id <<<"$BODY")"
echo

# ---------- 6. tuj host slike -> 400 ----------
echo "6) POST /api/drafts (featured_image_url na tujem hostu)"
python3 - "$FIXTURE" "$SLUG-tuj" > "$TMP/draft_bad.json" <<'PY'
import json, sys
json.dump({"content": json.load(open(sys.argv[1])),
           "featured_image_url": "https://example.com/slika.png",
           "run_slug": sys.argv[2]}, open(sys.stdout.fileno(), "w"))
PY
RESP="$(post /api/drafts "$TMP/draft_bad.json" kljuc)"
check "status" 400 "$(tail -n1 <<<"$RESP")"
echo

echo "-----"
echo "OK: $pass   NAPAK: $fail"
[[ -n "${EDIT1:-}" ]] && echo "Odpri v brskalniku: $EDIT1"
[[ $fail -gt 0 ]] && exit 1 || exit 0
