#!/usr/bin/env bash
# Builds the importable Notion package as a zip in dist/.
# Usage: ./scripts/build.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/template"
OUT="$ROOT/dist/Ultimate-Writer-Planner.zip"

if [ ! -d "$SRC" ]; then
  echo "error: template/ directory not found" >&2
  exit 1
fi

mkdir -p "$ROOT/dist"
rm -f "$OUT"

# Zip the CONTENTS of template/ so the page tree imports cleanly into Notion.
( cd "$SRC" && zip -r -X "$OUT" . -x ".*" >/dev/null )

echo "Built: $OUT"
unzip -l "$OUT"
