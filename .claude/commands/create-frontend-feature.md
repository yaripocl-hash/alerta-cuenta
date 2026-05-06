# Comando: create-frontend-feature

Pasos para agregar una nueva feature al frontend:

1. Determinar si va en una página existente o nueva
2. Si es nueva página: crear `frontend/<nombre>.html` siguiendo el patrón de las existentes
3. Agregar estilos en `frontend/assets/css/components.css` (no crear CSS nuevos si es posible)
4. Agregar lógica en `frontend/assets/js/` — preferir extender archivos existentes
5. Toda llamada HTTP pasa por `api.js` — agregar el método ahí
6. No usar `innerHTML` con datos del usuario
7. Verificar en mobile (viewport 375px) antes de dar por terminado
8. Verificar alto contraste y tamaño de botones (min 52px altura)
