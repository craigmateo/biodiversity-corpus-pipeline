"""Generate external-search anchors from occurrence metadata."""

from __future__ import annotations

from typing import Any


def generate_search_anchors(record: dict[str, Any]) -> list[str]:
    """Generate simple search queries from a GBIF occurrence record."""
    anchors: list[str] = []

    scientific_name = record.get("scientificName")
    dataset_title = record.get("datasetTitle")
    locality = record.get("locality") or record.get("verbatimLocality")
    year = record.get("year")
    recorded_by = record.get("recordedBy")

    if dataset_title:
        anchors.append(f'"{dataset_title}"')

    if scientific_name and locality:
        anchors.append(f'"{scientific_name}" "{locality}"')

    if scientific_name and year:
        anchors.append(f'"{scientific_name}" {year}')

    if recorded_by and locality:
        anchors.append(f'"{recorded_by}" "{locality}"')

    return list(dict.fromkeys(anchors))
