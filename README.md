# obbyconfigs

Obby terminal config installer for Arch Linux, Ubuntu, and Debian. It installs the packages that are missing, sets up tmux, zsh, Oh My Zsh, Powerlevel10k, zsh completions, autosuggestions, syntax highlighting, and a Tokyo Night terminal style.

## Quick install

```bash
git clone https://github.com/obnoxiousmods/obbyconfigs.git
cd obbyconfigs
python3 obbyinstaller.py --dry-run
python3 obbyinstaller.py --yes --overwrite --optional-packages
```

What the installer does:

- Detects Arch, Ubuntu, or Debian from `/etc/os-release` and available package tools.
- Installs only missing packages.
- Uses `pacman -Syu --needed --noconfirm` on Arch.
- Uses `apt-get update` and `apt-get install -y` on Ubuntu/Debian.
- Installs Oh My Zsh only if `~/.oh-my-zsh` is missing.
- Clones Powerlevel10k and zsh plugins only if they are missing.
- Backs up existing `~/.tmux.conf`, `~/.zshrc`, and `~/.p10k.zsh` before replacing them when `--overwrite` is used.
- Leaves existing dotfiles untouched unless `--overwrite` is used.

## Installer flags

```bash
python3 obbyinstaller.py --help
```

Useful options:

- `--dry-run`: preview package installs, clones, and file writes.
- `--yes` or `-y`: accept installer prompts.
- `--overwrite`: back up existing dotfiles and write the managed config.
- `--skip-packages`: do not install Linux packages.
- `--skip-shell-change`: do not run `chsh`.
- `--optional-packages`: also install helper packages like `gh`, `less`, and `tree`.
- `--print-windows-terminal-scheme`: print the Tokyo Night color scheme JSON.

## Windows Terminal: Meslo, Powerline, OS Icons, Tokyo Night

Install Meslo with Nerd Font symbols. Powerlevel10k expects a MesloLGS Nerd Font so Powerline arrows and OS icons render correctly.

1. Download the four MesloLGS NF font files from the Powerlevel10k font page:
   - `MesloLGS NF Regular.ttf`
   - `MesloLGS NF Bold.ttf`
   - `MesloLGS NF Italic.ttf`
   - `MesloLGS NF Bold Italic.ttf`
2. Windows 11 or Windows 10: select the `.ttf` files, right click, then choose `Install for all users`.
3. Open Windows Terminal.
4. Go to `Settings` > your Linux profile, such as Ubuntu, Debian, or Arch.
5. Set `Font face` to `MesloLGS NF`.
6. Open `Settings` > `Open JSON file`.
7. Add this object to the top-level `schemes` array:

```json
{
  "background": "#1A1B26",
  "black": "#15161E",
  "blue": "#7AA2F7",
  "brightBlack": "#414868",
  "brightBlue": "#7AA2F7",
  "brightCyan": "#7DCFFF",
  "brightGreen": "#9ECE6A",
  "brightPurple": "#BB9AF7",
  "brightRed": "#F7768E",
  "brightWhite": "#C0CAF5",
  "brightYellow": "#E0AF68",
  "cursorColor": "#C0CAF5",
  "cyan": "#7DCFFF",
  "foreground": "#C0CAF5",
  "green": "#9ECE6A",
  "name": "Tokyo Night",
  "purple": "#BB9AF7",
  "red": "#F7768E",
  "selectionBackground": "#33467C",
  "white": "#A9B1D6",
  "yellow": "#E0AF68"
}
```

8. In the same profile JSON, set:

```json
"font": {
  "face": "MesloLGS NF"
},
"colorScheme": "Tokyo Night"
```

9. Save the settings file and restart Windows Terminal.

You can also print the scheme from the installer:

```bash
python3 obbyinstaller.py --print-windows-terminal-scheme
```

## Manual install guide

Install packages.

Arch Linux:

```bash
sudo pacman -Syu --needed base-devel bat curl eza fd fzf git neovim ripgrep tmux unzip wget zoxide zsh
```

Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y bat build-essential curl fd-find fzf git neovim ripgrep tmux unzip wget zoxide zsh
```

Install Oh My Zsh:

```bash
RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Install the zsh theme and plugins:

```bash
ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM/themes/powerlevel10k"
git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions.git "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
git clone --depth=1 https://github.com/zsh-users/zsh-completions.git "$ZSH_CUSTOM/plugins/zsh-completions"
```

Run the installer only for dotfiles if you installed packages manually:

```bash
python3 obbyinstaller.py --skip-packages --yes --overwrite
```

Change your default shell:

```bash
chsh -s "$(command -v zsh)"
```

Restart the terminal, then configure the prompt:

```bash
p10k configure
```

Reload tmux after editing:

```bash
tmux source-file ~/.tmux.conf
```

## Safety

Run `--dry-run` first. The installer avoids reinstalling packages and does not overwrite existing dotfiles unless `--overwrite` is present. Replaced dotfiles are saved next to the original path with a `.backup-YYYYMMDD-HHMMSS` suffix.
