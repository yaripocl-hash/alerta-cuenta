/**
 * accessibility.js — Panel de accesibilidad persistente.
 * Aplica clases a <html> y guarda preferencias en localStorage ('ac_a11y').
 */

(function () {
  const STORAGE_KEY = 'ac_a11y';

  // ── Estado ────────────────────────────────────────────────────────────────

  function loadPrefs() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
    catch { return {}; }
  }

  function savePrefs(prefs) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs)); }
    catch {}
  }

  // ── Aplicar clases al <html> ──────────────────────────────────────────────

  function applyPrefs(prefs) {
    const html = document.documentElement;
    html.classList.remove('a11y-lg', 'a11y-xl');
    if (prefs.fontSize === 'lg')      html.classList.add('a11y-lg');
    else if (prefs.fontSize === 'xl') html.classList.add('a11y-xl');
    html.classList.toggle('a11y-contrast', !!prefs.contrast);
    html.classList.toggle('a11y-motion',   !!prefs.motion);
    html.classList.toggle('a11y-links',    !!prefs.links);
  }

  // ── Sincronizar UI del panel con estado ───────────────────────────────────

  function syncPanel(prefs) {
    const panel = document.getElementById('a11y-panel');
    if (!panel) return;
    ['normal', 'lg', 'xl'].forEach(size => {
      const btn = panel.querySelector('[data-size="' + size + '"]');
      if (btn) btn.setAttribute('aria-pressed', String(prefs.fontSize === (size === 'normal' ? null : size) || (size === 'normal' && !prefs.fontSize)));
    });
    ['contrast', 'motion', 'links'].forEach(key => {
      const input = panel.querySelector('[data-toggle="' + key + '"]');
      if (input) input.checked = !!prefs[key];
    });
  }

  // ── Helpers de construcción DOM ───────────────────────────────────────────

  function el(tag, props, children) {
    const node = document.createElement(tag);
    Object.entries(props || {}).forEach(([k, v]) => {
      if (k === 'class') node.className = v;
      else if (k === 'text') node.textContent = v;
      else if (k === 'style') node.style.cssText = v;
      else node.setAttribute(k, v);
    });
    (children || []).forEach(c => c && node.appendChild(c));
    return node;
  }

  function makeSizeBtn(size, label, fontSize) {
    const btn = el('button', {
      class: 'a11y-size-btn',
      'data-size': size,
      'aria-pressed': 'false',
      style: 'font-size:' + fontSize,
      text: label,
    });
    return btn;
  }

  function makeToggleRow(toggleKey, labelText) {
    const labelEl = el('span', { class: 'a11y-toggle-label', text: labelText });
    const input   = el('input', { type: 'checkbox', 'data-toggle': toggleKey });
    input.setAttribute('aria-label', labelText);
    const track   = el('span', { class: 'a11y-toggle-track' });
    const lbl     = el('label', { class: 'a11y-toggle', 'aria-label': labelText }, [input, track]);
    return el('div', { class: 'a11y-toggle-row' }, [labelEl, lbl]);
  }

  // ── Inyectar panel en el DOM ──────────────────────────────────────────────

  function injectPanel() {
    if (document.getElementById('a11y-panel')) return;

    // Header
    const titleSpan = el('span', { id: 'a11y-panel-title', text: 'Accesibilidad' });
    const closeBtn  = el('button', {
      class: 'a11y-panel-close',
      id: 'a11y-close-btn',
      'aria-label': 'Cerrar panel de accesibilidad',
      text: '✕',
    });
    const header = el('div', { class: 'a11y-panel-header' }, [titleSpan, closeBtn]);

    // Sección tamaño
    const sizeLabel   = el('div', { class: 'a11y-section-label', text: 'Tamaño de texto' });
    const btnNormal   = makeSizeBtn('normal', 'Normal',     '14px');
    const btnLg       = makeSizeBtn('lg',     'Grande',     '16px');
    const btnXl       = makeSizeBtn('xl',     'Muy grande', '18px');
    const sizeGroup   = el('div', { class: 'a11y-size-group', role: 'group', 'aria-label': 'Tamaño de texto' }, [btnNormal, btnLg, btnXl]);
    const sizeSection = el('div', { class: 'a11y-section' }, [sizeLabel, sizeGroup]);

    // Sección toggles
    const toggleLabel   = el('div', { class: 'a11y-section-label', text: 'Visualización' });
    const rowContrast   = makeToggleRow('contrast', 'Alto contraste');
    const rowMotion     = makeToggleRow('motion',   'Reducir movimiento');
    const rowLinks      = makeToggleRow('links',    'Subrayar enlaces');
    const toggleSection = el('div', { class: 'a11y-section' }, [toggleLabel, rowContrast, rowMotion, rowLinks]);

    // Sección reset
    const resetBtn     = el('button', { class: 'a11y-reset-btn', id: 'a11y-reset-btn', text: 'Restablecer todo' });
    const resetSection = el('div', { class: 'a11y-section' }, [resetBtn]);

    // Panel raíz
    const panel = el('div', {
      id:              'a11y-panel',
      role:            'dialog',
      'aria-modal':    'true',
      'aria-labelledby': 'a11y-panel-title',
      hidden:          '',
    }, [header, sizeSection, toggleSection, resetSection]);

    document.body.appendChild(panel);

    // Botones de tamaño
    [btnNormal, btnLg, btnXl].forEach(btn => {
      btn.addEventListener('click', () => {
        const size  = btn.dataset.size;
        const prefs = loadPrefs();
        prefs.fontSize = size === 'normal' ? null : size;
        savePrefs(prefs);
        applyPrefs(prefs);
        syncPanel(prefs);
      });
    });

    // Toggles
    panel.querySelectorAll('[data-toggle]').forEach(input => {
      input.addEventListener('change', () => {
        const prefs = loadPrefs();
        prefs[input.dataset.toggle] = input.checked;
        savePrefs(prefs);
        applyPrefs(prefs);
      });
    });

    // Reset
    resetBtn.addEventListener('click', () => {
      const prefs = {};
      savePrefs(prefs);
      applyPrefs(prefs);
      syncPanel(prefs);
    });

    // Cerrar
    closeBtn.addEventListener('click', closePanel);
  }

  // ── Abrir / cerrar ────────────────────────────────────────────────────────

  let _triggerBtn = null;

  function openPanel(triggerBtn) {
    const panel = document.getElementById('a11y-panel');
    if (!panel) return;
    _triggerBtn = triggerBtn || null;
    panel.removeAttribute('hidden');
    syncPanel(loadPrefs());
    trapFocus(panel);
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('mousedown', onOutsideClick);
  }

  function closePanel() {
    const panel = document.getElementById('a11y-panel');
    if (!panel) return;
    panel.setAttribute('hidden', '');
    document.removeEventListener('keydown', onKeyDown);
    document.removeEventListener('mousedown', onOutsideClick);
    if (_triggerBtn) { _triggerBtn.focus(); _triggerBtn = null; }
  }

  function onKeyDown(e) {
    if (e.key === 'Escape') { e.preventDefault(); closePanel(); }
  }

  function onOutsideClick(e) {
    const panel = document.getElementById('a11y-panel');
    if (!panel || panel.hasAttribute('hidden')) return;
    const triggers = document.querySelectorAll('[aria-label="Opciones de accesibilidad"]');
    if (panel.contains(e.target)) return;
    for (const t of triggers) { if (t.contains(e.target)) return; }
    closePanel();
  }

  // ── Trampa de foco ────────────────────────────────────────────────────────

  function trapFocus(panel) {
    const sel = 'button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])';
    const focusable = panel.querySelectorAll(sel);
    if (!focusable.length) return;
    focusable[0].focus();
    panel.addEventListener('keydown', function trap(e) {
      if (e.key !== 'Tab') return;
      const first = focusable[0];
      const last  = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────

  // Aplicar preferencias antes del primer paint para evitar flash
  applyPrefs(loadPrefs());

  document.addEventListener('DOMContentLoaded', () => {
    injectPanel();
    syncPanel(loadPrefs());

    document.querySelectorAll('[aria-label="Opciones de accesibilidad"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const panel = document.getElementById('a11y-panel');
        if (!panel) return;
        if (panel.hasAttribute('hidden')) openPanel(btn);
        else closePanel();
      });
    });
  });
})();
