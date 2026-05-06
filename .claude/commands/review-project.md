# Comando: review-project

Revisa el estado general del proyecto Alerta Cuenta.

Checklist:
1. ¿Existe `.env` con valores reales? (no debe estar en git)
2. ¿Hay secretos hardcodeados en algún archivo de `frontend/` o `backend/`?
3. ¿El endpoint `GET /api/health` responde?
4. ¿Los agentes tienen su prompt correspondiente en `prompts/`?
5. ¿El `prompt_manifest.yaml` está actualizado?
6. ¿Los stubs de integración (sernac, cmf, csirt, bank) siguen siendo stubs?
7. ¿El `CLAUDE.md` sigue siendo relevante?
8. ¿El `docs/roadmap.md` refleja el estado actual?
