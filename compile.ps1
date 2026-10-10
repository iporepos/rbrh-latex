# ==============================================================
# compile.ps1 — local build (Windows)
# ==============================================================
# Optional convenience script. Overleaf compiles this project on
# its own; use this only for a local/offline build. Mirrors
# compile.sh (Linux/macOS).
#
# Runs latexmk in silent mode, then (only if the compile
# succeeded) removes the regeneratable auxiliary files it left
# behind -- main.pdf is kept.
# ==============================================================
#Requires -Version 5.1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

latexmk -pdf -interaction=nonstopmode -halt-on-error -silent main.tex
if ($LASTEXITCODE -ne 0) {
    Write-Error "latexmk failed (exit code $LASTEXITCODE) -- see main.log"
    exit $LASTEXITCODE
}

latexmk -c

Write-Host "Build complete: main.pdf"
