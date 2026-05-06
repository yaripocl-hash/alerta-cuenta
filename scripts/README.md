# Scripts

| Script | Descripción |
|---|---|
| `setup.ps1` | Crea el venv e instala dependencias del backend |
| `run_backend.ps1` | Inicia FastAPI con uvicorn en modo desarrollo |
| `run_frontend.ps1` | Sirve el frontend con Python HTTP server en el puerto 5500 |
| `generate_app_secret.py` | Genera un `APP_SECRET` seguro para `.env` |
| `check_env.py` | Verifica que las variables de entorno requeridas estén configuradas |

## Uso rápido

```powershell
# Setup inicial
.\scripts\setup.ps1

# Correr backend (terminal 1)
.\scripts\run_backend.ps1

# Correr frontend (terminal 2)
.\scripts\run_frontend.ps1

# Generar secret
python scripts\generate_app_secret.py

# Verificar variables
python scripts\check_env.py
```
