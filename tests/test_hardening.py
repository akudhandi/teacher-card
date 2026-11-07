"""Hardening tests: input validation and explicit profile photos."""

import pytest
from PIL import Image

from countries import get_country
from countries.utils import clear_photo_cache, validate_dob


def _gen():
    g = get_country("us")()
    g._current_person_id = "john_smith"
    g._current_gender = "Male"
    clear_photo_cache()
    return g


def _render(g, **overrides):
    kwargs = dict(
        doc_type="teacher_id",
        first="John",
        last="Smith",
        school=g.schools[0],
        position="Head of Science Department",
        dob="12/05/1988",
        seed=1234,
    )
    kwargs.update(overrides)
    return g.generate_document_seeded(**kwargs)


def test_validate_dob_accepts_common_formats():
    for value in ("12/05/1988", "1988-05-12", "12 May 1988", "05.12.1988"):
        assert validate_dob(value)


def test_validate_dob_rejects_missing_or_yearless():
    for value in ("", "   ", "12/05/88", "unknown"):
        with pytest.raises(ValueError):
            validate_dob(value)


def test_empty_name_is_rejected():
    g = _gen()
    with pytest.raises(ValueError):
        _render(g, first="  ")


def test_bad_dob_is_rejected():
    g = _gen()
    with pytest.raises(ValueError):
        _render(g, dob="")


def test_explicit_photo_overrides_pool(tmp_path):
    g = _gen()
    baseline = _render(g)

    photo_file = tmp_path / "photo.jpg"
    Image.new("RGB", (400, 500), (12, 200, 90)).save(photo_file, format="JPEG")

    clear_photo_cache()
    with_photo = _render(g, photo_path=str(photo_file))
    assert with_photo[:8] == b"\x89PNG\r\n\x1a\n"
    assert with_photo != baseline