/**
 * MetalShop — Checkout
 * Validación del formulario, POST a /api/orders/checkout, redirect a confirmación.
 */

(function CheckoutPage() {
  'use strict';

  // Proteger página: requiere autenticación
  document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth('/login.html')) return;
    await initPage();
  });

  async function initPage() {
    // Esperar a que el carrito cargue
    await new Promise(r => setTimeout(r, 500));

    const items = Cart.getItems();

    if (!items.length) {
      document.getElementById('checkout-empty')?.classList.remove('hidden');
      document.getElementById('checkout-form')?.classList.add('hidden');
      lucide.createIcons();
      return;
    }

    renderOrderItems(items);
    await setupFulfillment();
    bindForm();
  }

  // ── Render items del pedido ──────────────────────────────────────────────────
  function renderOrderItems(items) {
    const $list    = document.getElementById('checkout-items-list');
    const $sub     = document.getElementById('co-subtotal');
    const $tot     = document.getElementById('co-total');
    const subtotal = Cart.getSubtotal();

    if ($list) {
      $list.innerHTML = items.map(item => {
        const img = item.product?.images?.[0];
        return `
          <div class="checkout-item">
            ${img
              ? `<img src="${img}" alt="${item.product?.name}" class="checkout-item-img" />`
              : `<div class="checkout-item-img" style="display:flex;align-items:center;justify-content:center"><i data-lucide="package" width="20" height="20"></i></div>`
            }
            <span class="checkout-item-name">${item.product?.name} ×${item.quantity}</span>
            <span class="checkout-item-price">${formatPrice((item.product?.price || 0) * item.quantity)}</span>
          </div>
        `;
      }).join('');
      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$list] });
    }

    if ($sub) $sub.textContent = formatPrice(subtotal);
    if ($tot) $tot.textContent = formatPrice(subtotal);
  }

  // ── Validación ────────────────────────────────────────────────────────────────
  const FIELDS = ['full_name', 'street', 'city', 'state', 'postal_code', 'phone'];

  function validateField(name) {
    const $input = document.getElementById(name);
    const $error = document.getElementById(`err-${name}`);
    const valid  = $input && $input.value.trim().length > 0;
    $input?.classList.toggle('invalid', !valid);
    $error?.classList.toggle('show', !valid);
    return valid;
  }

  function fulfillment() {
    return document.querySelector('input[name="fulfillment"]:checked')?.value || 'ship';
  }

  function validateForm() {
    // En "recoger en tienda" no se requiere dirección de envío.
    if (fulfillment() === 'pickup') {
      return !!document.getElementById('pickup-location')?.value;
    }
    return FIELDS.map(validateField).every(Boolean);
  }

  async function setupFulfillment() {
    const $block = document.getElementById('pickup-block');
    const $addr = document.getElementById('address-card');
    const $sel = document.getElementById('pickup-location');
    try {
      const cfg = await api.get('/config');
      if (cfg.pickup_enabled && $sel) {
        $sel.innerHTML = (cfg.pickup_locations || [])
          .map((l) => `<option value="${l.id}">${l.name} — ${l.address}</option>`)
          .join('');
      }
    } catch { /* opcional */ }
    document.querySelectorAll('input[name="fulfillment"]').forEach((r) =>
      r.addEventListener('change', () => {
        const pickup = fulfillment() === 'pickup';
        if ($block) $block.style.display = pickup ? 'block' : 'none';
        if ($addr) $addr.style.display = pickup ? 'none' : 'block';
      }));
  }

  // ── Submit ────────────────────────────────────────────────────────────────────
  function bindForm() {
    const $form = document.getElementById('checkout-form');
    const $btn  = document.getElementById('place-order-btn');

    // Limpiar error en focus
    FIELDS.forEach(name => {
      document.getElementById(name)?.addEventListener('input', () => validateField(name));
    });

    $form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!validateForm()) {
        showToast('Completa todos los campos obligatorios', 'error');
        return;
      }

      // Armar payload
      const paymentMethod = document.querySelector('input[name="payment_method"]:checked')?.value || 'card';

      const isPickup = fulfillment() === 'pickup';
      const payload = {
        fulfillment: isPickup ? 'pickup' : 'ship',
        pickup_location_id: isPickup
          ? document.getElementById('pickup-location')?.value
          : null,
        shipping_address: isPickup
          ? {}
          : {
              full_name:   document.getElementById('full_name').value.trim(),
              street:      document.getElementById('street').value.trim(),
              city:        document.getElementById('city').value.trim(),
              state:       document.getElementById('state').value.trim(),
              postal_code: document.getElementById('postal_code').value.trim(),
              phone:       document.getElementById('phone').value.trim(),
              country:     'México',
            },
        payment_method: paymentMethod,
      };

      // Estado de carga
      $btn.disabled = true;
      $btn.innerHTML = `<span class="spinner"></span> Procesando...`;

      try {
        const order = await api.post('/orders/checkout', payload);
        Cart.clear();
        window.location.href = `/order-confirm.html?order_id=${order.id}`;
      } catch (err) {
        showToast(err.message || 'Error al procesar el pedido', 'error');
        $btn.disabled = false;
        $btn.innerHTML = `<i data-lucide="shield-check" width="18" height="18"></i> Confirmar Pedido`;
        if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$btn] });
      }
    });
  }

})();
