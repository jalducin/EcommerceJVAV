/**
 * MetalShop — Página de Recuperación de Contraseña
 * Maneja el formulario para solicitar un enlace de restablecimiento.
 */

(function ForgotPasswordPage() {
  'use strict';

  // Si ya está autenticado → redirigir
  if (Auth.isAuthenticated()) {
    window.location.href = '/';
    return;
  }

  // ── Helpers ───────────────────────────────────────────────────────────────────
  function showError(message) {
    const $err = document.getElementById('forgot-error');
    const $msg = document.getElementById('forgot-error-msg');
    if ($err && $msg) {
      $msg.textContent = message;
      $err.classList.add('show');
      $err.style.display = 'flex'; // Asegurar que se muestre
    }
    document.getElementById('forgot-success')?.classList.remove('show');
    document.getElementById('forgot-success').style.display = 'none';
  }

  function showSuccess(message) {
    const $succ = document.getElementById('forgot-success');
    const $msg = document.getElementById('forgot-success-msg');
    if ($succ && $msg) {
      $msg.textContent = message;
      $succ.classList.add('show');
      $succ.style.display = 'flex'; // Asegurar que se muestre
    }
    document.getElementById('forgot-error')?.classList.remove('show');
    document.getElementById('forgot-error').style.display = 'none';
  }

  function hideMessages() {
    document.getElementById('forgot-error')?.classList.remove('show');
    document.getElementById('forgot-error').style.display = 'none';
    document.getElementById('forgot-success')?.classList.remove('show');
    document.getElementById('forgot-success').style.display = 'none';
  }

  function setLoading(btnId, loading, label) {
    const $btn = document.getElementById(btnId);
    if (!$btn) return;
    $btn.disabled = loading;
    $btn.innerHTML = loading
      ? `<span class="spinner"></span> Enviando...`
      : label;
    if (!loading && typeof lucide !== 'undefined') lucide.createIcons({ elements: [$btn] });
  }

  // ── Formulario ────────────────────────────────────────────────────────────────
  function bindForm() {
    const $form = document.getElementById('forgot-password-form');
    if (!$form) return;

    $form.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideMessages();

      const email = document.getElementById('email')?.value.trim();
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showError('Por favor, ingresa un email válido.');
        return;
      }

      setLoading('forgot-btn', true);
      try {
        // TODO: Implementar el endpoint POST /api/auth/forgot-password en el backend
        // Por ahora, simulamos una respuesta exitosa.
        // await api.post('/auth/forgot-password', { email });
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simular carga
        showSuccess('Si tu email está registrado, recibirás un enlace de recuperación en breve.');
      } catch (err) {
        showError(err.message || 'Ocurrió un error al procesar tu solicitud.');
      } finally {
        setLoading('forgot-btn', false, `<i data-lucide="mail" width="18" height="18"></i> Enviar Enlace`);
      }
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────────
  function init() {
    bindForm();
    // Ocultar mensajes al cargar la página
    hideMessages();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();