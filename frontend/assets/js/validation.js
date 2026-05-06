/**
 * validation.js — Validaciones simples para formularios.
 */

const validate = {
  required(value) {
    return value && value.trim().length > 0;
  },

  minLength(value, min) {
    return value && value.trim().length >= min;
  },

  email(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  },

  phone(value) {
    if (!value || value.trim() === '') return true; // Opcional
    return /^[\d\s+\-()]{7,15}$/.test(value.trim());
  },

  positiveNumber(value) {
    if (!value || value === '') return true; // Opcional
    return !isNaN(value) && Number(value) > 0;
  },
};

function showFieldError(inputId, errorId, show) {
  const input = document.getElementById(inputId);
  const error = document.getElementById(errorId);
  if (!input || !error) return;
  if (show) {
    input.classList.add('invalid');
    error.classList.add('visible');
  } else {
    input.classList.remove('invalid');
    error.classList.remove('visible');
  }
}
