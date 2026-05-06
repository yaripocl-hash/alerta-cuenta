# Seguridad — Alerta Cuenta

## Principios

1. **Secretos solo en backend**: `ANTHROPIC_API_KEY` y `SUPABASE_SERVICE_ROLE_KEY` nunca en frontend.
2. **Variables de entorno**: toda config sensible via `.env` (nunca hardcodeada).
3. **CORS restrictivo**: solo orígenes conocidos en producción.
4. **Rate limiting**: implementar en producción para endpoints públicos.
5. **Validación de inputs**: Pydantic en backend, validación básica en frontend.
6. **Upload seguro**: validar tipo y tamaño de archivos antes de subir a Storage.

## Autenticación en MVP

El MVP no usa autenticación con usuario/contraseña. El acceso a un caso se da por:
- `tracking_code` (código único generado en backend)
- Email del usuario (para recuperar el tracking_code)

Este modelo es suficiente para el demo. En producción habría que evaluar autenticación real.

## HMAC para Tracking Codes

El `tracking_code` se firma con HMAC usando `APP_SECRET` para evitar enumeración.
Ver implementación en `backend/app/core/hmac_utils.py`.

## CORS

En desarrollo, se permiten `localhost:5500` y `127.0.0.1:5500`.
En producción, solo el dominio de Vercel.

Configurar en `CORS_ORIGINS` en `.env`.

## Uploads de Evidencia

- Tipos permitidos: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`, `text/plain`
- Tamaño máximo: 10 MB por archivo
- Los archivos se guardan en Supabase Storage con paths que incluyen el `case_id`
- Nunca se sirven directamente al público — acceso por signed URL del backend

## Qué NO Hacer

- No logues PII (RUT, nombre completo, número de cuenta, monto) en texto plano
- No expongas el `SUPABASE_SERVICE_ROLE_KEY` en ningún endpoint
- No respondas con stack traces en producción (`APP_ENV=production`)
- No confíes en el `Content-Type` declarado por el cliente para uploads
