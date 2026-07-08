"""Tests for the airspace API routes."""

import io


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


def test_reset_restores_default(client, sample_airspace_bytes):
    client.post(
        "/api/airspaces/upload",
        data={"file": (io.BytesIO(sample_airspace_bytes), "sample.txt")},
        content_type="multipart/form-data",
    )
    resp = client.post("/api/airspaces/reset")
    assert resp.status_code == 200
    assert resp.get_json()["filename"] == "Switzerland.txt"
