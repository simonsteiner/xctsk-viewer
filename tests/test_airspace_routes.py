"""Tests for the airspace API routes."""

import io

import requests

import app.routes.airspace as airspace_routes


def test_get_airspaces_returns_feature_collection(client):
    resp = client.get("/api/airspaces")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0


def test_get_airspace_stats(client):
    resp = client.get("/api/airspaces/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_airspaces"] > 0
    assert data["filename"] == "Switzerland.txt"
    assert isinstance(data["classes"], dict)


def test_upload_custom_airspace(client, sample_airspace_bytes):
    data = {"file": (io.BytesIO(sample_airspace_bytes), "sample.txt")}
    resp = client.post(
        "/api/airspaces/upload", data=data, content_type="multipart/form-data"
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["filename"] == "sample.txt"
    assert body["count"] == 2
    # the active dataset is now the uploaded one
    assert client.get("/api/airspaces/stats").get_json()["filename"] == "sample.txt"


def test_upload_rejects_bad_extension(client):
    data = {"file": (io.BytesIO(b"nope"), "bad.pdf")}
    resp = client.post(
        "/api/airspaces/upload", data=data, content_type="multipart/form-data"
    )
    assert resp.status_code == 400
    assert "Invalid file type" in resp.get_json()["error"]


def test_upload_requires_a_file(client):
    resp = client.post(
        "/api/airspaces/upload", data={}, content_type="multipart/form-data"
    )
    assert resp.status_code == 400


def test_load_comp_ch(client, monkeypatch):
    raw = [
        {
            "name": "CBA C 25 FW",
            "class": "Restricted",
            "lowerBound": {"type": "FlightLevel", "val": 65},
            "upperBound": {"type": "FlightLevel", "val": 195},
            "geom": {
                "type": "Polygon",
                "segments": [
                    {"type": "Point", "lat": 47.7, "lng": 5.6},
                    {"type": "Point", "lat": 47.6, "lng": 6.0},
                    {"type": "Point", "lat": 47.4, "lng": 5.6},
                ],
            },
        }
    ]
    monkeypatch.setattr(
        airspace_routes, "fetch_comp_ch", lambda: (raw, "COMP CH: Test 2026")
    )
    resp = client.post("/api/airspaces/comp-ch")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] == 1
    assert body["filename"] == "COMP CH: Test 2026"
    # the active dataset is now COMP CH
    assert (
        client.get("/api/airspaces/stats").get_json()["filename"]
        == "COMP CH: Test 2026"
    )


def test_errors_do_not_leak_stacktrace_outside_debug(client, monkeypatch):
    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(airspace_routes, "get_airspace_service", boom)
    resp = client.get("/api/airspaces")
    assert resp.status_code == 500
    # no Python traceback is exposed to clients when not in debug mode
    assert "stacktrace" not in resp.get_json()


def test_load_comp_ch_upstream_failure_returns_502(client, monkeypatch):
    def boom():
        raise requests.RequestException("connection refused")

    monkeypatch.setattr(airspace_routes, "fetch_comp_ch", boom)
    resp = client.post("/api/airspaces/comp-ch")
    assert resp.status_code == 502


def test_reset_restores_default(client, sample_airspace_bytes):
    client.post(
        "/api/airspaces/upload",
        data={"file": (io.BytesIO(sample_airspace_bytes), "sample.txt")},
        content_type="multipart/form-data",
    )
    resp = client.post("/api/airspaces/reset")
    assert resp.status_code == 200
    assert resp.get_json()["filename"] == "Switzerland.txt"
