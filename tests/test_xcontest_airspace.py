"""Tests for the xcontest COMP CH fetch/adapter module."""

import json
from pathlib import Path

import pytest

from app.services import xcontest_airspace as xc

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def comp_ch_data():
    return json.loads((FIXTURES / "xcontest_comp_ch.json").read_text())


def test_map_altitude():
    assert xc._map_altitude({"hfeet": 6500, "htype": "FL"}) == {
        "type": "FlightLevel",
        "val": 65,
    }
    assert xc._map_altitude({"hfeet": 500, "htype": "AGL"}) == {
        "type": "FeetAgl",
        "val": 500,
    }
    assert xc._map_altitude({"hfeet": 9500, "htype": "AMSL"}) == {
        "type": "FeetAmsl",
        "val": 9500,
    }
    assert xc._map_altitude({"hfeet": 0, "htype": "GND"}) == {"type": "Gnd"}
    assert xc._map_altitude(None) == {"type": "Gnd"}
    # a limit without a height is an altitude openair-rs-py could not read
    assert xc._map_altitude({"hfeet": None, "htype": "FL"}) == {
        "type": "Other",
        "val": "FL",
    }


def test_adapt_airspace_shape(comp_ch_data):
    raw = xc._adapt_airspace(comp_ch_data["airspaces"][0])
    assert raw["name"] == "CBA C 25 FW"
    # xcontest's airclass is the raw AC token, as openair-rs-py returns it
    assert raw["class"] == "R"
    assert "type" not in raw
    assert raw["lowerBound"] == {"type": "FlightLevel", "val": 65}
    assert raw["geom"]["type"] == "Polygon"
    # [lat, lng] pairs become {type, lat, lng} point segments
    assert raw["geom"]["segments"][0] == {"type": "Point", "lat": 47.74, "lng": 5.60}


def test_adapt_airspace_without_name_or_class():
    raw = xc._adapt_airspace({"polygon": [[46.9, 8.4]]})
    assert raw["name"] is None
    assert raw["class"] == "UNC"


def test_adapted_airspaces_get_the_same_colours_as_parsed_ones(comp_ch_data):
    from app.model.openair_types import convert_raw_airspace
    from app.utils.geojson_converter import convert_airspace_to_geojson

    airspaces = [
        convert_raw_airspace(xc._adapt_airspace(a)) for a in comp_ch_data["airspaces"]
    ]
    props = [
        f["properties"] for f in convert_airspace_to_geojson(airspaces)["features"]
    ]
    assert [(p["class"], p["color"]) for p in props] == [
        ("Restricted", "#ffc107"),
        ("Prohibited", "#ff5722"),
        ("D", "#9c27b0"),
    ]


def test_fetch_comp_ch_uses_channel_and_data(monkeypatch, comp_ch_data):
    comp_id = int(comp_ch_data["oaid"])
    comp_name = comp_ch_data["name"]

    def fake_get_json(path):
        if path == "/api/v6/files":
            return [
                {"oaid": comp_id, "name": comp_name, "channame": "COMP CH"},
                {"oaid": 999, "name": "Other", "channame": "Switzerland"},
            ]
        assert path == f"/api/v6/data/{comp_id}"
        return comp_ch_data

    monkeypatch.setattr(xc, "_get_json", fake_get_json)
    raw_airspaces, label = xc.fetch_comp_ch()
    assert len(raw_airspaces) == 3
    assert "COMP CH" in label and comp_name in label


def test_fetch_comp_ch_raises_when_channel_empty(monkeypatch):
    monkeypatch.setattr(xc, "_get_json", lambda path: [])
    with pytest.raises(ValueError):
        xc.fetch_comp_ch()
