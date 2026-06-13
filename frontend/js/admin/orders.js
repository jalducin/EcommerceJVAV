/**
 * Admin — Pedidos unificados (storefront + canales) sobre /api/admin/orders.
 * Permite cambiar el estado de pedidos de canal.
 */
(function AdminOrders() {
  'use strict';

  const $tbody = document.getElementById('orders-tbody');
  const $count = document.getElementById('orders-count');
  const $search = document.getElementById('order-search');
  const $statusTabs = document.getElementById('status-tabs');

  let orders = [];
  let statusFilter = '';

  const STATUSES = ['pending', 'paid', 'shipped', 'delivered', 'cancelled'];

  async function load() {
    $tbody.innerHTML = `<tr><td colspan="6">Cargando…</td></tr>`;
    try {
      orders = await api.get('/admin/orders');
      render();
    } catch (err) {
      $tbody.innerHTML = `<tr><td colspan="6">Error: ${err.message}</td></tr>`;
    }
  }

  function render() {
    let list = orders;
    if (statusFilter) list = list.filter((o) => o.status === statusFilter);
    const q = ($search?.value || '').toLowerCase();
    if (q) list = list.filter((o) => String(o.id).toLowerCase().includes(q) || o.channel.toLowerCase().includes(q));

    if ($count) $count.textContent = `${list.length} pedido(s)`;
    if (!list.length) { $tbody.innerHTML = `<tr><td colspan="6">Sin pedidos</td></tr>`; return; }

    $tbody.innerHTML = list.map((o) => `
      <tr>
        <td><code>${String(o.id).slice(0, 10)}</code></td>
        <td><span class="badge">${o.channel}</span> <small>${o.source}</small></td>
        <td>${o.status}</td>
        <td>${formatPrice(o.total)} ${o.currency}</td>
        <td>
          ${o.source === 'channel'
            ? `<select data-id="${o.id}" class="status-select">
                 ${STATUSES.map((s) => `<option value="${s}" ${s === o.status ? 'selected' : ''}>${s}</option>`).join('')}
               </select>`
            : '<small>—</small>'}
        </td>
      </tr>`).join('');

    $tbody.querySelectorAll('.status-select').forEach((sel) =>
      sel.addEventListener('change', () => changeStatus(sel.dataset.id, sel.value)));
  }

  async function changeStatus(canonicalId, newStatus) {
    try {
      await api.patch(`/admin/orders/channel/${canonicalId}/status?new_status=${encodeURIComponent(newStatus)}`, {});
      showToast('Estado actualizado', 'success');
      load();
    } catch (err) { showToast(err.message, 'error'); }
  }

  function buildTabs() {
    if (!$statusTabs) return;
    const tabs = ['', ...STATUSES];
    $statusTabs.innerHTML = tabs.map((s) =>
      `<button class="status-tab${s === statusFilter ? ' active' : ''}" data-status="${s}">${s || 'Todos'}</button>`).join('');
    $statusTabs.querySelectorAll('[data-status]').forEach((b) =>
      b.addEventListener('click', () => { statusFilter = b.dataset.status; buildTabs(); render(); }));
  }

  async function init() {
    await requireAdmin();
    buildTabs();
    await load();
    $search?.addEventListener('input', render);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
