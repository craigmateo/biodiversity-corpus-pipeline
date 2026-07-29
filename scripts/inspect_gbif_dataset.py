"""Search GBIF dataset metadata by a free-text query."""

from __future__ import annotations

import argparse

from biodiversity_corpus.gbif import search_datasets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Dataset search text")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    response = search_datasets(query=args.query, limit=args.limit)

    for dataset in response.get("results", []):
        print()
        print(f"Title: {dataset.get('title')}")
        print(f"Key:   {dataset.get('key')}")
        print(f"Type:  {dataset.get('type')}")
        print(f"DOI:   {dataset.get('doi')}")
        print(f"Org:   {dataset.get('publishingOrganizationTitle')}")


if __name__ == "__main__":
    main()
