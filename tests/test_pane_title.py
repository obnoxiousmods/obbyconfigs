from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANE_TITLE = ROOT / "src/obbyconfigs/templates/tmux-bin/pane-title"


class PaneTitleTests(unittest.TestCase):
    def run_title(
        self,
        fixture: str,
        *,
        tty: str = "/dev/pts/42",
        fallback: str = "project",
        current_hint: str | None = None,
        process_environments: dict[int, dict[str, str]] | None = None,
    ) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_ps = temp_path / "ps"
            mock_ps.write_text("#!/bin/sh\nprintf '%s\\n' \"$OBBY_TEST_PS_OUTPUT\"\n", encoding="utf-8")
            mock_ps.chmod(0o755)
            proc_root = temp_path / "proc"
            proc_root.mkdir()
            for pid, variables in (process_environments or {}).items():
                process_dir = proc_root / str(pid)
                process_dir.mkdir()
                environment = b"\0".join(f"{name}={value}".encode() for name, value in variables.items()) + b"\0"
                (process_dir / "environ").write_bytes(environment)
            env = os.environ.copy()
            env["PATH"] = f"{temp_path}{os.pathsep}{env['PATH']}"
            env["OBBY_TEST_PS_OUTPUT"] = fixture
            env["OBBY_PROC_ROOT"] = str(proc_root)
            command = [str(PANE_TITLE), tty, fallback]
            if current_hint is not None:
                command.append(current_hint)
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
        return result.stdout.strip()

    def test_tmux_command_hint_fast_paths_without_calling_ps(self) -> None:
        cases = {
            "codex": "codex",
            "CODEX-LINUX-X64": "codex",
            "kimi": "kimi",
            "KIMI-CODE": "kimi",
            "deepseek": "deepseek",
            "DEEPSEEK-CLI": "deepseek",
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
            "zsh": "project",
            "BASH": "project",
        }
        for hint, expected in cases.items():
            with self.subTest(hint=hint):
                self.assertEqual(self.run_title("should not be read", current_hint=hint), expected)

    def test_claude_hint_scans_environment_for_deepseek_wrapper(self) -> None:
        fixture = "100 1 Sl+ claude claude --resume"
        self.assertEqual(
            self.run_title(
                fixture,
                current_hint="claude",
                process_environments={100: {"ANTHROPIC_BASE_URL": "https://api.deepseek.example/v1"}},
            ),
            "deepseek",
        )
        self.assertEqual(
            self.run_title(
                fixture,
                current_hint="claude",
                process_environments={100: {"ANTHROPIC_BASE_URL": "https://api.anthropic.com"}},
            ),
            "claude",
        )

    def test_explicit_agent_marker_identifies_custom_deepseek_wrapper(self) -> None:
        fixture = "100 1 Sl+ claude claude --resume"
        self.assertEqual(
            self.run_title(
                fixture,
                current_hint="claude",
                process_environments={100: {"OBBY_AGENT_LABEL": "deepseek"}},
            ),
            "deepseek",
        )

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
            "/opt/bin/CODEX": "codex",
            "claude": "claude",
            "claude-code": "claude",
            "/opt/bin/CLAUDE": "claude",
            "kimi": "kimi",
            "kimi-code": "kimi",
            "kimi-cli": "kimi",
            "/opt/bin/KIMI-CODE": "kimi",
            "deepseek": "deepseek",
            "deepseek-cli": "deepseek",
            "deepseek-coder": "deepseek",
            "/opt/bin/DEEPSEEK": "deepseek",
            "gemini": "gemini",
            "gemini-cli": "gemini",
            "antigravity": "antigravity",
            "antigravity-cli": "antigravity",
            "qwen": "qwen",
            "qwen-code": "qwen",
            "opencode": "opencode",
            "opencode-ai": "opencode",
            "aider": "aider",
            "aider-chat": "aider",
            "goose": "goose",
            "copilot": "copilot",
            "github-copilot": "copilot",
            "amp": "amp",
            "ampcode": "amp",
            "cursor-agent": "cursor",
            "kiro": "kiro",
            "kiro-cli": "kiro",
            "vibe": "vibe",
            "mistral-vibe": "vibe",
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

    def test_additional_agent_wrapper_signatures(self) -> None:
        cases = {
            "node /home/me/.local/bin/deepseek": "deepseek",
            "node /usr/local/lib/node_modules/@deepseek-ai/deepseek-cli/dist/cli.js": "deepseek",
            "node /home/me/.local/bin/gemini": "gemini",
            "node /usr/local/lib/node_modules/@google/gemini-cli/dist/index.js": "gemini",
            "node /home/me/.local/bin/antigravity-cli": "antigravity",
            "node /home/me/.local/bin/qwen": "qwen",
            "node /usr/local/lib/node_modules/@qwen-code/qwen-code/dist/cli.js": "qwen",
            "node /home/me/.local/bin/opencode": "opencode",
            "node /usr/local/lib/node_modules/opencode-ai/bin/opencode": "opencode",
            "node /home/me/.local/bin/copilot": "copilot",
            "node /usr/local/lib/node_modules/@github/copilot/index.js": "copilot",
            "node /home/me/.local/bin/goose": "goose",
            "node /home/me/.local/bin/amp": "amp",
            "node /home/me/.local/bin/cursor-agent": "cursor",
            "node /home/me/.local/bin/kiro-cli": "kiro",
            "python -m aider": "aider",
            "python3 /venv/lib/python3.13/site-packages/aider/main.py": "aider",
            "python /home/me/.local/bin/aider": "aider",
            "python -m mistral_vibe": "vibe",
            "python3 /venv/lib/python3.13/site-packages/mistral_vibe/cli.py": "vibe",
            "python /home/me/.local/bin/vibe": "vibe",
        }
        for command, expected in cases.items():
            comm = command.split()[0]
            with self.subTest(command=command):
                self.assertEqual(self.run_title(f"100 1 Sl+ {comm} {command}"), expected)

    def test_package_manager_agent_launchers(self) -> None:
        cases = {
            "npm exec @openai/codex": "codex",
            "npx @openai/codex@latest": "codex",
            "pnpm dlx codex": "codex",
            "yarn codex": "codex",
            "bunx codex": "codex",
            "npm exec @anthropic-ai/claude-code": "claude",
            "npx claude-code@latest": "claude",
            "pnpx claude": "claude",
            "yarn claude": "claude",
            "bunx @anthropic-ai/claude-code": "claude",
            "npm exec @moonshot-ai/kimi-cli": "kimi",
            "npx kimi-code@latest": "kimi",
            "pnpm dlx kimi-cli": "kimi",
            "yarn kimi": "kimi",
            "bunx @moonshot-ai/kimi-code": "kimi",
            "npm exec @deepseek-ai/deepseek-cli": "deepseek",
            "npx deepseek-cli@latest": "deepseek",
            "pnpm dlx deepseek-coder": "deepseek",
            "npm exec @google/gemini-cli": "gemini",
            "npx gemini-cli@latest": "gemini",
            "npx @google/antigravity-cli": "antigravity",
            "pnpm dlx @qwen-code/qwen-code": "qwen",
            "yarn qwen-code": "qwen",
            "bunx opencode-ai": "opencode",
            "npm exec @github/copilot": "copilot",
        }
        for args, expected in cases.items():
            comm = args.split()[0]
            with self.subTest(args=args):
                self.assertEqual(self.run_title(f"100 1 Sl+ {comm} {args}"), expected)

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

    def test_deepseek_claude_wrapper_beats_plain_claude_and_mcp_children(self) -> None:
        fixture = "\n".join(
            (
                "100 1 Sl+ claude claude --resume",
                "101 100 Sl+ node node /home/me/.local/share/camoufox-mcp/dist/index.js",
                "102 100 Sl+ node node /home/me/.npm/_npx/pkg/node_modules/.bin/playwright-mcp",
            )
        )
        environment = {
            "ANTHROPIC_BASE_URL": "https://api.deepseek.example/anthropic",
            "ANTHROPIC_API_KEY": "not-printed",
            "ANTHROPIC_MODEL": "deepseek-chat",
        }
        self.assertEqual(self.run_title(fixture, process_environments={100: environment}), "deepseek")

    def test_deepseek_environment_detection_does_not_depend_on_row_order(self) -> None:
        fixture = "\n".join(
            (
                "100 1 Sl+ claude claude --resume",
                "101 100 Sl+ claude claude-code --worker",
            )
        )
        self.assertEqual(
            self.run_title(
                fixture,
                process_environments={
                    100: {"ANTHROPIC_BASE_URL": "https://api.anthropic.com"},
                    101: {"CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4"},
                },
            ),
            "deepseek",
        )

    def test_agent_detection_does_not_depend_on_ps_row_order(self) -> None:
        fixture = "\n".join(
            (
                "500 100 Sl+ node node /home/me/.local/share/camoufox-mcp/dist/index.js",
                "100 1 Sl+ claude claude --resume",
                "501 500 Sl+ node node /home/me/.npm/_npx/pkg/node_modules/.bin/camoufox-mcp-server",
            )
        )
        self.assertEqual(self.run_title(fixture), "claude")

    def test_background_agent_does_not_override_foreground_command(self) -> None:
        fixture = "\n".join(
            (
                "100 1 Sl codex /home/me/.local/bin/codex",
                "200 1 Sl+ node node server.js",
            )
        )
        self.assertEqual(self.run_title(fixture), "node")

    def test_background_deepseek_claude_wrapper_does_not_override_foreground_command(self) -> None:
        fixture = "\n".join(
            (
                "100 1 Sl claude claude --resume",
                "200 1 Sl+ node node server.js",
            )
        )
        self.assertEqual(
            self.run_title(
                fixture,
                process_environments={100: {"ANTHROPIC_MODEL": "deepseek-chat"}},
            ),
            "node",
        )

    def test_agent_name_in_arbitrary_arguments_does_not_false_positive(self) -> None:
        names = (
            "codex",
            "claude",
            "kimi",
            "deepseek",
            "gemini",
            "antigravity",
            "qwen",
            "opencode",
            "aider",
            "goose",
            "copilot",
            "amp",
            "cursor",
            "kiro",
            "vibe",
        )
        for name in names:
            with self.subTest(name=name):
                fixture = f"100 1 Sl+ node node server.js --title {name}"
                self.assertEqual(self.run_title(fixture), "node")

    def test_secret_value_does_not_identify_deepseek(self) -> None:
        fixture = "100 1 Sl+ claude claude --resume"
        self.assertEqual(
            self.run_title(
                fixture,
                process_environments={
                    100: {
                        "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
                        "ANTHROPIC_API_KEY": "deepseek-is-just-secret-text",
                    }
                },
            ),
            "claude",
        )

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

    def test_script_remains_compatible_with_macos_bash_3(self) -> None:
        script = PANE_TITLE.read_text(encoding="utf-8")
        self.assertNotIn(",,}", script)
        self.assertNotIn("declare -A", script)
        self.assertNotIn("mapfile", script)
        self.assertNotIn("tr '[:upper:]' '[:lower:]'", script)
        self.assertIn("shopt -s nocasematch", script)


if __name__ == "__main__":
    unittest.main()
