# Security Policy

Report security issues privately through GitHub Security Advisories when available. Do not open a public issue for a vulnerability that can expose user systems, credentials, shell startup files, or package manager behavior.

Supported branch:

- `main`

The installer can run package manager commands, clone Git repositories, and write shell config. Use `--dry-run` and `--list-plan` before applying changes on a machine you care about.
