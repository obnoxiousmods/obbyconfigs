#!/usr/bin/env bash
set -euo pipefail

mkdir -p dist
python -m zipapp src \
  --main "obbyconfigs.installer:main" \
  --python "/usr/bin/env python3" \
  --output dist/obbyinstaller.pyz
chmod +x dist/obbyinstaller.pyz
