# Privacidad y PII — Alerta Cuenta

## Datos Sensibles que Manejamos

Los usuarios pueden ingresar datos personales muy sensibles:

| Campo | Tipo de dato | Nivel de sensibilidad |
|---|---|---|
| Nombre completo | PII directa | Alta |
| RUT | PII directa | Muy alta |
| Email | PII directa | Alta |
| Teléfono | PII directa | Alta |
| Número de cuenta bancaria | PII financiera | Muy alta |
| Banco o fintech afectada | Dato contextual | Media |
| Monto afectado | Dato financiero | Alta |
| Descripción del fraude | PII indirecta | Variable |
| Capturas de pantalla | PII potencial | Variable |

## Principios de Manejo

1. **Mínimo necesario**: Solo pedir los datos que sean indispensables para el caso.
2. **No persistir lo innecesario**: Si un dato no se usa en el expediente, no guardarlo.
3. **No loguar PII**: Los logs de aplicación no deben contener nombres, RUTs ni cuentas.
4. **Cifrado en tránsito**: HTTPS obligatorio en producción.
5. **Acceso controlado**: Los datos del caso solo son accesibles con `tracking_code` + email.

## Claude y los Datos del Usuario

- Claude recibe el relato y los datos del caso para generar el expediente.
- El prompt **no** debe incluir el RUT completo si no es necesario para la clasificación.
- Los outputs de Claude se guardan en `case_ai_outputs` — revisar qué PII queda en el JSON.
- Anthropic tiene sus propias políticas de privacidad para datos enviados a la API.

## Consideraciones Legales (orientativas, no asesoría legal)

- La Ley 19.628 (Chile) regula el tratamiento de datos personales.
- En producción, evaluar si se requiere aviso de privacidad explícito al usuario.
- Verificar política de retención de datos para casos cerrados.

**Este documento es orientativo. Consultar con profesional legal antes del lanzamiento.**

## Checklist de Privacidad para Nuevas Features

- [ ] ¿Esta feature requiere nuevos datos de PII?
- [ ] ¿Se puede lograr el objetivo con menos datos?
- [ ] ¿Estos datos van al log? (No deberían)
- [ ] ¿Estos datos van al prompt de Claude? ¿Es necesario?
- [ ] ¿Estos datos se exponen en algún endpoint público?
