"""Extract text-bearing fields from GBIF occurrence records."""

from __future__ import annotations

from typing import Any

LINGUISTIC_FIELDS = (
    "occurrenceRemarks",
    "identificationRemarks",
    "taxonRemarks",
    "fieldNotes",
    "habitat",
    "verbatimLocality",
    "locality",
    "vernacularName",
)


def extract_linguistic_fields(record: dict[str, Any]) -> dict[str, str]:
    """Return populated linguistic or narrative fields."""
    extracted: dict[str, str] = {}

    for field in LINGUISTIC_FIELDS:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            extracted[field] = value.strip()

    return extracted
