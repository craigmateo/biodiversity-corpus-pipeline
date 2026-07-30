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
