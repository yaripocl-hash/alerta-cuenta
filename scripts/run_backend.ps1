# run_backend.ps1 — Inicia el servidor FastAPI en modo desarrollo

$venvActivate = Join-Path $PSScriptRoot "..\backend\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) { & $venvActivate }

Set-Location (Join-Path $PSScriptRoot "..\backend")
Write-Host "Iniciando backend en http://localhost:8000 ..." -ForegroundColor Cyan
Write-Host "Docs disponibles en http://localhost:8000/docs" -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
