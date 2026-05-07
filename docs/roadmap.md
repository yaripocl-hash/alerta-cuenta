# Roadmap — Alerta Cuenta

## MVP (Demo Claude Impact Lab Chile 2026 )

### Fase 1 — Scaffold (actual)
- [x] Estructura de proyecto
- [x] Backend FastAPI base
- [x] Frontend HTML/CSS/JS base
- [x] Schema Supabase
- [x] Prompts versionados iniciales
- [x] Documentación base

### Fase 2 — Flujo Principal
- [ ] Formulario de denuncia completo (form-wizard)
- [ ] Endpoint POST /api/cases funcional
- [ ] Integración con Supabase (persistencia de casos)
- [ ] Agente fraud_classifier funcionando con Claude
- [ ] Agente case_summary funcionando con Claude
- [ ] Generación de tracking_code
- [ ] Vista de expediente básica

### Fase 3 — Evidencia y Seguimiento
- [ ] Upload de evidencia a Supabase Storage
- [ ] Consulta de caso por tracking_code + email
- [ ] Agente evidence_gap funcionando
- [ ] Agente risk_flags funcionando

### Fase 4 — Expediente y Demo
- [ ] Agente statement_generator funcionando
- [ ] Vista de expediente completa (expediente.html)
- [ ] Orientación a institución correcta
- [ ] Refinamiento UX para demo

## Post-Competencia (si el proyecto continúa)

- [ ] Autenticación real de usuarios
- [ ] Notificaciones por email
- [ ] Panel de seguimiento mejorado
- [ ] Rate limiting y seguridad de producción
- [ ] Integración real con SERNAC API (cuando esté disponible)
- [ ] Soporte multiidioma (español, inglés, otras lenguas migrantes)
- [ ] App móvil PWA
- [ ] Auditoría de seguridad independiente
- [ ] Cumplimiento Ley 19.628 verificado por profesional legal
