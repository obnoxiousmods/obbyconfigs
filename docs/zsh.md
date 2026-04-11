# Zsh Setup

The zsh template is based on the source machine's Manjaro/Dracula setup.

It includes:

- Powerlevel10k
- autosuggestions
- syntax highlighting
- completions
- history substring search
- fzf file and directory pickers
- zoxide `cd`
- icon `ls` through eza/exa/lsd
- themed `LS_COLORS`
- dev PATH support for Python, Node, Go, Rust, bun, deno, uv, pnpm, pyenv, rye, and local project bins
- automatic tmux attach or create
- nano Dracula colors are available with `--nano-mode auto`
- macOS/Homebrew and Linux package manager fallbacks for required tools

Disable auto-tmux for a shell:

```bash
NO_AUTO_TMUX=1 zsh
```

Use a different auto-created session name:

```bash
OBBY_TMUX_SESSION=work zsh
```
