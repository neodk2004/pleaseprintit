# AGENTS.md

Guide for AI coding agents (Claude Code, Codex, Copilot, Cursor …) working on this repository.

## What this is

PleasePrintit is a small, self-hosted **3D print request queue** for a private circle (up to ~50 people). Friends join via one-time invite link, submit print requests (model link or STL/3MF upload, filament, color, quantity), and the admin works through a sorted queue with 3D preview and cost estimate. Status flow: `neu` (submitted) → `geplant` (planned) → `gedruckt` (printed), or `abgelehnt` (rejected, with reason).

The **user interface, code comments and commit messages are German.** Keep new UI text German.

## Layout

| Path | Purpose |
|---|---|
| `app.py` | The whole Flask app: routes, auth, invites, orders, settings, security headers, SQLite schema (`db()`) |
| `models.py` | Validates uploaded 3D files by content (STL/3MF), dimensions, volume, 3MF thumbnails |
| `preview.py` | Fetches link previews (Open Graph) with SSRF protection — every IP must be public, connects to the checked IP |
| `mail.py` | SMTP e-mail via stdlib only; disabled when `SMTP_HOST` is empty |
| `backup.py` | Daily `.tar.gz` backups (`--once`, `--check FILE`) |
| `templates/` | Jinja2 templates (`base.html` layout, `_*.html` partials, `mail_*` e-mails) |
| `static/` | Plain JS/CSS, PWA manifest, vendored three.js in `static/three/` (no build step, no npm) |
| `test_*.py` | Self-tests, plain `assert`, no framework |
| `compose.yaml` / `compose.dockhand.yaml` | Docker Compose (bind mounts) / Dockhand variant (named volumes, `${VAR}` stack variables) |

## Commands

```sh
pip install -r requirements.txt
python test_app.py && python test_models.py && python test_preview.py   # each prints OK
docker compose up -d --build                                            # run locally on :8080
```

Tests set `SECRET_KEY`, `ADMIN_PASSWORD` and `DB_PATH` themselves and use a temp directory. CI (`.github/workflows/ci.yml`) runs the tests, validates both compose files and test-starts the Docker image on amd64 and arm64 (QEMU). On push to `main` (and `v*` tags) it then publishes a multi-arch image to `ghcr.io/neodk2004/pleaseprintit`, which both compose files reference (with `build: .` as fallback).

## Conventions

- **Keep it small.** Dependencies are only `flask` and `gunicorn`; prefer the standard library. No ORM, no frontend build, no new packages without a strong reason.
- **Schema changes** go into `db()` in `app.py`: `CREATE TABLE IF NOT EXISTS` plus `ALTER TABLE … ADD COLUMN` guarded by `PRAGMA table_info`. There are no migration files; never drop or rename columns.
- **Always use SQL parameters** (`?`), never string formatting with user input.
- **Security is a feature:** keep the CSP/HSTS headers, login throttling, invite-only signup, per-user limits (10 open orders, 500 MB files), content-based file checks and the SSRF guard in `preview.py`. Templates rely on Jinja2 autoescaping — don't use `|safe` on user data.
- The container runs as uid 1000 with a read-only filesystem; only `/data` and `/backups` are writable.
- Configuration comes from environment variables only (see `.env.example`). Never commit `.env`, secrets or real personal data; screenshots use demo data.
- Add or extend a test in the matching `test_*.py` for any non-trivial change.

## Security issues

Report privately as described in [SECURITY.md](SECURITY.md), not in public issues.
