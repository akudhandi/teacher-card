"""Determinism + watermark tests for the demo/testing pipeline."""

from io import BytesIO

from PIL import Image

from countries import get_country
from countries.utils import finalize_document, clear_photo_cache


def _render(seed, watermark=False, doc_type="teacher_id"):
    gen = get_country("us")()
    gen._current_person_id = "john_smith"
    gen._current_gender = "Male"
    clear_photo_cache()
    return gen.generate_document_seeded(
        doc_type=doc_type,
        first="John",
        last="Smith",
        school=gen.schools[0],
        position="Head of Science Department",
        dob="12/05/1988",
        seed=seed,
        watermark=watermark,
    )


def test_same_seed_is_reproducible():
    assert _render(seed=1234) == _render(seed=1234)


def test_different_seed_changes_output():
    assert _render(seed=1234) != _render(seed=5678)


def test_watermark_changes_output():
    plain = _render(seed=1234, watermark=False)
    stamped = _render(seed=1234, watermark=True)
    assert plain != stamped
    assert stamped[:8] == b"\x89PNG\r\n\x1a\n"


def test_finalize_document_returns_valid_png():
    plain = _render(seed=1234)
    stamped = finalize_document(plain, watermark=True)
    assert stamped[:8] == b"\x89PNG\r\n\x1a\n"
    with Image.open(BytesIO(stamped)) as img:
        img.load()
        assert img.size[0] > 0 and img.size[1] > 0


def test_finalize_document_noop_when_disabled():
    plain = _render(seed=1234)
    assert finalize_document(plain, watermark=False) == plain