# Reglas de Seguridad

- `ANTHROPIC_API_KEY` nunca en frontend, nunca en logs, nunca en responses de la API.
- `SUPABASE_SERVICE_ROLE_KEY` nunca en frontend.
- `APP_SECRET` nunca en logs ni en responses.
- No loguear PII (RUT, nombre, email, número de cuenta) en texto plano.
- Validar `Content-Type` de uploads — no confiar en lo que declara el cliente.
- Validar tamaño de archivos antes de procesar (máx. 10 MB).
- CORS restrictivo: solo orígenes configurados en `.env`.
- No retornar stack traces en producción (`APP_ENV=production`).
- No crear endpoints que expongan listados completos de casos sin autenticación.
