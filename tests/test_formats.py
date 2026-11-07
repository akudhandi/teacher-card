"""Output format encoding tests (png/jpg/pdf)."""

import pytest

from countries import get_country
from countries.utils import (
    clear_photo_cache,
    encode_document,
    format_extension,
    normalize_format,
)


def _png():
    gen = get_country("us")()
    gen._current_person_id = "john_smith"
    gen._current_gender = "Male"
    clear_photo_cache()
    return gen.generate_document_seeded(
        doc_type="teacher_id",
        first="John",
        last="Smith",
        school=gen.schools[0],
        position="Head of Science Department",
        dob="12/05/1988",
        seed=1234,
    )


def test_png_passthrough():
    data = _png()
    assert encode_document(data, fmt="png") == data


def test_jpeg_encoding():
    out = encode_document(_png(), fmt="jpg")
    assert out[:3] == b"\xff\xd8\xff", "not a JPEG"


def test_pdf_encoding():
    out = encode_document(_png(), fmt="pdf")
    assert out[:5] == b"%PDF-", "not a PDF"


def test_unsupported_format_raises():
    with pytest.raises(ValueError):
        normalize_format("gif")


def test_format_extension():
    assert format_extension("png") == ".png"
    assert format_extension("jpg") == ".jpg"
    assert format_extension("jpeg") == ".jpg"
    assert format_extension("PDF") == ".pdf"
