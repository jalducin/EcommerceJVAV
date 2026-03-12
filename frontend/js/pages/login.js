/**
 * MetalShop — Página de Login / Registro
 * Maneja tabs, formularios, tokens JWT, sync carrito y redirect.
 */

(function LoginPage() {
  'use strict';

  // Si ya está autenticado → redirigir
  if (Auth.isAuthenticated()) {
    window.location.href = getNextUrl() || '/';
    return;
  }

  // ── Helpers ───────────────────────────────────────────────────────────────────
  function getNextUrl() {
    return new URLSearchParams(location.search).get('next') || null;
  }

  function redirectAfterAuth() {
    window.location.href = getNextUrl() || '/';
  }

  function showError(panelId, message) {
    const $err = document.getElementById(`${panelId}-error`);
    const $msg = document.getElementById(`${panelId}-error-msg`);
    if ($err && $msg) {
      $msg.textContent = message;
      $err.classList.add('show');
    }
  }

  function hideError(panelId) {
    document.getElementById(`${panelId}-error`)?.classList.remove('show');
  }

  function setLoading(btnId, loading, label) {
    const $btn = document.getElementById(btnId);
    if (!$btn) return;
    $btn.disabled = loading;
    $btn.innerHTML = loading
      ? `<span class="spinner"></span> Procesando...`
      : label;
    if (!loading && typeof lucide !== 'undefined') lucide.createIcons({ elements: [$btn] });
  }

  // ── Post-auth: guardar tokens, user, sync carrito ─────────────────────────────
  async function handleAuthSuccess(data) {
    Auth.setTokens(data.access_token, data.refresh_token);

    // Obtener perfil del usuario
    try {
      const user = await api.get('/auth/me');
      Auth.setUser(user);
    } catch { /* continue */ }

    // Sincronizar carrito de localStorage con la BD
    if (typeof window.Cart !== 'undefined') {
      await Cart.syncAfterLogin();
    }

    showToast('¡Sesión iniciada correctamente!', 'success');
    setTimeout(redirectAfterAuth, 800);
  }

  // ── Tabs ──────────────────────────────────────────────────────────────────────
  function switchTab(tabId) {
    const panels = { login: 'panel-login', register: 'panel-register' };
    const tabs   = { login: 'tab-login',   register: 'tab-register'   };
    const footer = { login: '¿No tienes cuenta? <a href="#" id="switch-to-register">Regístrate gratis</a>',
                     register: '¿Ya tienes cuenta? <a href="#" id="switch-to-login">Inicia sesión</a>' };

    Object.entries(tabs).forEach(([key, id]) => {
      const tab = document.getElementById(id);
      const panel = document.getElementById(panels[key]);
      const isActive = key === tabId;
      tab?.classList.toggle('active', isActive);
      tab?.setAttribute('aria-selected', String(isActive));
      panel?.classList.toggle('active', isActive);
    });

    const $footer = document.getElementById('auth-footer-hint');
    if ($footer) {
      $footer.innerHTML = footer[tabId];
      // Re-bind switch links
      document.getElementById('switch-to-register')?.addEventListener('click', (e) => { e.preventDefault(); switchTab('register'); });
      document.getElementById('switch-to-login')?.addEventListener('click', (e) => { e.preventDefault(); switchTab('login'); });
    }
  }

  // ── Toggle visibilidad contraseña ─────────────────────────────────────────────
  function bindPasswordToggles() {
    document.querySelectorAll('.toggle-password').forEach((btn) => {
      btn.addEventListener('click', () => {
        const target = document.getElementById(btn.dataset.target);
        if (!target) return;
        const isPassword = target.type === 'password';
        target.type = isPassword ? 'text' : 'password';
        btn.innerHTML = isPassword
          ? `<i data-lucide="eye-off" width="16" height="16"></i>`
          : `<i data-lucide="eye" width="16" height="16"></i>`;
        if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [btn] });
      });
    });
  }

  // ── Strength de contraseña ────────────────────────────────────────────────────
  function getPasswordStrength(pwd) {
    let score = 0;
    if (pwd.length >= 8)  score++;
    if (pwd.length >= 12) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    return score;
  }

  function updateStrength(pwd) {
    const $bar    = document.getElementById('strength-fill');
    const $label  = document.getElementById('strength-label');
    const $wrap   = document.getElementById('password-strength');
    if (!$bar || !$label || !$wrap) return;

    $wrap.style.display = pwd.length > 0 ? 'block' : 'none';
    const score = getPasswordStrength(pwd);
    const configs = [
      { pct: '15%', color: '#FC8181', label: 'Muy débil' },
      { pct: '30%', color: '#F6AD55', label: 'Débil' },
      { pct: '55%', color: '#ECC94B', label: 'Regular' },
      { pct: '80%', color: '#68D391', label: 'Buena' },
      { pct: '100%',color: '#48BB78', label: 'Excelente' },
    ];
    const c = configs[Math.min(score, 4)];
    $bar.style.width = c.pct;
    $bar.style.background = c.color;
    $label.textContent = c.label;
    $label.style.color = c.color;
  }

  // ── Login form ────────────────────────────────────────────────────────────────
  function bindLoginForm() {
    const $form = document.getElementById('login-form');
    if (!$form) return;

    $form.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideError('login');

      const email    = document.getElementById('login-email')?.value.trim();
      const password = document.getElementById('login-password')?.value;

      if (!email || !password) {
        showError('login', 'Ingresa tu email y contraseña');
        return;
      }

      setLoading('login-btn', true);

      try {
        const data = await api.post('/auth/login', { email, password });
        await handleAuthSuccess(data);
      } catch (err) {
        showError('login', err.message || 'Credenciales incorrectas');
        setLoading('login-btn', false, `<i data-lucide="log-in" width="18" height="18"></i> Iniciar Sesión`);
      }
    });
  }

  // ── Register form ─────────────────────────────────────────────────────────────
  function bindRegisterForm() {
    const $form = document.getElementById('register-form');
    if (!$form) return;

    // Strength en tiempo real
    document.getElementById('reg-password')?.addEventListener('input', (e) => {
      updateStrength(e.target.value);
    });

    $form.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideError('register');

      const full_name = document.getElementById('reg-name')?.value.trim();
      const email     = document.getElementById('reg-email')?.value.trim();
      const password  = document.getElementById('reg-password')?.value;
      const confirm   = document.getElementById('reg-confirm')?.value;
      const terms     = document.getElementById('reg-terms')?.checked;

      // Validaciones client-side
      let valid = true;

      if (password !== confirm) {
        document.getElementById('confirm-error').style.display = 'block';
        valid = false;
      } else {
        document.getElementById('confirm-error').style.display = 'none';
      }

      if (!terms) {
        document.getElementById('terms-error').style.display = 'block';
        valid = false;
      } else {
        document.getElementById('terms-error').style.display = 'none';
      }

      if (!full_name || !email || !password) {
        showError('register', 'Completa todos los campos obligatorios');
        return;
      }

      if (password.length < 8) {
        showError('register', 'La contraseña debe tener al menos 8 caracteres');
        return;
      }

      if (!valid) return;

      setLoading('register-btn', true);

      try {
        // Registrar
        await api.post('/auth/register', { email, password, full_name });

        // Auto-login tras registro
        const loginData = await api.post('/auth/login', { email, password });
        await handleAuthSuccess(loginData);

        showToast('¡Cuenta creada exitosamente!', 'success');
      } catch (err) {
        showError('register', err.message || 'Error al crear la cuenta');
        setLoading('register-btn', false, `<i data-lucide="user-plus" width="18" height="18"></i> Crear Cuenta`);
      }
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────────
  function init() {
    // Tabs
    document.getElementById('tab-login')?.addEventListener('click', () => switchTab('login'));
    document.getElementById('tab-register')?.addEventListener('click', () => switchTab('register'));

    // Switch links en el footer
    document.getElementById('switch-to-register')?.addEventListener('click', (e) => { e.preventDefault(); switchTab('register'); });
    document.getElementById('switch-to-login')?.addEventListener('click', (e) => { e.preventDefault(); switchTab('login'); });

    // Forgot password link
    document.getElementById('go-forgot')?.addEventListener('click', (e) => {
      e.preventDefault();
      showToast('Recuperación de contraseña disponible próximamente', 'info');
    });

    // Si URL tiene ?tab=register, abrir pestaña de registro
    if (new URLSearchParams(location.search).get('tab') === 'register') {
      switchTab('register');
    }

    bindPasswordToggles();
    bindLoginForm();
    bindRegisterForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
