# XCTSK Viewer

A Flask app that shows paragliding competition tasks (XCTSK files) as turnpoint tables, distances, a QR code and a Leaflet map, with an optional OpenAir airspace overlay. Server-rendered Jinja2 pages call blueprints in `app/routes/`, which delegate to `app/services/` for the two pipelines: tasks (fetched from `tools.xcontest.org` or uploaded, processed by the `pyxctsk` package) and airspace (OpenAir files or the xcontest COMP CH layer, converted to GeoJSON). The map JS in `app/static/js/` gets the task GeoJSON from `app/templates/task_viewer.html` and the airspace overlay from `/api/airspaces*`.
Domain terms are in `GLOSSARY.md`; decisions and their trade-offs go in `docs/adr/` (none yet).

## Commands

```bash
uv sync  # install deps and dev tools into .venv
uv run lefthook install  # install git hooks, once per clone
uv run python run.py  # dev server on http://localhost:8080
uv run pytest  # run all tests
uv run pytest tests/test_airspace_service.py  # run one test file
uv run pytest tests/test_airspace_service.py::test_name  # run one test
uv run ruff check --fix .  # lint and autofix
uv run ruff check app/routes/api.py  # lint one file
uv run ruff format .  # format
uv run mypy --explicit-package-bases --config-file mypy.ini app tests  # type-check, as CI runs it
uv run rumdl check .  # lint Markdown; `uv run rumdl fmt .` fixes
npx --yes cspell --no-progress --config cspell.json app/routes/api.py  # spell-check files
uv lock  # refresh uv.lock after editing pyproject.toml
```

Hooks: Ruff, mypy, rumdl, cspell and the per-file token budget (`scripts/hooks/check-file-tokens.py`, 5,000 tokens) run on staged files at pre-commit, pytest at pre-push. CI runs all but the token budget on Python 3.12 and 3.14.

## Conventions

### Scope

- **Build only what was asked.** Don't add features, fallbacks or config options nobody requested.

### Routes

- **Routes are blueprints.** Add a blueprint under `app/routes/` and register it in `create_app()` in `app/__init__.py`.
- **Route handlers stay thin.** Parsing and business logic live in `app/services/` and `app/utils/`, never in a route handler.

### Tasks

- **Task fetching and processing live only in `XCTSKService`** (`app/services/xctsk_service.py`). Don't fetch or parse tasks anywhere else.
- **`pyxctsk` owns the task format.** Parsing, distances, GeoJSON and QR codes come from it; never re-implement them.
- **Task routes go through `app/utils/route_helpers.py`.** Its wrappers fetch or parse the task, send the Umami analytics events and fill the task cache.
- **Processed tasks are cached under `task_data_<code>`** in the in-memory `TaskCache` (`app/utils/task_cache.py`, 5-minute TTL). The JSON, QR and KML endpoints in `app/routes/api.py` read from it and re-fetch on a miss.

### Airspace

- **Every airspace source converges on one pipeline.** Raw `openair.types.Airspace` dicts → `convert_raw_airspace` (`app/model/openair_types.py`) → `convert_airspace_to_geojson` (`app/utils/geojson_converter.py`). A new source adapts its data to the raw dict shape, as `app/services/xcontest_airspace.py` does.
- **Class names come only from `display_class()`** in `app/model/openair_types.py`. It maps raw OpenAir `AC`/`AY` tokens (`"R"`, `"Q"`, `"UNC"` + `AY R`, …) to the names colours, legend and stats are keyed by (`"Restricted"`, `"Danger"`, …); unmapped tokens pass through.
- **Airspace colours live only in `app/utils/airspace_colors.py`.** They reach the browser as each GeoJSON feature's `color` property; don't hard-code class colours in JS or CSS.

### Frontend

- **Leaflet loads from a CDN** in the templates; nothing is bundled. Custom CSS goes in `app/static/css/style.css`; the map page's in `app/static/css/task_viewer.css`, linked after Leaflet's CSS so it overrides it.
- **The task map's JS lives in `app/static/js/`** as plain scripts the task page loads in order: `airspace_lookup.js` (shared helpers), `airspace_profile.js`, `airspace_sideview.js`, `airspace_overlay.js`, then `task_map.js`, whose `initMap(geojson)` the page calls with the task GeoJSON.

### Dependencies and spelling

- **Use `uv`, not `pip`.** Add a dependency to `pyproject.toml`, then run `uv lock`.
- **Unknown but correct words go in `cspell-dictionary.txt`.**

## Hard constraints

- **Never pass `normalize_legacy_classes=True` to openair.** It rejects a whole file when a legacy `AC` disagrees with its `AY`, which the French files do (`AC R` + `AY RTBA`).
- **Never commit a real `FLASK_SECRET_KEY`.** It is a Fly.io secret; the default in `create_app()` is a placeholder for local use only.

## Gotchas

- **Merging to `main` deploys to production** (`.github/workflows/fly-deploy.yml`), without waiting for CI.
- **`AirspaceService` is a module-global singleton** (`get_airspace_service()`) holding one active dataset. The autouse `reset_airspace_singleton` fixture in `tests/conftest.py` resets it around every test.
- **State lives in process memory.** The task cache and the airspace dataset are per process, which is why production runs one machine.
- **`uv sync` undoes a git install of `pyxctsk`.** See `docs/setup.md` for developing against the unreleased version.
- **Only `.xctsk` files are accepted as task uploads; airspace uploads take `.txt`, `.air` and `.openair`.**

## Docs

- `README.md` — what the project is and the quickstart.
- `docs/setup.md` — local setup, unreleased `pyxctsk`, code-quality tools, Docker; read when the environment misbehaves.
- `docs/deployment.md` — Fly.io release flow, secrets and scaling; read before touching `fly.toml`, the `Dockerfile` or the deploy workflow.
- `.env.example` — every env var, annotated.
- `GLOSSARY.md` — domain terms and the words to avoid.
