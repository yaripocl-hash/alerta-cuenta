# Roadmap — Legal Source Kernel

## v0.1 — Local Kernel (actual)

**Estado:** En desarrollo.

- CLI local con Typer
- SQLite local
- Ingesta manual (.md, .txt, .pdf opcional)
- Metadata YAML / frontmatter
- Segmentación por patrones (artículos, cláusulas, secciones)
- Búsqueda por LIKE
- Cita verificable simple
- Comparación de versiones (unified diff)
- Auditoría básica
- Tests automáticos (pytest)
- Documentación técnica

---

## v0.2 — Segmentación mejorada

- Mejores patrones para leyes con estructura compleja (títulos, párrafos, incisos)
- Soporte para decretos y reglamentos
- Segmentación de Historia de la Ley
- Mejora de locators normativos (artículo 3°, inciso 2°, letra b))
- Confianza de segmentación (`confidence` field)
- Tests de regresión para edge cases reales

---

## v0.3 — MCP Server

- Servidor MCP basado en `mcp` SDK de Anthropic
- Las 7 tool_contracts expuestas como tools MCP
- Documentación de tools para uso con Claude
- `legal-kernel serve` como comando CLI
- Tests del servidor MCP

---

## v0.4 — Fuentes BCN semi-automáticas

- Descarga manual guiada desde BCN (no scraping frágil)
- Parser de formatos HTML/XML de BCN
- Validación automática de integridad del texto
- Comando `legal-kernel import-bcn` para flujo asistido
- Primera cobertura real: leyes y decretos principales

---

## v0.5 — Monitor Diario Oficial

- Suscripción al feed RSS del Diario Oficial
- Detección de nuevas publicaciones relevantes por materia
- Notificaciones (CLI primero, email en v2)
- Comando `legal-kernel watch`
- No ingesta automática sin validación humana

---

## v0.6 — Contratos y NoClaims

- Soporte para ingestión de contratos propios
- Extracción de cláusulas con roles (obligación, derecho, prohibición)
- Matriz de obligaciones por parte
- Matriz de evidencia esperada
- Base para detección de incumplimiento

---

## v0.7 — Reguladores

- Ingestión de circulares CMF
- Ingestión de normativa Banco Central
- Ingestión de normativa UAF (lavado de activos)
- Monitor de cambios regulatorios

---

## v1.0 — Producto profesional

- API FastAPI con autenticación
- Dashboard web mínimo
- Multiusuario (equipos pequeños)
- Exportación a PDF / Word
- Auditoría profesional de outputs
- Documentación de usuario no técnico
- Integración con herramientas de abogados (DMS, gestores de casos)
