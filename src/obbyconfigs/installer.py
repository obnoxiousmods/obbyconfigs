from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

APP_NAME = "obbyconfigs"
SUPPORTED_FAMILIES = {"alpine", "arch", "debian", "fedora", "macos", "suse"}
SYSTEM_ROOT = Path("/usr/local/share/obbyconfigs")
SYSTEM_ETC = Path("/etc/obbyconfigs")
PACKAGE_MANAGERS = {
    "alpine": ["apk"],
    "arch": ["pacman"],
    "debian": ["apt-get"],
    "fedora": ["dnf", "yum"],
    "macos": ["brew"],
    "suse": ["zypper"],
}

BASE_PACKAGES = {
    "alpine": ["bat", "curl", "eza", "fd", "fzf", "git", "nano", "neovim", "python3", "ripgrep", "tmux", "unzip", "wget", "zoxide", "zsh"],
    "arch": ["base-devel", "bat", "curl", "eza", "fd", "fzf", "git", "neovim", "python", "ripgrep", "tmux", "unzip", "wget", "zoxide", "zsh"],
    "debian": ["bat", "build-essential", "curl", "fd-find", "fzf", "git", "neovim", "python3", "ripgrep", "tmux", "unzip", "wget", "zoxide", "zsh"],
    "fedora": ["bat", "curl", "eza", "fd-find", "fzf", "git", "nano", "neovim", "python3", "ripgrep", "tmux", "unzip", "wget", "zoxide", "zsh"],
    "macos": ["bat", "curl", "eza", "fd", "fzf", "git", "nano", "neovim", "python", "ripgrep", "tmux", "wget", "zoxide", "zsh"],
    "suse": ["bat", "curl", "eza", "fd", "fzf", "git", "nano", "neovim", "python3", "ripgrep", "tmux", "unzip", "wget", "zoxide", "zsh"],
}

OPTIONAL_PACKAGES = {
    "alpine": ["github-cli", "less", "nodejs", "npm", "py3-pip", "pipx", "tree", "uv"],
    "arch": ["github-cli", "less", "nano", "nodejs", "npm", "python-pip", "python-pipx", "tree", "uv"],
    "debian": ["gh", "less", "nano", "nodejs", "npm", "pipx", "python3-pip", "python3-venv", "tree"],
    "fedora": ["gh", "less", "nodejs", "npm", "pipx", "python3-pip", "python3-virtualenv", "tree", "uv"],
    "macos": ["gh", "less", "node", "pipx", "tree", "uv"],
    "suse": ["gh", "less", "nodejs", "npm", "python3-pip", "python3-virtualenv", "tree"],
}

PACKAGE_GROUPS = {
    "alpine": {
        "dev": ["btop", "direnv", "duf", "go", "htop", "jq", "lazygit", "mandoc", "ncdu", "rsync", "shellcheck", "shfmt", "starship", "tealdeer", "tree", "yq"],
        "python": ["py3-pip", "py3-virtualenv", "python3", "ruff", "uv"],
        "node": ["nodejs", "npm", "yarn"],
        "containers": ["docker", "docker-cli-compose"],
        "network": ["bind-tools", "mtr", "netcat-openbsd", "nmap", "openssh-client", "rsync", "socat", "traceroute", "whois"],
        "fonts": ["font-noto", "font-noto-emoji"],
    },
    "arch": {
        "dev": ["bat", "btop", "delta", "direnv", "duf", "dust", "github-cli", "glow", "go", "htop", "hyperfine", "jq", "lazygit", "man-db", "ncdu", "rsync", "shellcheck", "shfmt", "starship", "tealdeer", "tree", "yq"],
        "python": ["python", "python-pip", "python-pipx", "python-virtualenv", "ruff", "uv"],
        "node": ["nodejs", "npm", "pnpm", "yarn"],
        "containers": ["docker", "docker-buildx", "docker-compose", "lazydocker"],
        "network": ["bind", "dog", "inetutils", "mtr", "nmap", "openbsd-netcat", "openssh", "rsync", "socat", "traceroute", "whois"],
        "fonts": ["noto-fonts", "noto-fonts-cjk", "noto-fonts-emoji", "ttf-firacode-nerd", "ttf-jetbrains-mono-nerd", "ttf-meslo-nerd"],
    },
    "debian": {
        "dev": ["bat", "btop", "direnv", "duf", "fd-find", "glow", "golang-go", "htop", "hyperfine", "jq", "lazygit", "man-db", "ncdu", "rsync", "shellcheck", "shfmt", "tealdeer", "tree", "yq"],
        "python": ["pipx", "python3", "python3-pip", "python3-venv", "python3-virtualenv", "ruff"],
        "node": ["nodejs", "npm", "yarnpkg"],
        "containers": ["docker.io", "docker-buildx", "docker-compose", "docker-compose-plugin"],
        "network": ["bind9-dnsutils", "dnsutils", "inetutils-ping", "mtr-tiny", "netcat-openbsd", "nmap", "openssh-client", "rsync", "socat", "traceroute", "whois"],
        "fonts": ["fonts-firacode", "fonts-noto", "fonts-noto-color-emoji", "fonts-powerline"],
    },
    "fedora": {
        "dev": ["btop", "direnv", "duf", "golang", "htop", "hyperfine", "jq", "lazygit", "man-db", "ncdu", "rsync", "ShellCheck", "shfmt", "starship", "tealdeer", "tree", "yq"],
        "python": ["pipx", "python3", "python3-pip", "python3-virtualenv", "ruff", "uv"],
        "node": ["nodejs", "npm", "yarnpkg"],
        "containers": ["docker", "docker-compose", "podman"],
        "network": ["bind-utils", "mtr", "nmap", "openssh-clients", "rsync", "socat", "traceroute", "whois"],
        "fonts": ["fira-code-fonts", "google-noto-emoji-color-fonts", "powerline-fonts"],
    },
    "macos": {
        "dev": ["btop", "direnv", "duf", "dust", "gh", "glow", "go", "htop", "hyperfine", "jq", "lazygit", "ncdu", "rsync", "shellcheck", "shfmt", "starship", "tealdeer", "tree", "yq"],
        "python": ["pipx", "python", "ruff", "uv"],
        "node": ["node", "pnpm", "yarn"],
        "containers": ["docker", "docker-compose", "lazydocker"],
        "network": ["bind", "mtr", "nmap", "openbsd-netcat", "openssh", "rsync", "socat", "whois"],
        "fonts": ["font-fira-code-nerd-font", "font-jetbrains-mono-nerd-font", "font-meslo-lg-nerd-font", "font-noto-color-emoji"],
    },
    "suse": {
        "dev": ["btop", "direnv", "duf", "go", "htop", "jq", "lazygit", "man", "ncdu", "rsync", "ShellCheck", "shfmt", "starship", "tree", "yq"],
        "python": ["python3", "python3-pip", "python3-virtualenv"],
        "node": ["nodejs", "npm"],
        "containers": ["docker", "docker-compose", "podman"],
        "network": ["bind-utils", "mtr", "netcat-openbsd", "nmap", "openssh-clients", "rsync", "socat", "traceroute", "whois"],
        "fonts": ["google-noto-fonts", "google-noto-coloremoji-fonts", "powerline-fonts"],
    },
}

OH_MY_ZSH_REPO = "https://github.com/ohmyzsh/ohmyzsh.git"
ZSH_GIT_REPOS = {
    "themes/powerlevel10k": "https://github.com/romkatv/powerlevel10k.git",
    "plugins/zsh-autosuggestions": "https://github.com/zsh-users/zsh-autosuggestions.git",
    "plugins/zsh-syntax-highlighting": "https://github.com/zsh-users/zsh-syntax-highlighting.git",
    "plugins/zsh-completions": "https://github.com/zsh-users/zsh-completions.git",
    "plugins/zsh-history-substring-search": "https://github.com/zsh-users/zsh-history-substring-search.git",
}

P10K_ZSH = r"""# Managed by obbyconfigs.
# This setup keeps the Powerlevel10k theme configuration inline in ~/.zshrc
# to match the source machine's Manjaro/Dracula prompt behavior.
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
    tmux_bin: Path
    nanorc: Path
    nano_syntax_dir: Path


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


def read_template(relative_path: str) -> str:
    return files("obbyconfigs").joinpath("templates", relative_path).read_text(encoding="utf-8")


def render_zshrc(paths: InstallPaths) -> str:
    p10k_theme = paths.zsh_custom / "themes" / "powerlevel10k" / "powerlevel10k.zsh-theme"
    return (
        read_template("zshrc.zsh")
        .replace("__OBBY_ZSH_CUSTOM__", str(paths.zsh_custom))
        .replace("__OBBY_P10K_THEME__", str(p10k_theme))
    )


def render_tmux_conf(paths: InstallPaths) -> str:
    tmux_bin = str(paths.tmux_bin)
    if "\n" in tmux_bin or "\r" in tmux_bin:
        raise ValueError("tmux helper path cannot contain newlines")
    quoted_tmux_bin = '"' + tmux_bin.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"'
    return read_template("tmux.conf").replace("__OBBY_TMUX_BIN__", quoted_tmux_bin)


def tmux_helper_scripts() -> dict[str, str]:
    return {
        "git-info": read_template("tmux-bin/git-info"),
        "os-icon": read_template("tmux-bin/os-icon"),
        "pane-title": read_template("tmux-bin/pane-title"),
        "pane-context": read_template("tmux-bin/pane-context"),
    }


def render_nanorc(paths: InstallPaths) -> str:
    return read_template("nano/nanorc").replace("__OBBY_NANO_SYNTAX_DIR__", str(paths.nano_syntax_dir))


def nano_syntax_files() -> dict[str, str]:
    return {
        "obby-dracula.nanorc": read_template("nano/obby-dracula.nanorc"),
    }


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
        aliases = {"ubuntu": "debian", "rhel": "fedora", "centos": "fedora", "rocky": "fedora", "opensuse": "suse", "darwin": "macos"}
        return aliases.get(override, override)
    if platform.system() == "Darwin":
        return "macos"
    os_release = read_os_release()
    ids = " ".join(value.lower() for value in (os_release.get("ID", ""), os_release.get("ID_LIKE", "")))
    if "alpine" in ids or shutil.which("apk"):
        return "alpine"
    if "arch" in ids or shutil.which("pacman"):
        return "arch"
    if any(name in ids for name in ("debian", "ubuntu")) or shutil.which("apt-get"):
        return "debian"
    if any(name in ids for name in ("fedora", "rhel", "centos", "rocky")) or shutil.which("dnf"):
        return "fedora"
    if any(name in ids for name in ("suse", "opensuse")) or shutil.which("zypper"):
        return "suse"
    raise SystemExit("Unsupported OS. This installer supports Arch, Ubuntu, Debian, Fedora/RHEL, openSUSE, Alpine, and macOS with Homebrew.")


def has_command(command: str) -> bool:
    return shutil.which(command) is not None


def package_manager(family: str) -> str | None:
    for command in PACKAGE_MANAGERS[family]:
        if has_command(command):
            return command
    return None


def require_package_manager(family: str) -> str:
    command = package_manager(family)
    if command:
        return command
    expected = " or ".join(PACKAGE_MANAGERS[family])
    raise SystemExit(f"Could not find package manager for {family}: expected {expected}. Use --package-mode none to skip package installs.")


def has_package(family: str, package: str) -> bool:
    if family == "alpine":
        result = subprocess.run(["apk", "info", "-e", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    if family == "arch":
        result = subprocess.run(["pacman", "-Qq", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    if family == "fedora":
        result = subprocess.run(["rpm", "-q", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    if family == "macos":
        result = subprocess.run(["brew", "list", "--versions", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    if family == "suse":
        result = subprocess.run(["rpm", "-q", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    result = subprocess.run(["dpkg-query", "-W", "-f=${Status}", package], capture_output=True, text=True)
    return result.returncode == 0 and "install ok installed" in result.stdout


def package_available(family: str, package: str) -> bool:
    if family == "alpine":
        result = subprocess.run(["apk", "search", "-e", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    if family == "arch":
        result = subprocess.run(["pacman", "-Si", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    if family == "fedora":
        manager = package_manager("fedora") or "dnf"
        result = subprocess.run([manager, "list", "--available", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    if family == "macos":
        result = subprocess.run(["brew", "info", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    if family == "suse":
        result = subprocess.run(["zypper", "--non-interactive", "search", "--exact-match", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    result = subprocess.run(["apt-cache", "show", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def sudo_prefix() -> list[str]:
    if platform.system() == "Darwin":
        return []
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


def requested_packages(family: str, package_mode: str, package_groups: str) -> list[str]:
    if package_mode == "none":
        return []
    packages = list(BASE_PACKAGES[family])
    if package_mode in {"optional", "all", "force"}:
        packages.extend(OPTIONAL_PACKAGES[family])
    selected_groups = [group.strip() for group in package_groups.split(",") if group.strip()]
    if package_mode in {"all", "force"} and not selected_groups:
        selected_groups = sorted(PACKAGE_GROUPS[family])
    for group in selected_groups:
        if group not in PACKAGE_GROUPS[family]:
            known = ", ".join(sorted(PACKAGE_GROUPS[family]))
            raise SystemExit(f"Unknown package group '{group}'. Known groups: {known}")
        packages.extend(PACKAGE_GROUPS[family][group])
    return sorted(set(packages))


def install_packages(runner: Runner, family: str, package_mode: str, package_groups: str) -> None:
    if package_mode == "none":
        print("Skipping packages by request.")
        return
    packages = requested_packages(family, package_mode, package_groups)
    manager = require_package_manager(family)
    missing = packages if package_mode == "force" else [package for package in packages if not has_package(family, package)]
    if not missing:
        print("All requested packages are already installed.")
        return

    available = [package for package in missing if package_available(family, package)]
    unavailable = sorted(set(missing) - set(available))
    if unavailable:
        print("Skipping unavailable packages:", ", ".join(unavailable))
    if not available:
        print("No available missing packages to install.")
        return

    print("Packages to install:", ", ".join(available))
    if family == "alpine":
        runner.run(sudo_prefix() + ["apk", "update"])
        runner.run(sudo_prefix() + ["apk", "add", *available])
        return
    if family == "arch":
        runner.run(sudo_prefix() + ["pacman", "-Syu", "--needed", "--noconfirm", *available])
        return
    if family == "fedora":
        runner.run(sudo_prefix() + [manager, "install", "-y", *available])
        return
    if family == "macos":
        runner.run(["brew", "install", *available])
        return
    if family == "suse":
        runner.run(sudo_prefix() + ["zypper", "--non-interactive", "install", *available])
        return
    runner.run(sudo_prefix() + ["apt-get", "update"])
    runner.run(sudo_prefix() + ["apt-get", "install", "-y", *available])


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


def write_file(runner: Runner, path: Path, content: str, mode: str, backup: bool, file_mode: str = "0644") -> None:
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
            runner.run(sudo_prefix() + ["install", "-m", file_mode, tmp_path, str(path)])
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    else:
        path.write_text(next_content, encoding="utf-8")
        path.chmod(int(file_mode, 8))
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
            tmux_bin=Path(args.tmux_bin or SYSTEM_ROOT / "tmux" / "bin"),
            nanorc=Path(args.nanorc or "/etc/nanorc"),
            nano_syntax_dir=Path(args.nano_syntax_dir or SYSTEM_ROOT / "nano"),
        )
    return InstallPaths(
        home=home,
        tmux_conf=Path(args.tmux_conf or home / ".tmux.conf"),
        zshrc=Path(args.zshrc or home / ".zshrc"),
        p10k=Path(args.p10k or home / ".p10k.zsh"),
        oh_my_zsh=Path(args.oh_my_zsh or home / ".oh-my-zsh"),
        zsh_custom=Path(args.zsh_custom or home / ".oh-my-zsh" / "custom"),
        tmux_bin=Path(args.tmux_bin or home / ".tmux" / "bin"),
        nanorc=Path(args.nanorc or home / ".nanorc"),
        nano_syntax_dir=Path(args.nano_syntax_dir or home / ".nano"),
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
    parser.add_argument("--assume-distro", choices=["auto", "alpine", "arch", "centos", "debian", "darwin", "fedora", "macos", "opensuse", "rhel", "rocky", "suse", "ubuntu"], default="auto", help="override distro detection")
    parser.add_argument("--package-mode", choices=["required", "optional", "all", "none", "force"], default="required", help="package install strategy")
    parser.add_argument("--package-groups", default="", help="comma-separated extra package groups: dev,python,node,containers,network,fonts")
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
    parser.add_argument("--tmux-bin", help="custom tmux helper script directory")
    parser.add_argument("--nanorc", help="custom nano config destination")
    parser.add_argument("--nano-syntax-dir", help="custom nano syntax/theme include directory")
    parser.add_argument("--system-zsh-hook", action="store_true", help="make /etc/zsh/zshrc source /etc/obbyconfigs/zshrc in system scope")
    parser.add_argument("--nano-mode", choices=["skip", "auto", "force"], default="skip", help="nano config install strategy")
    parser.add_argument("--only-packages", action="store_true", help="only install packages")
    parser.add_argument("--only-dotfiles", action="store_true", help="only write tmux/zsh config files")
    parser.add_argument("--only-nano", action="store_true", help="only write nano config and syntax files")
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
        args.nano_mode = "force"
    if args.only_packages:
        args.zsh_mode = "skip"
        args.plugin_mode = "skip"
        args.dotfile_mode = "safe"
        args.shell_mode = "skip"
        args.nano_mode = "skip"
    if args.only_dotfiles:
        args.package_mode = "none"
        args.zsh_mode = "skip"
        args.plugin_mode = "skip"
        args.shell_mode = "skip"
    if args.only_nano:
        args.package_mode = "none"
        args.zsh_mode = "skip"
        args.plugin_mode = "skip"
        args.shell_mode = "skip"
        args.nano_mode = "auto"
    return args


def print_plan(family: str, paths: InstallPaths, args: argparse.Namespace) -> None:
    print(f"scope: {args.scope}")
    print(f"package family: {family}")
    print(f"package mode: {args.package_mode}")
    print(f"package groups: {args.package_groups or '(default)'}")
    print(f"zsh mode: {args.zsh_mode}")
    print(f"plugin mode: {args.plugin_mode}")
    print(f"dotfile mode: {args.dotfile_mode}")
    print(f"shell mode: {args.shell_mode}")
    print(f"tmux: {paths.tmux_conf}")
    print(f"zshrc: {paths.zshrc}")
    print(f"p10k: {paths.p10k}")
    print(f"oh-my-zsh: {paths.oh_my_zsh}")
    print(f"zsh custom: {paths.zsh_custom}")
    print(f"tmux helpers: {paths.tmux_bin}")
    print(f"nano mode: {args.nano_mode}")
    print(f"nanorc: {paths.nanorc}")
    print(f"nano syntax: {paths.nano_syntax_dir}")


def main(argv: list[str] | None = None) -> int:
    args = normalize_args(parse_args(argv))
    if args.print_windows_terminal_scheme:
        print(WINDOWS_TERMINAL_TOKYO_NIGHT)
        return 0
    if platform.system() not in {"Linux", "Darwin"}:
        raise SystemExit("This installer supports Linux and macOS hosts. Use the README for Windows Terminal and WSL setup.")

    family = detect_family(args.assume_distro)
    if family not in SUPPORTED_FAMILIES:
        raise SystemExit(f"Unsupported package family: {family}")

    paths = resolve_paths(args)
    runner = Runner(dry_run=args.dry_run, yes=args.yes)
    print_plan(family, paths, args)
    if args.list_plan:
        return 0

    if args.package_mode != "none":
        install_packages(runner, family, args.package_mode, args.package_groups)

    if not args.only_packages and not args.only_nano:
        install_zsh_assets(runner, paths, args.zsh_mode, args.plugin_mode)
        for script_name, script_content in tmux_helper_scripts().items():
            write_file(runner, paths.tmux_bin / script_name, script_content, args.dotfile_mode, not args.no_backup, file_mode="0755")
        write_file(runner, paths.tmux_conf, render_tmux_conf(paths), args.dotfile_mode, not args.no_backup)
        write_file(runner, paths.zshrc, render_zshrc(paths), args.dotfile_mode, not args.no_backup)
        write_file(runner, paths.p10k, P10K_ZSH, args.dotfile_mode, not args.no_backup)
        if args.scope in {"system", "all-users"} and args.system_zsh_hook:
            write_system_zsh_hook(runner, args.dotfile_mode, not args.no_backup)

    if not args.only_packages and args.nano_mode != "skip":
        nano_dotfile_mode = "force" if args.nano_mode == "force" else args.dotfile_mode
        for file_name, file_content in nano_syntax_files().items():
            write_file(runner, paths.nano_syntax_dir / file_name, file_content, nano_dotfile_mode, not args.no_backup)
        write_file(runner, paths.nanorc, render_nanorc(paths), nano_dotfile_mode, not args.no_backup)

    set_default_shell(runner, args.shell_mode, args.target_user)
    print_next_steps(args.scope)
    return 0
