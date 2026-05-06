-- ─────────────────────────────────────────────────────────────────────────────
-- Seed de desarrollo — NO contiene datos reales
-- Solo para pruebas locales
-- ─────────────────────────────────────────────────────────────────────────────

insert into cases (tracking_code, status, fraud_type, description, incident_date, amount_affected)
values (
    'AC-DEMO000001',
    'submitted',
    'smishing',
    'Recibí un mensaje de texto que parecía de mi banco. Hice clic en el link y perdí acceso a mi cuenta.',
    '2025-12-01',
    75000
);
