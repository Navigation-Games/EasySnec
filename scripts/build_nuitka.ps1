# Build a single self-contained EasySnec.exe with Nuitka (Windows).
#
# Usage:  pwsh scripts/build_nuitka.ps1   ->  dist/easysnec.exe
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

try { $version = (uvx hatch version) } catch { $version = "0.1.1" }

$args = @(
  "--standalone"
  "--onefile"
  "--assume-yes-for-downloads"
  "--output-dir=dist"
  "--output-filename=easysnec"
  "--remove-output"
  "--company-name=Navigation Games"
  "--product-name=EasySnec"
  "--product-version=$version"

  # No console window (Erkan's note: "the terminal is annoying").
  "--windows-console-mode=disable"
  # "--windows-icon-from-ico=build/icon.ico"   # uncomment to embed the icon

  # Force-include packages imported conditionally / at runtime.
  # winmm audio backend is pure-ctypes, so no pywin32 needed.
  "--include-package=slint"
  "--include-package=serial"
  "--include-module=sportident"
  "--include-module=sireader"
  "--include-package=playsound3"
  "--include-package=pydantic"
  "--include-package=click"
  "--include-package=pyxdameraulevenshtein"

  # Ship the entire UI tree (slint sources, material-1.0, images, sounds).
  "--include-data-dir=src/easysnec/ui=easysnec/ui"

  "src/easysnec/main.py"
)

# Run via `uv run` (NOT uvx) so Nuitka sees the project's installed packages.
uv run nuitka @args
