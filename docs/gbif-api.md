# GBIF API notes

## API base URL

```text
https://api.gbif.org/v1
```

The pilot initially uses four public endpoints:

```text
GET /occurrence/search
GET /occurrence/{gbifId}
GET /occurrence/{gbifId}/verbatim
GET /dataset/search
```

## Why preserve raw and normalized data?

The raw JSON records exactly what the API returned at retrieval time. The
interim CSV selects fields useful for corpus discovery and inspection. These
should remain separate so that normalization does not erase provenance or
unexpected fields.

## Search versus download

Occurrence search is appropriate for exploratory queries and small pilots. A
single page contains at most 300 records, and the searchable window is limited
to 100,000 records. Larger research datasets should use GBIF's asynchronous
download service and retain the resulting DOI.

## Interpreted and verbatim records

The normal occurrence endpoint returns GBIF's interpreted record. The
`/verbatim` endpoint exposes fields closer to the source record. Comparing the
two may itself be analytically useful because it makes data transformation and
standardization visible.
