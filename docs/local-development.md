# Desarrollo Local — Alerta Cuenta

## Requisitos

- Python 3.11+
- PowerShell (Windows) o Bash (Mac/Linux)
- Git
- Cuenta en Supabase (plan gratuito funciona)
- API Key de Anthropic

## Setup Inicial

### 1. Clonar y configurar entorno

```powershell
git clone https://github.com/yaripocl-hash/alerta-cuenta.git
cd alerta-cuenta
Copy-Item .env.example .env
# Editar .env con tus valores reales
```

### 2. Generar APP_SECRET

```powershell
python scripts/generate_app_secret.py
# Copiar el valor generado a APP_SECRET en .env
```

### 3. Verificar variables de entorno

```powershell
python scripts/check_env.py
```

### 4. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend disponible en:
- API: http://localhost:8000
- Docs Swagger: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

### 5. Frontend

```powershell
# En otra terminal
cd frontend
python -m http.server 5500
```

Frontend disponible en: http://localhost:5500

## Supabase Local (opcional)

Para desarrollo sin conexión, puedes usar Supabase CLI:

```bash
npm install -g supabase
supabase init
supabase start
```

Luego ejecutar el schema:
```bash
supabase db reset
```

## Scripts de Utilidad

```powershell
# Setup completo de backend
.\scripts\setup.ps1

# Correr backend
.\scripts\run_backend.ps1

# Correr frontend
.\scripts\run_frontend.ps1
```

## Linting

```powershell
cd backend
ruff check app/
ruff format app/
```

## Tests

```powershell
cd backend
pytest
```

## Estructura de URLs en Desarrollo

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5500 |
| Backend API | http://localhost:8000/api |
| Backend Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |
