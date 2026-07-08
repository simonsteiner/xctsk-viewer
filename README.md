# Python XCTSK Viewer

A Python-based interactive visualization tool for viewing XCTSK files.

This tool allows paragliding pilots, organizers, and enthusiasts to visualize XCTSK files—used to define competition tasks for XCTrack. Built with Python, the viewer provides an interactive map interface to inspect turnpoints, task types, and routes defined in XCTSK files, making it easier to review or debug tasks for competitions. An optional airspace overlay renders OpenAir airspace on the map, sourced from the bundled default, an uploaded file, or the live xcontest "COMP CH" competition layer.

## Quick Start

### Installation and Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Clone and navigate to the project directory
cd xctsk-viewer

# Install dependencies (creates a .venv automatically) including dev tools
uv sync

# Install the git hooks
uv run lefthook install
```

The `pyxctsk` dependency is installed from [PyPI](https://pypi.org/project/pyxctsk/). To
develop against the unreleased version from GitHub instead, install it on top of the
synced environment:

```bash
uv pip install --reinstall "pyxctsk @ git+https://github.com/simonsteiner/pyxctsk"
```

(Re-running `uv sync` restores the pinned PyPI release.)

### Running the Application

```bash
uv run python run.py
```

## Deployment

### Fly.io

This application can be deployed to [Fly.io](https://fly.io/) for production hosting.

#### Setup Requirements

Install the Fly.io CLI:

```bash
curl -L https://fly.io/install.sh | sh
# Add Fly.io to your PATH (add to `.bashrc` or `.zshrc`):
export FLYCTL_INSTALL="/home/$USER$/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

#### Deployment Setup

The project includes a `fly.toml` configuration file for Fly.io deployment. To deploy:

```bash
# Login to Fly.io
fly auth login
# Launch the application (--ha=false ensures single machine deployment)
fly launch --ha=false
# If you already have two machines deployed, scale down to one
fly scale count 1
# Set Flask secret key for security
python3 -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
# Copy the output and set it as a secret (replace with actual generated key)
fly secrets set FLASK_SECRET_KEY=your_generated_key_here
# Deploy updates
fly deploy

# For automated deployments via GitHub Actions, create a deploy token:
fly tokens create deploy -x 999999h
```

#### Local Docker Testing

Before deploying to Fly.io, you can test the Docker image locally:

```bash
# Build the Docker image
docker build -t my-fly-app .

# Run the container locally on port 8080
docker run -p 8080:8080 my-fly-app
```

The application will be available at <http://localhost:8080>.

---

## Code Quality & Formatting

To keep the codebase clean and consistent, this project uses [Ruff](https://docs.astral.sh/ruff/) (linting + formatting, replacing flake8/isort/black/pydocstyle), [mypy](https://mypy-lang.org/) (type checking) and [cspell](https://cspell.org/) (spell checking). These run automatically before each commit via [lefthook](https://github.com/evilmartians/lefthook), which also runs the [pytest](https://docs.pytest.org/) suite before each push.

### Git Hook Setup

Install the hooks once per clone:

```bash
uv run lefthook install
```

Every commit then runs Ruff, mypy and cspell on the staged files (see `lefthook.yml`).

### Running the tools manually

```bash
uv run ruff check --fix .   # lint and autofix
uv run ruff format .        # format
uv run mypy --explicit-package-bases --config-file mypy.ini app
npx cspell --config cspell.json "app/**"
uv run pytest               # run the test suite
```

If you need to skip hooks for a commit, use `git commit --no-verify` (or `git push --no-verify` for the pre-push tests).
