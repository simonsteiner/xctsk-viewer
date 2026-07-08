# Copilot Instructions for xctsk-viewer

## Simplicity & Maintainability
- Do **not** add features, fallbacks, or config unless explicitly requested.
- Keep code clean, minimal, and easy to understand. Use meaningful names; avoid over-engineering.
- Use concise comments to explain non-obvious or complex logic.

## Clarify Before Acting
- If requirements are ambiguous, **ask for clarification** before proceeding.

## Manual Execution & Environment
- Assume all scripts/commands are run manually unless automation is **explicitly requested**.
- This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Run commands via `uv run ...` instead of calling `python` or `flask` directly.
- Do not add new dependencies without updating `pyproject.toml`; run `uv lock` to refresh `uv.lock`.

## Project Architecture
- **Flask app** for visualizing XCTSK files (paragliding competition tasks for XCTrack).
- Core logic is in `app/`:
  - `routes/`: Flask blueprints for UI and static file serving.
  - `services/`: Business logic, especially `xctsk_service.py` for task download/processing.
  - `utils/`: Flask helpers for rendering, validation, and file handling.
  - `templates/` and `static/`: Jinja2 HTML and static assets.

## Key Workflows
- **Run locally:** `uv run python run.py` (Flask runs on port 8080).
- **Install dependencies:** `uv sync` (creates `.venv` automatically).
- **Lint/format/type-check:** `uv run ruff check --fix .`, `uv run ruff format .`, `uv run mypy ...` (run automatically on commit via lefthook).
- **Deploy:** Use Fly.io with `fly deploy` (see `fly.toml`). Dockerfile provided for container builds.
- **Testing:** `uv run pytest` runs the pytest suite in `tests/` (run automatically on push via lefthook). Fixtures live in `tests/conftest.py` and `tests/fixtures/`.

## Patterns & Conventions
- Register new routes as blueprints in `app/routes/` and add to `create_app()` in `app/__init__.py`.
- All XCTSK file/network logic is in `XCTSKService` (`app/services/xctsk_service.py`).
- Use the published `pyxctsk` PyPI package for all XCTSK parsing, QR, and data model logic.
- Only `.xctsk` files are accepted for upload (see `validate_xctsk_file`).
- Custom CSS in `app/static/css/style.css`.
- Set `FLASK_SECRET_KEY` for production (see README for Fly.io secrets).

## Integration Points
- Downloads XCTSK tasks from `https://tools.xcontest.org` via HTTP.
- Uses `qrcode`, `pyzbar`, and `Pillow` for QR code features.
- The `pyxctsk` package provides conversion and analysis tools for XCTSK files.

## Examples
- To add a new route: create a blueprint in `app/routes/` and register it in `app/__init__.py`.
- To process a new XCTSK file type: update `XCTSKService` as needed to work with the `pyxctsk` package.

## Important Notes
- Keep logic for XCTSK parsing and business rules in `services/` and use the `pyxctsk` package—not in route handlers.
- Avoid unnecessary configuration or complexity without clear need or request.
