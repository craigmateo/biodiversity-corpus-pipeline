#!/usr/bin/env bash

set -euo pipefail

PROJECT_PATH="${1:-./biodiversity-corpus-pipeline}"

if [[ ! -d "$PROJECT_PATH" ]]; then
  echo "Project directory not found: $PROJECT_PATH" >&2
  exit 1
fi

mkdir -p \
  "$PROJECT_PATH/src/biodiversity_corpus/languages" \
  "$PROJECT_PATH/config" \
  "$PROJECT_PATH/data/reference/languages" \
  "$PROJECT_PATH/docs" \
  "$PROJECT_PATH/tests"

cat > "$PROJECT_PATH/src/biodiversity_corpus/languages/__init__.py" <<'PY'
"""Indigenous language and vernacular-name enrichment."""

from .models import LanguageAssociation, VernacularNameRecord

__all__ = ["LanguageAssociation", "VernacularNameRecord"]
PY

cat > "$PROJECT_PATH/src/biodiversity_corpus/languages/models.py" <<'PY'
"""Data models for language and vernacular-name enrichment."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LanguageAssociation:
    """A candidate language association for a biodiversity occurrence."""

    gbif_id: str | None
    language_name: str
    language_id: str | None = None
    identifier_scheme: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    spatial_basis: str | None = None
    temporal_basis: str | None = None
    confidence: str = "unreviewed"
    notes: str | None = None


@dataclass(slots=True)
class VernacularNameRecord:
    """A documented species name in a particular language."""

    scientific_name: str
    language_name: str
    vernacular_name: str
    gbif_id: str | None = None
    language_id: str | None = None
    identifier_scheme: str | None = None
    source_title: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    orthography: str | None = None
    dialect_or_variety: str | None = None
    place_context: str | None = None
    time_context: str | None = None
    literal_gloss: str | None = None
    community_attribution: str | None = None
    confidence: str = "unreviewed"
    provenance_notes: list[str] = field(default_factory=list)
PY

cat > "$PROJECT_PATH/src/biodiversity_corpus/languages/spatial.py" <<'PY'
"""Spatial helpers for language-area enrichment."""

from __future__ import annotations

from typing import Any


def occurrence_point(record: dict[str, Any]) -> tuple[float, float] | None:
    """Return a GBIF coordinate as (longitude, latitude)."""
    lat = record.get("decimalLatitude")
    lon = record.get("decimalLongitude")

    if lat is None or lon is None:
        return None

    try:
        return float(lon), float(lat)
    except (TypeError, ValueError):
        return None


def build_language_lookup_context(record: dict[str, Any]) -> dict[str, Any]:
    """Prepare place and time information for a language lookup."""
    point = occurrence_point(record)

    return {
        "gbif_id": record.get("gbifID") or record.get("key"),
        "scientific_name": record.get("scientificName"),
        "event_date": record.get("eventDate"),
        "year": record.get("year"),
        "country": record.get("country"),
        "state_province": record.get("stateProvince"),
        "locality": record.get("locality") or record.get("verbatimLocality"),
        "longitude": point[0] if point else None,
        "latitude": point[1] if point else None,
        "coordinate_uncertainty_m": record.get("coordinateUncertaintyInMeters"),
    }
PY

cat > "$PROJECT_PATH/src/biodiversity_corpus/languages/identifiers.py" <<'PY'
"""Helpers for stable language identifiers."""

from __future__ import annotations


def normalized_language_key(
    *,
    glottocode: str | None = None,
    iso_639_3: str | None = None,
    local_identifier: str | None = None,
    language_name: str | None = None,
) -> str:
    """Return the strongest available language identifier."""
    if glottocode:
        return f"glottolog:{glottocode.strip()}"
    if iso_639_3:
        return f"iso639-3:{iso_639_3.strip().lower()}"
    if local_identifier:
        return f"local:{local_identifier.strip()}"
    if language_name:
        return f"name:{language_name.strip().casefold()}"

    raise ValueError("At least one identifier or language name is required")
PY

cat > "$PROJECT_PATH/src/biodiversity_corpus/languages/vernacular.py" <<'PY'
"""Search and validation helpers for vernacular species names."""

from __future__ import annotations

from typing import Any


def candidate_name_queries(
    *,
    scientific_name: str,
    language_name: str,
    common_name: str | None = None,
) -> list[str]:
    """Generate transparent search strings for lexical resources."""
    queries = [
        f'"{scientific_name}" "{language_name}"',
        f'"{language_name}" dictionary "{scientific_name}"',
    ]

    if common_name:
        queries.extend(
            [
                f'"{common_name}" "{language_name}"',
                f'"{language_name}" dictionary "{common_name}"',
            ]
        )

    return list(dict.fromkeys(queries))


def has_minimum_provenance(record: dict[str, Any]) -> bool:
    """Check whether a lexical record has minimum source attribution."""
    required = (
        record.get("scientific_name"),
        record.get("language_name"),
        record.get("vernacular_name"),
        record.get("source_url") or record.get("source_title"),
    )
    return all(bool(value) for value in required)
PY

cat > "$PROJECT_PATH/src/biodiversity_corpus/languages/registry.py" <<'PY'
"""Starter registry of language-data sources.

These are candidate source types, not automatically authoritative sources.
Each future connector should document licence, temporal coverage, spatial
assumptions, provenance, and community governance.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LanguageSource:
    name: str
    purpose: str
    identifier_scheme: str | None = None
    access_mode: str = "manual_review"
    notes: str | None = None


STARTER_SOURCES = (
    LanguageSource(
        name="Glottolog",
        purpose="Language identifiers, classification, coordinates, and bibliography",
        identifier_scheme="glottocode",
        access_mode="dataset_or_export",
    ),
    LanguageSource(
        name="Community language portals",
        purpose="Publicly documented lexical forms, audio, and usage notes",
        access_mode="source_specific",
        notes="Respect source-specific access and governance conditions.",
    ),
    LanguageSource(
        name="Historical dictionaries and archival texts",
        purpose="Time-specific lexical attestations and historical naming",
        access_mode="archive_search",
        notes="Record authorship, date, genre, translation, and colonial mediation.",
    ),
)
PY

cat > "$PROJECT_PATH/config/language_enrichment.yaml" <<'YAML'
enabled: false

spatial_lookup:
  require_coordinates: true
  retain_coordinate_uncertainty: true
  candidate_limit: 10

temporal_lookup:
  use_occurrence_year: true
  allow_undated_sources: true
  flag_temporal_mismatch: true

identifiers:
  preferred:
    - glottocode
    - iso_639_3
    - source_local_id

vernacular_names:
  require_source_attribution: true
  require_language_attribution: true
  preserve_original_orthography: true
  allow_multiple_names_per_species: true
  manual_validation_required: true

governance:
  public_sources_only: true
  record_access_conditions: true
  record_community_attribution: true
  do_not_infer_community_knowledge: true
YAML

cat > "$PROJECT_PATH/data/reference/languages/README.md" <<'MD'
# Language reference data

This directory is reserved for openly licensed language metadata, spatial
reference files, identifier mappings, and source registries.

Do not place restricted, culturally sensitive, community-governed, or
personally identifying material here.

Every imported resource should include provenance notes recording:

- title and publisher
- source URL
- version or retrieval date
- licence and access conditions
- identifier scheme
- spatial and temporal limitations
- transformations performed by this project
MD

cat > "$PROJECT_PATH/docs/indigenous-language-enrichment.md" <<'MD'
# Indigenous language and vernacular-name enrichment

## Aim

This layer explores whether a biodiversity occurrence can help identify
publicly documented language resources relevant to its place, time, and taxon.

It does not treat a coordinate as proof that one language or community is
uniquely associated with a record. It also does not claim to recover
community-held knowledge automatically.

## Workflow

```mermaid
flowchart TD
    A[GBIF occurrence] --> B[Coordinates, locality and date]
    B --> C[Candidate historical language areas]
    C --> D[Stable language identifiers]
    D --> E[Public language resources]
    E --> F[Documented vernacular species names]
    F --> G[Manual linguistic and provenance review]
    G --> H[Corpus manifest enrichment]
```

## Important distinction

The pipeline should preserve these as separate claims:

1. a GBIF record is associated with a place and date;
2. one or more sources associate languages with that place;
3. a lexical source documents a species name;
4. the lexical form may be specific to a dialect, orthography, period, or genre.

These should never be collapsed into a statement such as:

> The Indigenous name for this species is ...

## Suggested fields

### Language association

- GBIF ID
- coordinates
- coordinate uncertainty
- occurrence date
- candidate language
- stable language identifier
- spatial source
- temporal basis
- confidence
- review status

### Vernacular name

- scientific name
- language name and identifier
- documented lexical form
- orthography
- dialect or variety
- source title and URL
- source type
- place and time context
- community attribution
- provenance notes

## Guardrails

- Use publicly available resources unless explicit permission has been obtained.
- Preserve source-specific access and reuse conditions.
- Represent overlap and uncertainty.
- Do not infer undocumented names from related languages.
- Preserve dialectal, orthographic, and historical variation.
- Treat colonial dictionaries and archival texts as mediated historical sources.
- Require manual review before publication.
MD

cat > "$PROJECT_PATH/tests/test_languages.py" <<'PY'
from biodiversity_corpus.languages.identifiers import normalized_language_key
from biodiversity_corpus.languages.spatial import occurrence_point
from biodiversity_corpus.languages.vernacular import candidate_name_queries


def test_occurrence_point_uses_lon_lat_order() -> None:
    record = {
        "decimalLatitude": 69.5,
        "decimalLongitude": -105.2,
    }

    assert occurrence_point(record) == (-105.2, 69.5)


def test_glottocode_is_preferred() -> None:
    assert (
        normalized_language_key(
            glottocode="inuk1236",
            iso_639_3="iku",
            language_name="Inuktitut",
        )
        == "glottolog:inuk1236"
    )


def test_candidate_queries_include_common_name() -> None:
    queries = candidate_name_queries(
        scientific_name="Rangifer tarandus",
        common_name="caribou",
        language_name="Inuktitut",
    )

    assert '"caribou" "Inuktitut"' in queries
PY

echo
echo "Added Indigenous language enrichment starter files to:"
echo "  $PROJECT_PATH"
echo
echo "Next:"
echo "  cd \"$PROJECT_PATH\""
echo "  pytest"
echo "  git add ."
echo '  git commit -m "Add Indigenous language enrichment starter"'
