/**
 * form-wizard.js — Lógica de pasos del formulario de denuncia.
 * Usa DOM seguro (textContent, createElement) para evitar XSS.
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('case-form');
  if (!form) return;

  let currentStep = 1;
  const totalSteps = 4;

  function goTo(step) {
    document.querySelectorAll('.step-panel').forEach((el, i) => {
      el.classList.toggle('hidden', i + 1 !== step);
    });
    for (let i = 1; i <= totalSteps; i++) {
      const indicator = document.getElementById(`step-indicator-${i}`);
      if (!indicator) continue;
      indicator.classList.remove('active', 'done');
      if (i < step) indicator.classList.add('done');
      if (i === step) indicator.classList.add('active');
    }
    currentStep = step;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function validateStep1() {
    const desc = document.getElementById('description').value;
    const valid = validate.minLength(desc, 20);
    showFieldError('description', 'description-error', !valid);
    return valid;
  }

  function validateStep3() {
    const email = document.getElementById('email').value;
    const valid = validate.email(email);
    showFieldError('email', 'email-error', !valid);
    return valid;
  }

  function createSummaryRow(label, value) {
    const p = document.createElement('p');
    const strong = document.createElement('strong');
    strong.textContent = label + ': ';
    p.appendChild(strong);
    p.appendChild(document.createTextNode(value));
    return p;
  }

  function buildSummary() {
    const desc = document.getElementById('description').value;
    const fraudType = document.getElementById('fraud-type');
    const date = document.getElementById('incident-date').value;
    const amount = document.getElementById('amount').value;
    const email = document.getElementById('email').value;

    const summaryEl = document.getElementById('case-summary');
    if (!summaryEl) return;

    summaryEl.textContent = '';

    const shortDesc = desc.length > 120 ? desc.slice(0, 120) + '...' : desc;
    summaryEl.appendChild(createSummaryRow('Descripción', shortDesc));
    summaryEl.appendChild(createSummaryRow('Tipo', fraudType.options[fraudType.selectedIndex].text));
    if (date) summaryEl.appendChild(createSummaryRow('Fecha', date));
    if (amount) summaryEl.appendChild(createSummaryRow('Monto', `$${Number(amount).toLocaleString('es-CL')} CLP`));
    summaryEl.appendChild(createSummaryRow('Email', email));
  }

  document.getElementById('btn-next-1')?.addEventListener('click', () => {
    if (validateStep1()) goTo(2);
  });

  document.getElementById('btn-back-2')?.addEventListener('click', () => goTo(1));
  document.getElementById('btn-next-2')?.addEventListener('click', () => goTo(3));

  document.getElementById('btn-back-3')?.addEventListener('click', () => goTo(2));
  document.getElementById('btn-next-3')?.addEventListener('click', () => {
    if (validateStep3()) { buildSummary(); goTo(4); }
  });

  document.getElementById('btn-back-4')?.addEventListener('click', () => goTo(3));

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-submit');
    const text = document.getElementById('btn-submit-text');
    const spinner = document.getElementById('btn-spinner');

    btn.disabled = true;
    text.textContent = 'Enviando...';
    spinner.classList.remove('hidden');

    const payload = {
      description: document.getElementById('description').value,
      fraud_type: document.getElementById('fraud-type').value || null,
      incident_date: document.getElementById('incident-date').value || null,
      amount_affected: document.getElementById('amount').value ? Number(document.getElementById('amount').value) : null,
      contact_email: document.getElementById('email').value,
      contact_phone: document.getElementById('phone').value || null,
      target_institution: document.getElementById('institution').value || null,
    };

    try {
      const result = await api.createCase(payload);
      form.classList.add('hidden');
      const successEl = document.getElementById('submit-success');
      successEl.classList.remove('hidden');
      document.getElementById('tracking-code-display').textContent = result.tracking_code;
      const linkExp = document.getElementById('link-expediente');
      if (linkExp) linkExp.href = 'expediente.html?code=' + encodeURIComponent(result.tracking_code);
      sessionStorage.setItem('ac_tracking_code', result.tracking_code);
      sessionStorage.setItem('ac_case_id', result.id);
    } catch (err) {
      alert('Error al enviar: ' + err.message + '. Intenta de nuevo.');
    } finally {
      btn.disabled = false;
      text.textContent = 'Enviar caso';
      spinner.classList.add('hidden');
    }
  });
});
