#!/usr/bin/env bash
# ==============================================================
# compile.sh — local build (Linux/macOS)
# ==============================================================
# Optional convenience script. Overleaf compiles this project on
# its own; use this only for a local/offline build. Mirrors
# compile.ps1 (Windows).
#
# Runs latexmk in silent mode, then (only if the compile
# succeeded) removes the regeneratable auxiliary files it left
# behind -- main.pdf is kept.
# ==============================================================
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

latexmk -pdf -interaction=nonstopmode -halt-on-error -silent main.tex
latexmk -c

echo "Build complete: main.pdf"
