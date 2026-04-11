#!/usr/bin/env bash
set -euo pipefail

mkdir -p dist/bundles

zip_bundle() {
  local archive="$1"
  local directory="$2"
  if command -v zip >/dev/null 2>&1; then
    zip -qr "$archive" "$directory"
  else
    python3 -m zipfile -c "$archive" "$directory"
  fi
}

bundle_common() {
  local target="$1"
  mkdir -p "$target"
  cp README.md LICENSE dist/obbyinstaller.pyz "$target/"
}

bundle_common dist/bundles/obbyconfigs-linux
cp install.sh dist/bundles/obbyconfigs-linux/
cat > dist/bundles/obbyconfigs-linux/obbyinstaller <<'EOF'
#!/usr/bin/env sh
exec python3 "$(dirname "$0")/obbyinstaller.pyz" "$@"
EOF
chmod +x dist/bundles/obbyconfigs-linux/obbyinstaller

bundle_common dist/bundles/obbyconfigs-macos
cp install.sh dist/bundles/obbyconfigs-macos/
cat > dist/bundles/obbyconfigs-macos/obbyinstaller <<'EOF'
#!/usr/bin/env sh
exec python3 "$(dirname "$0")/obbyinstaller.pyz" "$@"
EOF
chmod +x dist/bundles/obbyconfigs-macos/obbyinstaller

bundle_common dist/bundles/obbyconfigs-windows
cp install.ps1 dist/bundles/obbyconfigs-windows/
cat > dist/bundles/obbyconfigs-windows/obbyinstaller.cmd <<'EOF'
@echo off
py "%~dp0obbyinstaller.pyz" %*
EOF

cd dist/bundles
zip_bundle ../obbyconfigs-linux-any.zip obbyconfigs-linux
zip_bundle ../obbyconfigs-macos-any.zip obbyconfigs-macos
zip_bundle ../obbyconfigs-windows-any.zip obbyconfigs-windows
