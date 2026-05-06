# Supabase Storage — Alerta Cuenta

## Bucket: `evidence`

### Crear el bucket

En el Dashboard de Supabase:
1. Ir a Storage
2. Crear nuevo bucket llamado `evidence`
3. **Desactivar** "Public bucket" (acceso privado)

### Políticas de acceso

El bucket `evidence` es privado. Solo el backend (con `service_role_key`) puede leer y escribir.

No crear políticas públicas para este bucket.

### Estructura de paths

```
evidence/
└── {case_id}/
    └── {uuid}-{filename}
```

Ejemplo: `evidence/abc123-def456/9f3a1b2c-factura.pdf`

### Acceso a archivos

El backend genera URLs firmadas temporales (signed URLs) con `storage_service.get_signed_url()`.
Los signed URLs expiran en 1 hora por defecto.

**Nunca exponer el path del archivo directamente en el frontend.**
