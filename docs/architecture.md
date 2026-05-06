# Arquitectura — Alerta Cuenta

## Visión General

```
[Usuario]
    │
    ▼
[Frontend — HTML/CSS/JS]  ──── fetch ────▶  [Backend — FastAPI]
  localhost:5500 / Vercel                       localhost:8000 / Render
                                                       │
                                        ┌──────────────┼──────────────┐
                                        ▼              ▼              ▼
                                   [Supabase]    [Claude API]   [Supabase Storage]
                                  (PostgreSQL)   (Anthropic)       (evidencia)
```

## Capas

### Frontend
- HTML estático, CSS propio, JS puro sin frameworks.
- Se comunica **solo** con el backend via `fetch()`.
- No accede a Supabase directamente.
- No conoce ninguna clave secreta.
- Deploy en Vercel desde la carpeta `frontend/`.

### Backend (FastAPI)
- Recibe peticiones del frontend.
- Valida datos con Pydantic.
- Llama a Supabase para persistencia.
- Llama a Claude API para los agentes de IA.
- Maneja uploads de evidencia a Supabase Storage.
- Genera códigos de seguimiento para casos.

### Agentes Claude
Cada agente es un módulo Python independiente en `backend/app/agents/`:

| Agente | Función |
|---|---|
| `fraud_classifier_agent` | Clasifica el tipo de fraude |
| `case_summary_agent` | Resume el caso en lenguaje estructurado |
| `evidence_gap_agent` | Identifica evidencia faltante |
| `statement_generator_agent` | Genera declaración preliminar |
| `risk_flags_agent` | Detecta señales de alerta en el relato |

Cada agente carga su prompt desde `prompts/<nombre>/v1.md`.

### Supabase
- PostgreSQL para datos del caso.
- Storage para archivos de evidencia (imágenes, PDFs).
- La `service_role_key` solo se usa desde el backend.
- La `anon_key` no se usa en esta arquitectura (todo pasa por backend).

## Flujo Principal

```
1. Usuario abre denuncia.html
2. Completa formulario paso a paso (form-wizard.js)
3. JS envía POST /api/cases al backend
4. Backend persiste caso en Supabase, asigna tracking_code
5. Backend llama a fraud_classifier_agent → Claude
6. Backend llama a case_summary_agent → Claude
7. Backend llama a risk_flags_agent → Claude
8. Backend guarda outputs en case_ai_outputs
9. Frontend recibe tracking_code y redirige a expediente.html
10. Usuario puede subir evidencia → POST /api/evidence
11. Backend sube archivo a Supabase Storage
12. Usuario puede consultar estado en seguimiento.html
```

## Seguridad

Ver `docs/security.md`.

## Privacidad

Ver `docs/privacy-and-pii.md`.
