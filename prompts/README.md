# Prompts — Alerta Cuenta

Los prompts de los agentes Claude se versionan aquí como archivos Markdown.

## Estructura

```
prompts/
├── <nombre_agente>/
│   ├── v1.md   ← versión actual
│   └── v2.md   ← nueva versión al iterar
└── prompt_manifest.yaml
```

## Cómo versionar

1. Nunca edites un prompt en producción directamente.
2. Crea una nueva versión (`v2.md`) con los cambios.
3. Actualiza `prompt_manifest.yaml` con la versión activa.
4. Evalúa la nueva versión en `notebooks/` antes de activarla.
5. Actualiza `prompt_version` en el agente Python correspondiente.

## Restricciones para todos los prompts

- No inventar leyes, artículos, normativas ni procedimientos chilenos específicos.
- No dar asesoría legal definitiva. Orientar, no dictaminar.
- Usar lenguaje simple, empático y directo.
- Si falta contexto, pedir más información en vez de asumir.
- El output siempre debe ser JSON estructurado.
- Incluir siempre un disclaimer en los outputs orientadores.
