# Modelo de Datos — Alerta Cuenta

Ver el schema completo en `infra/supabase/schema.sql`.

## Tablas Principales

### `cases`
El caso de fraude central. Un usuario crea un caso y recibe un `tracking_code`.

Campos clave:
- `id` (uuid)
- `tracking_code` (texto único, generado en backend)
- `status` (enum: draft, submitted, in_review, closed)
- `fraud_type` (clasificado por Claude)
- `description` (relato del usuario)
- `incident_date`
- `amount_affected` (decimal, opcional)
- `currency` (CLP por defecto)
- `created_at`, `updated_at`

### `case_people`
Personas involucradas en el caso (víctima, contacto de apoyo).

**Nota de privacidad:** Datos de identidad son sensibles. Ver `docs/privacy-and-pii.md`.

### `case_events`
Historial de eventos del caso (cambios de estado, acciones del usuario).

### `case_evidence`
Metadatos de archivos subidos (la evidencia real está en Supabase Storage).

- `storage_path` apunta al bucket en Supabase Storage
- Tipos permitidos: imagen (jpg, png, webp), PDF, texto

### `case_ai_outputs`
Outputs generados por los agentes Claude.

- `agent_name`: qué agente generó el output
- `prompt_version`: versión del prompt usada
- `output_json`: respuesta estructurada de Claude
- `model_used`: modelo Claude utilizado

### `audit_log`
Registro de acciones críticas. No registra PII en texto plano.

## Relaciones

```
cases (1) ──── (N) case_people
cases (1) ──── (N) case_events
cases (1) ──── (N) case_evidence
cases (1) ──── (N) case_ai_outputs
cases (1) ──── (N) audit_log
```

## Consideraciones de Diseño

- No se requiere autenticación de usuario en MVP (acceso por `tracking_code` + email).
- El `tracking_code` debe ser suficientemente impredecible (no secuencial).
- Todos los campos sensibles deben documentarse en `docs/privacy-and-pii.md`.
- Ningún campo de PII debe aparecer en logs.
