# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Flask web app that visualizes XCTSK files (paragliding competition tasks for XCTrack). Users load a task by its xcontest task code or by uploading a `.xctsk` file, and see turnpoints, distances, task metadata, a QR code, and an interactive Leaflet map. An optional airspace overlay renders OpenAir airspace data on the map.

## Commands

Uses [uv](https://docs.astral.sh/uv/) for dependency management; run everything through `uv run`.

```bash
uv sync                              # install deps + dev tools, creates .venv
uv run lefthook install              # install git hooks (once per clone)
uv run python run.py                 # run dev server on http://localhost:8080

uv run pytest                        # run the full test suite
uv run pytest tests/test_airspace_service.py            # single file
uv run pytest tests/test_airspace_service.py::test_name # single test

uv run ruff check --fix .            # lint + autofix
uv run ruff format .                 # format
uv run mypy --explicit-package-bases --config-file mypy.ini app   # type-check
npx cspell --config cspell.json "app/**"                          # spell-check
```

`ruff`, `mypy` and `cspell` run on staged files at **pre-commit**; `pytest` runs at **pre-push** (see `lefthook.yml`). Skip with `git commit --no-verify`.

To develop against the unreleased `pyxctsk` from GitHub instead of the pinned PyPI release:
`uv pip install --reinstall "pyxctsk @ git+https://github.com/simonsteiner/pyxctsk"` (re-running `uv sync` restores the PyPI version).

## Architecture

Standard Flask app-factory layout. `create_app()` in `app/__init__.py` registers four blueprints, each in `app/routes/`:

- **`main.py`** — HTML pages: task viewer (`/`, `/xctsk/view/<code>`), file upload (`/xctsk/upload`), about.
- **`api.py`** — JSON/binary task endpoints: task data, QR PNG, KML download.
- **`static_routes.py`** — favicons, webmanifest, and a proxy for the Umami `stats.js`.
- **`airspace.py`** — airspace overlay API (`/api/airspaces*`): get, stats, upload, reset, and `comp-ch` fetch.

Two independent data pipelines run through the `services/` layer. Keep parsing and business logic in `services/`/`utils/`, not in route handlers.

### XCTSK task pipeline

`XCTSKService` (`services/xctsk_service.py`) is the single entry point for all task file/network logic:
1. `download_task_data` fetches raw XCTSK JSON from `https://tools.xcontest.org` (session with retry/backoff).
2. `process_task_data` runs it through the **`pyxctsk`** PyPI package (`parse_task`, `calculate_task_distances`, `generate_task_geojson`, `QRCodeTask`) and assembles a task-info dict (task object, distances, GeoJSON, formatted turnpoints, metadata, QR code).

Route handlers call thin wrappers in `utils/route_helpers.py` (`process_xctsk_task`, `process_uploaded_xctsk_file`, `render_task_viewer`, `validate_xctsk_file`) which also emit Umami analytics events. Processed task dicts are cached in a **module-global in-memory `TaskCache`** (`utils/task_cache.py`, thread-safe, 5-min TTL) keyed `task_data_<code>`; the JSON/QR/KML API endpoints read from this cache and fall back to re-fetching. Only `.xctsk` files are accepted for upload.

### Airspace pipeline

`AirspaceService` (`services/airspace_service.py`) is a **module-global singleton** (`get_airspace_service()`) holding one active airspace dataset, cached as both typed objects and GeoJSON. The active dataset can come from three sources, all converging on the same conversion pipeline:
- bundled default OpenAir file `app/examples/Switzerland.txt`,
- a user-uploaded OpenAir file (`.txt`/`.air`/`.openair`),
- the live xcontest "COMP CH" competition layer via `services/xcontest_airspace.py` (`fetch_comp_ch`, uses the unauthenticated `airspace.xcontest.org/api/v6` JSON API).

Conversion flow for every source:
`parse_file` (the `openair` / `openair-rs-py` package) or adapted JSON → raw dicts → `convert_raw_airspace` → typed `Airspace` objects (`model/openair_types.py`) → `convert_airspace_to_geojson` (`utils/geojson_converter.py`, expands circles/arcs into polygons). Airspace class colors are centralized in `utils/airspace_colors.py` (single source of truth mirrored in Python/JS/CSS).

### Frontend

Server-rendered Jinja2 templates in `app/templates/` (`base.html`, `task_viewer.html`, `about.html`); custom CSS in `app/static/css/style.css`. The map is **Leaflet** (loaded from CDN in the templates, not bundled). `task_viewer.html` contains the bulk of the map JS inline: it renders the task GeoJSON and fetches `/api/airspaces` to draw the toggleable airspace overlay, legend, and upload control.

## Conventions

- New routes: add a blueprint under `app/routes/` and register it in `create_app()`.
- Ruff enforces `E`, `F`, `I` (isort), and `D` (Google-style docstrings); line length is handled by the formatter. Tests are exempt from docstring rules.
- Add new deps to `pyproject.toml`, then `uv lock` to refresh `uv.lock`. Add unknown-but-correct words to `cspell-dictionary.txt`.
- `FLASK_SECRET_KEY` must be set in production (the default in `create_app()` is a placeholder); see README for Fly.io deployment.

## Testing notes

`tests/` uses pytest with fixtures in `tests/conftest.py`. The `reset_airspace_singleton` autouse fixture resets the module-global `AirspaceService` around every test — important because the singleton would otherwise leak dataset state between tests. Fixtures/sample OpenAir data live in `tests/fixtures/`.
