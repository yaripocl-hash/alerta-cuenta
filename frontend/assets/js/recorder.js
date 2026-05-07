/**
 * recorder.js — Grabación de audio con consentimiento, validación y transcripción.
 * Requiere api.js cargado antes. No usa innerHTML con datos del usuario.
 */

(function () {
  const MIN_MS = 10_000;   // 10 segundos mínimo
  const MAX_MS = 120_000;  // 2 minutos máximo
  const SILENCE_THRESHOLD = 0.008; // RMS mínimo para considerar "hay voz"
  const SILENCE_RATIO_MAX = 0.85;  // si más del 85% es silencio, rechazar

  let mediaRecorder = null;
  let audioChunks = [];
  let startTime = null;
  let timerInterval = null;
  let analyser = null;
  let audioCtx = null;
  let silentFrames = 0;
  let totalFrames = 0;
  let stream = null;

  // ── Helpers de visibilidad ────────────────────────────────────────────────

  function show(id, flex) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('hidden');
    if (flex) el.style.display = 'flex';
  }

  function hide(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add('hidden');
    el.style.display = '';
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  // ── Flujo de consentimiento ───────────────────────────────────────────────

  function onStartClick() {
    hide('recorder-idle');
    show('recorder-consent');
    hide('recorder-error');
    hide('recorder-success');
  }

  function onCancelConsent() {
    hide('recorder-consent');
    show('recorder-idle');
    const check = document.getElementById('consent-check');
    if (check) check.checked = false;
    updateConsentBtn();
  }

  function updateConsentBtn() {
    const btn = document.getElementById('btn-confirm-consent');
    const check = document.getElementById('consent-check');
    if (btn && check) btn.disabled = !check.checked;
  }

  // ── Grabación ─────────────────────────────────────────────────────────────

  async function startRecording() {
    hide('recorder-error');
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    } catch {
      hide('recorder-consent');
      show('recorder-idle');
      showError('No se pudo acceder al micrófono. Revisa los permisos del navegador e inténtalo de nuevo.');
      return;
    }

    // Analizador de nivel de audio
    audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 512;
    source.connect(analyser);
    silentFrames = 0;
    totalFrames = 0;

    // MediaRecorder
    audioChunks = [];
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm'
      : 'audio/mp4';
    mediaRecorder = new MediaRecorder(stream, { mimeType });
    mediaRecorder.ondataavailable = (e) => { if (e.data?.size > 0) audioChunks.push(e.data); };
    mediaRecorder.onstop = handleStop;
    mediaRecorder.start(200);

    startTime = Date.now();
    hide('recorder-consent');
    show('recorder-ui');

    timerInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      updateTimer(elapsed);
      measureLevel();
      if (elapsed >= MAX_MS) stopRecording();
    }, 150);
  }

  function stopRecording() {
    clearInterval(timerInterval);
    if (stream) stream.getTracks().forEach(t => t.stop());
    if (audioCtx) audioCtx.close();
    if (mediaRecorder?.state !== 'inactive') mediaRecorder.stop();
  }

  function updateTimer(ms) {
    const s = Math.floor(ms / 1000);
    const min = Math.floor(s / 60);
    const sec = s % 60;
    setText('recorder-timer', `${min}:${sec.toString().padStart(2, '0')}`);
    const pct = Math.min((ms / MAX_MS) * 100, 100);
    const bar = document.getElementById('recorder-progress');
    if (bar) bar.style.width = pct + '%';
  }

  function measureLevel() {
    if (!analyser) return;
    const buf = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteTimeDomainData(buf);
    let sum = 0;
    for (let i = 0; i < buf.length; i++) sum += ((buf[i] - 128) / 128) ** 2;
    const rms = Math.sqrt(sum / buf.length);

    totalFrames++;
    if (rms < SILENCE_THRESHOLD) silentFrames++;

    const level = document.getElementById('recorder-level');
    if (level) {
      const pct = Math.min(rms * 600, 100);
      level.style.width = pct + '%';
      level.style.backgroundColor = pct > 8 ? '#22c55e' : '#ef4444';
    }
  }

  // ── Procesamiento post-grabación ─────────────────────────────────────────

  async function handleStop() {
    hide('recorder-ui');
    const duration = Date.now() - startTime;

    if (duration < MIN_MS) {
      showError(`Grabación muy corta (${Math.round(duration / 1000)}s). Habla al menos 10 segundos para que podamos transcribir bien tu relato.`);
      resetToIdle();
      return;
    }

    const silenceRatio = totalFrames > 0 ? silentFrames / totalFrames : 1;
    if (silenceRatio > SILENCE_RATIO_MAX) {
      showError('No detectamos voz en la grabación. Asegúrate de hablar cerca del micrófono y de que no esté silenciado.');
      resetToIdle();
      return;
    }

    const mimeType = mediaRecorder.mimeType.split(';')[0];
    const blob = new Blob(audioChunks, { type: mimeType });

    if (blob.size > 10 * 1024 * 1024) {
      showError('La grabación supera el límite de 10 MB. Intenta con un relato más breve.');
      resetToIdle();
      return;
    }

    show('recorder-status', true);
    try {
      const result = await api.transcribeAudio(blob, mimeType);
      hide('recorder-status');
      const textarea = document.getElementById('description');
      if (textarea && result.text) {
        const prev = textarea.value.trim();
        textarea.value = prev ? prev + '\n\n' + result.text.trim() : result.text.trim();
        textarea.dispatchEvent(new Event('input'));
      }
      showSuccess('Transcripción lista. Revisa el texto y corrígelo si es necesario antes de continuar.');
    } catch (err) {
      hide('recorder-status');
      showError(err.message || 'No se pudo transcribir el audio. Puedes escribir tu relato manualmente.');
    }

    resetToIdle();
  }

  function resetToIdle() {
    mediaRecorder = null;
    audioChunks = [];
    show('recorder-idle');
  }

  // ── Mensajes ──────────────────────────────────────────────────────────────

  function showError(msg) {
    hide('recorder-success');
    const el = document.getElementById('recorder-error');
    if (!el) return;
    el.textContent = msg;
    el.classList.remove('hidden');
    el.style.display = 'block';
  }

  function showSuccess(msg) {
    hide('recorder-error');
    const el = document.getElementById('recorder-success');
    if (!el) return;
    el.textContent = msg;
    el.classList.remove('hidden');
  }

  // ── Init ──────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('recorder-container')) return;

    document.getElementById('btn-start-record')?.addEventListener('click', onStartClick);
    document.getElementById('btn-cancel-consent')?.addEventListener('click', onCancelConsent);
    document.getElementById('btn-confirm-consent')?.addEventListener('click', startRecording);
    document.getElementById('btn-stop-record')?.addEventListener('click', stopRecording);
    document.getElementById('consent-check')?.addEventListener('change', updateConsentBtn);

    // Ocultar si el navegador no soporta grabación
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      document.getElementById('recorder-container')?.remove();
    }
  });
})();
