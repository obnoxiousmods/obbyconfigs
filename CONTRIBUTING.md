# Contributing

Use uv for local development.

```bash
uv sync --all-groups
uv run ruff check .
uv run python -m compileall obbyinstaller.py src
uv run obbyinstaller --list-plan --skip-packages --skip-shell-change
```

Keep installer behavior conservative:

- Default to user scope.
- Default to not overwriting dotfiles.
- Keep `--dry-run` accurate.
- Keep package installs distro-aware.
- Document every new CLI flag in `README.md`.
