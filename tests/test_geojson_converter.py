"""Tests for the airspace -> GeoJSON conversion."""

from app.model.openair_types import (
    Airspace,
    Altitude,
    AltitudeType,
    CircleGeometry,
    Point,
    PolygonGeometry,
)
from app.utils.geojson_converter import altitude_to_text, convert_airspace_to_geojson


def _polygon(points):
    return PolygonGeometry(segments=[Point(lat=la, lng=ln) for la, ln in points])


def test_altitude_to_text_accepts_objects_and_dicts():
    assert altitude_to_text(Altitude(AltitudeType.GND)) == "GND"
    assert altitude_to_text({"type": "FeetAmsl", "val": 5000}) == "1524 m AMSL"
    assert altitude_to_text({"type": "Bogus"}) == "?(None)"


def test_polygon_becomes_closed_polygon_feature():
    airspace = Airspace(
        name="P", class_="D", geom=_polygon([(46.9, 8.4), (46.95, 8.5), (46.8, 8.45)])
    )
    fc = convert_airspace_to_geojson([airspace])
    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 1
    geom = fc["features"][0]["geometry"]
    assert geom["type"] == "Polygon"
    ring = geom["coordinates"][0]
    # ring is closed and uses [lng, lat] ordering
    assert ring[0] == ring[-1]
    assert ring[0] == [8.4, 46.9]


def test_two_point_polygon_becomes_linestring():
    airspace = Airspace(
        name="Cable", class_="Danger", geom=_polygon([(46.9, 8.4), (46.95, 8.5)])
    )
    feature = convert_airspace_to_geojson([airspace])["features"][0]
    assert feature["geometry"]["type"] == "LineString"
    assert feature["properties"]["geometryType"] == "line"


def test_circle_becomes_polygon_approximation():
    airspace = Airspace(
        name="C",
        class_="R",
        geom=CircleGeometry(centerpoint={"lat": 46.5, "lng": 8.2}, radius=3.0),
    )
    geom = convert_airspace_to_geojson([airspace])["features"][0]["geometry"]
    assert geom["type"] == "Polygon"
    # 36 points around the circle plus the closing point
    assert len(geom["coordinates"][0]) == 37


def test_feature_properties_include_colour_and_bounds():
    airspace = Airspace(
        name="P",
        class_="D",
        lower_bound=Altitude(AltitudeType.GND),
        upper_bound=Altitude(AltitudeType.FEET_AMSL, 5000),
        geom=_polygon([(46.9, 8.4), (46.95, 8.5), (46.8, 8.45)]),
    )
    props = convert_airspace_to_geojson([airspace])["features"][0]["properties"]
    assert props["class"] == "D"
    assert props["lowerBound"] == "GND"
    assert props["upperBound"] == "1524 m AMSL"
    assert props["color"].startswith("#")
