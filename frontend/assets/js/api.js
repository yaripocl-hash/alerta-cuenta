/**
 * api.js — Cliente HTTP para el backend de Alerta Cuenta.
 * El backend es quien llama a Claude y Supabase. NUNCA pongas API keys aquí.
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : '/api'; // En producción, configurar proxy o variable de build

const api = {
  async post(endpoint, data) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
  },

  async get(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
  },

  async uploadFile(endpoint, file) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
  },

  transcribeAudio: async (blob, mimeType) => {
    const ext = mimeType.includes('mp4') ? 'mp4' : mimeType.includes('ogg') ? 'ogg' : 'webm';
    const form = new FormData();
    form.append('audio', blob, `recording.${ext}`);
    const res = await fetch(`${API_BASE}/ai/transcribe`, { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
  },

  createCase: (data) => api.post('/cases/', data),
  lookupCase: (data) => api.post('/tracking/lookup', data),
  getCase: (trackingCode) => api.get(`/cases/${trackingCode}`),
  classify: (data) => api.post('/ai/classify', data),
  summarize: (data) => api.post('/ai/summarize', data),
  uploadEvidence: (caseId, file) => api.uploadFile(`/evidence/${caseId}`, file),
  healthCheck: () => api.get('/health'),
};
