"""Tests for XCTSKService.process_task_data (the pyxctsk integration)."""

import json

from app.services.xctsk_service import XCTSKService


def _waypoint(name: str, lat: float, lon: float) -> dict:
    return {"name": name, "lat": lat, "lon": lon, "altSmoothed": 500}


def _task_json(goal: dict | None) -> str:
    task: dict = {
        "taskType": "CLASSIC",
        "version": 1,
        "earthModel": "WGS84",
        "turnpoints": [
            {"type": "TAKEOFF", "radius": 400, "waypoint": _waypoint("TO", 46.0, 8.0)},
            {"type": "SSS", "radius": 3000, "waypoint": _waypoint("S", 46.0, 8.0)},
            {"radius": 1000, "waypoint": _waypoint("TP", 46.2, 8.2)},
            {"type": "ESS", "radius": 1000, "waypoint": _waypoint("E", 46.3, 8.0)},
            {"radius": 200, "waypoint": _waypoint("G", 46.3, 8.0)},
        ],
    }
    if goal is not None:
        task["goal"] = goal
    return json.dumps(task)


def test_process_task_without_goal_defaults_to_cylinder():
    ok, message, info = XCTSKService().process_task_data(_task_json(goal=None))

    assert ok, message
    assert info is not None
    # The distances stay a plain dict: the JSON API serves them as-is.
    assert isinstance(info["distances"], dict)
    assert info["distances"]["optimized_distance_km"] > 0
    assert info["metadata"]["goal_type"] == "CYLINDER"
    assert info["turnpoints"][-1]["type"] == "Goal"
    assert info["qr_code"].startswith("XCTSK:")
    assert info["qr_code_base64"]
    assert info["geojson"]["features"]


def test_process_task_with_goal_line():
    goal = {"type": "LINE", "deadline": "17:00:00Z"}
    ok, message, info = XCTSKService().process_task_data(_task_json(goal=goal))

    assert ok, message
    assert info is not None
    assert info["metadata"]["goal_type"] == "LINE"
    assert info["metadata"]["goal_deadline"] == "17:00 (UTC)"
    assert info["turnpoints"][-1]["type"] == "Goal Line (400m)"
