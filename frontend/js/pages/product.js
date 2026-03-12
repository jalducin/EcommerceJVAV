/**
 * MetalShop — Detalle de Producto
 * Carga producto desde la API, galería de imágenes, selector de cantidad y CTA.
 */

(function ProductPage() {
  'use strict';

  const params = new URLSearchParams(location.search);
  const productId = params.get('id');

  // ── Referencias DOM ──────────────────────────────────────────────────────────
  const $loading = document.getElementById('product-loading');
  const $content = document.getElementById('product-content');
  const $error   = document.getElementById('product-error');

  // ── Cantidad seleccionada ────────────────────────────────────────────────────
  let selectedQty = 1;
  let currentProduct = null;

  // ── Inicializar ──────────────────────────────────────────────────────────────
  async function init() {
    if (!productId) { showError(); return; }

    try {
      const product = await api.get(`/products/${productId}`);
      currentProduct = product;
      document.title = `${product.name} — MetalShop`;
      renderProduct(product);
      hideLoading();
    } catch {
      showError();
    }
  }

  // ── Render ───────────────────────────────────────────────────────────────────
  function renderProduct(p) {
    const images = p.images?.length ? p.images : [null];
    const outOfStock = p.stock === 0;
    const lowStock   = p.stock > 0 && p.stock <= 5;

    const stockClass = outOfStock ? 'out' : lowStock ? 'low' : 'in';
    const stockText  = outOfStock
      ? 'Sin stock disponible'
      : lowStock
        ? `¡Solo quedan ${p.stock} unidades!`
        : `${p.stock} unidades disponibles`;

    $content.innerHTML = `
      <!-- Breadcrumb -->
      <nav class="breadcrumb" aria-label="Ruta de navegación">
        <a href="/">Catálogo</a>
        <span class="sep" aria-hidden="true">/</span>
        ${p.category ? `<a href="/?category=${encodeURIComponent(p.category)}">${p.category}</a><span class="sep" aria-hidden="true">/</span>` : ''}
        <span class="current" aria-current="page">${p.name}</span>
      </nav>

      <div class="product-grid">
        <!-- Galería -->
        <div class="gallery" id="product-gallery">
          <div class="gallery-main">
            ${renderMainImage(images[0], p.name)}
            <div class="gallery-badge-overlay">
              ${outOfStock ? `<span class="badge badge-error">Agotado</span>` : ''}
              ${lowStock   ? `<span class="badge badge-warning">Stock bajo</span>` : ''}
            </div>
          </div>
          ${images.length > 1 ? `
            <div class="gallery-thumbnails" role="list" aria-label="Miniaturas de imágenes">
              ${images.map((img, i) => `
                <div class="thumb${i === 0 ? ' active' : ''}" data-index="${i}" role="listitem"
                     tabindex="0" aria-label="Imagen ${i + 1}">
                  ${img ? `<img src="${img}" alt="${p.name} vista ${i + 1}" loading="lazy" />` : ''}
                </div>
              `).join('')}
            </div>
          ` : ''}
        </div>

        <!-- Info del producto -->
        <div class="product-info">
          <!-- Categoría -->
          ${p.category ? `
            <div class="product-category-badge">
              <span class="badge badge-steel">
                <i data-lucide="tag" width="10" height="10"></i>
                ${p.category}
              </span>
            </div>
          ` : ''}

          <!-- Nombre -->
          <h1 class="product-name">${p.name}</h1>

          <!-- Precio -->
          <div class="product-price-block">
            <span class="product-price">${formatPrice(p.price)}</span>
            <span class="product-price-note">IVA incluido</span>
          </div>

          <!-- Stock -->
          <div class="stock-indicator" aria-live="polite">
            <span class="stock-dot ${stockClass}" aria-hidden="true"></span>
            <span class="${outOfStock ? 'text-error' : lowStock ? 'text-warning' : 'text-success'}">${stockText}</span>
          </div>

          <!-- Descripción -->
          ${p.description ? `<p class="product-description">${p.description}</p>` : ''}

          <!-- Add to cart -->
          <div class="add-to-cart-section">
            ${!outOfStock ? `
              <div class="qty-selector">
                <span class="qty-label">Cantidad:</span>
                <div class="qty-controls" role="group" aria-label="Selector de cantidad">
                  <button id="qty-dec" aria-label="Reducir cantidad">−</button>
                  <input
                    type="number"
                    id="qty-input"
                    value="1"
                    min="1"
                    max="${p.stock}"
                    aria-label="Cantidad"
                  />
                  <button id="qty-inc" aria-label="Aumentar cantidad">+</button>
                </div>
              </div>
            ` : ''}

            <div class="cart-actions">
              <button
                class="btn btn-primary"
                id="add-to-cart-btn"
                ${outOfStock ? 'disabled' : ''}
                aria-label="${outOfStock ? 'Producto sin stock' : 'Agregar al carrito'}"
              >
                <i data-lucide="shopping-cart" width="18" height="18"></i>
                ${outOfStock ? 'Sin Stock' : 'Agregar al Carrito'}
              </button>
              <button class="btn btn-secondary" id="wishlist-btn" aria-label="Guardar en lista de deseos">
                <i data-lucide="heart" width="18" height="18"></i>
              </button>
            </div>
          </div>

          <!-- Meta info -->
          <div class="product-meta" role="complementary" aria-label="Información de envío">
            <div class="meta-row">
              <i data-lucide="truck" width="16" height="16"></i>
              <span>Envío express 24h disponible</span>
            </div>
            <div class="meta-row">
              <i data-lucide="shield-check" width="16" height="16"></i>
              <span>Certificado de calidad industrial</span>
            </div>
            <div class="meta-row">
              <i data-lucide="refresh-cw" width="16" height="16"></i>
              <span>Devoluciones gratis en 30 días</span>
            </div>
          </div>
        </div>
      </div>
    `;

    $content.classList.remove('hidden');
    if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$content] });

    bindProductEvents(p, images);
  }

  function renderMainImage(src, alt) {
    if (!src) return `
      <div class="card-image-placeholder" style="height:100%;min-height:320px">
        <i data-lucide="package" width="48" height="48"></i>
        <span>Sin imagen</span>
      </div>`;
    return `<img src="${src}" alt="${alt}" id="gallery-main-img" />`;
  }

  // ── Eventos del producto ─────────────────────────────────────────────────────
  function bindProductEvents(product, images) {
    // Galería thumbnails
    if (images.length > 1) {
      document.querySelectorAll('.thumb').forEach((thumb) => {
        thumb.addEventListener('click', () => switchImage(thumb, images));
        thumb.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') switchImage(thumb, images);
        });
      });
    }

    // Selector de cantidad
    const $input = document.getElementById('qty-input');
    const $dec   = document.getElementById('qty-dec');
    const $inc   = document.getElementById('qty-inc');

    if ($input && $dec && $inc) {
      $dec.addEventListener('click', () => {
        selectedQty = Math.max(1, selectedQty - 1);
        $input.value = selectedQty;
      });

      $inc.addEventListener('click', () => {
        selectedQty = Math.min(product.stock, selectedQty + 1);
        $input.value = selectedQty;
      });

      $input.addEventListener('change', () => {
        const v = parseInt($input.value, 10);
        selectedQty = Math.min(Math.max(1, isNaN(v) ? 1 : v), product.stock);
        $input.value = selectedQty;
      });
    }

    // Botón agregar al carrito
    document.getElementById('add-to-cart-btn')?.addEventListener('click', () => {
      if (typeof window.Cart === 'undefined') {
        showToast('Error al acceder al carrito', 'error');
        return;
      }
      window.Cart.add(
        { id: product.id, name: product.name, price: product.price, image: images[0] || null },
        selectedQty,
      );
      showToast(`"${product.name}" agregado al carrito (×${selectedQty})`, 'success');
    });

    // Wishlist (placeholder)
    document.getElementById('wishlist-btn')?.addEventListener('click', () => {
      showToast('Lista de deseos disponible próximamente', 'info');
    });
  }

  function switchImage(thumb, images) {
    const idx = parseInt(thumb.dataset.index, 10);
    const mainImg = document.getElementById('gallery-main-img');
    if (!mainImg || !images[idx]) return;

    mainImg.src = images[idx];
    document.querySelectorAll('.thumb').forEach((t) => t.classList.remove('active'));
    thumb.classList.add('active');
  }

  // ── States ───────────────────────────────────────────────────────────────────
  function hideLoading() {
    $loading?.classList.add('hidden');
  }

  function showError() {
    $loading?.classList.add('hidden');
    $error?.classList.remove('hidden');
    if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$error] });
  }

  // ── Arrancar ─────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
