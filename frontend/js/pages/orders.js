/**
 * MetalShop — Historial de Pedidos
 * Requiere autenticación. Carga órdenes, filtros por estado, detalle expandible.
 */

(function OrdersPage() {
  'use strict';

  const STATUS_STEPS = [
    { key: 'pending',   icon: 'clock',         label: 'Confirmado' },
    { key: 'shipped',   icon: 'package',        label: 'Preparando' },
    { key: 'shipped',   icon: 'truck',          label: 'Enviado' },
    { key: 'delivered', icon: 'check-circle-2', label: 'Entregado' },
  ];

  const STATUS_ORDER = ['pending', 'shipped', 'delivered'];

  let _allOrders  = [];
  let _activeFilter = 'all';
  let _detailCache  = {};

  // ── Inicializar ──────────────────────────────────────────────────────────────
  async function init() {
    if (!requireAuth('/login.html')) return;
    await loadOrders();
    bindFilters();
  }

  // ── Cargar órdenes ───────────────────────────────────────────────────────────
  async function loadOrders() {
    const $loading = document.getElementById('orders-loading');
    const $list    = document.getElementById('orders-list');
    const $empty   = document.getElementById('orders-empty');

    try {
      _allOrders = await api.get('/orders');
    } catch (err) {
      showToast(err.message || 'Error al cargar pedidos', 'error');
      _allOrders = [];
    }

    $loading?.classList.add('hidden');

    if (!_allOrders.length) {
      $empty?.classList.remove('hidden');
      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$empty] });
      return;
    }

    $list?.classList.remove('hidden');
    renderOrders(_allOrders);
  }

  // ── Render lista ─────────────────────────────────────────────────────────────
  function renderOrders(orders) {
    const $list = document.getElementById('orders-list');
    if (!$list) return;

    const filtered = _activeFilter === 'all'
      ? orders
      : orders.filter((o) => o.status === _activeFilter);

    if (!filtered.length) {
      $list.innerHTML = `
        <div style="text-align:center;padding:var(--space-12);color:var(--text-muted)">
          <i data-lucide="filter-x" width="40" height="40" style="margin:0 auto var(--space-4);opacity:0.4;display:block"></i>
          <p>No hay pedidos con ese estado.</p>
        </div>`;
      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$list] });
      return;
    }

    $list.innerHTML = filtered.map(buildOrderCard).join('');
    if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$list] });

    // Bind expand/collapse
    $list.querySelectorAll('.order-header').forEach((header) => {
      header.addEventListener('click', () => toggleOrderDetail(header.dataset.orderId));
    });
  }

  function buildOrderCard(order) {
    const statusClass = `status-${order.status}`;
    const statusLabel = getStatusLabel(order.status);
    const addr = order.shipping_address || {};

    return `
      <div class="order-card" id="order-card-${order.id}" data-status="${order.status}">
        <div class="order-header" data-order-id="${order.id}"
             role="button" tabindex="0" aria-expanded="false"
             aria-controls="order-detail-${order.id}"
             aria-label="Pedido #${String(order.id).padStart(4,'0')}">
          <div class="order-header-left">
            <span class="order-number">#${String(order.id).padStart(4, '0')}</span>
            <span class="order-date">
              <i data-lucide="calendar" width="12" height="12" style="display:inline;vertical-align:middle;margin-right:4px"></i>
              ${formatDate(order.created_at)}
            </span>
          </div>
          <div class="order-header-right">
            <span class="status-badge ${statusClass}">
              <span class="dot"></span>
              ${statusLabel}
            </span>
            <span class="order-total">${formatPrice(order.total)}</span>
            <span class="order-chevron">
              <i data-lucide="chevron-down" width="18" height="18"></i>
            </span>
          </div>
        </div>

        <div class="order-detail" id="order-detail-${order.id}" aria-hidden="true">
          <div class="order-detail-inner" id="order-detail-inner-${order.id}">
            <div style="text-align:center;padding:var(--space-4);color:var(--text-muted);font-size:var(--text-sm)">
              <span class="spinner" style="display:inline-block;width:16px;height:16px;border:2px solid rgba(255,255,255,0.2);border-top-color:var(--gold);border-radius:50%;animation:spin 0.6s linear infinite"></span>
              Cargando detalle...
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // ── Toggle detalle ────────────────────────────────────────────────────────────
  async function toggleOrderDetail(orderId) {
    const $card   = document.getElementById(`order-card-${orderId}`);
    const $detail = document.getElementById(`order-detail-${orderId}`);
    const $header = $card?.querySelector('.order-header');
    if (!$card || !$detail) return;

    const isExpanded = $card.classList.toggle('expanded');
    $header?.setAttribute('aria-expanded', String(isExpanded));
    $detail.setAttribute('aria-hidden', String(!isExpanded));

    if (!isExpanded) return;

    // Cargar detalle si no está en caché
    if (!_detailCache[orderId]) {
      try {
        _detailCache[orderId] = await api.get(`/orders/${orderId}`);
      } catch {
        document.getElementById(`order-detail-inner-${orderId}`).innerHTML =
          `<p style="color:var(--text-error);font-size:var(--text-sm)">Error al cargar el detalle.</p>`;
        return;
      }
    }

    renderOrderDetail(orderId, _detailCache[orderId]);
  }

  function renderOrderDetail(orderId, order) {
    const $inner = document.getElementById(`order-detail-inner-${orderId}`);
    if (!$inner) return;

    const statusIdx  = STATUS_ORDER.indexOf(order.status);
    const addr = order.shipping_address || {};

    const timelineHtml = STATUS_STEPS.map((step, i) => {
      const stepStatusIdx = STATUS_ORDER.indexOf(step.key);
      const isDone = stepStatusIdx <= statusIdx;
      return `
        <div class="timeline-step ${isDone ? 'done' : ''}">
          <div class="timeline-dot">
            <i data-lucide="${step.icon}" width="14" height="14"></i>
          </div>
          <span class="timeline-label">${step.label}</span>
        </div>
      `;
    }).join('');

    const itemsHtml = (order.items || []).map((item) => `
      <div class="order-item-row">
        <div class="order-item-img" style="display:flex;align-items:center;justify-content:center;background:var(--bg-surface)">
          <i data-lucide="package" width="20" height="20" style="color:var(--text-muted)"></i>
        </div>
        <div class="order-item-name">
          Producto #${item.product_id}
          <div class="order-item-qty">Cantidad: ${item.quantity}</div>
        </div>
        <span class="order-item-price">${formatPrice(item.unit_price * item.quantity)}</span>
      </div>
    `).join('');

    $inner.innerHTML = `
      <!-- Timeline de estado -->
      <div style="margin-bottom:var(--space-6)">
        <div class="orders-items-title" style="font-size:var(--text-xs);text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:var(--space-4)">
          Estado del envío
        </div>
        <div class="status-timeline">${timelineHtml}</div>
      </div>

      <!-- Ítems -->
      ${order.items?.length ? `
        <div>
          <div class="orders-items-title" style="font-size:var(--text-xs);text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:var(--space-3)">
            Productos (${order.items.length})
          </div>
          ${itemsHtml}
          <div style="display:flex;justify-content:flex-end;padding-top:var(--space-3);border-top:var(--border-metal);margin-top:var(--space-2)">
            <span style="font-family:var(--font-title);font-size:var(--text-xl);font-weight:700">
              Total: <span style="background:var(--gradient-gold);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">${formatPrice(order.total)}</span>
            </span>
          </div>
        </div>
      ` : ''}

      <!-- Dirección -->
      ${addr.street ? `
        <div class="order-address-box">
          <i data-lucide="map-pin" width="16" height="16"></i>
          <div>
            <div style="font-weight:500;color:var(--text-primary);margin-bottom:var(--space-1)">${addr.full_name || ''}</div>
            <div>${addr.street}, ${addr.city}</div>
            <div>${addr.state} ${addr.postal_code}, ${addr.country || 'México'}</div>
            ${addr.phone ? `<div style="margin-top:var(--space-1)">${addr.phone}</div>` : ''}
          </div>
        </div>
      ` : ''}
    `;

    if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$inner] });
  }

  // ── Filtros por estado ────────────────────────────────────────────────────────
  function bindFilters() {
    document.getElementById('status-filters')?.addEventListener('click', (e) => {
      const btn = e.target.closest('.filter-tab');
      if (!btn) return;

      document.querySelectorAll('.filter-tab').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');

      _activeFilter = btn.dataset.status || 'all';
      renderOrders(_allOrders);
    });
  }

  // ── Helpers ───────────────────────────────────────────────────────────────────
  function getStatusLabel(status) {
    const map = {
      pending:   'Pendiente',
      shipped:   'Enviado',
      delivered: 'Entregado',
      cancelled: 'Cancelado',
    };
    return map[status] || status;
  }

  // ── Arrancar ─────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
