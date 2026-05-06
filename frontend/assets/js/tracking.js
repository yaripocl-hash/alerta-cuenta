/**
 * tracking.js — Lógica de la página de seguimiento de casos.
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('lookup-form');
  if (!form) return;

  // Pre-rellenar si viene de sessionStorage
  const saved = sessionStorage.getItem('ac_tracking_code');
  if (saved) document.getElementById('tracking-code').value = saved;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const trackingCode = document.getElementById('tracking-code').value.trim();
    const email = document.getElementById('lookup-email').value.trim();

    let valid = true;
    if (!trackingCode) { showFieldError('tracking-code', 'tracking-error', true); valid = false; }
    else showFieldError('tracking-code', 'tracking-error', false);

    if (!validate.email(email)) { showFieldError('lookup-email', 'email-error', true); valid = false; }
    else showFieldError('lookup-email', 'email-error', false);

    if (!valid) return;

    const btn = document.getElementById('btn-lookup');
    const text = document.getElementById('btn-lookup-text');
    const spinner = document.getElementById('lookup-spinner');
    btn.disabled = true;
    text.textContent = 'Buscando...';
    spinner.classList.remove('hidden');

    document.getElementById('lookup-error').classList.add('hidden');
    document.getElementById('case-result').classList.add('hidden');

    try {
      const result = await api.lookupCase({ tracking_code: trackingCode, email });
      document.getElementById('lookup-form-card').classList.add('hidden');
      renderResult(result);
    } catch {
      document.getElementById('lookup-error').classList.remove('hidden');
    } finally {
      btn.disabled = false;
      text.textContent = 'Consultar caso';
      spinner.classList.add('hidden');
    }
  });
});

function renderResult(data) {
  document.getElementById('result-tracking-code').textContent = data.tracking_code;
  document.getElementById('result-fraud-type').textContent = data.fraud_type || 'Clasificando...';
  document.getElementById('result-summary').textContent = data.summary || 'El resumen estará disponible pronto.';

  const statusBadge = document.getElementById('result-status-badge');
  const statusLabels = { draft: 'Borrador', submitted: 'Enviado', in_review: 'En revisión', closed: 'Cerrado' };
  const statusColors = { draft: '#6b7280', submitted: '#1a4fa0', in_review: '#b45309', closed: '#1b7d4f' };
  statusBadge.textContent = statusLabels[data.status] || data.status;
  statusBadge.style.background = (statusColors[data.status] || '#6b7280') + '22';
  statusBadge.style.color = statusColors[data.status] || '#6b7280';

  const linkExp = document.getElementById('link-to-expediente');
  if (linkExp) linkExp.href = `expediente.html?code=${data.tracking_code}`;

  document.getElementById('case-result').classList.remove('hidden');
}
