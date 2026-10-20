"""Render the task viewer page and check every static file it links resolves."""

import re
from pathlib import Path

import pytest

import app.utils.route_helpers as route_helpers

SAMPLE_TASK = Path(__file__).parent / "fixtures" / "sample_task.xctsk"
STATIC_URL = re.compile(r'(?:href|src)="(/static/[^"]+)"')


@pytest.fixture(autouse=True)
def no_umami(monkeypatch):
    """Keep the upload route from sending analytics events over the network."""
    monkeypatch.setattr(route_helpers.umami, "new_page_view", lambda **_: None)
    monkeypatch.setattr(route_helpers.umami, "new_event", lambda **_: None)


def assert_static_files_resolve(client, html: str) -> list[str]:
    """Fetch every /static/ URL the page links and assert each one is served."""
    urls = STATIC_URL.findall(html)
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200, url
        response.close()
    return urls


def test_uploaded_task_renders_map_and_its_scripts(client):
    """An uploaded task renders the map and loads every map script and style."""
    with SAMPLE_TASK.open("rb") as f:
        response = client.post(
            "/xctsk/upload",
            data={"xctsk_file": (f, "sample_task.xctsk")},
            content_type="multipart/form-data",
        )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "initMap(" in html
    assert "Turnpoints" in html
    urls = assert_static_files_resolve(client, html)
    for name in (
        "css/task_viewer.css",
        "js/airspace_lookup.js",
        "js/airspace_profile.js",
        "js/airspace_sideview.js",
        "js/airspace_overlay.js",
        "js/task_map.js",
        "js/local_time.js",
    ):
        assert f"/static/{name}" in urls


def test_index_renders_load_form(client):
    """The landing page renders the load form partial and no map."""
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="loadform"' in html
    assert "initMap(" not in html
    assert_static_files_resolve(client, html)


def test_invalid_task_code_renders_error(client):
    """A blank task code renders the error alert without fetching anything."""
    response = client.get("/xctsk/view/%20")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Task not found!" in html
    assert 'id="loadform"' in html
