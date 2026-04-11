#!/usr/bin/env python3
"""
Install a portable tmux + zsh setup for Arch Linux, Ubuntu, and Debian.

The installer is intentionally conservative:
- detects the host distribution and package manager
- installs only missing packages
- backs up existing dotfiles before writing new ones
- clones optional zsh plugins/themes only when they are absent
- supports --dry-run for auditing the planned changes
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "obbyconfigs"
SUPPORTED_FAMILIES = {"arch", "debian"}

BASE_PACKAGES = {
    "arch": [
        "base-devel",
        "bat",
        "curl",
        "eza",
        "fd",
        "fzf",
        "git",
        "neovim",
        "ripgrep",
        "tmux",
        "unzip",
        "wget",
        "zoxide",
        "zsh",
    ],
    "debian": [
        "bat",
        "build-essential",
        "curl",
        "fd-find",
        "fzf",
        "git",
        "neovim",
        "ripgrep",
        "tmux",
        "unzip",
        "wget",
        "zoxide",
        "zsh",
    ],
}

OPTIONAL_PACKAGES = {
    "arch": ["github-cli", "less", "tree"],
    "debian": ["gh", "less", "tree"],
}

OH_MY_ZSH_URL = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
ZSH_CUSTOM_DEFAULT = "$HOME/.oh-my-zsh/custom"

ZSH_GIT_REPOS = {
    "themes/powerlevel10k": "https://github.com/romkatv/powerlevel10k.git",
    "plugins/zsh-autosuggestions": "https://github.com/zsh-users/zsh-autosuggestions.git",
    "plugins/zsh-syntax-highlighting": "https://github.com/zsh-users/zsh-syntax-highlighting.git",
    "plugins/zsh-completions": "https://github.com/zsh-users/zsh-completions.git",
}

TMUX_CONF = r"""# Managed by obbyconfigs.
set -g default-terminal "tmux-256color"
set -ag terminal-overrides ",xterm-256color:RGB"
set -g mouse on
set -g history-limit 50000
set -g escape-time 10
set -g focus-events on
set -g renumber-windows on
set -g base-index 1
setw -g pane-base-index 1

unbind C-b
set -g prefix C-a
bind C-a send-prefix

bind r source-file ~/.tmux.conf \; display-message "tmux config reloaded"
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
bind c new-window -c "#{pane_current_path}"
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

set -g status on
set -g status-interval 5
set -g status-position bottom
set -g status-style "bg=#1a1b26,fg=#c0caf5"
set -g status-left-length 60
set -g status-right-length 120
set -g status-left "#[bg=#7aa2f7,fg=#1a1b26,bold] #S #[bg=#24283b,fg=#7aa2f7]"
set -g status-right "#[fg=#414868]#[bg=#414868,fg=#c0caf5] %Y-%m-%d #[fg=#7dcfff] #[fg=#c0caf5]%H:%M "
setw -g window-status-format "#[fg=#565f89] #I:#W "
setw -g window-status-current-format "#[bg=#bb9af7,fg=#1a1b26,bold] #I:#W "
setw -g pane-border-style "fg=#414868"
setw -g pane-active-border-style "fg=#7aa2f7"
set -g message-style "bg=#7aa2f7,fg=#1a1b26"
"""

ZSHRC = r"""# Managed by obbyconfigs.
export ZSH="$HOME/.oh-my-zsh"
export EDITOR="${EDITOR:-nvim}"
export VISUAL="${VISUAL:-$EDITOR}"
export LANG="${LANG:-en_US.UTF-8}"

ZSH_THEME="powerlevel10k/powerlevel10k"

plugins=(
  git
  sudo
  command-not-found
  colored-man-pages
  history-substring-search
  zsh-autosuggestions
  zsh-syntax-highlighting
  zsh-completions
)

[[ -r "$ZSH/oh-my-zsh.sh" ]] && source "$ZSH/oh-my-zsh.sh"
[[ -r "$HOME/.p10k.zsh" ]] && source "$HOME/.p10k.zsh"

HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000
setopt appendhistory sharehistory hist_ignore_all_dups hist_reduce_blanks
setopt autocd correct interactivecomments

alias ll='ls -lah --color=auto'
alias grep='grep --color=auto'
alias tmux='tmux -2'
alias vim='nvim'

if command -v eza >/dev/null 2>&1; then
  alias ls='eza --icons=auto --group-directories-first'
  alias la='eza -la --icons=auto --group-directories-first'
  alias tree='eza --tree --icons=auto'
elif command -v exa >/dev/null 2>&1; then
  alias ls='exa --icons --group-directories-first'
fi

if command -v batcat >/dev/null 2>&1; then
  alias bat='batcat'
fi

if command -v fzf >/dev/null 2>&1; then
  source /usr/share/fzf/key-bindings.zsh 2>/dev/null || true
  source /usr/share/fzf/completion.zsh 2>/dev/null || true
fi

if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi
"""

P10K_ZSH = r"""# Minimal Powerlevel10k config managed by obbyconfigs.
typeset -g POWERLEVEL9K_INSTANT_PROMPT=quiet
typeset -g POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(os_icon dir vcs)
typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(status command_execution_time background_jobs time)
typeset -g POWERLEVEL9K_MODE=nerdfont-complete
typeset -g POWERLEVEL9K_PROMPT_ADD_NEWLINE=true
typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_PREFIX=''
typeset -g POWERLEVEL9K_MULTILINE_LAST_PROMPT_PREFIX='%F{blue}❯%f '
typeset -g POWERLEVEL9K_DIR_FOREGROUND=254
typeset -g POWERLEVEL9K_DIR_BACKGROUND=024
typeset -g POWERLEVEL9K_VCS_CLEAN_FOREGROUND=254
typeset -g POWERLEVEL9K_VCS_CLEAN_BACKGROUND=029
typeset -g POWERLEVEL9K_VCS_MODIFIED_FOREGROUND=254
typeset -g POWERLEVEL9K_VCS_MODIFIED_BACKGROUND=166
typeset -g POWERLEVEL9K_TIME_FORMAT='%D{%H:%M}'
"""

WINDOWS_TERMINAL_TOKYO_NIGHT = r"""{
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
}"""


class Runner:
    def __init__(self, dry_run: bool, yes: bool) -> None:
        self.dry_run = dry_run
        self.yes = yes

    def run(self, command: list[str], *, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        printable = " ".join(command)
        if self.dry_run:
            print(f"[dry-run] {printable}")
            return subprocess.CompletedProcess(command, 0, "", "")
        print(f"[run] {printable}")
        return subprocess.run(command, check=check, text=True, env=env)

    def confirm(self, prompt: str) -> bool:
        if self.yes:
            return True
        answer = input(f"{prompt} [y/N] ").strip().lower()
        return answer in {"y", "yes"}


def read_os_release() -> dict[str, str]:
    data: dict[str, str] = {}
    path = Path("/etc/os-release")
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key] = value.strip().strip('"')
    return data


def detect_family() -> str:
    os_release = read_os_release()
    ids = " ".join(
        value.lower()
        for value in (os_release.get("ID", ""), os_release.get("ID_LIKE", ""))
    )
    if "arch" in ids or shutil.which("pacman"):
        return "arch"
    if any(name in ids for name in ("debian", "ubuntu")) or shutil.which("apt-get"):
        return "debian"
    raise SystemExit(
        "Unsupported Linux distribution. This installer supports Arch, Ubuntu, and Debian."
    )


def has_command(command: str) -> bool:
    return shutil.which(command) is not None


def has_package(family: str, package: str) -> bool:
    if family == "arch":
        result = subprocess.run(["pacman", "-Qq", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    result = subprocess.run(["dpkg-query", "-W", "-f=${Status}", package], capture_output=True, text=True)
    return result.returncode == 0 and "install ok installed" in result.stdout


def sudo_prefix() -> list[str]:
    if os.geteuid() == 0:
        return []
    if not has_command("sudo"):
        raise SystemExit("sudo is required when running as a non-root user.")
    return ["sudo"]


def install_packages(runner: Runner, family: str, include_optional: bool) -> None:
    packages = list(BASE_PACKAGES[family])
    if include_optional:
        packages.extend(OPTIONAL_PACKAGES[family])
    missing = [package for package in packages if not has_package(family, package)]
    if not missing:
        print("All required packages are already installed.")
        return

    print("Missing packages:", ", ".join(missing))
    if family == "arch":
        runner.run(sudo_prefix() + ["pacman", "-Syu", "--needed", "--noconfirm", *missing])
        return

    runner.run(sudo_prefix() + ["apt-get", "update"])
    runner.run(sudo_prefix() + ["apt-get", "install", "-y", *missing])


def backup_path(path: Path) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return path.with_name(f"{path.name}.backup-{stamp}")


def write_file(runner: Runner, path: Path, content: str, overwrite: bool) -> None:
    path = path.expanduser()
    if path.exists():
        current = path.read_text(encoding="utf-8", errors="replace")
        if current == content:
            print(f"{path} is already up to date.")
            return
        if not overwrite:
            print(f"{path} exists; leaving it unchanged. Use --overwrite to replace it.")
            return
        backup = backup_path(path)
        if runner.dry_run:
            print(f"[dry-run] back up {path} to {backup}")
        else:
            path.replace(backup)
            print(f"Backed up {path} to {backup}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)

    if runner.dry_run:
        print(f"[dry-run] write {path}")
        return
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {path}")


def install_oh_my_zsh(runner: Runner) -> None:
    oh_my_zsh = Path.home() / ".oh-my-zsh"
    if oh_my_zsh.exists():
        print("Oh My Zsh is already installed.")
        return
    if not runner.confirm("Install Oh My Zsh from GitHub?"):
        print("Skipping Oh My Zsh.")
        return
    env = os.environ.copy()
    env.update({"RUNZSH": "no", "CHSH": "no", "KEEP_ZSHRC": "yes"})
    command = ["sh", "-c", f"curl -fsSL {OH_MY_ZSH_URL} | sh"]
    runner.run(command, env=env)


def clone_zsh_repos(runner: Runner) -> None:
    zsh_custom = Path(os.path.expandvars(os.environ.get("ZSH_CUSTOM", ZSH_CUSTOM_DEFAULT))).expanduser()
    if not zsh_custom.exists():
        if runner.dry_run:
            print(f"[dry-run] create {zsh_custom}")
        else:
            zsh_custom.mkdir(parents=True, exist_ok=True)
    for relative, url in ZSH_GIT_REPOS.items():
        destination = zsh_custom / relative
        if destination.exists():
            print(f"{destination} already exists.")
            continue
        if not runner.confirm(f"Clone {url} into {destination}?"):
            print(f"Skipping {destination.name}.")
            continue
        runner.run(["git", "clone", "--depth=1", url, str(destination)])


def set_default_shell(runner: Runner) -> None:
    zsh_path = shutil.which("zsh")
    if not zsh_path:
        print("zsh is not available; skipping default shell change.")
        return
    current_shell = os.environ.get("SHELL", "")
    if Path(current_shell).name == "zsh":
        print("zsh is already the current shell.")
        return
    if not runner.confirm(f"Change default shell to {zsh_path}?"):
        print("Skipping default shell change.")
        return
    runner.run(["chsh", "-s", zsh_path])


def print_next_steps() -> None:
    print(
        """
Next steps:
1. Install MesloLGS Nerd Font on your terminal host.
2. Set your terminal profile font to "MesloLGS NF".
3. Restart the terminal, then run: p10k configure
4. In tmux, press Ctrl-a then r to reload after editing ~/.tmux.conf.
"""
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Obby's tmux and zsh terminal config.")
    parser.add_argument("--dry-run", action="store_true", help="print planned actions without changing files")
    parser.add_argument("--yes", "-y", action="store_true", help="answer yes to interactive prompts")
    parser.add_argument("--overwrite", action="store_true", help="back up and replace existing dotfiles")
    parser.add_argument("--skip-packages", action="store_true", help="do not install OS packages")
    parser.add_argument("--skip-shell-change", action="store_true", help="do not run chsh")
    parser.add_argument("--optional-packages", action="store_true", help="also install gh/less/tree helper packages")
    parser.add_argument("--print-windows-terminal-scheme", action="store_true", help="print the Tokyo Night Windows Terminal scheme JSON and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.print_windows_terminal_scheme:
        print(WINDOWS_TERMINAL_TOKYO_NIGHT)
        return 0

    if platform.system() != "Linux":
        raise SystemExit("This installer is for Linux hosts. Use the README for manual Windows Terminal setup.")

    family = detect_family()
    if family not in SUPPORTED_FAMILIES:
        raise SystemExit(f"Unsupported package family: {family}")

    runner = Runner(dry_run=args.dry_run, yes=args.yes)
    print(f"Detected package family: {family}")

    if not args.skip_packages:
        install_packages(runner, family, include_optional=args.optional_packages)

    install_oh_my_zsh(runner)
    clone_zsh_repos(runner)

    write_file(runner, Path("~/.tmux.conf"), TMUX_CONF, overwrite=args.overwrite)
    write_file(runner, Path("~/.zshrc"), ZSHRC, overwrite=args.overwrite)
    write_file(runner, Path("~/.p10k.zsh"), P10K_ZSH, overwrite=args.overwrite)

    if not args.skip_shell_change:
        set_default_shell(runner)

    print_next_steps()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
