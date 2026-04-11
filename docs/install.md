# Install obbyconfigs

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

## pipx

```bash
pipx install git+https://github.com/obnoxiousmods/obbyconfigs.git
obbyinstaller --list-plan
```

## GitHub Release Assets

Tagged releases include:

- `obbyconfigs-*.whl`
- `obbyconfigs-*.tar.gz`
- `obbyinstaller.pyz`
- `install.sh`
- `install.ps1`
- nFPM Linux package artifacts for deb, rpm, apk, and Arch-style package workflows.
- GHCR images for `linux/amd64` and `linux/arm64`.

## Package Groups

```bash
obbyinstaller --package-mode all --package-groups dev,python,node,containers,network,fonts --dry-run
```
