# Deploy Frontend en Vercel

## Configuración

El archivo `vercel.json` en la raíz del proyecto ya está configurado para servir el frontend desde la carpeta `frontend/`.

## Primer Deploy

### Opción 1: CLI de Vercel

```bash
npm i -g vercel
vercel login
vercel --cwd frontend
```

### Opción 2: GitHub Integration

1. Ir a vercel.com y conectar el repositorio `yaripocl-hash/alerta-cuenta`
2. En "Configure Project":
   - Framework Preset: `Other`
   - Root Directory: `frontend`
   - Build Command: (dejar vacío)
   - Output Directory: `.` (el mismo directorio)
3. Deploy

## Variables de Entorno en Vercel

El frontend **no usa variables de entorno secretas**. Toda la configuración secreta está en el backend.

Si en el futuro se necesita configurar la URL del backend como variable:
```
VITE_API_URL=https://alerta-cuenta-api.onrender.com/api
```
(Pero en esta versión, la URL se resuelve automáticamente en `api.js`)

## Deploy del Backend

El backend (FastAPI) **no** se despliega en Vercel. Opciones recomendadas:

| Plataforma | Plan gratuito | Notas |
|---|---|---|
| Render | Sí (con sleep) | Fácil configuración |
| Railway | Sí (con límites) | Buen DX |
| Fly.io | Sí | Más control |

Variables de entorno a configurar en la plataforma del backend:
- `ANTHROPIC_API_KEY`
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `APP_SECRET`
- `CORS_ORIGINS` (dominio de Vercel)

## URL del Backend en Producción

Actualizar `CORS_ORIGINS` en el backend con el dominio de Vercel.
Actualizar `api.js` si se requiere una URL de backend específica.
