# Comando: create-backend-feature

Pasos para agregar una nueva feature al backend:

1. Definir el schema en `backend/app/schemas/<entidad>.py`
2. Crear o actualizar el service en `backend/app/services/<entidad>_service.py`
3. Crear o actualizar el router en `backend/app/api/<entidad>.py`
4. Registrar el router en `backend/app/main.py` si es nuevo
5. Si involucra Claude: crear el agente en `backend/app/agents/` y el prompt en `prompts/`
6. Verificar que no se expongan secretos en ningún response
7. Probar con `GET /api/health` primero, luego el nuevo endpoint
