# Reglas de Prompts

- Los prompts viven en `prompts/<agente>/v1.md` (y sucesivas versiones).
- Nunca editar una versión en producción. Crear `v2.md`, evaluar, luego activar.
- Actualizar `prompt_manifest.yaml` cuando cambie la versión activa.
- Evaluar nuevos prompts en `notebooks/` antes de producción.
- Todo prompt debe incluir las restricciones: no inventar leyes, no asesoría legal definitiva, output JSON.
- El output de cada agente debe ser JSON parseado — nunca texto libre sin estructura.
- Si un agente recibe contexto insuficiente, debe devolver `needs_clarification: true` en vez de inventar.
