class Obbyconfigs < Formula
  include Language::Python::Virtualenv

  desc "Obby's tmux, zsh, nano, and terminal config installer"
  homepage "https://github.com/obnoxiousmods/obbyconfigs"
  url "https://github.com/obnoxiousmods/obbyconfigs.git", tag: "v0.5.0"
  head "https://github.com/obnoxiousmods/obbyconfigs.git", branch: "main"
  license "MIT"

  depends_on "python@3.13"
  depends_on "git"
  depends_on "tmux"
  depends_on "zsh"
  depends_on "fzf"
  depends_on "zoxide"
  depends_on "ripgrep"
  depends_on "eza"
  depends_on "bat"
  depends_on "nano"

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"obbyinstaller", "--print-windows-terminal-scheme"
  end
end
