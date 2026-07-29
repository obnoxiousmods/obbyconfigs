from __future__ import annotations

import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from obbyconfigs.installer import InstallPaths, main, render_tmux_conf, tmux_helper_scripts


class InstallerTmuxTests(unittest.TestCase):
    def test_rendered_tmux_config_uses_safe_format_quoting(self) -> None:
        root = Path("/tmp/obby configs")
        paths = InstallPaths(
            home=root,
            tmux_conf=root / ".tmux.conf",
            zshrc=root / ".zshrc",
            p10k=root / ".p10k.zsh",
            oh_my_zsh=root / ".oh-my-zsh",
            zsh_custom=root / ".oh-my-zsh/custom",
            tmux_bin=root / ".tmux/bin",
            nanorc=root / ".nanorc",
            nano_syntax_dir=root / ".nano",
        )
        rendered = render_tmux_conf(paths)
        self.assertNotIn("__OBBY_TMUX_BIN__", rendered)
        self.assertIn('set-environment -g OBBY_TMUX_BIN "/tmp/obby configs/.tmux/bin"', rendered)
        self.assertIn("#{q:OBBY_TMUX_BIN}/pane-title", rendered)
        self.assertIn("#{q:pane_tty}", rendered)
        self.assertIn("#{q;b:pane_current_path}", rendered)
        self.assertIn("#{q:pane_current_command}", rendered)
        self.assertIn("#{q;b:pane_current_path} #{q:pane_current_command}", rendered)
        self.assertIn("#{q:pane_current_path}", rendered)
        self.assertNotIn("'#{pane_tty}'", rendered)
        self.assertNotIn("'#{pane_current_path}'", rendered)

    def test_helper_manifest_contains_all_executable_tmux_helpers(self) -> None:
        helpers = tmux_helper_scripts()
        self.assertEqual(set(helpers), {"git-info", "os-icon", "pane-context", "pane-title"})
        for name, content in helpers.items():
            with self.subTest(name=name):
                self.assertTrue(content.startswith("#!"))
                self.assertIn("set -", content)

    def test_user_install_writes_executable_helper_and_references_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            with contextlib.redirect_stdout(io.StringIO()):
                result = main(
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
            self.assertEqual(result, 0)

            helper_dir = home / ".tmux/bin"
            for name in ("git-info", "os-icon", "pane-context", "pane-title"):
                helper = helper_dir / name
                with self.subTest(name=name):
                    self.assertTrue(helper.is_file())
                    self.assertTrue(os.access(helper, os.X_OK))

            tmux_conf = (home / ".tmux.conf").read_text(encoding="utf-8")
            self.assertIn(f'set-environment -g OBBY_TMUX_BIN "{helper_dir}"', tmux_conf)
            self.assertIn("#{q:OBBY_TMUX_BIN}/pane-title", tmux_conf)
            self.assertNotIn("__OBBY_TMUX_BIN__", tmux_conf)

            mock_dir = home / "mock-bin"
            mock_dir.mkdir()
            mock_ps = mock_dir / "ps"
            mock_ps.write_text("#!/bin/sh\nprintf '%s\\n' \"$OBBY_TEST_PS_OUTPUT\"\n", encoding="utf-8")
            mock_ps.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{mock_dir}{os.pathsep}{env['PATH']}"
            env["OBBY_TEST_PS_OUTPUT"] = "100 1 Sl+ node node /home/me/.local/bin/codex"
            detected = subprocess.run(
                [str(helper_dir / "pane-title"), "/dev/pts/42", "node"],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(detected.stdout.strip(), "codex")


if __name__ == "__main__":
    unittest.main()
