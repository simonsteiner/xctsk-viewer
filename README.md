# Python XCTSK Viewer

A Python-based interactive visualization tool for viewing XCTSK files.

This tool allows paragliding pilots, organizers, and enthusiasts to visualize XCTSK files—used to define competition tasks for XCTrack. Built with Python, the viewer provides an interactive map interface to inspect turnpoints, task types, and routes defined in XCTSK files, making it easier to review or debug tasks for competitions. An optional airspace overlay renders OpenAir airspace on the map, sourced from the bundled default, an uploaded file, or the live xcontest "COMP CH" competition layer.

## Quick Start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                    # install dependencies and dev tools
uv run lefthook install    # install the git hooks
uv run python run.py       # serve on http://localhost:8080
```

## Development

`uv run lefthook install` sets up the git hooks. Before each commit they run Ruff, mypy, rumdl, cspell and a per-file token budget (no file over 5,000 tokens) on the staged files; before each push, pytest. To skip them once, in an emergency: `LEFTHOOK=0 git commit …`. See [docs/setup.md](docs/setup.md#code-quality) for the commands.

## Docs

- [docs/setup.md](docs/setup.md) — local setup, developing against unreleased `pyxctsk`, code-quality tools, Docker.
- [docs/deployment.md](docs/deployment.md) — deploying to Fly.io and the production secret.
- [.env.example](.env.example) — the environment variables the app reads.
- [GLOSSARY.md](GLOSSARY.md) — domain terms (task, turnpoint, SSS, airspace dataset, …).
- [AGENTS.md](AGENTS.md) — rules for changing the code, for coding agents and humans alike.
