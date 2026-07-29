from __future__ import annotations

import contextlib
import io
import shlex
import shutil
import subprocess
import tempfile
import time
import unittest
import uuid
from pathlib import Path

from obbyconfigs.installer import main

ROOT = Path(__file__).resolve().parents[1]
PANE_TITLE = ROOT / "src/obbyconfigs/templates/tmux-bin/pane-title"


@unittest.skipUnless(shutil.which("tmux") and shutil.which("node"), "tmux and node are required")
class TmuxIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(Path("/proc/self/environ").is_file(), "Linux procfs is required")
    def test_real_deepseek_backed_claude_environment(self) -> None:
        socket_name = f"obbyconfigs-deepseek-test-{uuid.uuid4().hex}"
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_dir = Path(temp_dir)
            claude_fixture = fixture_dir / "claude"
            claude_fixture.symlink_to(shutil.which("sleep") or "/usr/bin/sleep")

            try:
                subprocess.run(
                    [
                        "tmux",
                        "-L",
                        socket_name,
                        "-f",
                        "/dev/null",
                        "new-session",
                        "-d",
                        f"env ANTHROPIC_BASE_URL=https://api.deepseek.example {claude_fixture} 30",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )

                deadline = time.monotonic() + 5
                tty = ""
                command = ""
                while time.monotonic() < deadline:
                    tty, command = subprocess.run(
                        ["tmux", "-L", socket_name, "display-message", "-p", "#{pane_tty}|#{pane_current_command}"],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.strip().split("|", 1)
                    if command == "claude":
                        break
                    time.sleep(0.1)

                self.assertEqual(command, "claude")
                detected = subprocess.run(
                    [str(PANE_TITLE), tty, command, command],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                self.assertEqual(detected, "deepseek")
            finally:
                subprocess.run(
                    ["tmux", "-L", socket_name, "kill-server"],
                    check=False,
                    capture_output=True,
                    text=True,
                )

    def test_real_tmux_tty_and_node_wrappers(self) -> None:
        socket_name = f"obbyconfigs-test-{uuid.uuid4().hex}"
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_dir = Path(temp_dir)
            fixtures = {
                "codex": "codex",
                "claude": "claude",
                "kimi-code": "kimi",
                "deepseek": "deepseek",
                "gemini": "gemini",
                "antigravity-cli": "antigravity",
                "qwen": "qwen",
                "opencode": "opencode",
                "aider": "aider",
                "goose": "goose",
                "copilot": "copilot",
                "amp": "amp",
                "cursor-agent": "cursor",
                "kiro-cli": "kiro",
                "vibe": "vibe",
            }
            for script_name in fixtures:
                (fixture_dir / script_name).write_text("setInterval(() => {}, 1000);\n", encoding="utf-8")

            try:
                first = True
                for script_name in fixtures:
                    command = [
                        "tmux",
                        "-L",
                        socket_name,
                        "-f",
                        "/dev/null",
                        "new-session" if first else "new-window",
                        "-d",
                        f"node {fixture_dir / script_name}",
                    ]
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    first = False

                deadline = time.monotonic() + 5
                panes: list[tuple[str, str]] = []
                while time.monotonic() < deadline:
                    output = subprocess.run(
                        ["tmux", "-L", socket_name, "list-panes", "-a", "-F", "#{pane_tty}|#{pane_current_command}"],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout
                    panes = [tuple(line.split("|", 1)) for line in output.splitlines()]
                    if len(panes) == len(fixtures) and all(command == "node" for _, command in panes):
                        break
                    time.sleep(0.1)

                self.assertEqual(len(panes), len(fixtures))
                detected = {
                    subprocess.run(
                        [str(PANE_TITLE), tty, command],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                    for tty, command in panes
                }
                self.assertEqual(detected, set(fixtures.values()))
            finally:
                subprocess.run(
                    ["tmux", "-L", socket_name, "kill-server"],
                    check=False,
                    capture_output=True,
                    text=True,
                )

    def test_installed_config_safely_handles_shell_metacharacters_in_home_path(self) -> None:
        socket_name = f"obbyconfigs-space-test-{uuid.uuid4().hex}"
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / "home with spaces $cash \"double\" 'single' \\slash"
            home.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                main(
                    [
                        "--home",
                        str(home),
                        "--only-dotfiles",
                        "--dotfile-mode",
                        "overwrite",
                        "--no-backup",
                        "--yes",
                    ]
                )
            codex_fixture = home / "codex"
            codex_fixture.write_text("setInterval(() => {}, 1000);\n", encoding="utf-8")

            try:
                subprocess.run(
                    [
                        "tmux",
                        "-L",
                        socket_name,
                        "-f",
                        str(home / ".tmux.conf"),
                        "new-session",
                        "-d",
                        f"node {shlex.quote(str(codex_fixture))}",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                subprocess.run(
                    ["tmux", "-L", socket_name, "set-window-option", "automatic-rename", "off"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                subprocess.run(
                    ["tmux", "-L", socket_name, "set-window-option", "automatic-rename", "on"],
                    check=True,
                    capture_output=True,
                    text=True,
                )

                deadline = time.monotonic() + 5
                window_name = ""
                while time.monotonic() < deadline:
                    window_name = subprocess.run(
                        ["tmux", "-L", socket_name, "display-message", "-p", "#{window_name}"],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                    if window_name == "codex":
                        break
                    time.sleep(0.1)
                self.assertEqual(window_name, "codex")
                configured_bin = subprocess.run(
                    ["tmux", "-L", socket_name, "display-message", "-p", "#{OBBY_TMUX_BIN}"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                # tmux 3.2 prints a literal dollar as `\$` while newer tmux
                # prints `$`; successful helper execution above proves both
                # representations resolve to the same configured path.
                self.assertEqual(configured_bin.replace("\\$", "$"), str(home / ".tmux/bin"))
            finally:
                subprocess.run(
                    ["tmux", "-L", socket_name, "kill-server"],
                    check=False,
                    capture_output=True,
                    text=True,
                )


if __name__ == "__main__":
    unittest.main()
