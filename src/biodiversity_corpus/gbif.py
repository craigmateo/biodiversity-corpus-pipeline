"""Minimal GBIF occurrence API client."""

from __future__ import annotations

from typing import Any

import requests

BASE_URL = "https://api.gbif.org/v1"


def search_occurrences(
    *,
    country: str | None = None,
    scientific_name: str | None = None,
    dataset_key: str | None = None,
    year: str | None = None,
    limit: int = 20,
    offset: int = 0,
    **extra_params: Any,
) -> dict[str, Any]:
    """Search GBIF occurrence records.

    Parameters use friendly Python names and are converted to GBIF API names.
    """
    if not 1 <= limit <= 300:
        raise ValueError("limit must be between 1 and 300")

    params: dict[str, Any] = {
        "limit": limit,
        "offset": offset,
        **extra_params,
    }

    if country:
        params["country"] = country
    if scientific_name:
        params["scientific_name"] = scientific_name
    if dataset_key:
        params["dataset_key"] = dataset_key
    if year:
        params["year"] = year

    response = requests.get(
        f"{BASE_URL}/occurrence/search",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
