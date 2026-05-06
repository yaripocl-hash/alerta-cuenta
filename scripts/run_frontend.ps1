# run_frontend.ps1 — Sirve el frontend en http://localhost:5500

Set-Location (Join-Path $PSScriptRoot "..\frontend")
Write-Host "Sirviendo frontend en http://localhost:5500 ..." -ForegroundColor Cyan
python -m http.server 5500
