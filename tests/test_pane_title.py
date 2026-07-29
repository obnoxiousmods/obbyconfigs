from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANE_TITLE = ROOT / "src/obbyconfigs/templates/tmux-bin/pane-title"


class PaneTitleTests(unittest.TestCase):
    def run_title(self, fixture: str, *, tty: str = "/dev/pts/42", fallback: str = "project") -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_ps = temp_path / "ps"
            mock_ps.write_text("#!/bin/sh\nprintf '%s\\n' \"$OBBY_TEST_PS_OUTPUT\"\n", encoding="utf-8")
            mock_ps.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{temp_path}{os.pathsep}{env['PATH']}"
            env["OBBY_TEST_PS_OUTPUT"] = fixture
            result = subprocess.run(
                [str(PANE_TITLE), tty, fallback],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
        return result.stdout.strip()

    def test_rejects_missing_non_device_and_option_like_ttys(self) -> None:
        fixture = "100 1 Sl+ codex codex"
        for tty in ("", "pts/42", "/dev/-e", "/dev/pts/a b", "/dev/pts/a;b"):
            with self.subTest(tty=tty):
                self.assertEqual(self.run_title(fixture, tty=tty), "project")

    def test_uses_fallback_when_ps_has_no_processes(self) -> None:
        self.assertEqual(self.run_title(""), "project")

    def test_uses_fallback_when_only_background_processes_exist(self) -> None:
        fixture = "100 1 Sl node node /home/me/.local/bin/codex"
        self.assertEqual(self.run_title(fixture), "project")

    def test_shells_use_fallback(self) -> None:
        for shell in ("sh", "bash", "zsh", "fish", "dash", "ksh"):
            with self.subTest(shell=shell):
                self.assertEqual(self.run_title(f"100 1 Ss+ {shell} -{shell}"), "project")

    def test_direct_agent_commands(self) -> None:
        cases = {
            "codex": "codex",
            "codex-linux-x64": "codex",
            "claude": "claude",
            "claude-code": "claude",
            "kimi": "kimi",
            "kimi-code": "kimi",
            "kimi-cli": "kimi",
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(self.run_title(f"100 1 Sl+ {command} {command} --resume"), expected)

    def test_codex_node_wrapper_signatures(self) -> None:
        commands = (
            "node /home/me/.local/bin/codex",
            "node /usr/local/bin/codex resume",
            "node /home/me/.local/lib/node_modules/@openai/codex/bin/codex.js",
            "node /opt/pkg/@openai/codex/codex",
            "node /opt/pkg/codex-linux-x64/vendor/bin/codex",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.run_title(f"100 1 Sl+ node {command}"), "codex")

    def test_claude_node_wrapper_signatures(self) -> None:
        commands = (
            "node /home/me/.local/bin/claude",
            "node /usr/local/lib/node_modules/@anthropic-ai/claude-code/cli.js",
            "node /opt/claude-code/cli.js",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.run_title(f"100 1 Sl+ node {command}"), "claude")

    def test_kimi_node_wrapper_signatures(self) -> None:
        commands = (
            "node /home/me/.local/bin/kimi",
            "node /home/me/.local/bin/kimi-code",
            "node /usr/local/lib/node_modules/@moonshot-ai/kimi-cli/bin/kimi.js",
            "node /opt/kimi-code/cli.js",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.run_title(f"100 1 Sl+ node {command}"), "kimi")

    def test_real_codex_tree_prefers_agent_over_node_wrapper_and_helpers(self) -> None:
        fixture = "\n".join(
            (
                "3111830 3511839 Sl+ node node /home/me/.local/bin/codex",
                "3111838 3111830 Sl+ codex /home/me/.local/lib/node_modules/@openai/codex/vendor/bin/codex",
                "3112022 3111838 Sl node node /home/me/.local/share/camoufox-mcp/dist/index.js",
                "3112101 3112021 Sl node node /home/me/.npm/_npx/pkg/node_modules/.bin/camoufox-mcp-server",
            )
        )
        self.assertEqual(self.run_title(fixture), "codex")

    def test_real_claude_tree_prefers_agent_over_same_group_node_helpers(self) -> None:
        fixture = "\n".join(
            (
                "1035127 3672854 Sl+ claude claude --allow-dangerously-skip-permissions",
                "1035191 1035127 Sl+ node node /home/me/.local/share/camoufox-mcp/dist/index.js",
                "1035192 1035127 Sl+ npm npm exec camoufox-mcp-server@latest",
                "1035284 1035192 Sl+ node node /home/me/.npm/_npx/pkg/node_modules/.bin/camoufox-mcp-server",
                "3672854 1 Ss zsh -zsh",
            )
        )
        self.assertEqual(self.run_title(fixture), "claude")

    def test_real_kimi_tree_prefers_agent_over_same_group_node_helpers(self) -> None:
        fixture = "\n".join(
            (
                "320855 320676 Sl+ kimi-code kimi-code",
                "320985 320855 Sl+ node node /home/me/.npm/_npx/pkg/node_modules/.bin/playwright-mcp",
                "320991 320855 Sl+ node node /home/me/.npm/_npx/pkg/node_modules/.bin/camoufox-mcp-server",
                "321004 320940 Sl+ node node /home/me/.npm/_npx/pkg/node_modules/.bin/mcp-server-sqlite-npx",
            )
        )
        self.assertEqual(self.run_title(fixture), "kimi")

    def test_background_agent_does_not_override_foreground_command(self) -> None:
        fixture = "\n".join(
            (
                "100 1 Sl codex /home/me/.local/bin/codex",
                "200 1 Sl+ node node server.js",
            )
        )
        self.assertEqual(self.run_title(fixture), "node")

    def test_agent_name_in_arbitrary_arguments_does_not_false_positive(self) -> None:
        fixture = "100 1 Sl+ node node server.js --title codex"
        self.assertEqual(self.run_title(fixture), "node")

    def test_node_runtime_labels(self) -> None:
        cases = {
            "node ./node_modules/.bin/vite --host": "vite",
            "node ./node_modules/next/dist/bin/next dev": "next",
            "bun ./node_modules/.bin/astro dev": "astro",
            "deno run ./node_modules/.bin/tsx app.ts": "tsx",
            "node ./node_modules/.bin/ts-node app.ts": "ts-node",
        }
        for args, expected in cases.items():
            comm = args.split()[0]
            with self.subTest(args=args):
                self.assertEqual(self.run_title(f"100 1 Sl+ {comm} {args}"), expected)

    def test_python_runtime_labels(self) -> None:
        cases = {
            "python -m uvicorn app:api": "uvicorn",
            "python3 -m gunicorn app:api": "gunicorn",
            "python3 /venv/bin/pytest -q": "pytest",
            "python3 /venv/bin/django-admin runserver": "django",
        }
        for args, expected in cases.items():
            comm = args.split()[0]
            with self.subTest(args=args):
                self.assertEqual(self.run_title(f"100 1 Sl+ {comm} {args}"), expected)

    def test_generic_command_uses_first_foreground_process(self) -> None:
        fixture = "\n".join(
            (
                "100 1 Sl+ make make test",
                "101 100 Sl+ cc cc source.c",
            )
        )
        self.assertEqual(self.run_title(fixture), "make")


if __name__ == "__main__":
    unittest.main()
