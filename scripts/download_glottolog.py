#!/usr/bin/env python3
"""Download the pinned Glottolog geographic language dataset."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


VERSION = "5.3"

URL = (
    "https://cdstar.eva.mpg.de/bitstreams/"
    "EAEA0-608B-9919-A962-0/"
    "languages_and_dialects_geo.csv"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "languages"
    / "glottolog"
)
OUTPUT_FILE = OUTPUT_DIR / "languages_and_dialects_geo.csv"
PROVENANCE_FILE = OUTPUT_DIR / "provenance.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Downloading Glottolog {VERSION}...")
    print(URL)

    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": (
                "biodiversity-corpus-pipeline/0.1 "
                "(research data downloader)"
            )
        },
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()

    if not data:
        raise RuntimeError("Downloaded file is empty")

    OUTPUT_FILE.write_bytes(data)

    provenance = {
        "source": "Glottolog",
        "version": VERSION,
        "dataset": "languages_and_dialects_geo.csv",
        "source_url": URL,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256(OUTPUT_FILE),
        "license": "CC BY 4.0",
        "purpose": "Candidate language-location discovery",
        "limitations": [
            "Locations are representative points, not territorial polygons.",
            "The dataset is not inherently historical.",
            "Geographic proximity does not establish community association.",
        ],
    }

    PROVENANCE_FILE.write_text(
        json.dumps(provenance, indent=2) + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Saved: {PROVENANCE_FILE}")
    print(f"Size: {OUTPUT_FILE.stat().st_size:,} bytes")
    print(f"SHA-256: {provenance['sha256']}")


if __name__ == "__main__":
    main()
