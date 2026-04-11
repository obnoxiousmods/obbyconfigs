# CLI Arguments

Full docs: https://obnoxiousmods.github.io/obbyconfigs/
GitHub Wiki: https://github.com/obnoxiousmods/obbyconfigs/wiki

Run:

```bash
obbyinstaller --help
```

Common full install:

```bash
obbyinstaller --yes --dotfile-mode overwrite --package-mode optional --nano-mode auto
```

Maximal package install:

```bash
obbyinstaller --yes --dotfile-mode overwrite --package-mode all --package-groups dev,python,node,containers,network,fonts --nano-mode auto
```

Package-manager override checks:

```bash
obbyinstaller --assume-distro alpine --list-plan
obbyinstaller --assume-distro arch --list-plan
obbyinstaller --assume-distro debian --list-plan
obbyinstaller --assume-distro fedora --list-plan
obbyinstaller --assume-distro opensuse --list-plan
obbyinstaller --assume-distro macos --list-plan
```

System defaults:

```bash
sudo obbyinstaller --scope system --yes --dotfile-mode overwrite --package-mode optional --system-zsh-hook --nano-mode auto
```

Dry run:

```bash
obbyinstaller --dry-run --list-plan
```
