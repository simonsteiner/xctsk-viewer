"""Tests for the AirspaceService."""

from app.services.airspace_service import AirspaceService


def test_default_dataset_loads_switzerland():
    service = AirspaceService()
    airspaces, geojson = service.load_airspace_data()
    assert airspaces, "expected the bundled Switzerland dataset to load"
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == len(airspaces)
    assert service.get_current_filename() == "Switzerland.txt"


def test_current_filename_fallback_is_a_basename():
    # Before anything is loaded the fallback must be a bare filename, not a path
    service = AirspaceService()
    assert service.get_current_filename() == "Switzerland.txt"


def test_stats_report_total_and_classes():
    service = AirspaceService()
    stats = service.get_airspace_stats()
    assert stats["total_airspaces"] > 0
    assert isinstance(stats["classes"], dict)
    assert sum(stats["classes"].values()) == stats["total_airspaces"]


def test_load_from_uploaded_file(sample_airspace_path):
    service = AirspaceService()
    success, error = service.load_from_uploaded_file(sample_airspace_path, "sample.txt")
    assert success is True
    assert error is None
    airspaces, geojson = service.get_cached_data()
    assert len(airspaces) == 2  # one polygon + one circle
    assert service.get_current_filename() == "sample.txt"


def test_reset_to_default_after_upload(sample_airspace_path):
    service = AirspaceService()
    service.load_from_uploaded_file(sample_airspace_path, "sample.txt")
    service.reset_to_default()
    airspaces, _ = service.get_cached_data()
    assert len(airspaces) > 2
    assert service.get_current_filename() == "Switzerland.txt"
