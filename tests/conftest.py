"""Shared pytest fixtures for the Yowes document generator."""

import pytest

from countries import get_country, list_countries


@pytest.fixture(params=list_countries())
def country_code(request):
    """Every registered country code, one test run each."""
    return request.param


@pytest.fixture
def sample_person():
    """Fixed person inputs so tests are reproducible."""
    return {
        "first": "John",
        "last": "Smith",
        "position": "Head of Science Department",
        "dob": "12/05/1988",
        "gender": "Male",
    }


@pytest.fixture
def generator(country_code):
    """A generator instance plus its first school."""
    gen = get_country(country_code)()
    gen._current_person_id = "john_smith"
    gen._current_gender = "Male"
    return gen
