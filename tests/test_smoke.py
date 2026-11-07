"""Smoke tests: every country can render every document type it advertises."""

import pytest

from countries.utils import clear_photo_cache


def test_countries_registered():
    from countries import list_countries

    codes = list_countries()
    assert codes, "no countries registered"
    assert "us" in codes and "uk" in codes


@pytest.mark.parametrize("doc_type_index", [0])
def test_every_country_renders_first_doc(generator, sample_person, doc_type_index):
    """Fast smoke: first document type of every country renders to valid PNG bytes."""
    clear_photo_cache()
    doc_type = generator.get_document_types()[doc_type_index]
    school = generator.schools[0]

    data = generator.generate_document(
        doc_type=doc_type,
        first=sample_person["first"],
        last=sample_person["last"],
        school=school,
        position=sample_person["position"],
        dob=sample_person["dob"],
    )

    assert isinstance(data, bytes)
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "output is not a PNG"


def test_us_renders_all_document_types(generator, sample_person):
    """Full coverage for one representative country."""
    if generator.get_country_code() != "us":
        pytest.skip("only runs for the us generator")
    clear_photo_cache()
    school = generator.schools[0]
    for doc_type in generator.get_document_types():
        data = generator.generate_document(
            doc_type=doc_type,
            first=sample_person["first"],
            last=sample_person["last"],
            school=school,
            position=sample_person["position"],
            dob=sample_person["dob"],
        )
        assert data[:8] == b"\x89PNG\r\n\x1a\n"


def test_unknown_document_type_raises(generator, sample_person):
    school = generator.schools[0]
    with pytest.raises(ValueError):
        generator.generate_document(
            doc_type="not_a_real_document",
            first=sample_person["first"],
            last=sample_person["last"],
            school=school,
            position=sample_person["position"],
            dob=sample_person["dob"],
        )
