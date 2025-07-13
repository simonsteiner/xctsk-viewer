# Copilot Instructions for xctsk-viewer

## Simplicity & Maintainability
- Do **not** add features, fallbacks, or config unless explicitly requested.
- Keep code clean, minimal, and easy to understand. Use meaningful names; avoid over-engineering.
- Use concise comments to explain non-obvious or complex logic.

## Clarify Before Acting
- If requirements are ambiguous, **ask for clarification** before proceeding.

## Manual Execution & Environment
- Assume all scripts/commands are run manually unless automation is **explicitly requested**.
- Always use the local Python environment `.venv/bin/python` instead of `python` or `flask`.
- Do not add new dependencies without updating `requirements.txt` and `pyproject.toml`.

## Project Architecture
- **Flask app** for visualizing XCTSK files (paragliding competition tasks for XCTrack).
- Core logic is in `app/`:
  - `routes/`: Flask blueprints for UI and static file serving.
  - `services/`: Business logic, especially `xctsk_service.py` for task download/processing.
  - `utils/`: Flask helpers for rendering, validation, and file handling.
  - `templates/` and `static/`: Jinja2 HTML and static assets.

## Key Workflows
- **Run locally:** `.venv/bin/python run.py` (Flask runs on port 8080).
- **Install dependencies:** `pip install -e .` in an activated `.venv`.
- **Deploy:** Use Fly.io with `fly deploy` (see `fly.toml`). Dockerfile provided for container builds.
- **Testing:** No formal test suite; manual testing via web UI and CLI tools in `lib/pyxctsk/cli.py`.

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
- `app/lib/pyxctsk/cli.py` provides conversion and analysis tools for XCTSK files.

## Examples
- To add a new route: create a blueprint in `app/routes/` and register it in `app/__init__.py`.
- To process a new XCTSK file type: add parsing logic in `app/lib/pyxctsk/` and update `XCTSKService` as needed.

## Important Notes
- Keep logic for XCTSK parsing and business rules in `lib/pyxctsk/` and `services/`—not in route handlers.
- Avoid unnecessary configuration or complexity without clear need or request.
