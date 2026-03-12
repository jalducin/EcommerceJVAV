/**
 * MetalShop — Auth UI
 * Gestiona el estado de autenticación en la navbar y las páginas.
 */

(function AuthUI() {
  'use strict';

  // ── Renderizar botones de auth en la navbar ──────────────────────────────────
  function renderAuthNav() {
    const $authNav = document.getElementById('auth-nav');
    if (!$authNav) return;

    const user = Auth.getUser();

    if (user) {
      $authNav.innerHTML = `
        <div style="display:flex;align-items:center;gap:var(--space-2)">
          <span style="font-size:var(--text-sm);color:var(--text-secondary);display:none;" id="user-name-nav">
            ${user.full_name?.split(' ')[0] || user.email}
          </span>
          <button class="nav-btn" id="user-menu-btn" aria-label="Menú de usuario" aria-expanded="false">
            <i data-lucide="user-circle" width="20" height="20"></i>
          </button>
          <div id="user-dropdown" style="
            display:none;
            position:absolute;
            top:calc(var(--nav-height) + 4px);
            right:var(--space-4);
            background:var(--bg-modal);
            border:var(--border-gold);
            border-radius:var(--border-radius-lg);
            box-shadow:var(--shadow-card);
            min-width:180px;
            z-index:var(--z-modal);
            overflow:hidden;
          ">
            <div style="padding:var(--space-3) var(--space-4);border-bottom:var(--border-metal)">
              <div style="font-size:var(--text-sm);font-weight:600;color:var(--text-primary)">${user.full_name}</div>
              <div style="font-size:var(--text-xs);color:var(--text-muted)">${user.email}</div>
            </div>
            <a href="/orders.html" style="display:flex;align-items:center;gap:var(--space-2);padding:var(--space-3) var(--space-4);color:var(--text-secondary);font-size:var(--text-sm);transition:background var(--transition-fast)"
               onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">
              <i data-lucide="package" width="14" height="14"></i> Mis Pedidos
            </a>
            ${user.role === 'admin' ? `
              <a href="/admin/dashboard.html" style="display:flex;align-items:center;gap:var(--space-2);padding:var(--space-3) var(--space-4);color:var(--text-gold);font-size:var(--text-sm);transition:background var(--transition-fast)"
                 onmouseover="this.style.background='rgba(212,175,55,0.05)'" onmouseout="this.style.background='transparent'">
                <i data-lucide="layout-dashboard" width="14" height="14"></i> Panel Admin
              </a>
            ` : ''}
            <button id="logout-btn" style="display:flex;align-items:center;gap:var(--space-2);padding:var(--space-3) var(--space-4);color:var(--text-error);font-size:var(--text-sm);width:100%;transition:background var(--transition-fast);background:none;border:none;cursor:pointer;border-top:var(--border-metal)"
                    onmouseover="this.style.background='rgba(252,129,129,0.05)'" onmouseout="this.style.background='transparent'">
              <i data-lucide="log-out" width="14" height="14"></i> Cerrar sesión
            </button>
          </div>
        </div>
      `;

      // Mostrar nombre en desktop
      const $name = document.getElementById('user-name-nav');
      if ($name && window.innerWidth >= 768) $name.style.display = 'inline';

      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$authNav] });

      // Toggle dropdown
      document.getElementById('user-menu-btn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        const $dd = document.getElementById('user-dropdown');
        const btn = document.getElementById('user-menu-btn');
        const isOpen = $dd.style.display !== 'none';
        $dd.style.display = isOpen ? 'none' : 'block';
        btn?.setAttribute('aria-expanded', String(!isOpen));
      });

      document.addEventListener('click', () => {
        const $dd = document.getElementById('user-dropdown');
        if ($dd) $dd.style.display = 'none';
      });

      document.getElementById('logout-btn')?.addEventListener('click', logout);

    } else {
      $authNav.innerHTML = `
        <a href="/login.html" class="nav-btn nav-btn-primary" aria-label="Iniciar sesión">
          <i data-lucide="log-in" width="16" height="16"></i>
          Acceder
        </a>
      `;
      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$authNav] });
    }
  }

  // ── Logout ────────────────────────────────────────────────────────────────────
  async function logout() {
    Auth.clearTokens();
    if (typeof window.Cart !== 'undefined') window.Cart.clear();
    window.location.href = '/';
  }

  // ── Fetch perfil del usuario si hay token pero no datos guardados ─────────────
  async function hydrateUser() {
    if (!Auth.isAuthenticated()) return;
    if (Auth.getUser()) return;

    try {
      const user = await api.get('/auth/me');
      Auth.setUser(user);
    } catch {
      // Token inválido, limpiar
      Auth.clearTokens();
    }
  }

  // ── Guards de página ──────────────────────────────────────────────────────────
  window.requireAuth = function (redirectTo = '/login.html') {
    if (!Auth.isAuthenticated()) {
      window.location.href = `${redirectTo}?next=${encodeURIComponent(location.pathname)}`;
      return false;
    }
    return true;
  };

  window.requireAdmin = function () {
    if (!Auth.isAuthenticated()) {
      window.location.href = '/login.html';
      return false;
    }
    const user = Auth.getUser();
    if (!user || user.role !== 'admin') {
      window.location.href = '/';
      return false;
    }
    return true;
  };

  // ── Init ──────────────────────────────────────────────────────────────────────
  async function init() {
    await hydrateUser();
    renderAuthNav();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
