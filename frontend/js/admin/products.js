/**
 * Admin — Gestión de productos (catálogo serverless con variantes).
 * CRUD sobre /api/products (requiere rol admin).
 */
(function AdminProducts() {
  'use strict';

  const $tbody = document.getElementById('products-tbody');
  const $form = document.getElementById('product-form');
  const $modal = document.getElementById('product-modal');
  const $modalTitle = document.getElementById('modal-product-title');
  const $errBox = document.getElementById('product-form-error');
  const $errMsg = document.getElementById('product-form-error-msg');
  const $search = document.getElementById('product-search');
  const $filterStatus = document.getElementById('product-filter-status');
  const $deleteModal = document.getElementById('delete-modal');
  const $deleteName = document.getElementById('delete-product-name');

  let products = [];
  let deleteId = null;

  function totalStock(p) {
    return p.variants && p.variants.length
      ? p.variants.reduce((s, v) => s + (v.stock || 0), 0)
      : p.stock || 0;
  }

  async function loadCategories() {
    try {
      const cfg = await api.get('/config');
      const sel = document.getElementById('p-category');
      (cfg.categories || []).forEach((c) => {
        const o = document.createElement('option');
        o.value = c; o.textContent = c; sel.appendChild(o);
      });
    } catch { /* opcional */ }
  }

  async function load() {
    $tbody.innerHTML = `<tr><td colspan="7">Cargando…</td></tr>`;
    try {
      const data = await api.get('/products', { limit: 100 });
      products = data.items || [];
      render();
    } catch (err) {
      $tbody.innerHTML = `<tr><td colspan="7">Error: ${err.message}</td></tr>`;
    }
  }

  function render() {
    let list = products;
    const q = ($search?.value || '').toLowerCase();
    if (q) list = list.filter((p) => p.name.toLowerCase().includes(q));
    const status = $filterStatus?.value;
    if (status === 'active') list = list.filter((p) => p.is_active);
    if (status === 'inactive') list = list.filter((p) => !p.is_active);

    if (!list.length) { $tbody.innerHTML = `<tr><td colspan="7">Sin productos</td></tr>`; return; }

    $tbody.innerHTML = list.map((p) => `
      <tr>
        <td><code>${String(p.id).slice(0, 8)}</code></td>
        <td>${p.name}</td>
        <td>${p.category || '—'}</td>
        <td>${formatPrice(p.price)}</td>
        <td>${totalStock(p)}${p.variants?.length ? ` (${p.variants.length} var.)` : ''}</td>
        <td>${p.is_active ? 'Activo' : 'Inactivo'}</td>
        <td>
          <button class="btn btn-ghost btn-sm" data-edit="${p.id}">Editar</button>
          <button class="btn btn-ghost btn-sm" data-del="${p.id}">Eliminar</button>
        </td>
      </tr>`).join('');

    $tbody.querySelectorAll('[data-edit]').forEach((b) =>
      b.addEventListener('click', () => openEdit(b.dataset.edit)));
    $tbody.querySelectorAll('[data-del]').forEach((b) =>
      b.addEventListener('click', () => openDelete(b.dataset.del)));
  }

  function openModal(edit) {
    $modalTitle.textContent = edit ? 'Editar producto' : 'Nuevo producto';
    $errBox.style.display = 'none';
    $modal.classList.add('open');
  }
  function closeModal() {
    $modal.classList.remove('open');
    $form.reset();
    document.getElementById('product-id').value = '';
  }

  function openNew() {
    $form.reset();
    document.getElementById('product-id').value = '';
    document.getElementById('p-variants').value = '';
    openModal(false);
  }

  function openEdit(id) {
    const p = products.find((x) => x.id === id);
    if (!p) return;
    document.getElementById('product-id').value = p.id;
    document.getElementById('p-name').value = p.name;
    document.getElementById('p-description').value = p.description || '';
    document.getElementById('p-price').value = p.price;
    document.getElementById('p-stock').value = p.stock || 0;
    document.getElementById('p-category').value = p.category || '';
    document.getElementById('p-active').value = String(p.is_active);
    document.getElementById('p-images').value = (p.images && p.images[0]) || '';
    document.getElementById('p-variants').value = p.variants?.length
      ? JSON.stringify(p.variants)
      : '';
    openModal(true);
  }

  function showError(msg) { $errMsg.textContent = msg; $errBox.style.display = 'flex'; }

  async function submit(e) {
    e.preventDefault();
    $errBox.style.display = 'none';
    let variants = [];
    const vRaw = document.getElementById('p-variants').value.trim();
    if (vRaw) {
      try { variants = JSON.parse(vRaw); }
      catch { return showError('Variantes: JSON inválido'); }
    }
    const img = document.getElementById('p-images').value.trim();
    const payload = {
      name: document.getElementById('p-name').value.trim(),
      description: document.getElementById('p-description').value.trim(),
      price: parseFloat(document.getElementById('p-price').value),
      category: document.getElementById('p-category').value,
      stock: parseInt(document.getElementById('p-stock').value || '0', 10),
      images: img ? [img] : [],
      variants,
      is_active: document.getElementById('p-active').value === 'true',
    };
    const id = document.getElementById('product-id').value;
    try {
      if (id) await api.put(`/products/${id}`, payload);
      else await api.post('/products', payload);
      showToast('Producto guardado', 'success');
      closeModal();
      load();
    } catch (err) { showError(err.message); }
  }

  function openDelete(id) {
    deleteId = id;
    const p = products.find((x) => x.id === id);
    if ($deleteName) $deleteName.textContent = p ? p.name : '';
    $deleteModal.classList.add('open');
  }
  async function confirmDelete() {
    if (!deleteId) return;
    try { await api.delete(`/products/${deleteId}`); showToast('Producto eliminado', 'success'); }
    catch (err) { showToast(err.message, 'error'); }
    $deleteModal.classList.remove('open');
    deleteId = null;
    load();
  }

  async function init() {
    await requireAdmin();
    await loadCategories();
    await load();
    document.getElementById('btn-new-product')?.addEventListener('click', openNew);
    $form?.addEventListener('submit', submit);
    document.getElementById('cancel-product-modal')?.addEventListener('click', closeModal);
    document.getElementById('close-product-modal')?.addEventListener('click', closeModal);
    document.getElementById('confirm-delete-btn')?.addEventListener('click', confirmDelete);
    document.getElementById('cancel-delete-modal')?.addEventListener('click', () => $deleteModal.classList.remove('open'));
    document.getElementById('close-delete-modal')?.addEventListener('click', () => $deleteModal.classList.remove('open'));
    $search?.addEventListener('input', render);
    $filterStatus?.addEventListener('change', render);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
