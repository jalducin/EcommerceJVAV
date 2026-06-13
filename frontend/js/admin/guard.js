/**
 * Guard de admin: exige sesión con rol admin; si no, redirige a login.
 * Devuelve una promesa que resuelve con el usuario admin.
 */
async function requireAdmin() {
  if (!Auth.isAuthenticated()) {
    window.location.href = '/login.html?next=' + encodeURIComponent(location.pathname);
    throw new Error('no auth');
  }
  try {
    const me = await api.get('/auth/me');
    if (me.role !== 'admin') {
      showToast('Acceso solo para administradores', 'error');
      setTimeout(() => (window.location.href = '/'), 1500);
      throw new Error('no admin');
    }
    const nameEl = document.getElementById('admin-name');
    if (nameEl) nameEl.textContent = me.full_name || me.email;
    return me;
  } catch (err) {
    if (err.status === 401) window.location.href = '/login.html';
    throw err;
  }
}

// Logout en páginas admin
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('admin-logout')?.addEventListener('click', () => {
    Auth.clearTokens();
    window.location.href = '/login.html';
  });
});

window.requireAdmin = requireAdmin;
