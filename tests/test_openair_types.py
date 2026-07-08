"""Tests for the typed OpenAir model and raw-dict conversion."""

from app.model.openair_types import (
    Altitude,
    AltitudeType,
    CircleGeometry,
    PolygonGeometry,
    convert_raw_airspace,
)


def test_altitude_to_text():
    assert Altitude(AltitudeType.GND).to_text() == "GND"
    assert Altitude(AltitudeType.UNLIMITED).to_text() == "Unlimited"
    assert Altitude(AltitudeType.FLIGHT_LEVEL, 75).to_text() == "FL 75"
    # feet are converted to metres
    assert Altitude(AltitudeType.FEET_AMSL, 5000).to_text() == "1524 m AMSL"
    assert Altitude(AltitudeType.FEET_AGL, 1000).to_text() == "304 m AGL"


def test_convert_raw_polygon():
    raw = {
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
    raw = {
        "name": "TEST CIRCLE",
        "class": "R",
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
    airspace = convert_raw_airspace(raw)
    assert airspace.lower_bound is not None
    assert airspace.lower_bound.type == AltitudeType.OTHER
