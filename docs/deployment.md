# Deployment

The app runs on [Fly.io](https://fly.io/) as a single machine, configured by `fly.toml` and built from the `Dockerfile` (gunicorn serving `wsgi.py` on port 8080).

## Release flow

Merging to `main` deploys: `.github/workflows/fly-deploy.yml` runs `flyctl deploy --remote-only` on every push to `main`. CI (`.github/workflows/ci.yml`) checks the same push, but the deploy does not wait for it, so keep `main` green through pull requests.

## Secrets

- **`FLASK_SECRET_KEY`** — a Fly.io app secret; signs the session cookie that carries flash messages. See [`.env.example`](../.env.example).
- **`FLY_API_TOKEN`** — a GitHub Actions repository secret holding a Fly.io deploy token, used by the deploy workflow.

## First-time setup

Install the Fly.io CLI and add it to your `PATH` (in `.bashrc` or `.zshrc`):

```bash
curl -L https://fly.io/install.sh | sh
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

Then create the app and its secrets:

```bash
fly auth login
fly launch --ha=false                 # --ha=false keeps it to a single machine
fly scale count 1                     # only if two machines were already deployed
python3 -c "import secrets; print(secrets.token_hex(32))"
fly secrets set FLASK_SECRET_KEY=<generated key>
fly tokens create deploy -x 999999h   # store as the FLY_API_TOKEN GitHub secret
```

## Manual deploy

```bash
fly deploy
```

## Scaling

`fly.toml` runs one shared-CPU machine with 1 GB of memory that stops when idle and starts on the next request. Keep it to one machine: the task cache and the active airspace dataset live in process memory, so a second machine would not share them.
