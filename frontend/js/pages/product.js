/**
 * MetalShop — Detalle de Producto
 * Carga producto desde la API, galería, selector de variante (talla/color…) y CTA.
 */

(function ProductPage() {
  "use strict";

  const params = new URLSearchParams(location.search);
  const productId = params.get("id");

  const $loading = document.getElementById("product-loading");
  const $content = document.getElementById("product-content");
  const $error = document.getElementById("product-error");

  let selectedQty = 1;
  let currentProduct = null;
  let selectedSku = "-"; // "-" cuando el producto no tiene variantes

  // Stock disponible de la selección actual.
  function currentStock() {
    const p = currentProduct;
    if (!p) return 0;
    if (p.variants && p.variants.length) {
      const v = p.variants.find((v) => v.sku === selectedSku);
      return v ? v.stock || 0 : 0;
    }
    return p.stock || 0;
  }

  function variantLabel(v) {
    const attrs = Object.entries(v.attrs || {})
      .map(([k, val]) => `${k}: ${val}`)
      .join(" · ");
    const agotado = (v.stock || 0) === 0 ? " (agotado)" : "";
    return `${attrs || v.sku}${agotado}`;
  }

  async function init() {
    if (!productId) {
      showError();
      return;
    }
    try {
      const product = await api.get(`/products/${productId}`);
      currentProduct = product;
      // Variante por defecto: primera con stock, o la primera.
      if (product.variants && product.variants.length) {
        const firstInStock = product.variants.find((v) => (v.stock || 0) > 0);
        selectedSku = (firstInStock || product.variants[0]).sku;
      } else {
        selectedSku = "-";
      }
      document.title = `${product.name} — MetalShop`;
      renderProduct(product);
      hideLoading();
    } catch {
      showError();
    }
  }

  function renderProduct(p) {
    const images = p.images?.length ? p.images : [null];
    const stock = currentStock();
    const outOfStock = stock === 0;
    const lowStock = stock > 0 && stock <= 5;
    const hasVariants = p.variants && p.variants.length;

    const stockClass = outOfStock ? "out" : lowStock ? "low" : "in";
    const stockText = outOfStock
      ? "Sin stock disponible"
      : lowStock
        ? `¡Solo quedan ${stock} unidades!`
        : `${stock} unidades disponibles`;

    const variantSelector = hasVariants
      ? `
        <div class="variant-selector">
          <label for="variant-select" class="qty-label">Variante:</label>
          <select id="variant-select" aria-label="Seleccionar variante">
            ${p.variants
              .map(
                (v) =>
                  `<option value="${v.sku}" ${v.sku === selectedSku ? "selected" : ""} ${(v.stock || 0) === 0 ? "disabled" : ""}>${variantLabel(v)}</option>`,
              )
              .join("")}
          </select>
        </div>`
      : "";

    $content.innerHTML = `
      <nav class="breadcrumb" aria-label="Ruta de navegación">
        <a href="/">Catálogo</a>
        <span class="sep" aria-hidden="true">/</span>
        ${p.category ? `<a href="/?category=${encodeURIComponent(p.category)}">${p.category}</a><span class="sep" aria-hidden="true">/</span>` : ""}
        <span class="current" aria-current="page">${p.name}</span>
      </nav>

      <div class="product-grid">
        <div class="gallery" id="product-gallery">
          <div class="gallery-main">
            ${renderMainImage(images[0], p.name)}
            <div class="gallery-badge-overlay" id="badge-overlay"></div>
          </div>
          ${
            images.length > 1
              ? `
            <div class="gallery-thumbnails" role="list" aria-label="Miniaturas de imágenes">
              ${images
                .map(
                  (img, i) => `
                <div class="thumb${i === 0 ? " active" : ""}" data-index="${i}" role="listitem"
                     tabindex="0" aria-label="Imagen ${i + 1}">
                  ${img ? `<img src="${img}" alt="${p.name} vista ${i + 1}" loading="lazy" />` : ""}
                </div>`,
                )
                .join("")}
            </div>`
              : ""
          }
        </div>

        <div class="product-info">
          ${
            p.category
              ? `<div class="product-category-badge">
                  <span class="badge badge-steel"><i data-lucide="tag" width="10" height="10"></i> ${p.category}</span>
                </div>`
              : ""
          }
          <h1 class="product-name">${p.name}</h1>

          <div class="product-price-block">
            <span class="product-price">${formatPrice(p.price)}</span>
            <span class="product-price-note">IVA incluido</span>
          </div>

          <div class="stock-indicator" aria-live="polite" id="stock-indicator">
            <span class="stock-dot ${stockClass}" aria-hidden="true"></span>
            <span class="${outOfStock ? "text-error" : lowStock ? "text-warning" : "text-success"}">${stockText}</span>
          </div>

          ${p.description ? `<p class="product-description">${p.description}</p>` : ""}

          <div class="add-to-cart-section">
            ${variantSelector}
            <div class="qty-selector" id="qty-selector">
              <span class="qty-label">Cantidad:</span>
              <div class="qty-controls" role="group" aria-label="Selector de cantidad">
                <button id="qty-dec" aria-label="Reducir cantidad">−</button>
                <input type="number" id="qty-input" value="1" min="1" max="${Math.max(stock, 1)}" aria-label="Cantidad" />
                <button id="qty-inc" aria-label="Aumentar cantidad">+</button>
              </div>
            </div>

            <div class="cart-actions">
              <button class="btn btn-primary" id="add-to-cart-btn" ${outOfStock ? "disabled" : ""}
                      aria-label="${outOfStock ? "Producto sin stock" : "Agregar al carrito"}">
                <i data-lucide="shopping-cart" width="18" height="18"></i>
                <span id="add-btn-label">${outOfStock ? "Sin Stock" : "Agregar al Carrito"}</span>
              </button>
              <button class="btn btn-ghost" id="wishlist-btn" aria-label="Agregar a lista de deseos">
                <i data-lucide="heart" width="18" height="18"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    `;

    $content.classList.remove("hidden");
    if (typeof lucide !== "undefined") lucide.createIcons({ elements: [$content] });

    bindProductEvents(p, images);
  }

  function renderMainImage(src, alt) {
    if (!src)
      return `
      <div class="card-image-placeholder" style="height:100%;min-height:320px">
        <i data-lucide="package" width="48" height="48"></i>
        <span>Sin imagen</span>
      </div>`;
    return `<img src="${src}" alt="${alt}" id="gallery-main-img" />`;
  }

  function refreshStockUI() {
    const stock = currentStock();
    const $input = document.getElementById("qty-input");
    const $btn = document.getElementById("add-to-cart-btn");
    const $label = document.getElementById("add-btn-label");
    selectedQty = Math.min(selectedQty, Math.max(stock, 1));
    if ($input) {
      $input.max = Math.max(stock, 1);
      $input.value = stock === 0 ? 0 : selectedQty;
      $input.disabled = stock === 0;
    }
    if ($btn) $btn.disabled = stock === 0;
    if ($label) $label.textContent = stock === 0 ? "Sin Stock" : "Agregar al Carrito";
  }

  function bindProductEvents(product, images) {
    if (images.length > 1) {
      document.querySelectorAll(".thumb").forEach((thumb) => {
        thumb.addEventListener("click", () => switchImage(thumb, images));
        thumb.addEventListener("keydown", (e) => {
          if (e.key === "Enter") switchImage(thumb, images);
        });
      });
    }

    // Selector de variante
    document.getElementById("variant-select")?.addEventListener("change", (e) => {
      selectedSku = e.target.value;
      selectedQty = 1;
      refreshStockUI();
    });

    const $input = document.getElementById("qty-input");
    const $dec = document.getElementById("qty-dec");
    const $inc = document.getElementById("qty-inc");
    if ($input && $dec && $inc) {
      $dec.addEventListener("click", () => {
        selectedQty = Math.max(1, selectedQty - 1);
        $input.value = selectedQty;
      });
      $inc.addEventListener("click", () => {
        selectedQty = Math.min(currentStock(), selectedQty + 1);
        $input.value = selectedQty;
      });
      $input.addEventListener("change", () => {
        const v = parseInt($input.value, 10);
        selectedQty = Math.min(Math.max(1, isNaN(v) ? 1 : v), currentStock());
        $input.value = selectedQty;
      });
    }

    document.getElementById("add-to-cart-btn")?.addEventListener("click", () => {
      if (currentStock() === 0) return;
      if (typeof window.Cart === "undefined") {
        showToast("Error al acceder al carrito", "error");
        return;
      }
      window.Cart.add(
        {
          id: product.id,
          name: product.name,
          price: product.price,
          image: images[0] || null,
          sku: selectedSku,
        },
        selectedQty,
      );
      showToast(`"${product.name}" agregado al carrito (×${selectedQty})`, "success");
    });

    document.getElementById("wishlist-btn")?.addEventListener("click", async () => {
      if (typeof Auth === "undefined" || !Auth.isAuthenticated()) {
        window.location.href = "/login.html";
        return;
      }
      try {
        await api.post(`/wishlist/${product.id}`);
        showToast("Agregado a tu lista de deseos", "success");
      } catch (err) {
        showToast(err.message || "No se pudo agregar a la lista", "error");
      }
    });
  }

  function switchImage(thumb, images) {
    const idx = parseInt(thumb.dataset.index, 10);
    const mainImg = document.getElementById("gallery-main-img");
    if (!mainImg || !images[idx]) return;
    mainImg.src = images[idx];
    document.querySelectorAll(".thumb").forEach((t) => t.classList.remove("active"));
    thumb.classList.add("active");
  }

  function hideLoading() {
    $loading?.classList.add("hidden");
  }

  function showError() {
    $loading?.classList.add("hidden");
    $error?.classList.remove("hidden");
    if (typeof lucide !== "undefined") lucide.createIcons({ elements: [$error] });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
