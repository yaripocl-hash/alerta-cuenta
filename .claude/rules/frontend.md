# Reglas Frontend

- Sin frameworks. Solo HTML, CSS y JS puro.
- Mobile-first: diseñar para pantalla pequeña primero.
- Botones grandes (min-height: 52px) y alto contraste — accesibilidad para adultos mayores.
- Toda comunicación con el backend pasa por `assets/js/api.js`.
- No poner URLs de backend hardcodeadas en los HTMLs.
- No usar `innerHTML` con datos del usuario. Usar `textContent` y `createElement`.
- Validar siempre en el frontend antes de enviar — pero el backend siempre valida de nuevo.
- No guardar datos sensibles en `localStorage`. Usar `sessionStorage` solo para tracking_code.
- Usar `aria-*` y roles semánticos. Testear con lector de pantalla si es posible.
