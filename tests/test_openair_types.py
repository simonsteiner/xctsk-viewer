"""Tests for the typed OpenAir model and raw-dict conversion."""

from typing import cast

import pytest
from openair.types import Airspace as RawAirspace

from app.model.openair_types import (
    Airspace,
    Altitude,
    AltitudeType,
    CircleGeometry,
    PolygonGeometry,
    convert_raw_airspace,
    display_class,
)
from app.utils.airspace_colors import AIRSPACE_COLORS


def test_altitude_to_text():
    assert Altitude(AltitudeType.GND).to_text() == "GND"
    assert Altitude(AltitudeType.UNLIMITED).to_text() == "Unlimited"
    assert Altitude(AltitudeType.FLIGHT_LEVEL, 75).to_text() == "FL 75"
    # feet are converted to metres
    assert Altitude(AltitudeType.FEET_AMSL, 5000).to_text() == "1524 m AMSL"
    assert Altitude(AltitudeType.FEET_AGL, 1000).to_text() == "304 m AGL"


def test_convert_raw_polygon():
    raw: RawAirspace = {
        "name": "TEST CTR",
        "class": "D",
        "lowerBound": {"type": "Gnd"},
        "upperBound": {"type": "FeetAmsl", "val": 5000},
        "geom": {
            "type": "Polygon",
            "segments": [
                {"type": "Point", "lat": 46.9, "lng": 8.4},
                {"type": "Point", "lat": 46.95, "lng": 8.5},
                {"type": "Point", "lat": 46.8, "lng": 8.45},
            ],
        },
    }
    airspace = convert_raw_airspace(raw)
    assert airspace.name == "TEST CTR"
    assert airspace.airspace_class == "D"
    assert isinstance(airspace.geom, PolygonGeometry)
    assert airspace.geom.segments is not None
    assert len(airspace.geom.segments) == 3
    assert airspace.upper_bound is not None
    assert airspace.upper_bound.to_text() == "1524 m AMSL"


def test_convert_raw_circle():
    raw: RawAirspace = {
        "name": "TEST CIRCLE",
        "class": "R",
        "lowerBound": {"type": "Gnd"},
        "upperBound": {"type": "FlightLevel", "val": 130},
        "geom": {
            "type": "Circle",
            "centerpoint": {"lat": 46.5, "lng": 8.2},
            "radius": 3.0,
        },
    }
    airspace = convert_raw_airspace(raw)
    assert isinstance(airspace.geom, CircleGeometry)
    assert airspace.geom.radius == 3.0
    assert airspace.geom.centerpoint == {"lat": 46.5, "lng": 8.2}


def test_convert_raw_unknown_altitude_type_falls_back_to_other():
    raw = {"name": "X", "class": "E", "lowerBound": {"type": "Bogus", "val": 1}}
    airspace = convert_raw_airspace(cast(RawAirspace, raw))
    assert airspace.lower_bound is not None
    assert airspace.lower_bound.type == AltitudeType.OTHER


@pytest.mark.parametrize(
    ("ac", "ay", "expected"),
    [
        # standard classes are unchanged
        ("D", None, "D"),
        ("CTR", None, "CTR"),
        # legacy AC tokens get the names openair-rs-py 0.1.x returned
        ("R", None, "Restricted"),
        ("Q", None, "Danger"),
        ("P", None, "Prohibited"),
        ("GP", None, "GliderProhibited"),
        ("W", None, "WaveWindow"),
        ("FFVL", None, "Ffvl"),
        ("NOTAM ref", None, "NotamRef"),
        # the AY type does not override a real class
        ("D", "TMA", "D"),
        ("R", "RTBA", "Restricted"),
        # OpenAir v2: AC UNC is shown by its AY type
        ("UNC", "R", "Restricted"),
        ("UNC", "CTR", "CTR"),
        ("UNC", "TMA", "TMA"),
        ("UNC", "NONE", "UNC"),
        ("UNC", None, "UNC"),
        # tokens nobody maps pass through
        ("XYZ", None, "XYZ"),
    ],
)
def test_display_class(ac, ay, expected):
    assert display_class(ac, ay) == expected


def test_every_coloured_class_is_reachable_from_a_token():
    # a colour keyed by a name no token maps to would never be used
    reachable = {display_class(t) for t in ("A", "B", "C", "D", "E", "CTR", "R")}
    reachable |= {display_class(t) for t in ("Q", "P", "GP", "W")}
    assert set(AIRSPACE_COLORS) <= reachable


def test_convert_raw_keeps_tokens_and_shows_display_class():
    raw: RawAirspace = {
        "name": "V2 DANGER",
        "class": "UNC",
        "type": "Q",
        "lowerBound": {"type": "Gnd"},
        "upperBound": {"type": "FlightLevel", "val": 95},
        "geom": {"type": "Polygon", "segments": []},
        "frequency": "123.450",
    }
    airspace = convert_raw_airspace(raw)
    assert airspace.class_ == "UNC"
    assert airspace.type_ == "Q"
    assert airspace.airspace_class == "Danger"


def test_convert_raw_name_none():
    raw: RawAirspace = {
        "name": None,
        "class": "D",
        "lowerBound": {"type": "Gnd"},
        "upperBound": {"type": "Unlimited"},
        "geom": {"type": "Polygon", "segments": []},
    }
    assert convert_raw_airspace(raw).name is None


def test_other_altitude_is_shown_verbatim():
    raw: RawAirspace = {
        "name": "X",
        "class": "R",
        "lowerBound": {"type": "Gnd"},
        "upperBound": {"type": "Other", "val": "4500.0.5FT"},
        "geom": {"type": "Polygon", "segments": []},
    }
    airspace = convert_raw_airspace(raw)
    assert isinstance(airspace, Airspace)
    assert airspace.upper_bound is not None
    assert airspace.upper_bound.to_text() == "?(4500.0.5FT)"
