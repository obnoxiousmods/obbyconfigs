# tmux Hotkeys

Full docs: https://obnoxiousmods.github.io/obbyconfigs/
GitHub Wiki: https://github.com/obnoxiousmods/obbyconfigs/wiki

This config keeps both tmux-style and common terminal-style bindings. `Prefix` means either `Ctrl-a` or `Ctrl-b`.

## Prefixes

- `Ctrl-a`: tmux prefix.
- `Ctrl-b`: secondary tmux prefix.
- `Prefix Ctrl-a`: send `Ctrl-a` to the running program.
- `Prefix Ctrl-b`: send `Ctrl-b` to the running program.

## Config

- `Prefix r`: reload `~/.tmux.conf`.
- `Prefix Ctrl-r`: reload `~/.tmux.conf`.
- `Prefix R`: reload `~/.tmux.conf`.
- `Prefix :`: open the tmux command prompt.

## Panes

- `Prefix |`: split pane horizontally, keeping the current directory.
- `Prefix \`: split pane horizontally, keeping the current directory.
- `Prefix %`: split pane horizontally, keeping the current directory.
- `Prefix v`: split pane horizontally, keeping the current directory.
- `Prefix _`: split pane vertically, keeping the current directory.
- `Prefix -`: split pane vertically, keeping the current directory.
- `Prefix "`: split pane vertically, keeping the current directory.
- `Prefix V`: split pane vertically, keeping the current directory.
- `Prefix h` / `Prefix j` / `Prefix k` / `Prefix l`: move left/down/up/right.
- `Prefix Left` / `Prefix Down` / `Prefix Up` / `Prefix Right`: move left/down/up/right.
- `Prefix Ctrl-Left` / `Prefix Ctrl-Down` / `Prefix Ctrl-Up` / `Prefix Ctrl-Right`: move left/down/up/right.
- `Alt-Left` / `Alt-Down` / `Alt-Up` / `Alt-Right`: move left/down/up/right without prefix.
- `Alt-h` / `Alt-j` / `Alt-k` / `Alt-l`: move left/down/up/right without prefix.
- `Prefix H` / `Prefix J` / `Prefix K` / `Prefix L`: resize left/down/up/right.
- `Prefix Shift-Left` / `Prefix Shift-Down` / `Prefix Shift-Up` / `Prefix Shift-Right`: resize left/down/up/right.
- `Prefix Ctrl-Shift-Left` / `Prefix Ctrl-Shift-Down` / `Prefix Ctrl-Shift-Up` / `Prefix Ctrl-Shift-Right`: resize left/down/up/right when your terminal sends those keys.
- `Prefix Alt-H` / `Prefix Alt-J` / `Prefix Alt-K` / `Prefix Alt-L`: resize left/down/up/right.
- `Alt-Shift-Left` / `Alt-Shift-Down` / `Alt-Shift-Up` / `Alt-Shift-Right`: resize left/down/up/right without prefix when your terminal sends those keys.
- `Prefix m`: toggle zoom for the current pane.
- `Prefix z`: toggle zoom for the current pane.
- `Prefix Enter`: toggle zoom for the current pane.
- `Alt-Enter`: toggle zoom for the current pane without prefix.
- `Prefix o`: move to the next pane.
- `Prefix q`: show pane numbers.
- `Prefix x`: confirm and kill the current pane.

## Windows

- `Prefix c`: create a new window in the current directory.
- `Prefix Ctrl-c`: create a new window in the current directory.
- `Prefix n`: next window.
- `Prefix Ctrl-n`: next window.
- `Alt-n`: next window without prefix.
- `Prefix p`: previous window.
- `Prefix N`: previous window.
- `Alt-p`: previous window without prefix.
- `Prefix Tab`: last window.
- `Alt-Tab`: last window when your terminal sends it to tmux.
- `Prefix w`: choose a window from the window tree.
- `Prefix W`: choose a window.
- `Prefix f`: find a window.
- `Prefix /`: find a window.
- `Prefix ,`: rename the current window.
- `Prefix .`: move the current window to a chosen index.
- `Prefix >`: swap the current window forward.
- `Prefix <`: swap the current window backward.
- `Prefix X`: confirm and kill the current window.

## Sessions And Clients

- `Prefix s`: choose a session from the session tree.
- `Prefix P`: rename the current session.
- `Prefix d`: detach the current client.
- `Prefix D`: choose a client to detach.

## Layouts

- `Prefix Space`: move to the next layout.
- `Prefix Ctrl-Space`: move to the previous layout.
- `Prefix E`: set even-horizontal layout.
- `Prefix Ctrl-e`: set even-vertical layout.
- `Prefix Ctrl-o`: rotate panes in the window.

## Popup Shell

- `Prefix Ctrl-p`: open a scratch shell popup in the current directory.
- `Prefix Ctrl-t`: open a scratch shell popup in the current directory.

## Copy Mode

- `Prefix [`: enter copy mode.
- In copy mode, `v`: begin selection.
- In copy mode, `Ctrl-v`: toggle rectangle selection.
- In copy mode, `y`: copy selection and exit copy mode.
- In copy mode, `Escape`: cancel copy mode.
- Mouse drag end in copy mode: copy selection and exit copy mode.

## Mouse

- Mouse support is enabled.
- Wheel up enters copy mode unless mouse forwarding is already active.
- Wheel down sends the wheel event to the pane when mouse forwarding is active.

## Optional TPM

- If `~/.tmux/plugins/tpm/tpm` exists, it is loaded automatically.
