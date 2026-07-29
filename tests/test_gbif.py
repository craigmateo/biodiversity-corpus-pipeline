from biodiversity_corpus.gbif import search_occurrences


def test_rejects_invalid_limit() -> None:
    try:
        search_occurrences(limit=0)
    except ValueError:
        return

    raise AssertionError("Expected ValueError for limit=0")
