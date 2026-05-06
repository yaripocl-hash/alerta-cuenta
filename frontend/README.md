# Frontend — Alerta Cuenta

HTML + CSS + JS puro. Sin frameworks, sin Node, sin bundlers.

## Páginas

| Archivo | Descripción |
|---|---|
| `index.html` | Landing principal |
| `denuncia.html` | Formulario de denuncia paso a paso |
| `seguimiento.html` | Consulta de caso por tracking_code + email |
| `expediente.html` | Vista del expediente preliminar generado por IA |

## Archivos JS

| Archivo | Responsabilidad |
|---|---|
| `api.js` | Cliente HTTP hacia el backend. Único punto de comunicación. |
| `validation.js` | Funciones de validación reutilizables |
| `form-wizard.js` | Lógica de pasos del formulario de denuncia |
| `tracking.js` | Lógica de la página de seguimiento |
| `main.js` | Inicialización global y carga del expediente |

## Correr en local

```powershell
cd frontend
python -m http.server 5500
# Abrir http://localhost:5500
```

## Regla clave

**Nunca** pongas `ANTHROPIC_API_KEY` ni `SUPABASE_SERVICE_ROLE_KEY` aquí.
El frontend solo habla con el backend.
