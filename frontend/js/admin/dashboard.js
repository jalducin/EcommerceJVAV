/**
 * MetalShop — Admin Dashboard
 * Carga métricas, gráfica CSS de ventas, pedidos recientes.
 */

(function AdminDashboard() {
  'use strict';

  document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAdmin()) return;

    // Mostrar nombre del admin
    const user = Auth.getUser();
    const $name = document.getElementById('admin-name');
    if ($name && user) $name.textContent = user.full_name?.split(' ')[0] || user.email;

    // Fecha actual
    const $date = document.getElementById('topbar-date');
    if ($date) $date.textContent = new Date().toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long' });

    // Logout
    document.getElementById('admin-logout')?.addEventListener('click', () => {
      Auth.clearTokens();
      window.location.href = '/login.html';
    });

    // Sidebar mobile toggle
    const $sidebar = document.getElementById('admin-sidebar');
    document.getElementById('sidebar-toggle')?.addEventListener('click', () => {
      $sidebar?.classList.toggle('open');
    });

    await loadDashboard();
  });

  async function loadDashboard() {
    try {
      const [stats, ordersData] = await Promise.all([
        api.get('/admin/dashboard'),
        api.get('/admin/orders', { limit: 5, offset: 0 }),
      ]);

      renderMetrics(stats);
      renderChart(stats.sales_last_7_days);
      renderRecentOrders(ordersData.items);

      // Badge pedidos pendientes en sidebar
      const $badge = document.getElementById('pending-count');
      if ($badge && stats.orders_pending > 0) {
        $badge.textContent = stats.orders_pending;
        $badge.style.display = 'inline-block';
      }

      document.getElementById('dash-loading')?.classList.add('hidden');
      document.getElementById('dash-content')?.classList.remove('hidden');
      lucide.createIcons();
    } catch (err) {
      showToast(err.message || 'Error al cargar el dashboard', 'error');
    }
  }

  // ── Métricas ─────────────────────────────────────────────────────────────────
  function renderMetrics(s) {
    setText('m-sales',       formatPrice(s.sales_today));
    setText('m-orders-today', `${s.orders_today} orden${s.orders_today !== 1 ? 'es' : ''}`);
    setText('m-pending',     s.orders_pending);
    setText('m-low-stock',   s.products_low_stock);
    setText('m-out-stock',   `${s.products_out_stock} agotado${s.products_out_stock !== 1 ? 's' : ''}`);
    setText('m-products',    s.total_products);
    setText('m-users',       `${s.total_users} cliente${s.total_users !== 1 ? 's' : ''}`);
  }

  // ── Gráfica de barras CSS ─────────────────────────────────────────────────────
  function renderChart(days) {
    const $chart = document.getElementById('sales-chart');
    const $total = document.getElementById('chart-total');
    if (!$chart) return;

    const maxVal = Math.max(...days.map((d) => d.total), 1);
    const weekTotal = days.reduce((s, d) => s + d.total, 0);
    if ($total) $total.textContent = formatPrice(weekTotal);

    $chart.innerHTML = days.map((d) => {
      const pct = Math.max((d.total / maxVal) * 100, d.total > 0 ? 8 : 2);
      return `
        <div class="bar-col">
          <div class="bar-wrap">
            <div class="bar-fill"
                 style="height:${pct}%"
                 data-value="${formatPrice(d.total)}"
                 title="${d.date}: ${formatPrice(d.total)}"
                 role="img"
                 aria-label="${d.date}: ${formatPrice(d.total)}">
            </div>
          </div>
          <div class="bar-label">${d.date}</div>
        </div>
      `;
    }).join('');
  }

  // ── Pedidos recientes ─────────────────────────────────────────────────────────
  function renderRecentOrders(orders) {
    const $tbody = document.getElementById('recent-orders-tbody');
    if (!$tbody) return;

    if (!orders.length) {
      $tbody.innerHTML = `<tr><td colspan="5" class="table-empty"><p>Sin pedidos aún.</p></td></tr>`;
      return;
    }

    $tbody.innerHTML = orders.map((o) => `
      <tr>
        <td class="td-id">#${String(o.id).padStart(4, '0')}</td>
        <td class="td-primary">${o.user_email || `Usuario #${o.user_id}`}</td>
        <td class="td-price">${formatPrice(o.total)}</td>
        <td><span class="status-badge status-${o.status}">${getStatusLabel(o.status)}</span></td>
        <td>${formatDate(o.created_at)}</td>
      </tr>
    `).join('');
  }

  // ── Helpers ───────────────────────────────────────────────────────────────────
  function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  function getStatusLabel(s) {
    return { pending: 'Pendiente', shipped: 'Enviado', delivered: 'Entregado', cancelled: 'Cancelado' }[s] || s;
  }

})();
