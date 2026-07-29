from biodiversity_corpus.gbif import search_occurrences


def test_rejects_occurrence_limit_above_300() -> None:
    try:
        search_occurrences(limit=301)
    except ValueError:
        return

    raise AssertionError("Expected ValueError for limit=301")


def test_rejects_negative_offset() -> None:
    try:
        search_occurrences(offset=-1)
    except ValueError:
        return

    raise AssertionError("Expected ValueError for a negative offset")
