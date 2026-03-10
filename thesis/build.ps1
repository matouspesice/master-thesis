# Rebuild thesis PDF: pdflatex -> bibtex -> pdflatex -> pdflatex
# Run from thesis/ folder: .\build.ps1

Set-Location $PSScriptRoot
$ErrorActionPreference = "Stop"
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
Write-Host "Done. Output: main.pdf"
