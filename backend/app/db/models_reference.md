# Referencia de Modelos — Base de Datos

Este archivo documenta la correspondencia entre las tablas de Supabase y los schemas Pydantic del backend.

Ver schema completo en `infra/supabase/schema.sql`.

| Tabla Supabase | Schema Pydantic | Service |
|---|---|---|
| `cases` | `schemas/case.py` | `services/case_service.py` |
| `case_people` | (incluido en CaseCreate) | `services/case_service.py` |
| `case_events` | (interno) | `services/audit_service.py` |
| `case_evidence` | `schemas/evidence.py` | `services/evidence_service.py` |
| `case_ai_outputs` | `schemas/ai.py` | `services/ai_service.py` |
| `audit_log` | (interno) | `services/audit_service.py` |
