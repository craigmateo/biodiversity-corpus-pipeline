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
