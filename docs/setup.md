# Local setup

## Install

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Python 3.12 or newer is required; `.python-version` pins 3.14, the version the Docker image runs.

```bash
cd xctsk-viewer
uv sync                    # install dependencies and dev tools into .venv
uv run lefthook install    # install the git hooks, once per clone
```

## Run

```bash
uv run python run.py
```

The dev server runs with debug mode on <http://localhost:8080>. In VS Code the same command is the **Run Flask App** task.

## Configuration

The app reads one environment variable, `FLASK_SECRET_KEY`; see [`.env.example`](../.env.example). Locally the placeholder default is fine.

## Developing against unreleased `pyxctsk`

The `pyxctsk` dependency is installed from [PyPI](https://pypi.org/project/pyxctsk/). To develop against the unreleased version from GitHub, install it on top of the synced environment:

```bash
uv pip install --reinstall "pyxctsk[qr] @ git+https://github.com/simonsteiner/pyxctsk"
```

Re-running `uv sync` restores the pinned PyPI release.

## Code quality

The project uses [Ruff](https://docs.astral.sh/ruff/) (linting and formatting), [mypy](https://mypy-lang.org/) (type checking), [rumdl](https://rumdl.dev/) (Markdown linting, configured in `.rumdl.toml`), [cspell](https://cspell.org/) (spell checking) and [pytest](https://docs.pytest.org/). [lefthook](https://github.com/evilmartians/lefthook) runs Ruff, mypy, rumdl and cspell on the staged files before each commit, and pytest before each push (see `lefthook.yml`).

```bash
uv run ruff check --fix .                                               # lint and autofix
uv run ruff format .                                                    # format
uv run mypy --explicit-package-bases --config-file mypy.ini app tests   # type-check
uv run rumdl check .                                                    # lint Markdown (`rumdl fmt .` fixes)
git ls-files '*.py' '*.md' '*.txt' '*.toml' '*.yml' '*.json' '*.ini' \
  | xargs npx --yes cspell --no-progress --config cspell.json           # spell-check
uv run pytest                                                           # run the test suite
```

To skip the hooks, use `git commit --no-verify` or `git push --no-verify`.

CI (`.github/workflows/ci.yml`) runs the same checks on every pull request and push to `main`, on Python 3.12 and 3.14, and builds the Docker image.

## Docker

To test the production image locally:

```bash
docker build -t xctsk-viewer .
docker run -p 8080:8080 xctsk-viewer
```

The application is then available at <http://localhost:8080>.
