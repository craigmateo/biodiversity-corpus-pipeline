"""Run a small, reproducible GBIF API pilot."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from biodiversity_corpus.extract_language import extract_linguistic_fields
from biodiversity_corpus.gbif import iter_occurrences, save_json
from biodiversity_corpus.query_anchors import generate_search_anchors

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "pilot.yaml"
RAW_DIR = ROOT / "data" / "raw" / "gbif"
INTERIM_DIR = ROOT / "data" / "interim" / "gbif"


def load_config() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def main() -> None:
    config = load_config()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    year_from = config.get("year_from")
    year_to = config.get("year_to")
    year = None
    if year_from and year_to:
        year = f"{year_from},{year_to}"

    records = list(
        iter_occurrences(
            country=config.get("country"),
            scientific_name=config.get("scientific_name"),
            dataset_key=config.get("dataset_key"),
            year=year,
            max_records=int(config.get("limit", 100)),
        )
    )

    raw_path = save_json(
        {
            "retrieved_at": timestamp,
            "query": config,
            "record_count": len(records),
            "records": records,
        },
        RAW_DIR / f"occurrences_{timestamp}.json",
    )

    rows: list[dict[str, Any]] = []

    for record in records:
        linguistic = extract_linguistic_fields(record)
        anchors = generate_search_anchors(record)

        rows.append(
            {
                "gbifID": record.get("gbifID") or record.get("key"),
                "occurrenceID": record.get("occurrenceID"),
                "datasetKey": record.get("datasetKey"),
                "datasetTitle": record.get("datasetTitle"),
                "scientificName": record.get("scientificName"),
                "acceptedScientificName": record.get("acceptedScientificName"),
                "eventDate": record.get("eventDate"),
                "year": record.get("year"),
                "country": record.get("country"),
                "stateProvince": record.get("stateProvince"),
                "locality": record.get("locality"),
                "recordedBy": record.get("recordedBy"),
                "basisOfRecord": record.get("basisOfRecord"),
                "linguisticFieldCount": len(linguistic),
                "linguisticFields": " | ".join(
                    f"{key}: {value}" for key, value in linguistic.items()
                ),
                "searchAnchors": " | ".join(anchors),
                "references": record.get("references"),
                "license": record.get("license"),
            }
        )

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = INTERIM_DIR / f"occurrences_{timestamp}.csv"

    if rows:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        csv_path.write_text("", encoding="utf-8")

    print(f"Retrieved {len(records)} records")
    print(f"Raw JSON: {raw_path}")
    print(f"Working CSV: {csv_path}")


if __name__ == "__main__":
    main()
