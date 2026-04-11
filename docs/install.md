# Install obbyconfigs

Full docs: https://obnoxiousmods.github.io/obbyconfigs/
GitHub Wiki: https://github.com/obnoxiousmods/obbyconfigs/wiki

## One Liner

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/obnoxiousmods/obbyconfigs/main/install.sh)" -- --yes --dotfile-mode overwrite --package-mode optional --nano-mode auto
```

The one-liner bootstraps `git` and Python 3 with `pacman`, `apt-get`, `dnf`, `zypper`, `apk`, or Homebrew when possible, then runs `obbyinstaller.py`.

## Windows

```powershell
iwr https://raw.githubusercontent.com/obnoxiousmods/obbyconfigs/main/install.ps1 -OutFile install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1 -InstallFonts -PrintScheme
```

Run against WSL:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -WslDistro Ubuntu -- --yes --dotfile-mode overwrite --package-mode optional --nano-mode auto
```

## uv

```bash
uv tool install git+https://github.com/obnoxiousmods/obbyconfigs.git
obbyinstaller --help
```

After PyPI trusted publishing is enabled:

```bash
uv tool install obbyconfigs
```

## pipx

```bash
pipx install git+https://github.com/obnoxiousmods/obbyconfigs.git
obbyinstaller --list-plan
```

After PyPI trusted publishing is enabled:

```bash
pipx install obbyconfigs
```

## AUR

After `AUR_SSH_PRIVATE_KEY` is configured and a release publishes the AUR package:

```bash
yay -S obbyconfigs
```

## Homebrew

After `HOMEBREW_TAP_REPO` and `HOMEBREW_TAP_TOKEN` are configured:

```bash
brew tap obnoxiousmods/obbyconfigs
brew install obbyconfigs
```

## GitHub Release Assets

Tagged releases include:

- `obbyconfigs-*.whl`
- `obbyconfigs-*.tar.gz`
- `obbyinstaller.pyz`
- `install.sh`
- `install.ps1`
- `obbyconfigs-linux-any.zip`
- `obbyconfigs-macos-any.zip`
- `obbyconfigs-windows-any.zip`
- nFPM Linux package artifacts for deb, rpm, apk, and Arch-style package workflows.
- GHCR images for `linux/amd64` and `linux/arm64`.
- PyPI publishing through trusted publishing when `ENABLE_PYPI_PUBLISH=true` is configured.
- Optional AUR and Homebrew tap publishing through repository secrets/variables.

Registry setup:

- PyPI: configure trusted publishing for `obnoxiousmods/obbyconfigs`, workflow `PyPI`, environment `pypi`, then set `ENABLE_PYPI_PUBLISH=true`.
- AUR: configure `AUR_SSH_PRIVATE_KEY`.
- Homebrew: use tap repo `obnoxiousmods/homebrew-obbyconfigs`, repo variable `HOMEBREW_TAP_REPO`, and secret `HOMEBREW_TAP_TOKEN`.

## Package Groups

```bash
obbyinstaller --package-mode all --package-groups dev,python,node,containers,network,fonts --dry-run
```
