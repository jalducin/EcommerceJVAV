/**
 * MetalShop — API Client
 * Fetch wrapper con autenticación JWT, refresh automático y manejo de errores.
 */

const API_BASE = '/api';

// ── Storage helpers ──────────────────────────────────────────────────────────

const Auth = {
  getAccessToken:  () => localStorage.getItem('access_token'),
  getRefreshToken: () => localStorage.getItem('refresh_token'),
  setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
  },
  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
  getUser() {
    const raw = localStorage.getItem('user');
    try { return raw ? JSON.parse(raw) : null; } catch { return null; }
  },
  setUser(user) { localStorage.setItem('user', JSON.stringify(user)); },
  isAuthenticated() { return !!Auth.getAccessToken(); },
};

// ── Token refresh ────────────────────────────────────────────────────────────

let _refreshPromise = null;

async function refreshTokens() {
  if (_refreshPromise) return _refreshPromise;

  _refreshPromise = (async () => {
    const refreshToken = Auth.getRefreshToken();
    if (!refreshToken) throw new Error('No refresh token');

    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) {
      Auth.clearTokens();
      window.location.href = '/login.html';
      throw new Error('Sesión expirada');
    }

    const data = await res.json();
    Auth.setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  })().finally(() => { _refreshPromise = null; });

  return _refreshPromise;
}

// ── Core request ─────────────────────────────────────────────────────────────

async function request(path, options = {}, retry = true) {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;

  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = Auth.getAccessToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });

  // Token expirado — intentar refresh una sola vez
  if (res.status === 401 && retry && Auth.getRefreshToken()) {
    try {
      await refreshTokens();
      return request(path, options, false);
    } catch {
      return res;
    }
  }

  return res;
}

// ── HTTP helpers ─────────────────────────────────────────────────────────────

async function parseResponse(res) {
  const contentType = res.headers.get('Content-Type') || '';
  const isJson = contentType.includes('application/json');

  if (res.ok) {
    if (res.status === 204) return null;
    return isJson ? res.json() : res.text();
  }

  let errorDetail = `Error ${res.status}`;
  if (isJson) {
    try {
      const err = await res.json();
      errorDetail = err.detail || err.message || errorDetail;
    } catch { /* ignore */ }
  }
  throw new ApiError(errorDetail, res.status);
}

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

const api = {
  async get(path, params = {}) {
    const query = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== null && v !== undefined && v !== ''))
    ).toString();
    const res = await request(`${path}${query ? '?' + query : ''}`);
    return parseResponse(res);
  },

  async post(path, body) {
    const res = await request(path, { method: 'POST', body: JSON.stringify(body) });
    return parseResponse(res);
  },

  async put(path, body) {
    const res = await request(path, { method: 'PUT', body: JSON.stringify(body) });
    return parseResponse(res);
  },

  async patch(path, body) {
    const res = await request(path, { method: 'PATCH', body: JSON.stringify(body) });
    return parseResponse(res);
  },

  async delete(path) {
    const res = await request(path, { method: 'DELETE' });
    return parseResponse(res);
  },
};

// ── Toast ─────────────────────────────────────────────────────────────────────

function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = { success: 'check-circle', error: 'alert-circle', info: 'info' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <i data-lucide="${icons[type] || 'info'}" width="16" height="16"></i>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [toast] });

  setTimeout(() => {
    toast.style.animation = 'toast-in 0.3s ease reverse forwards';
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }, duration);
}

// ── Format helpers ────────────────────────────────────────────────────────────

function formatPrice(price) {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'USD' }).format(price);
}

function formatDate(dateStr) {
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'long' }).format(new Date(dateStr));
}

// Exponer globalmente
window.api    = api;
window.Auth   = Auth;
window.ApiError = ApiError;
window.showToast  = showToast;
window.formatPrice = formatPrice;
window.formatDate  = formatDate;
