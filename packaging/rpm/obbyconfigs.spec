Name:           obbyconfigs
Version:        0.5.4
Release:        1%{?dist}
Summary:        Obby's tmux, zsh, nano, and terminal config installer
License:        MIT
URL:            https://github.com/obnoxiousmods/obbyconfigs
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
Requires:       python3
Requires:       git
Requires:       tmux
Requires:       zsh
Requires:       fzf
Requires:       zoxide
Requires:       ripgrep
Requires:       nano
Requires:       curl
Requires:       wget
Requires:       unzip

%description
Installs and manages Obby's terminal environment: tmux, zsh, Powerlevel10k,
zsh plugins, nano syntax highlighting, and related terminal tooling.

%prep
%autosetup

%build
python3 -m pip wheel --no-deps --wheel-dir dist .

%install
python3 -m pip install --no-deps --root %{buildroot} --prefix %{_prefix} dist/*.whl
install -Dm755 install.sh %{buildroot}%{_datadir}/obbyconfigs/install.sh
install -Dm644 README.md %{buildroot}%{_docdir}/obbyconfigs/README.md
install -Dm644 docs/TMUX_HOTKEYS.md %{buildroot}%{_docdir}/obbyconfigs/TMUX_HOTKEYS.md
install -Dm644 LICENSE %{buildroot}%{_licensedir}/obbyconfigs/LICENSE

%files
%license %{_licensedir}/obbyconfigs/LICENSE
%doc %{_docdir}/obbyconfigs/README.md
%doc %{_docdir}/obbyconfigs/TMUX_HOTKEYS.md
%{_bindir}/obbyinstaller
%{python3_sitelib}/obbyconfigs*
%{_datadir}/obbyconfigs/install.sh

%changelog
* Wed Jul 29 2026 obnoxiousmods <noreply@github.com> - 0.5.4-1
- Detect DeepSeek-backed Claude wrappers and additional coding-agent CLIs.

* Wed Jul 29 2026 obnoxiousmods <noreply@github.com> - 0.5.3-1
- Avoid repeated subprocesses during tmux title refreshes.
- Fast-path direct agent and idle-shell pane names.

* Wed Jul 29 2026 obnoxiousmods <noreply@github.com> - 0.5.2-1
- Support macOS Bash 3 and safely quote tmux helper arguments.
- Expand AI CLI launch detection and end-to-end tmux coverage.

* Wed Jul 29 2026 obnoxiousmods <noreply@github.com> - 0.5.1-1
- Reliably detect Codex, Claude, and Kimi in tmux pane titles.

* Sat Apr 11 2026 obnoxiousmods <noreply@github.com> - 0.5.0-1
- Initial RPM packaging.
