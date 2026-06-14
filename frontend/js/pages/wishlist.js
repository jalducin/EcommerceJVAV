/**
 * JV Market — Lista de deseos
 * Lista los productos guardados, permite quitarlos y agregarlos al carrito.
 */

(function WishlistPage() {
  'use strict';

  document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth('/login.html')) return;
    await load();
  });

  async function load() {
    const $grid = document.getElementById('wishlist-grid');
    try {
      const products = await api.get('/wishlist');
      render(products);
    } catch (err) {
      $grid.innerHTML = `<p>${err.message || 'No se pudo cargar tu lista'}</p>`;
    }
  }

  function render(products) {
    const $grid = document.getElementById('wishlist-grid');
    if (!products.length) {
      $grid.innerHTML = `
        <div class="empty-state">
          <i data-lucide="heart-off" width="40" height="40"></i>
          <p>Tu lista de deseos está vacía.</p>
          <a href="/products.html" class="btn btn-primary">Explorar productos</a>
        </div>`;
      if (typeof lucide !== 'undefined') lucide.createIcons();
      return;
    }

    $grid.innerHTML = products.map((p) => {
      const img = p.images?.[0];
      return `
        <div class="product-card" data-id="${p.id}">
          <a href="/product.html?id=${p.id}" class="product-card-img-link">
            ${img
              ? `<img src="${img}" alt="${p.name}" class="product-card-img" loading="lazy" />`
              : `<div class="product-card-img" style="display:flex;align-items:center;justify-content:center"><i data-lucide="package" width="28" height="28"></i></div>`}
          </a>
          <div class="product-card-body">
            <h3 class="product-card-name">${p.name}</h3>
            <span class="product-card-price">${formatPrice(p.price)}</span>
            <div class="product-card-actions">
              <button class="btn btn-primary btn-sm js-add" data-id="${p.id}">
                <i data-lucide="shopping-cart" width="16" height="16"></i> Agregar
              </button>
              <button class="btn btn-ghost btn-sm js-remove" data-id="${p.id}" aria-label="Quitar de la lista">
                <i data-lucide="trash-2" width="16" height="16"></i>
              </button>
            </div>
          </div>
        </div>`;
    }).join('');

    if (typeof lucide !== 'undefined') lucide.createIcons();

    const byId = Object.fromEntries(products.map((p) => [p.id, p]));

    $grid.querySelectorAll('.js-add').forEach((b) =>
      b.addEventListener('click', () => {
        const p = byId[b.dataset.id];
        if (!p) return;
        Cart.add({ id: p.id, name: p.name, price: p.price, image: p.images?.[0] || null }, 1);
        showToast('Agregado al carrito', 'success');
      }));

    $grid.querySelectorAll('.js-remove').forEach((b) =>
      b.addEventListener('click', async () => {
        try {
          await api.delete(`/wishlist/${b.dataset.id}`);
          b.closest('.product-card')?.remove();
          if (!$grid.querySelector('.product-card')) render([]);
        } catch (err) {
          showToast(err.message || 'No se pudo quitar', 'error');
        }
      }));
  }
})();
