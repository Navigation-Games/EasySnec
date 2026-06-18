#!/usr/bin/env bash
# Build a single self-contained EasySnec binary with Nuitka (macOS / Linux).
#
# Usage:
#   scripts/build_nuitka.sh                # -> dist/easysnec   (single binary)
#   APP_BUNDLE=1 scripts/build_nuitka.sh   # -> dist/EasySnec.app (macOS .app bundle)
#
set -euo pipefail
cd "$(dirname "$0")/.."

# Shared arguments. Anything loaded dynamically (not via a plain `import`) must
# be force-included or it won't be in the binary.
ARGS=(
  --standalone
  --assume-yes-for-downloads
  --output-dir=dist
  --remove-output
  --company-name="Navigation Games"
  --product-name="EasySnec"
  --product-version="$(uvx hatch version 2>/dev/null || echo 0.1.1)"

  # Force-include packages that are imported conditionally / at runtime.
  --include-package=slint
  --include-package=serial
  --include-module=sportident
  --include-module=sireader
  --include-package=playsound3
  --include-package=pydantic
  --include-package=click
  --include-package=pyxdameraulevenshtein

  # Ship the entire UI tree as data files. This one mapping covers BOTH:
  #   1. slint.loader.easysnec.ui  (walks sys.path for easysnec/ui/*.slint)
  #   2. Path(__file__).parent/'ui'/'resources'/'sounds'  (sound playback)
  # The referenced images (@image-url) live under the same tree.
  --include-data-dir=src/easysnec/ui=easysnec/ui
)

if [[ "$(uname)" == "Darwin" && "${APP_BUNDLE:-0}" == "1" ]]; then
  # Proper macOS .app: gets a Dock icon, correct focus/menu behavior, and is
  # the standard single drag-and-drop unit. Recommended for real distribution.
  ARGS+=( --macos-create-app-bundle --macos-app-name="EasySnec" )
  # ARGS+=( --macos-app-icon=build/EasySnec.icns )   # add an .icns to enable
else
  # Single self-extracting binary (literally one file to hand someone).
  ARGS+=( --onefile --output-filename=easysnec )
fi

# Run via `uv run` (NOT uvx) so Nuitka sees the project's installed packages.
exec uv run nuitka "${ARGS[@]}" src/easysnec/main.py
