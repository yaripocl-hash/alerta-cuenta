# Notebooks — Evaluación de Prompts

Esta carpeta se usa para evaluar y comparar versiones de prompts antes de activarlos en producción.

## Cómo usar

1. Copiar `prompt_evaluation_template.md` con el nombre del agente y la versión.
2. Definir casos de prueba cubriendo: casos normales, casos límite, inputs insuficientes.
3. Registrar outputs de Claude para cada caso.
4. Comparar con la versión anterior si existe.
5. Si el nuevo prompt es mejor, actualizar `prompt_manifest.yaml`.
