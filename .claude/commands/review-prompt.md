# Comando: review-prompt

Checklist para revisar un prompt antes de activar una nueva versión:

1. ¿El system prompt tiene las restricciones obligatorias?
   - No inventar leyes ni normativas
   - No asesoría legal definitiva
   - Output siempre JSON
   - Pedir clarificación si falta contexto
2. ¿El output JSON esperado tiene todos los campos que usa el agente Python?
3. ¿El prompt usa lenguaje empático y simple?
4. ¿Se evaluó en `notebooks/prompt_evaluation_template.md` con casos de prueba?
5. ¿Se actualizó `prompt_manifest.yaml` con la nueva versión activa?
6. ¿Se actualizó `prompt_version` en el agente Python correspondiente?
