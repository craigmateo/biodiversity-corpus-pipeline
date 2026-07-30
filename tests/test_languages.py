from biodiversity_corpus.languages.identifiers import normalized_language_key
from biodiversity_corpus.languages.spatial import occurrence_point
from biodiversity_corpus.languages.vernacular import candidate_name_queries


def test_occurrence_point_uses_lon_lat_order() -> None:
    record = {
        "decimalLatitude": 69.5,
        "decimalLongitude": -105.2,
    }

    assert occurrence_point(record) == (-105.2, 69.5)


def test_glottocode_is_preferred() -> None:
    assert (
        normalized_language_key(
            glottocode="inuk1236",
            iso_639_3="iku",
            language_name="Inuktitut",
        )
        == "glottolog:inuk1236"
    )


def test_candidate_queries_include_common_name() -> None:
    queries = candidate_name_queries(
        scientific_name="Rangifer tarandus",
        common_name="caribou",
        language_name="Inuktitut",
    )

    assert '"caribou" "Inuktitut"' in queries
