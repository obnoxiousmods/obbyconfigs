# Copilot Instructions

This project is a Python CLI package managed by uv.

- Keep the checkout wrapper `obbyinstaller.py` working without installation.
- Keep the package entry point `obbyinstaller = obbyconfigs.installer:main` working.
- Prefer standard library code unless a dependency clearly pays for itself.
- Installer changes must preserve `--dry-run`, `--list-plan`, and safe default dotfile behavior.
- Never make system-scope writes implicit; require `--scope system` or `--scope all-users`.
- Add or update README docs for every new user-facing flag.
