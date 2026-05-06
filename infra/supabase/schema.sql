-- ─────────────────────────────────────────────────────────────────────────────
-- Alerta Cuenta — Schema Supabase (PostgreSQL)
-- Ejecutar en: Supabase Dashboard > SQL Editor
-- ─────────────────────────────────────────────────────────────────────────────

-- Extensión para UUIDs
create extension if not exists "pgcrypto";

-- ─── Tabla: cases ─────────────────────────────────────────────────────────────
create table if not exists cases (
    id              uuid primary key default gen_random_uuid(),
    tracking_code   text unique not null,        -- Código para consulta pública (AC-XXXX)
    status          text not null default 'draft' check (status in ('draft','submitted','in_review','closed')),
    fraud_type      text,                         -- Clasificado por Claude
    description     text not null,               -- Relato del usuario (campo sensible)
    incident_date   date,
    amount_affected numeric(12,2),
    currency        text default 'CLP',
    target_institution text,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);

-- ─── Tabla: case_people ───────────────────────────────────────────────────────
-- Datos personales de la víctima. Todos los campos son PII sensible.
create table if not exists case_people (
    id              uuid primary key default gen_random_uuid(),
    case_id         uuid not null references cases(id) on delete cascade,
    role            text not null default 'victim' check (role in ('victim','support_contact')),
    -- CAMPOS PII — ver docs/privacy-and-pii.md antes de agregar campos
    contact_email   text,                        -- PII: encriptar en producción
    contact_phone   text,                        -- PII: opcional
    created_at      timestamptz not null default now()
);

-- ─── Tabla: case_events ───────────────────────────────────────────────────────
create table if not exists case_events (
    id              uuid primary key default gen_random_uuid(),
    case_id         uuid not null references cases(id) on delete cascade,
    event_type      text not null,               -- 'status_change','evidence_uploaded','ai_output_generated', etc.
    description     text,
    actor           text default 'system',
    created_at      timestamptz not null default now()
);

-- ─── Tabla: case_evidence ─────────────────────────────────────────────────────
create table if not exists case_evidence (
    id              uuid primary key default gen_random_uuid(),
    case_id         uuid not null references cases(id) on delete cascade,
    filename        text not null,
    content_type    text not null,
    size_bytes      integer,
    storage_path    text not null,               -- Path en Supabase Storage bucket 'evidence'
    description     text,
    created_at      timestamptz not null default now()
);

-- ─── Tabla: case_ai_outputs ───────────────────────────────────────────────────
create table if not exists case_ai_outputs (
    id              uuid primary key default gen_random_uuid(),
    case_id         uuid not null references cases(id) on delete cascade,
    agent_name      text not null,               -- 'fraud_classifier','case_summary', etc.
    prompt_version  text not null,               -- 'v1', 'v2', etc.
    output_json     jsonb not null,              -- Respuesta estructurada de Claude
    model_used      text not null,
    created_at      timestamptz not null default now()
);

-- ─── Tabla: audit_log ─────────────────────────────────────────────────────────
-- Registro de acciones críticas. NO registrar PII en metadata.
create table if not exists audit_log (
    id              uuid primary key default gen_random_uuid(),
    case_id         uuid references cases(id) on delete set null,
    action          text not null,               -- 'case_created','evidence_uploaded','ai_called', etc.
    actor           text default 'system',
    metadata        jsonb default '{}',          -- Solo datos no-PII
    created_at      timestamptz not null default now()
);

-- ─── Índices ──────────────────────────────────────────────────────────────────
create index if not exists idx_cases_tracking_code on cases(tracking_code);
create index if not exists idx_cases_status on cases(status);
create index if not exists idx_case_people_case_id on case_people(case_id);
create index if not exists idx_case_evidence_case_id on case_evidence(case_id);
create index if not exists idx_case_ai_outputs_case_id on case_ai_outputs(case_id);
create index if not exists idx_audit_log_case_id on audit_log(case_id);

-- ─── Trigger: updated_at ──────────────────────────────────────────────────────
create or replace function update_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger cases_updated_at
    before update on cases
    for each row execute function update_updated_at();
