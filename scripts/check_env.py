"""Verifica que las variables de entorno requeridas estén configuradas.
No imprime los valores de los secretos.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

REQUIRED = [
    "APP_SECRET",
    "ANTHROPIC_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
]

OPTIONAL = [
    "ANTHROPIC_MODEL",
    "SUPABASE_STORAGE_BUCKET",
    "CORS_ORIGINS",
    "EMAIL_PROVIDER",
    "LOG_LEVEL",
]

print("=== Verificación de variables de entorno ===\n")

all_ok = True
for var in REQUIRED:
    val = os.getenv(var, "")
    if not val or val.startswith("replace_with"):
        print(f"  FALTA   {var}")
        all_ok = False
    else:
        masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
        print(f"  OK      {var} ({masked})")

print()
for var in OPTIONAL:
    val = os.getenv(var, "")
    status = "OK" if val else "no configurado (opcional)"
    print(f"  {status:30} {var}")

print()
if all_ok:
    print("Todas las variables requeridas están configuradas.")
else:
    print("Hay variables faltantes. Edita tu archivo .env")
    exit(1)
