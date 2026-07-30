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
