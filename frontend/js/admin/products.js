/**
 * Admin — Gestión de productos (catálogo serverless con variantes).
 * CRUD sobre /api/products + galería de imágenes (presigned upload) y categorías.
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
  const $gallery = document.getElementById('image-gallery');
  const $catModal = document.getElementById('categories-modal');
  const $catList = document.getElementById('categories-list');

  const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
  const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'image/avif'];

  let products = [];
  let categories = [];
  let currentImages = [];
  let deleteId = null;

  function totalStock(p) {
    return p.variants && p.variants.length
      ? p.variants.reduce((s, v) => s + (v.stock || 0), 0)
      : p.stock || 0;
  }

  // ── Categorías ────────────────────────────────────────────────────────────
  async function loadCategories() {
    try {
      const cfg = await api.get('/config');
      categories = cfg.categories || [];
    } catch { categories = []; }
    fillCategorySelect();
  }

  function fillCategorySelect() {
    const sel = document.getElementById('p-category');
    if (!sel) return;
    const current = sel.value;
    sel.innerHTML = '<option value="">Sin categoría</option>'
      + categories.map((c) => `<option value="${c}">${c}</option>`).join('');
    if (current) sel.value = current;
  }

  function categoryUsage(name) {
    return products.filter((p) => p.is_active && p.category === name).length;
  }

  function renderCategories() {
    if (!$catList) return;
    $catList.innerHTML = categories.length
      ? categories.map((c) => {
        const used = categoryUsage(c);
        return `
          <li style="display:flex;align-items:center;justify-content:space-between;gap:var(--space-2);padding:var(--space-2);border:var(--border-metal);border-radius:var(--border-radius-sm)">
            <span>${c}${used ? ` <span style="color:var(--text-muted);font-size:var(--text-xs)">(${used} en uso)</span>` : ''}</span>
            <button class="btn btn-ghost btn-sm js-del-cat" data-name="${c}" ${used ? 'disabled title="En uso por productos activos"' : ''}>
              <i data-lucide="trash-2" width="14" height="14"></i>
            </button>
          </li>`;
      }).join('')
      : '<li style="color:var(--text-muted)">Sin categorías todavía.</li>';
    if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$catList] });
    $catList.querySelectorAll('.js-del-cat').forEach((b) =>
      b.addEventListener('click', () => deleteCategory(b.dataset.name)));
  }

  async function addCategory() {
    const $in = document.getElementById('new-category-name');
    const name = ($in.value || '').trim();
    if (!name) return;
    try {
      const res = await api.post('/admin/categories', { name });
      categories = res.categories || [];
      $in.value = '';
      fillCategorySelect();
      renderCategories();
      showToast('Categoría agregada', 'success');
    } catch (err) { showToast(err.message || 'No se pudo agregar', 'error'); }
  }

  async function deleteCategory(name) {
    try {
      await api.delete(`/admin/categories/${encodeURIComponent(name)}`);
      categories = categories.filter((c) => c !== name);
      fillCategorySelect();
      renderCategories();
      showToast('Categoría eliminada', 'success');
    } catch (err) {
      showToast(err.message || 'La categoría está en uso', 'error');
    }
  }

  function openCategories() { renderCategories(); $catModal.classList.add('open'); }
  function closeCategories() { $catModal.classList.remove('open'); }

  // ── Galería de imágenes ─────────────────────────────────────────────────────
  function renderGallery() {
    if (!$gallery) return;
    $gallery.innerHTML = currentImages.map((src, i) => `
      <div class="gallery-item" style="position:relative;width:84px;height:84px;border:${i === 0 ? 'var(--border-glow)' : 'var(--border-metal)'};border-radius:var(--border-radius-sm);overflow:hidden">
        <img src="${src}" alt="imagen ${i + 1}" style="width:100%;height:100%;object-fit:cover" />
        ${i === 0 ? '<span style="position:absolute;top:2px;left:2px;background:var(--gold);color:var(--text-inverse);font-size:9px;padding:1px 4px;border-radius:3px">Principal</span>' : ''}
        <div style="position:absolute;bottom:2px;right:2px;display:flex;gap:2px">
          ${i > 0 ? `<button type="button" class="js-img-left" data-i="${i}" title="Mover a la izquierda" style="background:rgba(0,0,0,.6);color:#fff;border:none;border-radius:3px;cursor:pointer;width:18px;height:18px">‹</button>` : ''}
          <button type="button" class="js-img-del" data-i="${i}" title="Quitar" style="background:rgba(0,0,0,.6);color:#fff;border:none;border-radius:3px;cursor:pointer;width:18px;height:18px">×</button>
        </div>
      </div>`).join('');
    $gallery.querySelectorAll('.js-img-del').forEach((b) =>
      b.addEventListener('click', () => { currentImages.splice(+b.dataset.i, 1); renderGallery(); }));
    $gallery.querySelectorAll('.js-img-left').forEach((b) =>
      b.addEventListener('click', () => {
        const i = +b.dataset.i;
        [currentImages[i - 1], currentImages[i]] = [currentImages[i], currentImages[i - 1]];
        renderGallery();
      }));
  }

  function addImageUrl() {
    const $in = document.getElementById('p-image-url');
    const url = ($in.value || '').trim();
    if (!url) return;
    currentImages.push(url);
    $in.value = '';
    renderGallery();
  }

  async function uploadImageFile(file) {
    if (!ALLOWED_TYPES.includes(file.type)) {
      showToast('Tipo de imagen no permitido', 'error');
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      showToast('La imagen supera 5 MB', 'error');
      return;
    }
    try {
      const presign = await api.post('/admin/uploads/presign', {
        filename: file.name,
        content_type: file.type,
      });
      const res = await fetch(presign.upload_url, {
        method: 'PUT',
        headers: { 'Content-Type': file.type },
        body: file,
      });
      if (!res.ok) throw new Error('Falló la subida a S3');
      currentImages.push(presign.public_url);
      renderGallery();
      showToast('Imagen subida', 'success');
    } catch (err) {
      showToast(err.message || 'No se pudo subir la imagen', 'error');
    }
  }

  // ── Catálogo ──────────────────────────────────────────────────────────────
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
    currentImages = [];
    renderGallery();
  }

  function openNew() {
    $form.reset();
    document.getElementById('product-id').value = '';
    document.getElementById('p-variants').value = '';
    currentImages = [];
    renderGallery();
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
    currentImages = Array.isArray(p.images) ? [...p.images] : [];
    renderGallery();
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
    const payload = {
      name: document.getElementById('p-name').value.trim(),
      description: document.getElementById('p-description').value.trim(),
      price: parseFloat(document.getElementById('p-price').value),
      category: document.getElementById('p-category').value,
      stock: parseInt(document.getElementById('p-stock').value || '0', 10),
      images: [...currentImages],
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
    await load();
    await loadCategories();
    document.getElementById('btn-new-product')?.addEventListener('click', openNew);
    $form?.addEventListener('submit', submit);
    document.getElementById('cancel-product-modal')?.addEventListener('click', closeModal);
    document.getElementById('close-product-modal')?.addEventListener('click', closeModal);
    document.getElementById('confirm-delete-btn')?.addEventListener('click', confirmDelete);
    document.getElementById('cancel-delete-modal')?.addEventListener('click', () => $deleteModal.classList.remove('open'));
    document.getElementById('close-delete-modal')?.addEventListener('click', () => $deleteModal.classList.remove('open'));
    // Galería
    document.getElementById('btn-add-image-url')?.addEventListener('click', addImageUrl);
    document.getElementById('p-image-file')?.addEventListener('change', (ev) => {
      const file = ev.target.files?.[0];
      if (file) uploadImageFile(file);
      ev.target.value = '';
    });
    // Categorías
    document.getElementById('btn-manage-categories')?.addEventListener('click', openCategories);
    document.getElementById('btn-add-category')?.addEventListener('click', addCategory);
    document.getElementById('close-categories-modal')?.addEventListener('click', closeCategories);
    document.getElementById('cancel-categories-modal')?.addEventListener('click', closeCategories);
    $search?.addEventListener('input', render);
    $filterStatus?.addEventListener('change', render);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
