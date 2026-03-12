/**
 * MetalShop — Admin: Gestión de Productos
 * CRUD completo con modal, búsqueda, filtro de estado y paginación.
 */

(function AdminProducts() {
  'use strict';

  const PAGE_SIZE = 15;

  let _allProducts = [];
  let _filtered    = [];
  let _page        = 0;
  let _editingId   = null;
  let _deletingId  = null;

  // ── Init ──────────────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAdmin()) return;

    const user = Auth.getUser();
    const $name = document.getElementById('admin-name');
    if ($name && user) $name.textContent = user.full_name?.split(' ')[0] || user.email;

    document.getElementById('admin-logout')?.addEventListener('click', () => {
      Auth.clearTokens(); window.location.href = '/login.html';
    });
    document.getElementById('sidebar-toggle')?.addEventListener('click', () => {
      document.getElementById('admin-sidebar')?.classList.toggle('open');
    });

    bindModalEvents();
    bindSearchFilter();
    await loadProducts();
  });

  // ── Cargar productos ──────────────────────────────────────────────────────────
  async function loadProducts() {
    try {
      // Cargamos todos los productos (activos e inactivos) para el panel admin
      // Se hace paginando hasta obtenerlos todos (max 1000 según spec)
      const data = await api.get('/products', { limit: 100, offset: 0 });
      _allProducts = data.items || [];
      applyFilter();
    } catch (err) {
      showToast(err.message || 'Error al cargar productos', 'error');
    }
  }

  // ── Filtro y búsqueda ─────────────────────────────────────────────────────────
  function applyFilter() {
    const search = document.getElementById('product-search')?.value.toLowerCase() || '';
    const status = document.getElementById('product-filter-status')?.value;

    _filtered = _allProducts.filter((p) => {
      const matchSearch = !search || p.name.toLowerCase().includes(search);
      const matchStatus = !status
        || (status === 'active'   &&  p.is_active)
        || (status === 'inactive' && !p.is_active);
      return matchSearch && matchStatus;
    });

    _page = 0;
    renderTable();
    renderPagination();
  }

  function bindSearchFilter() {
    let timer;
    document.getElementById('product-search')?.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(applyFilter, 250);
    });
    document.getElementById('product-filter-status')?.addEventListener('change', applyFilter);
  }

  // ── Render tabla ──────────────────────────────────────────────────────────────
  function renderTable() {
    const $tbody = document.getElementById('products-tbody');
    if (!$tbody) return;

    const start = _page * PAGE_SIZE;
    const page  = _filtered.slice(start, start + PAGE_SIZE);

    if (!page.length) {
      $tbody.innerHTML = `<tr><td colspan="7" class="table-empty">
        <i data-lucide="package-search" width="32" height="32"></i>
        <p>No se encontraron productos</p>
      </td></tr>`;
      lucide.createIcons({ elements: [$tbody] });
      return;
    }

    $tbody.innerHTML = page.map((p) => {
      const img = p.images?.[0];
      const stockClass = p.stock === 0 ? 'out' : p.stock < 5 ? 'low' : 'ok';
      const stockLabel = p.stock === 0 ? 'Agotado' : p.stock < 5 ? `${p.stock} bajo` : p.stock;

      return `
        <tr data-id="${p.id}">
          <td class="td-id">#${p.id}</td>
          <td>
            <div style="display:flex;align-items:center;gap:var(--space-3)">
              ${img
                ? `<img src="${img}" alt="${p.name}" class="td-thumb" />`
                : `<div class="td-thumb" style="display:flex;align-items:center;justify-content:center;background:var(--bg-surface)"><i data-lucide="image" width="16" height="16" style="color:var(--text-muted)"></i></div>`
              }
              <span class="td-primary" title="${p.name}">${p.name}</span>
            </div>
          </td>
          <td>${p.category ? `<span class="badge badge-steel">${p.category}</span>` : '<span style="color:var(--text-muted)">—</span>'}</td>
          <td class="td-price">${formatPrice(p.price)}</td>
          <td><span class="stock-pill ${stockClass}">${stockLabel}</span></td>
          <td>
            <span class="badge ${p.is_active ? 'badge-success' : 'badge-steel'}">
              ${p.is_active ? 'Activo' : 'Inactivo'}
            </span>
          </td>
          <td>
            <div class="td-actions">
              <button class="btn btn-ghost btn-sm btn-edit" data-id="${p.id}" aria-label="Editar ${p.name}">
                <i data-lucide="pencil" width="14" height="14"></i>
              </button>
              ${p.is_active ? `
                <button class="btn btn-sm btn-delete" data-id="${p.id}" data-name="${p.name}"
                  style="background:rgba(252,129,129,0.08);color:var(--text-error);border:1px solid rgba(252,129,129,0.2)"
                  aria-label="Desactivar ${p.name}">
                  <i data-lucide="trash-2" width="14" height="14"></i>
                </button>
              ` : `
                <button class="btn btn-sm btn-restore" data-id="${p.id}"
                  style="background:rgba(104,211,145,0.08);color:var(--text-success);border:1px solid rgba(104,211,145,0.2)"
                  aria-label="Reactivar ${p.name}">
                  <i data-lucide="refresh-cw" width="14" height="14"></i>
                </button>
              `}
            </div>
          </td>
        </tr>
      `;
    }).join('');

    lucide.createIcons({ elements: [$tbody] });

    // Bind botones
    $tbody.querySelectorAll('.btn-edit').forEach((btn) =>
      btn.addEventListener('click', () => openEditModal(parseInt(btn.dataset.id)))
    );
    $tbody.querySelectorAll('.btn-delete').forEach((btn) =>
      btn.addEventListener('click', () => openDeleteModal(parseInt(btn.dataset.id), btn.dataset.name))
    );
    $tbody.querySelectorAll('.btn-restore').forEach((btn) =>
      btn.addEventListener('click', () => restoreProduct(parseInt(btn.dataset.id)))
    );
  }

  function renderPagination() {
    const $pag = document.getElementById('products-pagination');
    if (!$pag) return;

    const total = _filtered.length;
    const pages = Math.ceil(total / PAGE_SIZE);
    const start = _page * PAGE_SIZE + 1;
    const end   = Math.min((_page + 1) * PAGE_SIZE, total);

    $pag.innerHTML = `
      <span class="pagination-info">${total === 0 ? 'Sin resultados' : `Mostrando ${start}–${end} de ${total}`}</span>
      <div class="pagination-btns">
        <button class="page-btn" id="pag-prev" ${_page === 0 ? 'disabled' : ''} aria-label="Anterior">
          <i data-lucide="chevron-left" width="14" height="14"></i>
        </button>
        <span style="font-size:var(--text-sm);color:var(--text-muted);padding:0 var(--space-2)">Pág ${_page + 1} / ${pages || 1}</span>
        <button class="page-btn" id="pag-next" ${_page >= pages - 1 ? 'disabled' : ''} aria-label="Siguiente">
          <i data-lucide="chevron-right" width="14" height="14"></i>
        </button>
      </div>
    `;

    lucide.createIcons({ elements: [$pag] });

    document.getElementById('pag-prev')?.addEventListener('click', () => { _page--; renderTable(); renderPagination(); window.scrollTo(0,0); });
    document.getElementById('pag-next')?.addEventListener('click', () => { _page++; renderTable(); renderPagination(); window.scrollTo(0,0); });
  }

  // ── Modal Crear/Editar ────────────────────────────────────────────────────────
  function openCreateModal() {
    _editingId = null;
    document.getElementById('modal-product-title').textContent = 'Nuevo Producto';
    document.getElementById('product-form')?.reset();
    document.getElementById('product-id').value = '';
    hideFormError();
    openModal('product-modal');
  }

  function openEditModal(productId) {
    const product = _allProducts.find((p) => p.id === productId);
    if (!product) return;

    _editingId = productId;
    document.getElementById('modal-product-title').textContent = 'Editar Producto';
    document.getElementById('product-id').value  = productId;
    document.getElementById('p-name').value       = product.name;
    document.getElementById('p-description').value = product.description || '';
    document.getElementById('p-price').value      = product.price;
    document.getElementById('p-stock').value      = product.stock;
    document.getElementById('p-category').value   = product.category || '';
    document.getElementById('p-active').value     = String(product.is_active);
    document.getElementById('p-images').value     = product.images?.[0] || '';
    hideFormError();
    openModal('product-modal');
  }

  function openDeleteModal(productId, productName) {
    _deletingId = productId;
    document.getElementById('delete-product-name').textContent = productName;
    openModal('delete-modal');
  }

  // ── Guardar producto ──────────────────────────────────────────────────────────
  async function saveProduct() {
    const $btn = document.getElementById('save-product-btn');
    hideFormError();

    const name  = document.getElementById('p-name')?.value.trim();
    const price = parseFloat(document.getElementById('p-price')?.value);
    const stock = parseInt(document.getElementById('p-stock')?.value, 10);

    if (!name) { showFormError('El nombre es obligatorio'); return; }
    if (!price || price <= 0) { showFormError('El precio debe ser mayor a 0'); return; }
    if (isNaN(stock) || stock < 0) { showFormError('El stock debe ser ≥ 0'); return; }

    const imageUrl = document.getElementById('p-images')?.value.trim();
    const payload = {
      name,
      description: document.getElementById('p-description')?.value.trim() || null,
      price,
      stock,
      category: document.getElementById('p-category')?.value || null,
      images: imageUrl ? [imageUrl] : null,
      is_active: document.getElementById('p-active')?.value === 'true',
    };

    $btn.disabled = true;
    $btn.innerHTML = `<span class="spinner"></span> Guardando...`;

    try {
      if (_editingId) {
        const updated = await api.put(`/products/${_editingId}`, payload);
        const idx = _allProducts.findIndex((p) => p.id === _editingId);
        if (idx !== -1) _allProducts[idx] = updated;
        showToast('Producto actualizado', 'success');
      } else {
        const created = await api.post('/products', payload);
        _allProducts.unshift(created);
        showToast('Producto creado', 'success');
      }

      closeModal('product-modal');
      applyFilter();
    } catch (err) {
      showFormError(err.message || 'Error al guardar');
    } finally {
      $btn.disabled = false;
      $btn.innerHTML = `<i data-lucide="save" width="14" height="14"></i> Guardar`;
      lucide.createIcons({ elements: [$btn] });
    }
  }

  // ── Soft delete / restore ─────────────────────────────────────────────────────
  async function deleteProduct() {
    if (!_deletingId) return;
    const $btn = document.getElementById('confirm-delete-btn');
    $btn.disabled = true;

    try {
      await api.delete(`/products/${_deletingId}`);
      const idx = _allProducts.findIndex((p) => p.id === _deletingId);
      if (idx !== -1) _allProducts[idx].is_active = false;
      showToast('Producto desactivado', 'info');
      closeModal('delete-modal');
      applyFilter();
    } catch (err) {
      showToast(err.message || 'Error al desactivar', 'error');
    } finally {
      $btn.disabled = false;
    }
  }

  async function restoreProduct(productId) {
    try {
      const updated = await api.put(`/products/${productId}`, { is_active: true });
      const idx = _allProducts.findIndex((p) => p.id === productId);
      if (idx !== -1) _allProducts[idx] = updated;
      showToast('Producto reactivado', 'success');
      applyFilter();
    } catch (err) {
      showToast(err.message || 'Error al reactivar', 'error');
    }
  }

  // ── Modal helpers ─────────────────────────────────────────────────────────────
  function openModal(id)  { document.getElementById(id)?.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function closeModal(id) { document.getElementById(id)?.classList.remove('open'); document.body.style.overflow = ''; }

  function showFormError(msg) {
    const $err = document.getElementById('product-form-error');
    const $msg = document.getElementById('product-form-error-msg');
    if ($err && $msg) { $msg.textContent = msg; $err.classList.add('show'); }
  }

  function hideFormError() {
    document.getElementById('product-form-error')?.classList.remove('show');
  }

  // ── Bind events ───────────────────────────────────────────────────────────────
  function bindModalEvents() {
    // Open modals
    document.getElementById('btn-new-product')?.addEventListener('click', openCreateModal);

    // Close modals
    ['close-product-modal', 'cancel-product-modal'].forEach((id) =>
      document.getElementById(id)?.addEventListener('click', () => closeModal('product-modal'))
    );
    ['close-delete-modal', 'cancel-delete-modal'].forEach((id) =>
      document.getElementById(id)?.addEventListener('click', () => closeModal('delete-modal'))
    );

    // Click fuera del modal
    document.querySelectorAll('.modal-overlay').forEach((overlay) => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal(overlay.id);
      });
    });

    // Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeModal('product-modal');
        closeModal('delete-modal');
      }
    });

    // Submit form con Enter
    document.getElementById('product-form')?.addEventListener('submit', (e) => { e.preventDefault(); saveProduct(); });
    document.getElementById('save-product-btn')?.addEventListener('click', saveProduct);
    document.getElementById('confirm-delete-btn')?.addEventListener('click', deleteProduct);
  }

})();
