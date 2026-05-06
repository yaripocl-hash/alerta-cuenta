# setup.ps1 — Instala el entorno de desarrollo del backend

$ErrorActionPreference = "Stop"

Write-Host "=== Alerta Cuenta — Setup Backend ===" -ForegroundColor Cyan

# Verificar Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python no encontrado. Instala Python 3.11+ desde python.org"
    exit 1
}
Write-Host "Python: $(python --version)" -ForegroundColor Green

# Crear venv si no existe
$venvPath = Join-Path $PSScriptRoot "..\backend\.venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv $venvPath
}

# Activar venv
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

# Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
pip install -r (Join-Path $PSScriptRoot "..\backend\requirements.txt") --quiet

# Verificar .env
$envFile = Join-Path $PSScriptRoot "..\.env"
if (-not (Test-Path $envFile)) {
    Write-Host ""
    Write-Host "AVISO: No se encontro .env" -ForegroundColor Yellow
    Write-Host "Crea el archivo con: Copy-Item .env.example .env" -ForegroundColor Yellow
    Write-Host "Luego edita .env con tus valores reales." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup completo." -ForegroundColor Green
Write-Host "Para correr el backend: .\scripts\run_backend.ps1" -ForegroundColor Cyan
