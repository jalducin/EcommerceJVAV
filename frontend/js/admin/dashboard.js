/**
 * MetalShop — Admin: Dashboard
 * Carga de métricas y gráfica de ventas.
 */

(function AdminDashboard() {
  'use strict';

  // ── Init ──────────────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', async () => {
    // Guard de ruta: solo accesible con rol 'admin'
    if (!requireAdmin()) {
      // Ocultar contenido para evitar flash of unstyled/unauthorized content
      document.body.style.display = 'none';
      return;
    }

    // Inicializar iconos de Lucide
    lucide.createIcons();

    // Init User Info
    const user = Auth.getUser();
    const $name = document.getElementById('admin-name');
    if ($name && user) $name.textContent = user.full_name?.split(' ')[0] || user.email;

    // Sidebar & Logout
    document.getElementById('admin-logout')?.addEventListener('click', () => {
      Auth.clearTokens();
      window.location.href = '/login.html';
    });
    document.getElementById('sidebar-toggle')?.addEventListener('click', () => {
      document.getElementById('admin-sidebar')?.classList.toggle('open');
    });

    // Carga de datos
    await loadDashboardData();
  });

  // ── Load Data ─────────────────────────────────────────────────────────────────
  async function loadDashboardData() {
    try {
      const data = await api.get('/admin/dashboard');
      renderMetrics(data);
      renderSalesChart(data.sales_last_7_days);
      updatePendingOrdersBadge(data.orders_pending);
    } catch (err) {
      console.error('Error al cargar datos del dashboard:', err);
      showToast(err.message || 'No se pudieron cargar las métricas', 'error');
    }
  }

  // ── Rendering ─────────────────────────────────────────────────────────────────

  function renderMetrics(data) {
    const metrics = [
      {
        label: 'Ventas de Hoy',
        value: formatPrice(data.sales_today),
        icon: 'dollar-sign',
        color: 'gold',
        sub: `${data.orders_today} pedido(s) hoy`,
      },
      {
        label: 'Pedidos Pendientes',
        value: data.orders_pending,
        icon: 'package',
        color: 'silver',
        sub: 'Listos para procesar',
      },
      {
        label: 'Productos con Bajo Stock',
        value: data.products_low_stock,
        icon: 'battery-warning',
        color: 'copper',
        sub: 'Menos de 5 unidades',
      },
      {
        label: 'Productos Agotados',
        value: data.products_out_stock,
        icon: 'battery-dead',
        color: 'red',
        sub: 'Sin unidades disponibles',
      },
    ];

    const $grid = document.getElementById('metrics-grid');
    if (!$grid) return;

    $grid.innerHTML = metrics.map(metric => `
      <div class="metric-card ${metric.color}">
        <div class="metric-icon ${metric.color}">
          <i data-lucide="${metric.icon}" width="20" height="20"></i>
        </div>
        <div class="metric-value">${metric.value}</div>
        <div class="metric-label">${metric.label}</div>
        <p class="metric-sub">${metric.sub}</p>
      </div>
    `).join('');

    lucide.createIcons({ elements: [$grid] });
  }

  function renderSalesChart(salesData) {
    const $chart = document.getElementById('sales-chart');
    if (!$chart) return;

    const maxSale = Math.max(...salesData.map(d => d.total), 1); // Evitar división por cero

    $chart.innerHTML = salesData.map(day => {
      const heightPercent = (day.total / maxSale) * 100;
      return `
        <div class="bar-col">
          <div class="bar-wrap">
            <div class="bar-fill"
                 style="height: ${heightPercent}%;"
                 data-value="${formatPrice(day.total)}">
            </div>
          </div>
          <div class="bar-label">${day.date}</div>
        </div>
      `;
    }).join('');
  }

  function updatePendingOrdersBadge(count) {
    const $badge = document.getElementById('pending-orders-badge');
    if (!$badge) return;
    if (count > 0) {
      $badge.textContent = count;
      $badge.style.display = 'inline-block';
    } else {
      $badge.style.display = 'none';
    }
  }

})();