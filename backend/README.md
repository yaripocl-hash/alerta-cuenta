# Backend — Alerta Cuenta

FastAPI + Python. Toda la lógica de negocio y las llamadas a Claude viven aquí.

## Estructura

```
app/
├── main.py          ← Entry point FastAPI
├── config.py        ← Variables de entorno (pydantic-settings)
├── api/             ← Routers HTTP (solo validar y delegar a services)
├── core/            ← Utilidades compartidas (tracking codes, HMAC, etc.)
├── db/              ← Cliente Supabase
├── schemas/         ← Modelos Pydantic de request/response
├── services/        ← Lógica de negocio
├── agents/          ← Agentes Claude (uno por función de IA)
└── integrations/    ← Clientes externos (Anthropic, Supabase, stubs)
```

## Correr

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints

| Método | Path | Estado |
|---|---|---|
| GET | /api/health | Funcional |
| POST | /api/cases/ | Stub (Fase 2) |
| GET | /api/cases/{code} | Stub (Fase 2) |
| POST | /api/evidence/{case_id} | Stub (Fase 3) |
| POST | /api/tracking/lookup | Stub (Fase 3) |
| POST | /api/ai/classify | Stub (Fase 2) |
| POST | /api/ai/summarize | Stub (Fase 2) |
