/**
 * MetalShop — Admin: Gestión de Pedidos
 * Listado, filtrado, cambio de estado y detalle de órdenes.
 */

(function AdminOrders() {
  'use strict';

  const PAGE_SIZE = 20;
  
  let _page = 0;
  let _currentStatus = '';
  let _orders = [];
  let _abortController = null;

  // ── Init ──────────────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAdmin()) return;

    // Init User Info
    const user = Auth.getUser();
    const $name = document.getElementById('admin-name');
    if ($name && user) $name.textContent = user.full_name?.split(' ')[0] || user.email;

    // Sidebar & Logout
    document.getElementById('admin-logout')?.addEventListener('click', () => {
      Auth.clearTokens(); window.location.href = '/login.html';
    });
    document.getElementById('sidebar-toggle')?.addEventListener('click', () => {
      document.getElementById('admin-sidebar')?.classList.toggle('open');
    });

    bindFilters();
    bindModalEvents();
    
    // Initial load
    await loadOrders();
  });

  // ── Load Orders ───────────────────────────────────────────────────────────────
  async function loadOrders() {
    const $tbody = document.getElementById('orders-tbody');
    if (!$tbody) return;

    // Cancelar petición anterior si existe (evita race conditions en búsqueda/filtros)
    if (_abortController) _abortController.abort();
    _abortController = new AbortController();

    // Mostrar loading solo si es la primera carga o cambio drástico
    $tbody.style.opacity = '0.5';
    
    try {
      const params = {
        limit: PAGE_SIZE,
        offset: _page * PAGE_SIZE
      };
      if (_currentStatus) params.status = _currentStatus;

      // Nota: Búsqueda por texto no implementada en backend aún, se omite.

      const data = await api.get('/admin/orders', params);
      
      _orders = data.items || [];
      const total = data.total || 0;

      updateCount(total);
      renderTable(_orders);
      renderPagination(total);

    } catch (err) {
      if (err.name === 'AbortError') return;
      console.error(err);
      $tbody.innerHTML = `<tr><td colspan="7" class="table-empty" style="color:var(--text-error)"><p>Error: ${err.message}</p></td></tr>`;
    } finally {
      $tbody.style.opacity = '1';
    }
  }

  function updateCount(total) {
    const $count = document.getElementById('orders-count');
    if ($count) $count.textContent = `${total} pedido${total !== 1 ? 's' : ''}`;
  }

  // ── Rendering ─────────────────────────────────────────────────────────────────
  function renderTable(orders) {
    const $tbody = document.getElementById('orders-tbody');
    
    if (!orders.length) {
      $tbody.innerHTML = `<tr><td colspan="7" class="table-empty">
        <i data-lucide="inbox" width="32" height="32"></i>
        <p>No se encontraron pedidos</p>
      </td></tr>`;
      lucide.createIcons({ elements: [$tbody] });
      return;
    }

    $tbody.innerHTML = orders.map(order => {
      const date = new Date(order.created_at).toLocaleDateString('es-ES', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute:'2-digit'
      });
      
      const status = order.status;
      const badgeClass = getStatusBadgeColor(status);
      const label = getStatusLabel(status);

      // Selector de estado
      const options = [
        { val: 'pending', label: 'Pendiente' },
        { val: 'shipped', label: 'Enviado' },
        { val: 'delivered', label: 'Entregado' },
        { val: 'cancelled', label: 'Cancelado' }
      ];

      return `
        <tr>
          <td class="td-id">
            <button class="btn-ghost" onclick="AdminOrders.showDetail(${order.id})" style="color:var(--gold);font-weight:700">#${order.id}</button>
          </td>
          <td>
             <div class="td-primary">${order.user_email || 'Cliente'}</div>
          </td>
          <td class="td-price">${formatPrice(order.total)}</td>
          <td>
             <span class="badge badge-${badgeClass}">${label}</span>
          </td>
          <td style="font-size:11px;color:var(--text-muted);text-transform:capitalize">
            ${order.shipping_address ? 'Domicilio' : 'Retiro'}
          </td>
          <td style="font-size:var(--text-xs);color:var(--text-muted)">${date}</td>
          <td>
            <select class="status-select ${status}" onchange="AdminOrders.changeStatus(${order.id}, this.value)">
              ${options.map(o => `<option value="${o.val}" ${status === o.val ? 'selected' : ''}>${o.label}</option>`).join('')}
            </select>
          </td>
        </tr>
      `;
    }).join('');
    
    lucide.createIcons({ elements: [$tbody] });
  }

  function renderPagination(total) {
    const $pag = document.getElementById('orders-pagination');
    if (!$pag) return;

    const pages = Math.ceil(total / PAGE_SIZE);
    const start = _page * PAGE_SIZE + 1;
    const end   = Math.min((_page + 1) * PAGE_SIZE, total);

    $pag.innerHTML = `
      <span class="pagination-info">${total === 0 ? 'Sin resultados' : `Mostrando ${start}–${end} de ${total}`}</span>
      <div class="pagination-btns">
        <button class="page-btn" id="pag-prev" ${_page === 0 ? 'disabled' : ''}><i data-lucide="chevron-left" width="14" height="14"></i></button>
        <span style="font-size:var(--text-sm);color:var(--text-muted);padding:0 var(--space-2)">Pág ${_page + 1} / ${pages || 1}</span>
        <button class="page-btn" id="pag-next" ${_page >= pages - 1 ? 'disabled' : ''}><i data-lucide="chevron-right" width="14" height="14"></i></button>
      </div>
    `;
    lucide.createIcons({ elements: [$pag] });

    document.getElementById('pag-prev')?.addEventListener('click', () => { _page--; loadOrders(); });
    document.getElementById('pag-next')?.addEventListener('click', () => { _page++; loadOrders(); });
  }

  // ── Filters ──────────────────────────────────────────────────────────────────
  function bindFilters() {
    const tabs = document.querySelectorAll('.filter-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        _currentStatus = tab.dataset.status;
        _page = 0;
        loadOrders();
      });
    });

    // Search listener (visual feedback only for now as API support is pending)
    const searchInput = document.getElementById('order-search');
    if (searchInput) {
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') showToast('Búsqueda por servidor no implementada', 'info');
      });
    }
  }

  // ── Actions ──────────────────────────────────────────────────────────────────
  window.AdminOrders = {
    changeStatus: async (id, newStatus) => {
      try {
        await api.patch(`/admin/orders/${id}/status`, { status: newStatus });
        showToast(`Estado actualizado`, 'success');
        loadOrders(); // Refresh to update badges/filters
      } catch (err) {
        showToast(err.message || 'Error al actualizar', 'error');
        loadOrders(); // Revert UI
      }
    },
    showDetail: async (id) => {
      const order = _orders.find(o => o.id === id);
      // En una implementación completa aquí podríamos hacer fetch al endpoint de detalle
      // GET /api/orders/{id} para ver los ítems. Por ahora mostramos JSON raw o básico.
      const $body = document.getElementById('order-detail-body');
      $body.innerHTML = `<pre style="font-size:11px;overflow:auto">${JSON.stringify(order, null, 2)}</pre>`;
      document.getElementById('order-detail-modal')?.classList.add('open');
    }
  };

  function bindModalEvents() {
    document.getElementById('close-order-modal')?.addEventListener('click', () => {
      document.getElementById('order-detail-modal')?.classList.remove('open');
    });
  }

  // ── Helpers ──────────────────────────────────────────────────────────────────
  function getStatusLabel(s) { const map = { pending: 'Pendiente', shipped: 'Enviado', delivered: 'Entregado', cancelled: 'Cancelado' }; return map[s] || s; }
  function getStatusBadgeColor(s) { if (s === 'delivered') return 'success'; if (s === 'cancelled') return 'error'; if (s === 'pending') return 'gold'; return 'steel'; }
})();