/**
 * main.js — Inicialización global y utilidades compartidas.
 */

// Cargar expediente en expediente.html si hay tracking_code en URL o sessionStorage
document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const code = params.get('code') || sessionStorage.getItem('ac_tracking_code');

  if (document.getElementById('expediente-content') && code) {
    loadExpediente(code);
  }
});

async function loadExpediente(trackingCode) {
  document.getElementById('exp-tracking-code').textContent = trackingCode;
  try {
    const data = await api.getCase(trackingCode);
    renderExpediente(data);
  } catch {
    document.getElementById('loading-state').classList.add('hidden');
    document.getElementById('exp-error').classList.remove('hidden');
  }
}

function renderExpediente(data) {
  document.getElementById('loading-state').classList.add('hidden');
  document.getElementById('expediente-content').classList.remove('hidden');

  document.getElementById('exp-tracking-code').textContent = data.tracking_code;
  document.getElementById('exp-status').textContent = data.status;
  document.getElementById('exp-date').textContent = new Date(data.created_at).toLocaleDateString('es-CL');
  document.getElementById('exp-fraud-type').textContent = data.fraud_type || 'Clasificando...';

  // Campos generados por agentes (disponibles cuando se implementen)
  const ai = data.ai_outputs || {};
  document.getElementById('exp-summary').textContent = ai.summary || 'El resumen estará disponible pronto.';

  const actionsEl = document.getElementById('exp-actions');
  (ai.recommended_actions || ['Contactar al banco inmediatamente', 'No realizar más transacciones hasta aclarar el caso']).forEach(a => {
    const li = document.createElement('li');
    li.textContent = a;
    actionsEl.appendChild(li);
  });

  const gapsEl = document.getElementById('exp-evidence-gaps');
  (ai.missing_evidence || ['Capturas de pantalla del mensaje o llamada', 'Comprobante de transferencia']).forEach(e => {
    const li = document.createElement('li');
    li.textContent = e;
    gapsEl.appendChild(li);
  });

  const instEl = document.getElementById('exp-institutions');
  (ai.institutions || ['Banco', 'SERNAC']).forEach(inst => {
    const span = document.createElement('span');
    span.className = 'institution-tag';
    span.textContent = inst;
    instEl.appendChild(span);
  });

  document.getElementById('exp-statement').textContent = ai.statement || 'La declaración preliminar estará disponible una vez que el caso sea analizado.';
}

function copyStatement() {
  const text = document.getElementById('exp-statement').textContent;
  navigator.clipboard.writeText(text).then(() => {
    alert('Declaración copiada al portapapeles.');
  });
}

// Upload de evidencia
document.addEventListener('DOMContentLoaded', () => {
  const uploadArea = document.getElementById('upload-area');
  const input = document.getElementById('evidence-input');
  if (!uploadArea || !input) return;

  uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('dragover'); });
  uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
  uploadArea.addEventListener('drop', e => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
  });

  input.addEventListener('change', () => handleFiles(input.files));
});

async function handleFiles(files) {
  const caseId = sessionStorage.getItem('ac_case_id');
  if (!caseId) { alert('No se encontró el ID del caso. Vuelve a la página de denuncia.'); return; }
  const listEl = document.getElementById('upload-list');
  for (const file of files) {
    const item = document.createElement('div');
    item.style.cssText = 'padding:.5rem; background:var(--color-accent); border-radius:var(--radius); margin-bottom:.5rem; font-size:.9rem;';
    item.textContent = `Subiendo ${file.name}...`;
    listEl.appendChild(item);
    try {
      await api.uploadEvidence(caseId, file);
      item.textContent = `✅ ${file.name}`;
    } catch (err) {
      item.textContent = `❌ ${file.name} — ${err.message}`;
      item.style.background = '#fef2f2';
    }
  }
}
