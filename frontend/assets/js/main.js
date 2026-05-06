/**
 * main.js — Expediente y subida de evidencia.
 */

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
    const caseData = await api.getCase(trackingCode);

    const savedClassify = sessionStorage.getItem('ac_classify_output');
    const savedSummarize = sessionStorage.getItem('ac_summarize_output');
    const classifyOutput = savedClassify ? JSON.parse(savedClassify) : null;
    const summarizeOutput = savedSummarize ? JSON.parse(savedSummarize) : null;

    renderExpediente(caseData, classifyOutput, summarizeOutput);
  } catch (e) {
    console.error(e);
    document.getElementById('loading-state').classList.add('hidden');
    document.getElementById('exp-error').classList.remove('hidden');
  }
}

function renderExpediente(caseData, classify, summary) {
  document.getElementById('loading-state').classList.add('hidden');
  document.getElementById('expediente-content').classList.remove('hidden');

  const statusLabels = { draft: 'Borrador', submitted: 'Enviado', in_review: 'En revisión', closed: 'Cerrado' };
  document.getElementById('exp-tracking-code').textContent = caseData.tracking_code;
  document.getElementById('exp-status').textContent = statusLabels[caseData.status] || caseData.status;
  document.getElementById('exp-date').textContent = new Date(caseData.created_at).toLocaleDateString('es-CL');

  const fraudType = classify?.classification?.fraud_type || classify?.fraud_type || caseData.fraud_type;
  document.getElementById('exp-fraud-type').textContent = fraudType || 'Clasificando...';

  const casoResumen = summary?.caso_resumen || {};
  const summaryText = casoResumen?.tipo_fraude?.descripcion || summary?.summary || '';
  document.getElementById('exp-summary').textContent = summaryText || 'Resumen no disponible.';

  const actionsEl = document.getElementById('exp-actions');
  actionsEl.textContent = '';
  const rawActions = classify?.immediate_steps
    || casoResumen?.acciones_recomendadas
    || ['Contacta a tu banco inmediatamente', 'Guarda toda la evidencia disponible'];
  rawActions.forEach(a => {
    const li = document.createElement('li');
    li.textContent = typeof a === 'string' ? a : (a.accion || '');
    actionsEl.appendChild(li);
  });

  const gapsEl = document.getElementById('exp-evidence-gaps');
  gapsEl.textContent = '';
  const gaps = casoResumen?.informacion_faltante?.missing_info
    || (Array.isArray(classify?.needs_clarification) ? classify.needs_clarification : [])
    || ['Capturas del mensaje o llamada', 'Comprobante de la transacción no autorizada'];
  gaps.forEach(g => {
    const li = document.createElement('li');
    li.textContent = typeof g === 'string' ? g : JSON.stringify(g);
    gapsEl.appendChild(li);
  });

  const instEl = document.getElementById('exp-institutions');
  instEl.textContent = '';
  _extractInstitutions(casoResumen?.acciones_recomendadas || []).forEach(inst => {
    const span = document.createElement('span');
    span.className = 'institution-tag';
    span.textContent = inst;
    instEl.appendChild(span);
  });

  document.getElementById('exp-statement').textContent = _composeStatement(caseData, fraudType, casoResumen);
}

function _extractInstitutions(actions) {
  const known = ['SERNAC', 'CMF', 'PDI', 'Carabineros', 'CSIRT'];
  const text = JSON.stringify(actions).toUpperCase();
  const found = known.filter(i => text.includes(i));
  return found.length ? ['Tu banco', ...found] : ['Tu banco', 'SERNAC'];
}

function _composeStatement(caseData, fraudType, casoResumen) {
  const date = new Date(caseData.created_at).toLocaleDateString('es-CL');
  const descripcion = casoResumen?.tipo_fraude?.descripcion || '';
  const hechos = (casoResumen?.hechos_relevantes || []).map((h, i) => `${i + 1}. ${h}`).join('\n');
  return [
    `DECLARACIÓN PRELIMINAR — ${date}`,
    `Código de caso: ${caseData.tracking_code}`,
    '',
    descripcion || `Declaro haber sido víctima de ${fraudType || 'fraude financiero'}.`,
    hechos ? '\nHechos relevantes:\n' + hechos : '',
    '',
    'Este documento fue generado con IA por Alerta Cuenta como orientación. No constituye asesoría legal.',
  ].join('\n').trim();
}

function copyStatement() {
  const text = document.getElementById('exp-statement').textContent;
  navigator.clipboard.writeText(text).then(() => alert('Declaración copiada al portapapeles.'));
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
    item.style.cssText = 'padding:.5rem;background:var(--color-accent);border-radius:var(--radius);margin-bottom:.5rem;font-size:.9rem;';
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
