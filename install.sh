#!/usr/bin/env bash
set -euo pipefail

repo_url="${OBBYCONFIGS_REPO:-https://github.com/obnoxiousmods/obbyconfigs.git}"
ref="${OBBYCONFIGS_REF:-main}"
workdir="${OBBYCONFIGS_WORKDIR:-}"

need() {
  command -v "$1" >/dev/null 2>&1
}

sudo_prefix() {
  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    return 0
  fi
  if need sudo; then
    printf 'sudo'
    return 0
  fi
  echo "sudo is required when bootstrapping as a non-root user." >&2
  exit 1
}

install_bootstrap_deps() {
  if need git && need python3; then
    return 0
  fi

  if need pacman; then
    "$(sudo_prefix)" pacman -Syu --needed --noconfirm git python
  elif need apt-get; then
    "$(sudo_prefix)" apt-get update
    "$(sudo_prefix)" apt-get install -y git python3
  elif need dnf; then
    "$(sudo_prefix)" dnf install -y git python3
  elif need zypper; then
    "$(sudo_prefix)" zypper --non-interactive install git python3
  elif need apk; then
    "$(sudo_prefix)" apk update
    "$(sudo_prefix)" apk add git python3
  elif need brew; then
    brew install git python
  else
    echo "Install git and Python 3, then rerun this installer." >&2
    exit 1
  fi
}

install_bootstrap_deps

if [[ -z "$workdir" ]]; then
  workdir="$(mktemp -d)"
  trap 'rm -rf "$workdir"' EXIT
fi

if [[ -d "$workdir/.git" ]]; then
  git -C "$workdir" fetch --depth=1 origin "$ref"
  git -C "$workdir" checkout FETCH_HEAD
else
  git clone --depth=1 --branch "$ref" "$repo_url" "$workdir"
fi

cd "$workdir"
exec python3 obbyinstaller.py "$@"
