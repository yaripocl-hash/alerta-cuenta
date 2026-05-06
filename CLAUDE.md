# CLAUDE.md — Instrucciones para Claude Code

Este archivo define cómo Claude Code debe comportarse al trabajar en **Alerta Cuenta**.

---

## Arquitectura que debes respetar

```
frontend/            → HTML + CSS + JS puro. Sin frameworks. Sin Node. Sin bundlers.
backend/             → FastAPI en Python. Aquí vive toda la lógica y las llamadas a Claude API.
prompts/             → Archivos Markdown versionados. Un subdirectorio por agente, v1.md, v2.md...
backend/app/agents/  → Módulos Python en backend/app/agents/. Uno por función de IA.  No crear carpeta agents/ en la raíz.
infra/               → Schema SQL y docs de deploy. No contiene lógica.
```

## Reglas de Seguridad (obligatorias)

- **NUNCA** pongas `ANTHROPIC_API_KEY` en frontend, HTML, JS ni en ningún archivo público.
- **NUNCA** pongas `SUPABASE_SERVICE_ROLE_KEY` en frontend.
- **NUNCA** hardcodees secretos en código. Usa siempre variables de entorno via `config.py`.
- **NUNCA** crees archivos `.env` con valores reales. Solo `.env.example`.
- Toda llamada a Claude API se hace desde `backend/app/integrations/anthropic_client.py`.
- El frontend llama al backend, el backend llama a Claude.
- En esta fase, el frontend NO se conecta directamente a Supabase. El frontend llama al backend; el backend valida, guarda y consulta datos.

## Reglas de Código

- Código simple, legible y testeable. Sin abstracciones innecesarias.
- Sin comentarios obvios. Solo cuando el "por qué" no es evidente.
- Priorizar claridad sobre cleverness.
- Backend: seguir patrones de `backend/app/` ya establecidos.
- Frontend: mobile-first, alto contraste, botones grandes, accesible para adultos mayores.
- Usar `ruff` para linting en Python.

## Reglas de IA y Prompts

- Los prompts viven en `prompts/<nombre_agente>/v1.md` (y sucesivas versiones).
- Cada agente en `backend/app/agents/` carga su prompt desde el archivo Markdown.
- **NUNCA** inventes leyes, normativas, instituciones ni procedimientos legales chilenos.
- Los outputs de Claude deben ser orientadores, no asesoría legal definitiva.
- Usa lenguaje simple, directo y empático — el usuario puede estar en pánico.
- Si falta contexto, el agente debe pedir más información en vez de asumir.

## Integrations (stubs)

Los archivos en `backend/app/integrations/sernac_stub.py`, `cmf_stub.py`, `csirt_stub.py` y `bank_stub.py` son **placeholders**. No implementes integraciones reales con estas instituciones sin instrucción explícita del equipo.

## Orientación de la Demo

- Este proyecto se presenta en el **Claude Impact Lab Chile 2026**.
- La demo debe ser clara, funcional y demostrar uso real de Claude.
- Priorizar impacto ciudadano visible sobre complejidad técnica oculta.
- El flujo principal: usuario describe fraude → Claude clasifica → Claude genera expediente.
- No construyas features que no contribuyan al flujo principal de la demo.

## Dónde trabajar

| Qué hacer | Dónde |
|---|---|
| Nueva página web | `frontend/*.html` + `frontend/assets/` |
| Nuevo endpoint API | `backend/app/api/` + `backend/app/schemas/` |
| Nueva lógica de negocio | `backend/app/services/` |
| Nuevo agente IA | `backend/app/agents/` + `prompts/<nombre>/v1.md` |
| Nuevo prompt | `prompts/<nombre>/v1.md` |
| Config de infra | `infra/` |
| Documentación | `docs/` |

## Privacidad y PII

- Los datos del usuario (nombre, RUT, banco, monto) son sensibles.
- Ver `docs/privacy-and-pii.md` antes de diseñar cualquier formulario o schema.
- No loguees PII en texto plano.
- El `audit_log` debe registrar acciones, no contenido sensible.
- No pedir ni almacenar claves bancarias, PIN, coordenadas exactas, número completo de tarjeta, CVV, fotos de cédula ni credenciales.

## Criterios de aceptación

Antes de considerar una tarea terminada, verifica:

- El backend sigue levantando correctamente.
- El endpoint `/health` responde.
- El frontend puede abrirse localmente.
- No se agregaron secretos reales.
- No se creó ni modificó un `.env` real.
- No se expuso `ANTHROPIC_API_KEY` ni `SUPABASE_SERVICE_ROLE_KEY`.
- Los cambios respetan la separación frontend/backend/prompts/agentes.
- El flujo principal de demo sigue siendo claro:
  usuario describe fraude → Claude clasifica → Claude genera expediente.
- Si se modifica un prompt, debe mantenerse versionado en `prompts/`.
- Si se agrega lógica de IA, debe pasar por `backend/app/services/ai_service.py` o por un agente en `backend/app/agents/`.

## Supabase

- En esta fase, el frontend NO se conecta directamente a Supabase.
- El frontend llama al backend.
- El backend valida, guarda y consulta datos en Supabase.
- `SUPABASE_SERVICE_ROLE_KEY` solo puede existir en variables de entorno del backend.
- Si se usa `SUPABASE_ANON_KEY`, debe justificarse explícitamente y nunca mezclarse con permisos administrativos.

## Datos que no se deben pedir

No pedir, almacenar ni procesar:

- Claves bancarias.
- PIN.
- CVV.
- Número completo de tarjeta.
- Contraseñas.
- Coordenadas exactas.
- Fotos de cédula o pasaporte en esta fase.
- Credenciales de acceso a bancos, fintechs o correos.

Si el usuario entrega accidentalmente esos datos, el sistema debe advertir que no son necesarios y evitar registrarlos en logs.

## Criterio de competencia

Este proyecto está orientado al Claude Impact Lab Chile 2026. Prioriza siempre:

- Impacto ciudadano visible.
- Uso real y demostrable de Claude.
- Manejo responsable de datos personales.
- Demo funcional antes que arquitectura excesiva.
- Narrativa simple para jurado y usuarios no técnicos.
- No alucinar normativa, instituciones ni procedimientos.