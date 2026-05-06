# CLAUDE.md — Instrucciones para Claude Code

Este archivo define cómo Claude Code debe comportarse al trabajar en **Alerta Cuenta**.

---

## Arquitectura que debes respetar

```
frontend/   → HTML + CSS + JS puro. Sin frameworks. Sin Node. Sin bundlers.
backend/    → FastAPI en Python. Aquí vive toda la lógica y las llamadas a Claude API.
prompts/    → Archivos Markdown versionados. Un subdirectorio por agente, v1.md, v2.md...
agents/     → Módulos Python en backend/app/agents/. Uno por función de IA.
infra/      → Schema SQL y docs de deploy. No contiene lógica.
```

## Reglas de Seguridad (obligatorias)

- **NUNCA** pongas `ANTHROPIC_API_KEY` en frontend, HTML, JS ni en ningún archivo público.
- **NUNCA** pongas `SUPABASE_SERVICE_ROLE_KEY` en frontend.
- **NUNCA** hardcodees secretos en código. Usa siempre variables de entorno via `config.py`.
- **NUNCA** crees archivos `.env` con valores reales. Solo `.env.example`.
- Toda llamada a Claude API se hace desde `backend/app/integrations/anthropic_client.py`.
- El frontend llama al backend, el backend llama a Claude.

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
