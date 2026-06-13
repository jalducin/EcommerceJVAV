/**
 * Admin — Dashboard (métricas serverless): ventas, pendientes, stock bajo, conectores.
 */
(function AdminDashboard() {
  'use strict';

  const $metrics = document.getElementById('metrics-grid');
  const $pendingBadge = document.getElementById('pending-orders-badge');

  function card(icon, label, value, extra = '') {
    return `
      <div class="metric-card">
        <div class="metric-icon"><i data-lucide="${icon}" width="20" height="20"></i></div>
        <div class="metric-body">
          <div class="metric-value">${value}</div>
          <div class="metric-label">${label}</div>
          ${extra ? `<div class="metric-extra">${extra}</div>` : ''}
        </div>
      </div>`;
  }

  async function init() {
    await requireAdmin();
    $metrics.innerHTML = '<p>Cargando métricas…</p>';
    try {
      const d = await api.get('/admin/dashboard');
      const c = d.connectors || {};
      $metrics.innerHTML = [
        card('dollar-sign', 'Ventas totales', formatPrice(d.sales_total || 0)),
        card('shopping-bag', 'Pedidos', d.orders_count || 0, `${d.pending_orders || 0} pendientes`),
        card('alert-triangle', 'Stock bajo', d.low_stock_count || 0,
          (d.low_stock || []).slice(0, 5).map((p) => `${p.name} (${p.stock})`).join(', ')),
        card('plug', 'Conectores', `${c.available || 0}/${c.total || 0}`, `${c.deferred || 0} en deuda técnica`),
      ].join('');
      if ($pendingBadge) $pendingBadge.textContent = d.pending_orders || 0;
      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$metrics] });
    } catch (err) {
      $metrics.innerHTML = `<p>Error al cargar el dashboard: ${err.message}</p>`;
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
