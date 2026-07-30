#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/data/reference/languages/glottolog"
URL="https://glottolog.org/static/download/glottolog-5.3/languages_and_dialects_geo.csv"

mkdir -p "$OUTPUT_DIR"

echo "Downloading Glottolog geographic language data..."

curl --fail --location \
  "$URL" \
  --output "$OUTPUT_DIR/languages_and_dialects_geo.csv"

cat > "$OUTPUT_DIR/provenance.yaml" <<PROVENANCE
source: Glottolog
version: "5.3"
retrieved: "$(date --iso-8601=seconds)"
source_url: "$URL"
license: CC BY 4.0
purpose: Candidate language-location discovery
limitations:
  - Representative language points, not territorial polygons
  - Not inherently historical
  - Geographic proximity does not establish community association
PROVENANCE

echo "Saved:"
echo "  $OUTPUT_DIR/languages_and_dialects_geo.csv"
