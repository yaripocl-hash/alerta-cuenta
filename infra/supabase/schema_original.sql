-- =============================================================================
-- Alerta Cuenta — Schema Supabase (PostgreSQL)
-- Ejecutar en: Supabase Dashboard > SQL Editor
--
-- MODELO DE SEGURIDAD:
--   - El frontend NO accede a estas tablas directamente.
--   - El backend usa SUPABASE_SERVICE_ROLE_KEY (bypass de RLS).
--   - RLS habilitado en todas las tablas como defensa en profundidad.
--   - Sin policies para anon ni authenticated. Toda lectura/escritura pasa por backend.
--   - El bucket de Storage 'evidence' es privado; acceso solo mediante signed URLs.
--
-- RE-EJECUTABLE: puede correrse como primera instalación sin errores.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- EXTENSIONES
-- ---------------------------------------------------------------------------
create extension if not exists "pgcrypto";


-- ---------------------------------------------------------------------------
-- FUNCIÓN: actualiza updated_at automáticamente
-- ---------------------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;


-- ---------------------------------------------------------------------------
-- FUNCIÓN: bloquea UPDATE y DELETE en audit_log (append-only)
-- ---------------------------------------------------------------------------
create or replace function public.deny_audit_log_mutation()
returns trigger
language plpgsql
as $$
begin
    raise exception 'audit_log es append-only: operación % no permitida', tg_op;
end;
$$;


-- ---------------------------------------------------------------------------
-- FUNCIÓN: bloquea UPDATE y DELETE en case_ai_outputs (append-only)
-- Los outputs de IA son inmutables una vez creados.
-- ---------------------------------------------------------------------------
create or replace function public.deny_case_ai_outputs_mutation()
returns trigger
language plpgsql
as $$
begin
    raise exception 'case_ai_outputs es append-only: operación % no permitida', tg_op;
end;
$$;


-- =============================================================================
-- TABLA: cases
-- Caso de fraude central. Un usuario crea un caso y recibe un tracking_code.
-- SENSIBLE: description contiene el relato libre del usuario. No loguear.
-- =============================================================================
create table if not exists public.cases (
    id                      uuid            primary key default gen_random_uuid(),

    -- Código de seguimiento legible (AC-XXXXXXXX). Único. Generado en backend.
    tracking_code           text            unique not null,

    status                  text            not null default 'draft'
                                            check (status in (
                                                'draft',        -- En edición
                                                'submitted',    -- Enviado por usuario
                                                'in_review',    -- En revisión interna
                                                'closed'        -- Cerrado (resuelto o descartado)
                                            )),

    -- Clasificado por Claude. Null hasta que el agente corra.
    fraud_type              text            check (fraud_type in (
                                                'phishing',
                                                'vishing',
                                                'smishing',
                                                'whatsapp_impersonation',
                                                'deceptive_transfer',
                                                'fake_online_purchase',
                                                'unauthorized_account_access',
                                                'other'
                                            )),

    -- Relato libre del usuario. Campo sensible — no loguear nunca.
    description             text            not null,

    -- Canal por el que ocurrió el fraude.
    channel                 text            check (channel in (
                                                'email',
                                                'sms',
                                                'phone_call',
                                                'whatsapp',
                                                'web',
                                                'social_media',
                                                'bank_app',
                                                'marketplace',
                                                'other',
                                                'unknown'
                                            )),

    -- Fecha de referencia del incidente (cuando no se conoce la hora exacta).
    incident_date           date,

    -- Timestamp completo si se conoce la hora aproximada.
    incident_occurred_at    timestamptz,

    -- Precisión de la fecha/hora reportada por el usuario.
    incident_time_precision text            check (incident_time_precision in (
                                                'exact',        -- Fecha y hora exactas
                                                'approximate',  -- Aproximadas (±1-2 horas)
                                                'date_only',    -- Solo se sabe el día
                                                'week_only',    -- Solo se sabe la semana
                                                'unknown'       -- No recuerda
                                            )),

    -- Monto afectado. Debe ser positivo si se ingresa.
    amount_affected         numeric(14,2)   check (amount_affected is null or amount_affected >= 0),

    -- Código ISO 4217 de 3 letras mayúsculas (ej: CLP, USD, EUR).
    currency                text            not null default 'CLP'
                                            check (currency ~ '^[A-Z]{3}$'),

    -- Banco o fintech involucrada (slug libre, ej: 'banco_estado', 'mercadopago').
    target_institution      text,

    -- Soft delete: no eliminar filas, marcar como eliminado.
    deleted_at              timestamptz,

    -- Hasta cuándo conservar este caso para cumplimiento de retención de datos.
    retention_until         timestamptz,

    created_at              timestamptz     not null default now(),
    updated_at              timestamptz     not null default now()
);

-- RLS: habilitado. El backend usa service_role_key (bypass de RLS).
-- No se crean policies aquí. El acceso es exclusivo al backend.
-- Para policies futuras (autenticación real), usar infra/supabase/policies.sql.
alter table public.cases enable row level security;

drop trigger if exists trg_cases_updated_at on public.cases;
create trigger trg_cases_updated_at
    before update on public.cases
    for each row execute function public.set_updated_at();


-- =============================================================================
-- TABLA: case_people
-- Personas vinculadas al caso: víctima, denunciante, familiar, tercero.
-- SENSIBLE: todos los campos son PII. Ver docs/privacy-and-pii.md.
-- NO guardar: RUT completo, PIN, contraseñas, credenciales, fotos de cédula.
-- =============================================================================
create table if not exists public.case_people (
    id                  uuid        primary key default gen_random_uuid(),
    case_id             uuid        not null references public.cases(id) on delete cascade,

    -- Rol de esta persona en el caso.
    person_role         text        not null default 'victim'
                                    check (person_role in (
                                        'victim',           -- La persona afectada directamente
                                        'reporter',         -- Quien reporta (puede no ser la víctima)
                                        'family_member',    -- Familiar de la víctima
                                        'third_party',      -- Tercero que asiste
                                        'suspect',          -- Sospechoso (registrar solo metadata mínima)
                                        'other'
                                    )),

    -- ── Edad / Rango etario ─────────────────────────────────────────────────
    -- Preferir victim_age_range sobre victim_age exacta para minimizar PII.
    victim_age          smallint    check (victim_age is null or (victim_age >= 0 and victim_age <= 130)),
    victim_age_range    text        check (victim_age_range in (
                                        'under_18',
                                        '18_30',
                                        '31_50',
                                        '51_65',
                                        'over_65',
                                        'unknown'
                                    )),

    -- ── Identidad ───────────────────────────────────────────────────────────
    -- No guardar documento completo. Solo tipo, últimos 4 caracteres y hash.
    is_foreign_person   boolean     not null default false,

    -- Tipo de documento de identidad.
    identity_type       text        check (identity_type in (
                                        'rut',              -- RUT chileno
                                        'passport',         -- Pasaporte
                                        'foreign_id',       -- Cédula extranjera / RUT provisorio
                                        'none',             -- Sin documento formal
                                        'other'
                                    )),

    -- Últimos 4 caracteres del documento. Nunca el número completo.
    identity_last4      text        check (identity_last4 is null or length(identity_last4) <= 6),

    -- HMAC-SHA256 del documento completo (salt = APP_SECRET, calculado en backend).
    -- Permite deduplicación sin almacenar el valor real. Nunca calcular en frontend.
    identity_hash       text        check (identity_hash is null or identity_hash ~ '^[a-f0-9]{64}$'),

    -- ── Contacto ────────────────────────────────────────────────────────────
    -- Email y teléfono completos: guardar solo si es estrictamente necesario.
    -- Preferir los hashes para lookup de casos.
    contact_email       text,       -- PII directa — evaluar cifrado en producción
    contact_phone       text,       -- PII directa — opcional

    -- HMAC-SHA256 de email y teléfono para lookup sin exponer el valor real.
    contact_email_hash  text        check (contact_email_hash is null or contact_email_hash ~ '^[a-f0-9]{64}$'),
    contact_phone_hash  text        check (contact_phone_hash is null or contact_phone_hash ~ '^[a-f0-9]{64}$'),

    created_at          timestamptz not null default now()
);

-- Sin policies para anon ni authenticated. Acceso exclusivo via service_role en backend.
alter table public.case_people enable row level security;


-- =============================================================================
-- TABLA: case_events
-- Historial de eventos del ciclo de vida del caso.
-- NO debe contener PII ni datos sensibles del relato.
-- =============================================================================
create table if not exists public.case_events (
    id          uuid        primary key default gen_random_uuid(),
    case_id     uuid        not null references public.cases(id) on delete cascade,

    event_type  text        not null
                            check (event_type in (
                                'case_created',
                                'case_submitted',
                                'status_changed',
                                'evidence_uploaded',
                                'evidence_deleted',
                                'ai_output_generated',
                                'tracking_lookup',
                                'note_added',
                                'case_closed',
                                'other'
                            )),

    -- Descripción libre del evento. NO incluir PII.
    description text,

    -- Quién generó el evento: 'system', 'backend', o identificador anónimo de sesión.
    actor       text        not null default 'system',

    created_at  timestamptz not null default now()
);

alter table public.case_events enable row level security;


-- =============================================================================
-- TABLA: case_evidence
-- Metadatos de archivos de evidencia. El archivo real está en Supabase Storage.
-- SENSIBLE: puede referenciar imágenes, PDFs, audios de la víctima.
-- ACCESO: bucket 'evidence' privado. URLs de lectura son signed (TTL ≤ 1h).
-- UPLOAD: solo desde backend usando service_role_key. Nunca desde frontend.
-- =============================================================================
create table if not exists public.case_evidence (
    id              uuid        primary key default gen_random_uuid(),
    case_id         uuid        not null references public.cases(id) on delete cascade,

    -- Nombre original del archivo, sanitizado en backend antes de guardar.
    filename        text        not null,

    -- MIME type validado en backend contra magic bytes. No confiar en el cliente.
    content_type    text        not null,

    -- Tamaño del archivo en bytes. Validar en backend (máx 10 MB en MVP).
    size_bytes      integer     check (size_bytes is null or size_bytes >= 0),

    -- Path en Supabase Storage: '{case_id}/{uuid}-{sanitized_filename}'.
    -- Único para evitar colisiones y sobreescritura accidental.
    storage_path    text        not null unique,

    -- Bucket de Supabase Storage donde se almacena el archivo.
    bucket_id       text        not null default 'evidence',

    -- SHA-256 del contenido del archivo, calculado en backend antes del upload.
    -- Útil para verificación de integridad y deduplicación.
    sha256          text        check (sha256 is null or sha256 ~ '^[a-f0-9]{64}$'),

    -- Estado del escaneo de contenido / antivirus.
    -- Implementar validación mínima en backend (magic bytes + MIME).
    scan_status     text        not null default 'pending'
                                check (scan_status in (
                                    'pending',      -- Sin escanear aún
                                    'clean',        -- Sin amenazas detectadas
                                    'flagged',      -- Sospechoso — requiere revisión manual
                                    'quarantined',  -- En cuarentena, no servir
                                    'skipped'       -- Escaneo no disponible en este entorno
                                )),

    -- Quién realizó el upload. 'backend' en todos los flujos normales.
    uploaded_by     text        not null default 'backend',

    -- Descripción opcional aportada por el usuario sobre este archivo.
    description     text,

    -- Soft delete: marcar como eliminado sin borrar el registro ni el archivo inmediatamente.
    deleted_at      timestamptz,

    created_at      timestamptz not null default now()
);

alter table public.case_evidence enable row level security;


-- =============================================================================
-- TABLA: case_ai_outputs
-- Outputs de los agentes Claude. Inmutables una vez creados.
-- SENSIBLE: output_json puede contener resumen del relato del usuario.
-- =============================================================================
create table if not exists public.case_ai_outputs (
    id              uuid        primary key default gen_random_uuid(),
    case_id         uuid        not null references public.cases(id) on delete cascade,

    -- Nombre del agente: 'fraud_classifier', 'case_summary', etc.
    agent_name      text        not null,

    -- Versión del prompt (corresponde a prompts/<agent_name>/<version>.md).
    prompt_version  text        not null,

    -- Proveedor de IA. 'anthropic' por defecto; campo para extensibilidad futura.
    provider        text        not null default 'anthropic',

    -- Modelo utilizado (ej: 'claude-sonnet-4-6').
    model           text        not null,

    -- HMAC-SHA256 del input enviado al modelo. Auditoría sin guardar el input completo.
    input_hash      text        check (input_hash is null or input_hash ~ '^[a-f0-9]{64}$'),

    -- Respuesta estructurada del agente (JSON parseado y validado en backend).
    output_json     jsonb       not null,

    -- Métricas de la llamada. Todas opcionales, >= 0 si se proveen.
    latency_ms      integer     check (latency_ms is null or latency_ms >= 0),
    tokens_input    integer     check (tokens_input is null or tokens_input >= 0),
    tokens_output   integer     check (tokens_output is null or tokens_output >= 0),

    created_at      timestamptz not null default now()
);

alter table public.case_ai_outputs enable row level security;

-- Trigger append-only: bloquea UPDATE y DELETE. Los outputs de IA no se modifican.
drop trigger if exists trg_case_ai_outputs_deny_mutation on public.case_ai_outputs;
create trigger trg_case_ai_outputs_deny_mutation
    before update or delete on public.case_ai_outputs
    for each row execute function public.deny_case_ai_outputs_mutation();


-- =============================================================================
-- TABLA: audit_log
-- Registro append-only de acciones críticas del sistema.
-- REGLA DE PRIVACIDAD: metadata NO debe contener PII.
--   Solo incluir: IDs de caso, nombres de acciones, conteos, duraciones, códigos
--   de error. NUNCA: emails, teléfonos, nombres, RUTs, IPs completas, tokens.
-- INTEGRIDAD: UPDATE y DELETE están bloqueados por trigger.
-- =============================================================================
create table if not exists public.audit_log (
    id          uuid        primary key default gen_random_uuid(),

    -- Null si la acción no está asociada a un caso específico.
    case_id     uuid        references public.cases(id) on delete set null,

    -- Tipo de acción registrada.
    action      text        not null
                            check (action in (
                                'case_created',
                                'case_submitted',
                                'case_status_changed',
                                'evidence_uploaded',
                                'evidence_deleted',
                                'ai_agent_called',
                                'tracking_lookup',
                                'tracking_lookup_failed',
                                'email_sent',
                                'rate_limit_exceeded',
                                'system_error',
                                'other'
                            )),

    -- Quién realizó la acción: 'system', 'backend', 'scheduled_job', etc.
    actor       text        not null default 'system',

    -- Metadata NO-PII: conteos, duraciones, tipos, códigos de error.
    -- NUNCA incluir emails, teléfonos, nombres, RUTs ni IPs completas.
    metadata    jsonb       not null default '{}',

    created_at  timestamptz not null default now()
);

alter table public.audit_log enable row level security;

-- Trigger append-only: cualquier intento de UPDATE o DELETE lanza excepción.
drop trigger if exists trg_audit_log_deny_mutation on public.audit_log;
create trigger trg_audit_log_deny_mutation
    before update or delete on public.audit_log
    for each row execute function public.deny_audit_log_mutation();


-- =============================================================================
-- ÍNDICES
-- tracking_code y storage_path ya tienen índice único implícito por su
-- constraint UNIQUE en la definición de la tabla. No se duplican aquí.
-- =============================================================================

-- cases
create index if not exists idx_cases_status
    on public.cases(status)
    where deleted_at is null;

create index if not exists idx_cases_created_at
    on public.cases(created_at desc);

create index if not exists idx_cases_incident_occurred_at
    on public.cases(incident_occurred_at)
    where incident_occurred_at is not null;

-- case_people
create index if not exists idx_case_people_case_id
    on public.case_people(case_id);

create index if not exists idx_case_people_email_hash
    on public.case_people(contact_email_hash)
    where contact_email_hash is not null;

create index if not exists idx_case_people_phone_hash
    on public.case_people(contact_phone_hash)
    where contact_phone_hash is not null;

create index if not exists idx_case_people_identity_hash
    on public.case_people(identity_hash)
    where identity_hash is not null;

-- case_events
create index if not exists idx_case_events_case_id
    on public.case_events(case_id);

create index if not exists idx_case_events_event_type
    on public.case_events(event_type);

-- case_evidence
create index if not exists idx_case_evidence_case_id
    on public.case_evidence(case_id);

create index if not exists idx_case_evidence_scan_status
    on public.case_evidence(scan_status)
    where scan_status in ('pending', 'flagged');

-- case_ai_outputs
create index if not exists idx_case_ai_outputs_case_id
    on public.case_ai_outputs(case_id);

create index if not exists idx_case_ai_outputs_agent_name
    on public.case_ai_outputs(agent_name);

-- audit_log
create index if not exists idx_audit_log_case_id
    on public.audit_log(case_id);

create index if not exists idx_audit_log_action
    on public.audit_log(action);

create index if not exists idx_audit_log_created_at
    on public.audit_log(created_at desc);


-- =============================================================================
-- PENDIENTES FUERA DE ESTE SCRIPT
-- =============================================================================
--
-- BUCKET STORAGE:
--   Crear manualmente en Supabase Dashboard > Storage.
--   Nombre: 'evidence'. Tipo: PRIVADO (no marcar como public).
--   Ver instrucciones detalladas en infra/supabase/storage.md.
--   Las URLs de lectura deben ser signed URLs con TTL máximo de 1 hora.
--   El upload lo realiza exclusivamente el backend con service_role_key.
--
-- POLÍTICAS RLS:
--   No se crean policies en este archivo intencionalmente.
--   El backend bypasea RLS con service_role_key.
--   Si en el futuro se implementa Supabase Auth para usuarios,
--   crear un archivo separado: infra/supabase/policies.sql
--
-- HASHES DE PII:
--   identity_hash, contact_email_hash, contact_phone_hash e input_hash
--   deben calcularse en el backend usando HMAC-SHA256 con APP_SECRET como salt.
--   Nunca calcular ni transmitir hashes desde el frontend.
--   Cambiar APP_SECRET invalida los hashes existentes — planificar la rotación.
--
-- CIFRADO DE COLUMNAS PII:
--   En producción, evaluar cifrado a nivel de aplicación antes de persistir para:
--   contact_email, contact_phone, description, identity_last4.
--   La extensión pgcrypto está habilitada si se opta por cifrado en base de datos.
--
-- RETENCIÓN DE DATOS:
--   retention_until en cases permite borrado automático programado.
--   Implementar job que marque deleted_at y elimine archivos del bucket
--   cuando retention_until < now().
--
-- RATE LIMITING:
--   Implementar como middleware en FastAPI antes de los endpoints de creación.
--   El audit_log puede usarse para detección de abuso por acción/actor.
--
-- ESCANEO DE EVIDENCIA:
--   scan_status = 'pending' por defecto. El backend debe validar al menos:
--   magic bytes, tamaño máximo (10 MB en MVP), MIME type contra lista permitida.
--   Un servicio de antivirus dedicado es opcional en MVP.
--
-- ROTACIÓN DE SECRETOS:
--   APP_SECRET, ANTHROPIC_API_KEY y SUPABASE_SERVICE_ROLE_KEY deben rotarse
--   periódicamente. Coordinar la rotación de APP_SECRET con re-hash de PII existente.
--
-- MONITOREO:
--   Configurar alertas en Supabase o plataforma de deploy para:
--   errores 5xx sostenidos, crecimiento anormal de audit_log,
--   archivos con scan_status = 'flagged', y expiración próxima de secretos.
