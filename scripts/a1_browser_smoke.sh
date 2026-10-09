#!/usr/bin/env bash
# Real Chrome playback gate, no network assets used by the animation page.
set -euo pipefail
cd "$(dirname "$0")/.."
BROWSER="$(printenv CHROME_BIN || true)"
if [[ -z "$BROWSER" ]]; then
  for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
    if command -v "$candidate" >/dev/null 2>&1; then
      BROWSER="$(command -v "$candidate")"
      break
    fi
  done
fi
if [[ -z "$BROWSER" || ! -x "$BROWSER" ]]; then
  echo "A1 browser unavailable; cannot claim actual playback passed" >&2
  exit 1
fi
PORT=18765
python3 -m http.server "$PORT" --bind 127.0.0.1 > /tmp/zitie-a1-http.log 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$PORT/animation/index.html',timeout=1)" >/dev/null 2>&1; then
    break
  fi
  sleep .2
done
out="$(mktemp)"
trap 'kill "$server_pid" 2>/dev/null || true; rm -f "$out"' EXIT
timeout 55 "$BROWSER" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --disable-background-timer-throttling --disable-renderer-backgrounding \
  --window-size=1280,1400 --disable-backgrounding-occluded-windows \
  --virtual-time-budget=16000 --dump-dom \
  "http://127.0.0.1:$PORT/animation/tests/browser-smoke.html" > "$out"
if ! grep -q 'data-result="PASS"' "$out"; then
  echo "A1 real-browser playback smoke failed; final result:" >&2
  grep -o 'FAIL:[^<]*' "$out" >&2 || true
  grep -o '<pre id="result">[^<]*' "$out" >&2 || true
  exit 1
fi
echo "PASS: real Chrome SVG playback/controller smoke"
grep -o 'PASS: offline gallery[^<]*' "$out" | head -n 1 || true
