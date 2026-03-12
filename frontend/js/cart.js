/**
 * MetalShop — Cart Manager
 * Dual mode: localStorage (visitante) ↔ API (autenticado).
 * Controla el drawer lateral y sincroniza al hacer login.
 */

(function CartManager() {
  'use strict';

  const LS_KEY = 'ms_cart';

  // ── Almacenamiento local ─────────────────────────────────────────────────────

  const local = {
    get() {
      try { return JSON.parse(localStorage.getItem(LS_KEY) || '[]'); } catch { return []; }
    },
    save(items) {
      localStorage.setItem(LS_KEY, JSON.stringify(items));
    },
    add(product, qty) {
      const items = local.get();
      const existing = items.find((i) => i.product_id === product.id);
      if (existing) {
        existing.quantity += qty;
      } else {
        items.push({
          id: Date.now(),           // ID temporal
          product_id: product.id,
          product: { id: product.id, name: product.name, price: product.price, stock: 999, images: product.image ? [product.image] : null },
          quantity: qty,
        });
      }
      local.save(items);
      return items;
    },
    update(productId, qty) {
      const items = local.get().map((i) =>
        i.product_id === productId ? { ...i, quantity: qty } : i
      );
      local.save(items);
      return items;
    },
    remove(productId) {
      const items = local.get().filter((i) => i.product_id !== productId);
      local.save(items);
      return items;
    },
    clear() { localStorage.removeItem(LS_KEY); },
  };

  // ── Estado ───────────────────────────────────────────────────────────────────

  let _items = [];
  let _subtotal = 0;
  let _count = 0;

  // ── Carga inicial ─────────────────────────────────────────────────────────────

  async function loadCart() {
    if (Auth.isAuthenticated()) {
      try {
        const data = await api.get('/cart');
        _items    = data.items;
        _subtotal = data.subtotal;
        _count    = data.item_count;
      } catch {
        _items = local.get();
        _count = _items.reduce((s, i) => s + i.quantity, 0);
        _subtotal = _items.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0);
      }
    } else {
      _items = local.get();
      _count = _items.reduce((s, i) => s + i.quantity, 0);
      _subtotal = _items.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0);
    }
    renderDrawer();
    updateBadge();
  }

  // ── API pública ───────────────────────────────────────────────────────────────

  const Cart = {
    async add(product, qty = 1) {
      if (Auth.isAuthenticated()) {
        try {
          const data = await api.post('/cart/items', { product_id: product.id, quantity: qty });
          _items = data.items; _subtotal = data.subtotal; _count = data.item_count;
        } catch (err) {
          showToast(err.message || 'Error al agregar al carrito', 'error');
          return;
        }
      } else {
        _items = local.add(product, qty);
        _count    = _items.reduce((s, i) => s + i.quantity, 0);
        _subtotal = _items.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0);
      }
      renderDrawer();
      updateBadge();
      openDrawer();
    },

    async update(itemId, productId, qty) {
      if (Auth.isAuthenticated()) {
        try {
          const data = await api.put(`/cart/items/${itemId}`, { quantity: qty });
          _items = data.items; _subtotal = data.subtotal; _count = data.item_count;
        } catch (err) {
          showToast(err.message || 'Error al actualizar', 'error');
          return;
        }
      } else {
        _items = local.update(productId, qty);
        _count    = _items.reduce((s, i) => s + i.quantity, 0);
        _subtotal = _items.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0);
      }
      renderDrawer();
      updateBadge();
    },

    async remove(itemId, productId) {
      if (Auth.isAuthenticated()) {
        try {
          await api.delete(`/cart/items/${itemId}`);
          const data = await api.get('/cart');
          _items = data.items; _subtotal = data.subtotal; _count = data.item_count;
        } catch (err) {
          showToast(err.message || 'Error al eliminar', 'error');
          return;
        }
      } else {
        _items = local.remove(productId);
        _count    = _items.reduce((s, i) => s + i.quantity, 0);
        _subtotal = _items.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0);
      }
      renderDrawer();
      updateBadge();
    },

    clear() {
      local.clear();
      _items = []; _subtotal = 0; _count = 0;
      renderDrawer();
      updateBadge();
    },

    getItems:    () => _items,
    getSubtotal: () => _subtotal,
    getCount:    () => _count,

    /** Sync localStorage → API tras login */
    async syncAfterLogin() {
      const localItems = local.get();
      if (!localItems.length) { await loadCart(); return; }
      try {
        const payload = { items: localItems.map((i) => ({ product_id: i.product_id, quantity: i.quantity })) };
        const data = await api.post('/cart/sync', payload);
        _items = data.items; _subtotal = data.subtotal; _count = data.item_count;
        local.clear();
      } catch {
        await loadCart();
      }
      renderDrawer();
      updateBadge();
    },
  };

  // ── Drawer UI ─────────────────────────────────────────────────────────────────

  function openDrawer() {
    document.getElementById('cart-overlay')?.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    document.getElementById('cart-overlay')?.classList.remove('open');
    document.body.style.overflow = '';
  }

  function updateBadge() {
    const $badge = document.getElementById('cart-count');
    if (!$badge) return;
    if (_count > 0) {
      $badge.textContent = _count > 99 ? '99+' : _count;
      $badge.style.display = 'flex';
    } else {
      $badge.style.display = 'none';
    }
  }

  function renderDrawer() {
    const $body   = document.getElementById('cart-items');
    const $footer = document.getElementById('cart-footer');
    if (!$body) return;

    if (!_items.length) {
      $body.innerHTML = `
        <div class="drawer-empty">
          <i data-lucide="shopping-cart" width="48" height="48"></i>
          <p>Tu carrito está vacío</p>
          <a href="/" class="btn btn-ghost btn-sm">Ver productos</a>
        </div>`;
      if ($footer) $footer.style.display = 'none';
      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$body] });
      return;
    }

    $body.innerHTML = _items.map((item) => {
      const img = item.product?.images?.[0];
      return `
        <div class="cart-item" data-item-id="${item.id}" data-product-id="${item.product_id}">
          <div>
            ${img
              ? `<img src="${img}" alt="${item.product?.name}" class="cart-item-img" />`
              : `<div class="cart-item-img" style="display:flex;align-items:center;justify-content:center;background:var(--bg-surface)"><i data-lucide="package" width="24" height="24"></i></div>`
            }
          </div>
          <div class="cart-item-info">
            <span class="cart-item-name">${item.product?.name || 'Producto'}</span>
            <span class="cart-item-price">${formatPrice(item.product?.price || 0)}</span>
            <div class="cart-item-controls">
              <button class="qty-btn btn-qty-dec" aria-label="Reducir cantidad">−</button>
              <span class="qty-display">${item.quantity}</span>
              <button class="qty-btn btn-qty-inc" aria-label="Aumentar cantidad">+</button>
              <button class="cart-item-remove btn-remove" aria-label="Eliminar">
                <i data-lucide="trash-2" width="12" height="12"></i> Eliminar
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$body] });

    // Actualizar subtotal / total
    const $sub = document.getElementById('cart-subtotal');
    const $tot = document.getElementById('cart-total');
    if ($sub) $sub.textContent = formatPrice(_subtotal);
    if ($tot) $tot.textContent = formatPrice(_subtotal);
    if ($footer) $footer.style.display = 'block';

    // Eventos de items
    $body.querySelectorAll('.cart-item').forEach((el) => {
      const itemId    = parseInt(el.dataset.itemId, 10);
      const productId = parseInt(el.dataset.productId, 10);
      const $qty      = el.querySelector('.qty-display');
      let   qty       = parseInt($qty.textContent, 10);

      el.querySelector('.btn-qty-dec')?.addEventListener('click', async () => {
        if (qty <= 1) return;
        qty--;
        $qty.textContent = qty;
        await Cart.update(itemId, productId, qty);
      });

      el.querySelector('.btn-qty-inc')?.addEventListener('click', async () => {
        qty++;
        $qty.textContent = qty;
        await Cart.update(itemId, productId, qty);
      });

      el.querySelector('.btn-remove')?.addEventListener('click', async () => {
        el.style.opacity = '0.4';
        el.style.pointerEvents = 'none';
        await Cart.remove(itemId, productId);
      });
    });
  }

  // ── Event listeners globales ──────────────────────────────────────────────────
  function bindEvents() {
    document.getElementById('cart-toggle')?.addEventListener('click', openDrawer);
    document.getElementById('cart-close')?.addEventListener('click', closeDrawer);
    document.getElementById('cart-overlay')?.addEventListener('click', (e) => {
      if (e.target === e.currentTarget) closeDrawer();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeDrawer();
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────────
  async function init() {
    bindEvents();
    await loadCart();
  }

  window.Cart = Cart;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
