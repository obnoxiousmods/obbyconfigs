from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

APP_NAME = "obbyconfigs"
SUPPORTED_FAMILIES = {"arch", "debian"}
SYSTEM_ROOT = Path("/usr/local/share/obbyconfigs")
SYSTEM_ETC = Path("/etc/obbyconfigs")

BASE_PACKAGES = {
    "arch": ["base-devel", "bat", "curl", "eza", "fd", "fzf", "git", "neovim", "python", "ripgrep", "tmux", "unzip", "wget", "zoxide", "zsh"],
    "debian": ["bat", "build-essential", "curl", "fd-find", "fzf", "git", "neovim", "python3", "ripgrep", "tmux", "unzip", "wget", "zoxide", "zsh"],
}

OPTIONAL_PACKAGES = {
    "arch": ["github-cli", "less", "nodejs", "npm", "python-pip", "python-pipx", "tree", "uv"],
    "debian": ["gh", "less", "nodejs", "npm", "pipx", "python3-pip", "python3-venv", "tree"],
}

OH_MY_ZSH_REPO = "https://github.com/ohmyzsh/ohmyzsh.git"
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


@dataclass(frozen=True)
class InstallPaths:
    home: Path
    tmux_conf: Path
    zshrc: Path
    p10k: Path
    oh_my_zsh: Path
    zsh_custom: Path


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


def zshrc_template(oh_my_zsh: Path, p10k: Path) -> str:
    return f"""# Managed by obbyconfigs.
export ZSH="{oh_my_zsh}"
export EDITOR="${{EDITOR:-nvim}}"
export VISUAL="${{VISUAL:-$EDITOR}}"
export LANG="${{LANG:-en_US.UTF-8}}"

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
[[ -r "{p10k}" ]] && source "{p10k}"

HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000
setopt appendhistory sharehistory hist_ignore_all_dups hist_reduce_blanks
setopt autocd correct interactivecomments

obby_path_prepend() {{
  [[ -n "$1" && -d "$1" && ":$PATH:" != *":$1:"* ]] && export PATH="$1:$PATH"
}}

obby_path_prepend "$HOME/.local/bin"
obby_path_prepend "$HOME/bin"
obby_path_prepend "$HOME/.cargo/bin"
obby_path_prepend "$HOME/go/bin"
obby_path_prepend "$HOME/.npm-global/bin"
obby_path_prepend "$HOME/.yarn/bin"
obby_path_prepend "$HOME/.bun/bin"
obby_path_prepend "$HOME/.deno/bin"
obby_path_prepend "$HOME/.pyenv/bin"
obby_path_prepend "$HOME/.rye/shims"
obby_path_prepend "$HOME/.local/share/uv/tools"
obby_path_prepend "$HOME/.local/share/pnpm"
obby_path_prepend "$HOME/.config/yarn/global/node_modules/.bin"
obby_path_prepend "$PWD/node_modules/.bin"
[[ -d ".venv/bin" ]] && obby_path_prepend "$PWD/.venv/bin"
[[ -d "venv/bin" ]] && obby_path_prepend "$PWD/venv/bin"

export PNPM_HOME="${{PNPM_HOME:-$HOME/.local/share/pnpm}}"
export BUN_INSTALL="${{BUN_INSTALL:-$HOME/.bun}}"
export GOPATH="${{GOPATH:-$HOME/go}}"

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

if command -v uv >/dev/null 2>&1; then
  alias uvr='uv run'
  alias uvs='uv sync'
  alias uvx='uv tool run'
fi

if command -v pyenv >/dev/null 2>&1; then
  eval "$(pyenv init - zsh)"
fi

if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
  source "$HOME/.nvm/nvm.sh"
fi

if [[ -s "$BUN_INSTALL/_bun" ]]; then
  source "$BUN_INSTALL/_bun"
fi
"""


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


def detect_family(override: str | None = None) -> str:
    if override and override != "auto":
        return "debian" if override in {"ubuntu", "debian"} else override
    os_release = read_os_release()
    ids = " ".join(value.lower() for value in (os_release.get("ID", ""), os_release.get("ID_LIKE", "")))
    if "arch" in ids or shutil.which("pacman"):
        return "arch"
    if any(name in ids for name in ("debian", "ubuntu")) or shutil.which("apt-get"):
        return "debian"
    raise SystemExit("Unsupported Linux distribution. This installer supports Arch, Ubuntu, and Debian.")


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


def needs_sudo(path: Path) -> bool:
    if os.geteuid() == 0:
        return False
    normalized = str(path)
    return normalized in {"/etc", "/usr/local"} or normalized.startswith(("/etc/", "/usr/local/"))


def install_packages(runner: Runner, family: str, package_mode: str) -> None:
    if package_mode == "none":
        print("Skipping packages by request.")
        return
    packages = list(BASE_PACKAGES[family])
    if package_mode in {"optional", "all", "force"}:
        packages.extend(OPTIONAL_PACKAGES[family])
    missing = packages if package_mode == "force" else [package for package in packages if not has_package(family, package)]
    if not missing:
        print("All requested packages are already installed.")
        return

    print("Packages to install:", ", ".join(missing))
    if family == "arch":
        runner.run(sudo_prefix() + ["pacman", "-Syu", "--needed", "--noconfirm", *missing])
        return
    runner.run(sudo_prefix() + ["apt-get", "update"])
    runner.run(sudo_prefix() + ["apt-get", "install", "-y", *missing])


def backup_path(path: Path) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return path.with_name(f"{path.name}.backup-{stamp}")


def ensure_parent(runner: Runner, path: Path) -> None:
    parent = path.parent
    if parent.exists():
        return
    if needs_sudo(parent):
        runner.run(sudo_prefix() + ["mkdir", "-p", str(parent)])
    elif runner.dry_run:
        print(f"[dry-run] create {parent}")
    else:
        parent.mkdir(parents=True, exist_ok=True)


def write_file(runner: Runner, path: Path, content: str, mode: str, backup: bool) -> None:
    path = path.expanduser()
    next_content = content.rstrip() + "\n"
    if path.exists():
        current = path.read_text(encoding="utf-8", errors="replace")
        if current == next_content:
            print(f"{path} is already up to date.")
            return
        if mode == "safe":
            print(f"{path} exists; leaving it unchanged. Use --dotfile-mode overwrite or force.")
            return
        if backup:
            backup_target = backup_path(path)
            if needs_sudo(path):
                runner.run(sudo_prefix() + ["cp", str(path), str(backup_target)])
            elif runner.dry_run:
                print(f"[dry-run] back up {path} to {backup_target}")
            else:
                path.replace(backup_target)
                print(f"Backed up {path} to {backup_target}")

    ensure_parent(runner, path)
    if runner.dry_run:
        print(f"[dry-run] write {path}")
        return
    if needs_sudo(path):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            tmp.write(next_content)
            tmp_path = tmp.name
        try:
            runner.run(sudo_prefix() + ["install", "-m", "0644", tmp_path, str(path)])
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    else:
        path.write_text(next_content, encoding="utf-8")
    print(f"Wrote {path}")


def clone_repo(runner: Runner, url: str, destination: Path, mode: str) -> None:
    if mode == "skip":
        return
    destination = destination.expanduser()
    if destination.exists() and mode != "force":
        print(f"{destination} already exists.")
        return
    if destination.exists() and mode == "force":
        backup = backup_path(destination)
        runner.run(sudo_prefix() + ["mv", str(destination), str(backup)] if needs_sudo(destination) else ["mv", str(destination), str(backup)])
    ensure_parent(runner, destination)
    runner.run((sudo_prefix() if needs_sudo(destination) else []) + ["git", "clone", "--depth=1", url, str(destination)])


def install_zsh_assets(runner: Runner, paths: InstallPaths, zsh_mode: str, plugin_mode: str) -> None:
    if zsh_mode != "skip":
        clone_repo(runner, OH_MY_ZSH_REPO, paths.oh_my_zsh, zsh_mode)
    if plugin_mode != "skip":
        for relative, url in ZSH_GIT_REPOS.items():
            clone_repo(runner, url, paths.zsh_custom / relative, plugin_mode)


def set_default_shell(runner: Runner, shell_mode: str, target_user: str | None) -> None:
    if shell_mode == "skip":
        print("Skipping default shell change.")
        return
    zsh_path = shutil.which("zsh")
    if not zsh_path:
        print("zsh is not available; skipping default shell change.")
        return
    current_shell = os.environ.get("SHELL", "")
    if Path(current_shell).name == "zsh" and shell_mode != "force":
        print("zsh is already the current shell.")
        return
    prompt = f"Change default shell to {zsh_path}"
    if target_user:
        prompt += f" for {target_user}"
    if shell_mode == "ask" and not runner.confirm(prompt + "?"):
        print("Skipping default shell change.")
        return
    command = ["chsh", "-s", zsh_path]
    if target_user:
        command.append(target_user)
    runner.run(sudo_prefix() + command if target_user and os.geteuid() != 0 else command)


def write_system_zsh_hook(runner: Runner, dotfile_mode: str, backup: bool) -> None:
    zshrc = Path("/etc/zsh/zshrc")
    hook = "\n# Source obbyconfigs for all interactive zsh users.\n[[ -r /etc/obbyconfigs/zshrc ]] && source /etc/obbyconfigs/zshrc\n"
    if zshrc.exists():
        current = zshrc.read_text(encoding="utf-8", errors="replace")
        if "/etc/obbyconfigs/zshrc" in current:
            print("/etc/zsh/zshrc already sources obbyconfigs.")
            return
        write_file(runner, zshrc, current.rstrip() + hook, dotfile_mode, backup)
    else:
        write_file(runner, zshrc, hook.lstrip(), dotfile_mode, backup)


def resolve_paths(args: argparse.Namespace) -> InstallPaths:
    home = Path(args.home).expanduser() if args.home else Path.home()
    if args.scope in {"system", "all-users"}:
        return InstallPaths(
            home=home,
            tmux_conf=Path(args.tmux_conf or "/etc/tmux.conf"),
            zshrc=Path(args.zshrc or SYSTEM_ETC / "zshrc"),
            p10k=Path(args.p10k or SYSTEM_ETC / "p10k.zsh"),
            oh_my_zsh=Path(args.oh_my_zsh or SYSTEM_ROOT / "oh-my-zsh"),
            zsh_custom=Path(args.zsh_custom or SYSTEM_ROOT / "oh-my-zsh" / "custom"),
        )
    return InstallPaths(
        home=home,
        tmux_conf=Path(args.tmux_conf or home / ".tmux.conf"),
        zshrc=Path(args.zshrc or home / ".zshrc"),
        p10k=Path(args.p10k or home / ".p10k.zsh"),
        oh_my_zsh=Path(args.oh_my_zsh or home / ".oh-my-zsh"),
        zsh_custom=Path(args.zsh_custom or home / ".oh-my-zsh" / "custom"),
    )


def print_next_steps(scope: str) -> None:
    extra = "System zsh config is in /etc/obbyconfigs; users may need to start a new shell." if scope in {"system", "all-users"} else "Restart the terminal, then run: p10k configure"
    print(
        f"""
Next steps:
1. Install MesloLGS Nerd Font on your terminal host.
2. Set your terminal profile font to "MesloLGS NF".
3. {extra}
4. In tmux, press Ctrl-a then r to reload after editing tmux config.
"""
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Obby's tmux and zsh terminal config.")
    parser.add_argument("--dry-run", action="store_true", help="print planned actions without changing files")
    parser.add_argument("--yes", "-y", action="store_true", help="answer yes to interactive prompts")
    parser.add_argument("--scope", choices=["user", "system", "all-users"], default="user", help="install for one user or system defaults")
    parser.add_argument("--home", help="home directory for user-scoped config")
    parser.add_argument("--target-user", help="user passed to chsh for system/all-users shell changes")
    parser.add_argument("--assume-distro", choices=["auto", "arch", "ubuntu", "debian"], default="auto", help="override distro detection")
    parser.add_argument("--package-mode", choices=["required", "optional", "all", "none", "force"], default="required", help="package install strategy")
    parser.add_argument("--zsh-mode", choices=["auto", "skip", "force"], default="auto", help="Oh My Zsh install strategy")
    parser.add_argument("--plugin-mode", choices=["auto", "skip", "force"], default="auto", help="zsh plugin install strategy")
    parser.add_argument("--dotfile-mode", choices=["safe", "overwrite", "force"], default="safe", help="dotfile write strategy")
    parser.add_argument("--shell-mode", choices=["ask", "skip", "force"], default="ask", help="default shell strategy")
    parser.add_argument("--no-backup", action="store_true", help="do not save .backup files before replacing configs")
    parser.add_argument("--tmux-conf", help="custom tmux config destination")
    parser.add_argument("--zshrc", help="custom zshrc destination")
    parser.add_argument("--p10k", help="custom Powerlevel10k config destination")
    parser.add_argument("--oh-my-zsh", help="custom Oh My Zsh destination")
    parser.add_argument("--zsh-custom", help="custom Oh My Zsh custom directory")
    parser.add_argument("--system-zsh-hook", action="store_true", help="make /etc/zsh/zshrc source /etc/obbyconfigs/zshrc in system scope")
    parser.add_argument("--only-packages", action="store_true", help="only install packages")
    parser.add_argument("--only-dotfiles", action="store_true", help="only write tmux/zsh config files")
    parser.add_argument("--list-plan", action="store_true", help="print the resolved install plan and exit")
    parser.add_argument("--overwrite", action="store_true", help="legacy alias for --dotfile-mode overwrite")
    parser.add_argument("--skip-packages", action="store_true", help="legacy alias for --package-mode none")
    parser.add_argument("--skip-shell-change", action="store_true", help="legacy alias for --shell-mode skip")
    parser.add_argument("--optional-packages", action="store_true", help="legacy alias for --package-mode optional")
    parser.add_argument("--force", action="store_true", help="force packages, zsh assets, plugins, shell, and dotfiles")
    parser.add_argument("--print-windows-terminal-scheme", action="store_true", help="print the Tokyo Night Windows Terminal scheme JSON and exit")
    return parser.parse_args(argv)


def normalize_args(args: argparse.Namespace) -> argparse.Namespace:
    if args.overwrite:
        args.dotfile_mode = "overwrite"
    if args.skip_packages:
        args.package_mode = "none"
    if args.optional_packages:
        args.package_mode = "optional"
    if args.skip_shell_change:
        args.shell_mode = "skip"
    if args.force:
        args.package_mode = "force"
        args.zsh_mode = "force"
        args.plugin_mode = "force"
        args.dotfile_mode = "force"
        args.shell_mode = "force"
    if args.only_packages:
        args.zsh_mode = "skip"
        args.plugin_mode = "skip"
        args.dotfile_mode = "safe"
        args.shell_mode = "skip"
    if args.only_dotfiles:
        args.package_mode = "none"
        args.zsh_mode = "skip"
        args.plugin_mode = "skip"
        args.shell_mode = "skip"
    return args


def print_plan(family: str, paths: InstallPaths, args: argparse.Namespace) -> None:
    print(f"scope: {args.scope}")
    print(f"package family: {family}")
    print(f"package mode: {args.package_mode}")
    print(f"zsh mode: {args.zsh_mode}")
    print(f"plugin mode: {args.plugin_mode}")
    print(f"dotfile mode: {args.dotfile_mode}")
    print(f"shell mode: {args.shell_mode}")
    print(f"tmux: {paths.tmux_conf}")
    print(f"zshrc: {paths.zshrc}")
    print(f"p10k: {paths.p10k}")
    print(f"oh-my-zsh: {paths.oh_my_zsh}")
    print(f"zsh custom: {paths.zsh_custom}")


def main(argv: list[str] | None = None) -> int:
    args = normalize_args(parse_args(argv))
    if args.print_windows_terminal_scheme:
        print(WINDOWS_TERMINAL_TOKYO_NIGHT)
        return 0
    if platform.system() != "Linux":
        raise SystemExit("This installer is for Linux hosts. Use the README for manual Windows Terminal setup.")

    family = detect_family(args.assume_distro)
    if family not in SUPPORTED_FAMILIES:
        raise SystemExit(f"Unsupported package family: {family}")

    paths = resolve_paths(args)
    runner = Runner(dry_run=args.dry_run, yes=args.yes)
    print_plan(family, paths, args)
    if args.list_plan:
        return 0

    if args.package_mode != "none":
        install_packages(runner, family, args.package_mode)

    if not args.only_packages:
        install_zsh_assets(runner, paths, args.zsh_mode, args.plugin_mode)
        write_file(runner, paths.tmux_conf, TMUX_CONF, args.dotfile_mode, not args.no_backup)
        write_file(runner, paths.zshrc, zshrc_template(paths.oh_my_zsh, paths.p10k), args.dotfile_mode, not args.no_backup)
        write_file(runner, paths.p10k, P10K_ZSH, args.dotfile_mode, not args.no_backup)
        if args.scope in {"system", "all-users"} and args.system_zsh_hook:
            write_system_zsh_hook(runner, args.dotfile_mode, not args.no_backup)

    set_default_shell(runner, args.shell_mode, args.target_user)
    print_next_steps(args.scope)
    return 0
