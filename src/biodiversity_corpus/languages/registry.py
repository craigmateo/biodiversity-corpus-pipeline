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
