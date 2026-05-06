# Reglas Backend

- Toda lógica de negocio va en `services/`, no en los routers de `api/`.
- Routers (`api/`) solo validan el request y llaman al service.
- Schemas Pydantic en `schemas/` — uno por entidad.
- Config solo desde `config.py` via `get_settings()`. Nunca `os.getenv()` directo.
- Cliente Supabase solo via `db/supabase.py`. Nunca crear instancias inline.
- Cliente Anthropic solo via `integrations/anthropic_client.py`.
- Los agentes leen su prompt desde el archivo Markdown versionado, no desde strings hardcodeados.
- Usa `ruff` para linting antes de cada commit.
- Los endpoints stubs deben retornar `HTTP 501` con mensaje claro.
