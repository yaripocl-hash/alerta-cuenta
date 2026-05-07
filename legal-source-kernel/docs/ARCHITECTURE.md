# Architecture — Legal Source Kernel v0.1

## Capas del sistema

```
┌─────────────────────────────────────────────────────────────┐
│  CLI (typer)          │  Future: MCP Server / FastAPI        │
├─────────────────────────────────────────────────────────────┤
│  tool_contracts.py    ← API pública unificada               │
├─────────────────────────────────────────────────────────────┤
│  ingest  │  search  │  cite  │  versioning  │  audit        │
├─────────────────────────────────────────────────────────────┤
│  normalize.py         │  segment.py                         │
├─────────────────────────────────────────────────────────────┤
│  db.py  (SQLite)      │  models.py  (Pydantic)              │
├─────────────────────────────────────────────────────────────┤
│  config.py  (paths, env vars)                               │
└─────────────────────────────────────────────────────────────┘
```

Cada capa tiene responsabilidad única. Las capas superiores llaman a las inferiores; nunca al revés.

---

## Flujo de ingesta

```
Archivo (.md / .txt / .pdf)
    │
    ▼
normalize.read_file()          ← lee bytes, extrae frontmatter YAML
    │
    ├── YAML manifest externo  ← si se provee --metadata
    │
    ▼
normalize.normalize_text()     ← limpia whitespace, normaliza LF
    │
    ▼
segment.segment_text()         ← detecta artículos / cláusulas / secciones
    │
    ▼
db.insert_source()             ← guarda texto original + normalizado
    │
    ▼
db.insert_segment() ×N        ← un registro por segmento citable
    │
    ▼
audit.log()                    ← registra la acción en audit_log
```

---

## Modelo de datos

### `sources`

| Campo | Descripción |
|---|---|
| `id` | PK autoincremental |
| `title` | Título de la fuente |
| `source_type` | `law`, `regulation`, `contract`, etc. |
| `jurisdiction` | `Chile` por defecto |
| `authority` | Organismo emisor (BCN, CMF, etc.) |
| `source_url` | URL de la fuente original |
| `original_path` | Ruta al archivo original en disco |
| `normalized_text` | Texto limpio en Markdown |
| `date_published` | Fecha de publicación |
| `date_effective_from` | Inicio de vigencia |
| `date_effective_to` | Fin de vigencia (null = vigente) |
| `version_label` | Etiqueta de versión libre |
| `status` | `active`, `sample`, `test`, etc. |
| `trust_level` | `high`, `medium`, `low` |
| `topics_json` | Lista JSON de temas |
| `created_at` | Timestamp de ingesta |
| `updated_at` | Timestamp de última modificación |

### `segments`

| Campo | Descripción |
|---|---|
| `id` | PK autoincremental |
| `source_id` | FK a `sources.id` |
| `segment_type` | `article`, `clause`, `section`, `unknown` |
| `locator` | Texto normalizado del encabezado (ej: `artículo 3`) |
| `title` | Encabezado original completo |
| `text` | Contenido del segmento |
| `start_char` / `end_char` | Posición en el texto normalizado |
| `page` | Número de página (para PDF) |
| `order_index` | Orden de aparición en la fuente |

### `audit_log`

| Campo | Descripción |
|---|---|
| `id` | PK autoincremental |
| `action` | Nombre de la acción (ej: `ingest_source`) |
| `entity_type` | `source`, `segment`, etc. |
| `entity_id` | ID de la entidad afectada |
| `details_json` | Detalles adicionales en JSON |
| `created_at` | Timestamp |

---

## Separación de tipos de información

El kernel distingue explícitamente:

| Tipo | Dónde vive |
|---|---|
| Fuente original | `sources.original_path` (disco) |
| Texto normalizado | `sources.normalized_text` (DB) |
| Metadata | `sources.*` (DB) |
| Segmento citable | `segments.*` (DB) |
| Cita generada | Generada en tiempo real por `cite.py` |
| Resultado analítico | Fuera del kernel (responsabilidad del agente) |
| Output generado | Fuera del kernel (responsabilidad del agente o usuario) |

Esta separación es deliberada: el kernel sólo gestiona fuentes y segmentos. Los análisis y outputs son responsabilidad de la capa de agentes.

---

## Diseño preparado para MCP

`tool_contracts.py` define 7 funciones que mapean directamente a tools MCP:

| Tool | Función |
|---|---|
| `ingest_source` | `tc.ingest_source(file_path, metadata_path)` |
| `list_sources` | `tc.list_sources(source_type, topic)` |
| `search_sources` | `tc.search_sources(query, source_type, limit)` |
| `get_segment` | `tc.get_segment(source_id, locator, segment_id)` |
| `cite_segment` | `tc.cite_segment(segment_id)` |
| `compare_sources` | `tc.compare_sources(source_id_a, source_id_b)` |
| `audit_trail` | `tc.audit_trail(entity_type, entity_id)` |

Para exponer estas funciones como un servidor MCP (v0.3), bastará con:
1. Instalar `mcp` SDK de Anthropic.
2. Crear `src/legal_source_kernel/mcp_server.py`.
3. Registrar cada función de `tool_contracts.py` como un tool MCP.
4. Arrancar el servidor con `legal-kernel serve`.

Las firmas de `tool_contracts.py` son intencionalmente simples (solo tipos primitivos y listas/dicts), lo que hace la serialización JSON trivial.

---

## Extensión futura

Para agregar un nuevo tipo de segmentación (ej: decretos con numeración especial):
1. Agregar un nuevo regex en `segment.py`.
2. Agregar el `source_type` al dispatcher en `segment_text()`.
3. Agregar un test en `tests/test_segment.py`.

Para agregar búsqueda semántica (v0.4+):
1. Agregar una tabla `embeddings` con vector BLOB.
2. Usar `sentence-transformers` para generar embeddings al ingestar.
3. Implementar `search.semantic_search()` con similitud coseno.
4. El resto del sistema no cambia.
