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
