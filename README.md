# Alerta Cuenta

**Plataforma web de emergencia y orientación ciudadana para fraude financiero digital.**

Creada para el **Claude Impact Lab Chile 2026** dentro del Chile Fintech Forum.

---

## El Problema

Muchas personas en Chile son víctimas de fraudes financieros digitales: phishing, vishing, smishing, suplantación por WhatsApp, transferencias engañosas y falsas compras online. El problema no es solo técnico — las víctimas **no saben qué hacer primero**, qué evidencia guardar, cómo ordenar el relato ni qué institución contactar.

## La Solución

Alerta Cuenta guía al usuario paso a paso:

1. Describe lo ocurrido en lenguaje simple
2. Sube evidencia (capturas, comprobantes)
3. Recibe acciones urgentes prioritizadas
4. Obtiene un resumen estructurado del caso
5. Genera un expediente preliminar para banco, fintech, SERNAC, CMF, CSIRT u otra institución

El motor de inteligencia es **Claude (Anthropic)**, llamado exclusivamente desde el backend.

---

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | HTML, CSS, JavaScript puro |
| Backend | Python + FastAPI |
| Base de datos | Supabase (PostgreSQL) |
| Almacenamiento | Supabase Storage |
| IA | Claude API (Anthropic) — solo desde backend |
| Deploy frontend | Vercel |
| Deploy backend | Render / Railway / Fly.io |

---

## Estructura del Proyecto

```
alerta-cuenta/
├── frontend/          # Páginas HTML + CSS + JS
├── backend/           # FastAPI app + agentes Claude
├── prompts/           # Prompts versionados en Markdown
├── docs/              # Documentación técnica y de contexto
├── infra/             # Schema Supabase + config Vercel
├── scripts/           # Scripts de setup y utilidad
├── notebooks/         # Evaluación de prompts
└── .claude/           # Reglas y comandos para Claude Code
```

---

## Correr en Local

### Frontend

```powershell
cd frontend
python -m http.server 5500
# Abrir http://localhost:5500
```

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
# API disponible en http://localhost:8000
# Docs en http://localhost:8000/docs
```

### Generar APP_SECRET

```powershell
python scripts/generate_app_secret.py
```

### Verificar variables de entorno

```powershell
python scripts/check_env.py
```

---

## Variables de Entorno

Copia `.env.example` a `.env` y completa los valores:

```powershell
Copy-Item .env.example .env
```

**Nunca subas `.env` a Git. Está en `.gitignore`.**

Variables críticas:
- `ANTHROPIC_API_KEY` — solo en backend
- `SUPABASE_SERVICE_ROLE_KEY` — solo en backend
- `APP_SECRET` — generar con el script

---

## Supabase

1. Crear proyecto en [supabase.com](https://supabase.com)
2. Ejecutar `infra/supabase/schema.sql` en el SQL Editor
3. Crear bucket `evidence` en Storage (ver `infra/supabase/storage.md`)
4. Copiar URL y claves a `.env`

---

## Deploy Frontend en Vercel

```bash
# Con Vercel CLI
vercel --cwd frontend

# O conectar el repositorio en vercel.com
# Root directory: frontend
```

Ver guía completa en `infra/vercel/deployment.md`.

El backend **no** se despliega en Vercel — usar Render, Railway o Fly.io.

---

## Remote Git

```powershell
git remote add origin https://github.com/yaripocl-hash/alerta-cuenta.git
git branch -M main
git push -u origin main
```

---

## Advertencia de Seguridad

> **NUNCA** subas archivos `.env`, claves API, service role keys ni secretos a Git.
> Revisa `.gitignore` antes de cada commit.
> La API key de Anthropic y la service_role_key de Supabase deben estar **solo en el backend**.
