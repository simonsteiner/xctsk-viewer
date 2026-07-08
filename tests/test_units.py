"""Tests for unit-conversion helpers."""

import pytest

from app.utils.units import (
    feet_to_meters,
    kilometers_to_meters,
    meters_to_feet,
    meters_to_nautical_miles,
    nautical_miles_to_meters,
    statute_miles_to_meters,
)


def test_feet_meters_roundtrip():
    assert meters_to_feet(feet_to_meters(1000)) == pytest.approx(1000)


def test_nautical_miles_to_meters():
    assert nautical_miles_to_meters(1) == pytest.approx(1852)
    assert meters_to_nautical_miles(1852) == pytest.approx(1)


def test_other_conversions():
    assert feet_to_meters(1) == pytest.approx(0.3048)
    assert statute_miles_to_meters(1) == pytest.approx(1609.344)
    assert kilometers_to_meters(1) == pytest.approx(1000)
