# Legal Source Kernel Chile — v0.1

**Fuente de verdad local, verificable y auditable para fuentes jurídicas chilenas.**

---

## ¿Qué es este proyecto?

Legal Source Kernel es una librería Python y herramienta de línea de comandos que permite a abogados y agentes de IA gestionar fuentes jurídicas chilenas de forma local, trazable y citable — sin depender de la memoria del modelo, sin inventar citas, y sin conexión a servicios externos en esta primera versión.

El objetivo no es construir un chatbot legal. Es construir la **infraestructura mínima** que hace posible que cualquier herramienta futura opere sobre fuentes jurídicas confiables.

---

## ¿Qué problema resuelve?

| Problema | Lo que hace este kernel |
|---|---|
| Los modelos de IA alucinan citas legales | Las citas salen de fuentes almacenadas localmente, no de la memoria del modelo |
| No hay forma de versionar normas | Cada fuente tiene versión, fecha y estado explícitos |
| Las citas no son verificables | Cada cita incluye título, locator, versión, fecha y URL de origen |
| No hay trazabilidad de uso | Toda acción queda registrada en AuditLog |
| Las fuentes se mezclan con el análisis | El kernel separa: texto original → normalizado → segmento → cita → análisis |

---

## ¿Qué NO resuelve todavía?

- Scraping automático de BCN, CMF, Diario Oficial o Poder Judicial
- Sincronización automática de textos vigentes
- RAG vectorial / embeddings semánticos
- Múltiples usuarios
- Interfaz web
- OCR de documentos escaneados complejos
- Garantía automática de vigencia normativa
- Generación de informes jurídicos
- Despliegue en la nube

---

## Instalación

Requiere Python 3.11+.

```bash
cd legal-source-kernel
pip install -e ".[dev]"
```

Para soporte PDF opcional:

```bash
pip install -e ".[pdf]"
```

---

## Uso rápido

### Inicializar la base de datos

```bash
legal-kernel init
```

### Ingestar una fuente

```bash
legal-kernel ingest examples/sources/ley_19799_sample.md \
  --metadata examples/manifests/ley_19799_sample.yaml

legal-kernel ingest examples/sources/contrato_sample.md \
  --metadata examples/manifests/contrato_sample.yaml
```

### Listar fuentes

```bash
legal-kernel list
legal-kernel list --type law
legal-kernel list --topic "firma electrónica"
```

### Buscar

```bash
legal-kernel search "firma electrónica avanzada"
legal-kernel search "prestación de servicios" --type contract
```

### Obtener un artículo o cláusula

```bash
legal-kernel get --source-id 1 --locator "artículo 3"
legal-kernel get --source-id 2 --locator "cláusula 12.3"
legal-kernel get --segment-id 4
```

### Generar una cita

```bash
legal-kernel cite --segment-id 3
```

Salida de ejemplo:
```
Ley de prueba, artículo 3, versión v0.1-test, consultado 2026-05-06.
Fuente: https://example.com/ley
```

### Comparar dos versiones

```bash
legal-kernel compare --source-a 1 --source-b 2
```

### Ver auditoría

```bash
legal-kernel audit
legal-kernel audit --type source --id 1
```

---

## Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `LEGAL_KERNEL_DB` | Ruta a la base de datos SQLite | `~/.legal_source_kernel/kernel.db` |

---

## Ejecutar tests

```bash
pytest
```

---

## Uso como librería Python

```python
from legal_source_kernel import tool_contracts as tc

# Ingestar
result = tc.ingest_source("ley.md", metadata_path="ley.yaml")

# Buscar
results = tc.search_sources("firma electrónica")

# Obtener segmento
seg = tc.get_segment(source_id=1, locator="artículo 3")

# Citar
cit = tc.cite_segment(segment_id=3)
print(cit["citation_text"])

# Comparar versiones
diff = tc.compare_sources(1, 2)

# Auditoría
trail = tc.audit_trail(entity_type="source", entity_id="1")
```

---

## Estructura del proyecto

```
legal-source-kernel/
  src/legal_source_kernel/   # Librería principal
  tests/                     # Tests automáticos (pytest)
  examples/                  # Fixtures de ejemplo
    sources/                 # Archivos .md de muestra
    manifests/               # Manifiestos YAML de muestra
  docs/                      # Documentación técnica
    ARCHITECTURE.md
    ROADMAP.md
    DECISIONS.md
    TOOL_MAP.md
```

---

## Roadmap

Ver [docs/ROADMAP.md](docs/ROADMAP.md).

---

## Precauciones jurídicas importantes

> **Este sistema no reemplaza la revisión de un abogado.**
>
> Las fuentes cargadas en esta versión son ingresadas manualmente y pueden estar desactualizadas. Las citas generadas deben verificarse antes de uso profesional. v0.1 no garantiza vigencia automática de ninguna norma. El texto almacenado puede diferir del texto oficial vigente. Siempre consulte la fuente oficial (BCN, CMF, Diario Oficial) antes de actuar jurídicamente.

---

## Licencia

MIT
