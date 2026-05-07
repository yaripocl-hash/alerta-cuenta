# Tool Map — Legal Source Kernel v0.1

Mapa de las funciones que serán expuestas como MCP tools en v0.3.

| Verbo | Tool | Input principal | Output | Riesgo | Validación futura |
|---|---|---|---|---|---|
| Ingestar | `ingest_source` | `file_path`, `metadata_path` | `{source_id, title, segments}` | Bajo (solo lectura/escritura local) | Validar hash del archivo para detectar re-ingesta |
| Listar | `list_sources` | `source_type?`, `topic?` | Lista de fuentes con metadata | Ninguno | Paginación para volúmenes grandes |
| Buscar | `search_sources` | `query`, `source_type?`, `limit` | Lista de resultados con snippet | Bajo | Scoring BM25, filtro por fecha de vigencia |
| Obtener segmento | `get_segment` | `source_id`, `locator?`, `segment_id?` | Segmento con cita sugerida | Bajo | Validar que locator sea exacto, no parcial |
| Citar | `cite_segment` | `segment_id` | Texto de cita verificable | Bajo | Advertir si `trust_level = low` o fuente no vigente |
| Comparar | `compare_sources` | `source_id_a`, `source_id_b` | `{diff, identical}` | Bajo | Detectar si son la misma fuente en distintas versiones |
| Auditar | `audit_trail` | `entity_type?`, `entity_id?` | Lista de entradas de auditoría | Ninguno | Exportar a CSV para reportes |

---

## Notas de diseño para MCP

1. **Todas las funciones retornan dicts o listas de dicts.** No hay objetos Pydantic en el boundary — la serialización JSON es trivial.

2. **Ninguna función tiene efectos secundarios implícitos.** `search_sources` no modifica el estado. `ingest_source` sí crea registros, pero lo documenta en el AuditLog.

3. **Los IDs son enteros.** No UUIDs, para que las citas sean legibles para humanos.

4. **Las funciones de solo lectura son seguras de llamar múltiples veces.** Idempotencia garantizada en `list`, `search`, `get`, `cite`, `compare`, `audit`.

5. **`ingest_source` NO es idempotente.** Llamarla dos veces con el mismo archivo crea dos fuentes distintas. En v0.2 se agregará un hash de archivo para detección de duplicados.

---

## Mapping futuro a MCP tools

```python
# v0.3: mcp_server.py (ejemplo de estructura)
from mcp import tool
from legal_source_kernel import tool_contracts as tc

@tool
def ingest_source(file_path: str, metadata_path: str | None = None) -> dict:
    """Ingesta un archivo jurídico en el kernel local."""
    return tc.ingest_source(file_path, metadata_path)

@tool
def search_sources(query: str, source_type: str | None = None, limit: int = 10) -> list[dict]:
    """Busca fuentes jurídicas por texto."""
    return tc.search_sources(query, source_type, limit)

# ... etc.
```
