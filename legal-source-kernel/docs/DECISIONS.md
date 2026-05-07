# Architecture Decision Records

## ADR-001 — Por qué SQLite

**Decisión:** Usar SQLite nativo via `sqlite3` de Python estándar, sin ORM.

**Contexto:** El kernel v0.1 es una herramienta personal/profesional local. No tiene requerimientos de concurrencia alta ni multiusuario.

**Razones:**
- Zero dependencies: `sqlite3` viene en Python stdlib.
- Simple de instalar, simple de respaldar (es un archivo).
- Suficientemente performante para miles de documentos jurídicos.
- WAL mode habilita lecturas concurrentes si se necesita en el futuro.
- Fácil de migrar a PostgreSQL si el sistema escala (cambiar `get_db()` y adaptar DDL).

**Alternativas descartadas:**
- PostgreSQL: sobredimensionado para uso local personal.
- SQLAlchemy ORM: agrega complejidad de mapeo innecesaria para este alcance.
- TinyDB / JSON: no tiene FTS, índices ni transacciones.

---

## ADR-002 — Por qué Python

**Decisión:** Python 3.11+ como lenguaje único.

**Razones:**
- Ecosistema dominante en LegalTech y NLP.
- Compatibilidad natural con Anthropic SDK y MCP.
- Typer + Rich hacen CLIs excelentes con poco código.
- Pydantic v2 tiene validación robusta y serialización JSON trivial.
- El equipo ya trabaja en Python.

**Alternativas descartadas:**
- TypeScript/Node: menos maduro para NLP y procesamiento de documentos.
- Go: más performante pero sin ecosistema relevante para el dominio.

---

## ADR-003 — Por qué no scraping en v0.1

**Decisión:** No implementar scraping automático de BCN, CMF, Diario Oficial ni Poder Judicial.

**Razones:**
1. El HTML de estos sitios cambia frecuentemente → fragilidad alta.
2. No hay APIs públicas oficiales con contratos de estabilidad.
3. El scraping frágil generaría falsos positivos jurídicos (peor que no tener el dato).
4. El valor del v0.1 está en la infraestructura, no en el volumen de datos.
5. En v0.4+ se puede agregar ingestión BCN semi-automática controlada.

**Principio:** Preferir ingesta manual confiable a ingesta automática frágil. Las fuentes manuales saben su procedencia; las scrapeadas no siempre.

---

## ADR-004 — Por qué separar fuente original y texto normalizado

**Decisión:** Almacenar la ruta al archivo original (`original_path`) Y el texto normalizado (`normalized_text`) como campos separados.

**Razones:**
1. Trazabilidad: siempre se puede verificar que el texto normalizado corresponde al original.
2. Reproducibilidad: la normalización es determinista y puede rehacerse.
3. Independencia: si la normalización cambia en el futuro, se puede re-normalizar sin perder el original.
4. Seguridad: el texto normalizado en DB es el que se indexa y busca; el original en disco se preserva sin modificar.

---

## ADR-005 — Por qué no implementar RAG avanzado todavía

**Decisión:** No usar embeddings, vectores ni búsqueda semántica en v0.1.

**Razones:**
1. La búsqueda por LIKE es suficiente para el volumen de v0.1 (decenas, no miles de documentos).
2. Los embeddings agregan una dependencia pesada (sentence-transformers, numpy) sin que haya demanda validada.
3. El riesgo de falsos positivos semánticos en contexto jurídico es alto si no se calibra bien.
4. Es más fácil agregar semántica encima de LIKE que quitarla si genera problemas.

**Preparación:** La tabla `segments` tiene los campos necesarios (`text`, `source_id`, `order_index`) para agregar una tabla `embeddings` en v0.4+ sin cambiar el schema base.

---

## ADR-006 — Por qué tool_contracts.py como capa intermedia

**Decisión:** Toda la API pública pasa por `tool_contracts.py`, que actúa como fachada entre la CLI/MCP y los módulos internos.

**Razones:**
1. El MCP server del futuro sólo necesita importar `tool_contracts`.
2. Las firmas de las funciones son simples (primitivos Python, no objetos complejos).
3. Facilita tests de integración sin depender de CLI.
4. Mantiene la CLI delgada: sólo formatea output, no tiene lógica.
