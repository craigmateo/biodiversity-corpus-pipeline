"""Small, transparent client for the public GBIF API."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterator

import requests

API_BASE_URL = "https://api.gbif.org/v1"
DEFAULT_TIMEOUT = 30
MAX_SEARCH_PAGE_SIZE = 300


class GbifApiError(RuntimeError):
    """Raised when a GBIF API request fails."""


def _get_json(
    endpoint: str,
    *,
    params: dict[str, Any] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = 3,
) -> dict[str, Any]:
    """Send a GET request and return a JSON object.

    Retries transient request failures with a short incremental delay.
    """
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=timeout,
                headers={"User-Agent": "biodiversity-corpus-pipeline/0.1"},
            )
            response.raise_for_status()
            payload = response.json()

            if not isinstance(payload, dict):
                raise GbifApiError(f"Expected a JSON object from {url}")

            return payload

        except (requests.RequestException, ValueError, GbifApiError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(attempt)

    raise GbifApiError(f"GBIF request failed: {url}") from last_error


def search_occurrences(
    *,
    country: str | None = None,
    scientific_name: str | None = None,
    taxon_key: int | None = None,
    dataset_key: str | None = None,
    year: str | None = None,
    has_coordinate: bool | None = None,
    limit: int = 20,
    offset: int = 0,
    **extra_params: Any,
) -> dict[str, Any]:
    """Search indexed GBIF occurrence records.

    Friendly Python parameter names are translated to GBIF API parameter names.
    A single search page may contain at most 300 records.
    """
    if not 0 <= limit <= MAX_SEARCH_PAGE_SIZE:
        raise ValueError(
            f"limit must be between 0 and {MAX_SEARCH_PAGE_SIZE}"
        )
    if offset < 0:
        raise ValueError("offset cannot be negative")

    params: dict[str, Any] = {
        "limit": limit,
        "offset": offset,
        **extra_params,
    }

    optional = {
        "country": country,
        "scientificName": scientific_name,
        "taxonKey": taxon_key,
        "datasetKey": dataset_key,
        "year": year,
        "hasCoordinate": has_coordinate,
    }

    params.update({key: value for key, value in optional.items() if value is not None})
    return _get_json("occurrence/search", params=params)


def iter_occurrences(
    *,
    page_size: int = 300,
    max_records: int | None = None,
    **search_params: Any,
) -> Iterator[dict[str, Any]]:
    """Yield occurrence records across paginated GBIF search results.

    GBIF occurrence search has a 100,000-record search-window limit. Larger
    reproducible retrievals should use the asynchronous GBIF download service.
    """
    if not 1 <= page_size <= MAX_SEARCH_PAGE_SIZE:
        raise ValueError(
            f"page_size must be between 1 and {MAX_SEARCH_PAGE_SIZE}"
        )

    offset = 0
    yielded = 0

    while True:
        remaining = None if max_records is None else max_records - yielded
        if remaining is not None and remaining <= 0:
            return

        current_limit = page_size if remaining is None else min(page_size, remaining)

        page = search_occurrences(
            limit=current_limit,
            offset=offset,
            **search_params,
        )
        records = page.get("results", [])

        if not isinstance(records, list):
            raise GbifApiError("GBIF search response did not contain a results list")

        for record in records:
            if isinstance(record, dict):
                yield record
                yielded += 1

        if page.get("endOfRecords", True) or not records:
            return

        offset += len(records)

        if offset >= 100_000:
            raise GbifApiError(
                "Occurrence search cannot page beyond 100,000 records; "
                "use a GBIF download for larger retrievals."
            )


def get_occurrence(gbif_id: int | str) -> dict[str, Any]:
    """Retrieve one interpreted occurrence record by GBIF ID."""
    return _get_json(f"occurrence/{gbif_id}")


def get_verbatim_occurrence(gbif_id: int | str) -> dict[str, Any]:
    """Retrieve the verbatim source fields for one occurrence."""
    return _get_json(f"occurrence/{gbif_id}/verbatim")


def search_datasets(
    *,
    query: str,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """Search GBIF dataset metadata."""
    if not 0 <= limit <= 1000:
        raise ValueError("limit must be between 0 and 1000")

    return _get_json(
        "dataset/search",
        params={"q": query, "limit": limit, "offset": offset},
    )


def get_dataset(dataset_key: str) -> dict[str, Any]:
    """Retrieve metadata for one GBIF dataset UUID."""
    return _get_json(f"dataset/{dataset_key}")


def save_json(data: Any, path: str | Path) -> Path:
    """Write JSON as UTF-8 without altering the source structure."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output
