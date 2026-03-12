/**
 * MetalShop — Catálogo de Productos
 * Carga productos, filtros reactivos, búsqueda con debounce 300ms, paginación.
 */

(function CatalogPage() {
  'use strict';

  const PAGE_SIZE = 12;

  // ── Estado ─────────────────────────────────────────────────────────────────
  const state = {
    page: 0,
    total: 0,
    loading: false,
    filters: {
      search: '',
      category: '',
      min_price: '',
      max_price: '',
    },
  };

  // ── Referencias DOM ─────────────────────────────────────────────────────────
  const $grid       = document.getElementById('products-grid');
  const $count      = document.getElementById('results-count');
  const $pagination = document.getElementById('pagination');
  const $minPrice   = document.getElementById('min-price');
  const $maxPrice   = document.getElementById('max-price');
  const $resetBtn   = document.getElementById('reset-filters');
  const $applyBtn   = document.getElementById('apply-filters');
  const $sortSel    = document.getElementById('sort-select');
  const $navSearch  = document.getElementById('nav-search-input');
  const $catFilters = document.getElementById('category-filters');
  const $openFilt   = document.getElementById('open-filters');
  const $closeFilt  = document.getElementById('close-filters');
  const $sidebar    = document.getElementById('filters-sidebar');

  // Categorías del catálogo
  const CATEGORIES = [
    'Herramientas', 'Protección', 'Seguridad', 'Cuchillería',
    'Navegación', 'Iluminación', 'Accesorios', 'Escalada', 'Supervivencia',
  ];

  // ── Inicializar ─────────────────────────────────────────────────────────────
  function init() {
    buildCategoryFilters();
    loadFromURL();
    fetchProducts();
    bindEvents();
  }

  // ── Construir filtros de categoría ──────────────────────────────────────────
  function buildCategoryFilters() {
    const items = CATEGORIES.map((cat) => `
      <label class="filter-check">
        <input type="checkbox" name="category" value="${cat}" />
        <span>${cat}</span>
      </label>
    `).join('');
    $catFilters.innerHTML = `
      <label class="filter-check">
        <input type="checkbox" name="category" value="" checked id="cat-all"/>
        <label for="cat-all">Todas</label>
      </label>
      ${items}
    `;
  }

  // ── Leer estado inicial desde URL ───────────────────────────────────────────
  function loadFromURL() {
    const params = new URLSearchParams(location.search);
    if (params.get('search')) {
      state.filters.search = params.get('search');
      if ($navSearch) $navSearch.value = state.filters.search;
    }
    if (params.get('category')) {
      state.filters.category = params.get('category');
      const cb = $catFilters?.querySelector(`input[value="${state.filters.category}"]`);
      if (cb) cb.checked = true;
    }
  }

  // ── Fetch productos ──────────────────────────────────────────────────────────
  async function fetchProducts(resetPage = false) {
    if (state.loading) return;
    if (resetPage) state.page = 0;

    state.loading = true;
    renderSkeletons();

    try {
      const params = {
        limit: PAGE_SIZE,
        offset: state.page * PAGE_SIZE,
        ...(state.filters.search   && { search: state.filters.search }),
        ...(state.filters.category && { category: state.filters.category }),
        ...(state.filters.min_price && { min_price: state.filters.min_price }),
        ...(state.filters.max_price && { max_price: state.filters.max_price }),
      };

      const data = await api.get('/products', params);

      state.total = data.total;
      renderProducts(data.items);
      updateCount(data.total);
      renderPagination(data.total);
    } catch (err) {
      $grid.innerHTML = `
        <div class="no-results">
          <i data-lucide="alert-triangle" width="48" height="48"></i>
          <h3>Error al cargar productos</h3>
          <p>${err.message}</p>
          <button class="btn btn-ghost btn-sm" onclick="location.reload()">Reintentar</button>
        </div>`;
      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$grid] });
    } finally {
      state.loading = false;
    }
  }

  // ── Render ───────────────────────────────────────────────────────────────────
  function renderSkeletons() {
    $grid.innerHTML = Array.from({ length: 8 }, () => `
      <div class="product-card-skeleton">
        <div class="skeleton skeleton-img"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text-sm"></div>
        <div class="skeleton skeleton-price"></div>
      </div>
    `).join('');
  }

  function renderProducts(products) {
    if (!products.length) {
      $grid.innerHTML = `
        <div class="no-results">
          <i data-lucide="package-search" width="48" height="48"></i>
          <h3>Sin resultados</h3>
          <p>No encontramos productos con esos filtros. Intenta con otros términos.</p>
          <button class="btn btn-ghost btn-sm" id="clear-no-results">Limpiar filtros</button>
        </div>`;
      if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$grid] });
      document.getElementById('clear-no-results')?.addEventListener('click', resetFilters);
      return;
    }

    $grid.innerHTML = products.map(buildCard).join('');
    if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$grid] });

    // Añadir eventos a los botones "Agregar"
    $grid.querySelectorAll('.btn-add-cart').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const product = JSON.parse(btn.dataset.product);
        if (typeof window.Cart !== 'undefined') {
          window.Cart.add(product, 1);
          showToast(`"${product.name}" agregado al carrito`, 'success');
        }
      });
    });

    // Clic en card → detalle
    $grid.querySelectorAll('.product-card[data-id]').forEach((card) => {
      card.addEventListener('click', () => {
        window.location.href = `/product.html?id=${card.dataset.id}`;
      });
    });
  }

  function buildCard(p) {
    const imageUrl  = p.images?.[0] || null;
    const outOfStock = p.stock === 0;
    const lowStock   = p.stock > 0 && p.stock <= 5;

    const stockBadge = outOfStock
      ? `<span class="badge badge-error">Agotado</span>`
      : lowStock
        ? `<span class="badge badge-warning">Stock bajo</span>`
        : '';

    const image = imageUrl
      ? `<img src="${imageUrl}" alt="${p.name}" loading="lazy" />`
      : `<div class="card-image-placeholder"><i data-lucide="package" width="32" height="32"></i><span>Sin imagen</span></div>`;

    return `
      <article class="product-card" data-id="${p.id}" role="button" tabindex="0"
               aria-label="Ver ${p.name}, precio ${formatPrice(p.price)}">
        <div class="card-image">
          ${image}
          <div class="card-badges">${stockBadge}</div>
          <div class="card-actions-overlay">
            <button
              class="btn btn-primary btn-sm btn-add-cart"
              data-product='${JSON.stringify({ id: p.id, name: p.name, price: p.price, image: imageUrl })}'
              ${outOfStock ? 'disabled' : ''}
              aria-label="Agregar ${p.name} al carrito"
            >
              <i data-lucide="shopping-cart" width="14" height="14"></i>
              ${outOfStock ? 'Sin stock' : 'Agregar'}
            </button>
            <a href="/product.html?id=${p.id}" class="btn btn-secondary btn-sm"
               aria-label="Ver detalle de ${p.name}" onclick="event.stopPropagation()">
              <i data-lucide="eye" width="14" height="14"></i>
            </a>
          </div>
        </div>
        <div class="card-body">
          ${p.category ? `<span class="card-category">${p.category}</span>` : ''}
          <h2 class="card-name">${p.name}</h2>
          <div class="card-footer">
            <span class="card-price">${formatPrice(p.price)}</span>
            <span class="card-stock ${outOfStock ? 'out' : ''}">
              ${outOfStock ? 'Agotado' : `${p.stock} en stock`}
            </span>
          </div>
        </div>
      </article>
    `;
  }

  function updateCount(total) {
    $count.textContent = total === 0
      ? 'Sin resultados'
      : `${total} producto${total !== 1 ? 's' : ''} encontrado${total !== 1 ? 's' : ''}`;
  }

  function renderPagination(total) {
    const pages = Math.ceil(total / PAGE_SIZE);
    if (pages <= 1) { $pagination.style.display = 'none'; return; }

    $pagination.style.display = 'flex';
    const cur = state.page;

    let html = `
      <button class="page-btn" ${cur === 0 ? 'disabled' : ''} data-page="${cur - 1}" aria-label="Página anterior">
        <i data-lucide="chevron-left" width="16" height="16"></i>
      </button>
    `;

    for (let i = 0; i < pages; i++) {
      if (pages > 7 && Math.abs(i - cur) > 2 && i !== 0 && i !== pages - 1) {
        if (i === cur - 3 || i === cur + 3) html += `<span style="padding:0 4px;color:var(--text-muted)">…</span>`;
        continue;
      }
      html += `<button class="page-btn${i === cur ? ' active' : ''}" data-page="${i}" aria-label="Página ${i + 1}" aria-current="${i === cur}">${i + 1}</button>`;
    }

    html += `
      <button class="page-btn" ${cur >= pages - 1 ? 'disabled' : ''} data-page="${cur + 1}" aria-label="Página siguiente">
        <i data-lucide="chevron-right" width="16" height="16"></i>
      </button>
    `;

    $pagination.innerHTML = html;
    if (typeof lucide !== 'undefined') lucide.createIcons({ elements: [$pagination] });

    $pagination.querySelectorAll('.page-btn[data-page]').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.page = parseInt(btn.dataset.page, 10);
        fetchProducts();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    });
  }

  // ── Debounce ─────────────────────────────────────────────────────────────────
  function debounce(fn, delay) {
    let timer;
    return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
  }

  // ── Filtros ──────────────────────────────────────────────────────────────────
  function getSelectedCategory() {
    const checked = $catFilters?.querySelector('input[name="category"]:checked');
    return checked ? checked.value : '';
  }

  function applyFilters() {
    state.filters.category  = getSelectedCategory();
    state.filters.min_price = $minPrice?.value || '';
    state.filters.max_price = $maxPrice?.value || '';
    fetchProducts(true);

    // Cerrar sidebar móvil
    $sidebar?.classList.remove('mobile-open');
  }

  function resetFilters() {
    state.filters = { search: '', category: '', min_price: '', max_price: '' };
    if ($minPrice) $minPrice.value = '';
    if ($maxPrice) $maxPrice.value = '';
    if ($navSearch) $navSearch.value = '';
    $catFilters?.querySelectorAll('input[name="category"]').forEach((cb) => {
      cb.checked = cb.value === '';
    });
    fetchProducts(true);
  }

  // ── Eventos ──────────────────────────────────────────────────────────────────
  function bindEvents() {
    // Búsqueda desde navbar (debounce 300ms)
    $navSearch?.addEventListener('input', debounce((e) => {
      state.filters.search = e.target.value.trim();
      fetchProducts(true);
    }, 300));

    $navSearch?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        state.filters.search = e.target.value.trim();
        fetchProducts(true);
      }
    });

    // Categorías — solo un checkbox activo a la vez
    $catFilters?.addEventListener('change', (e) => {
      if (e.target.name !== 'category') return;
      $catFilters.querySelectorAll('input[name="category"]').forEach((cb) => {
        cb.checked = cb === e.target;
      });
    });

    // Aplicar / reset
    $applyBtn?.addEventListener('click', applyFilters);
    $resetBtn?.addEventListener('click', resetFilters);

    // Enter en inputs de precio
    [$minPrice, $maxPrice].forEach((el) => {
      el?.addEventListener('keydown', (e) => { if (e.key === 'Enter') applyFilters(); });
    });

    // Sidebar móvil
    $openFilt?.addEventListener('click', () => {
      $sidebar?.classList.add('mobile-open');
      if ($closeFilt) $closeFilt.style.display = 'flex';
    });

    $closeFilt?.addEventListener('click', () => {
      $sidebar?.classList.remove('mobile-open');
    });

    // Accesibilidad: teclado en cards
    $grid?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        const card = e.target.closest('[data-id]');
        if (card) { e.preventDefault(); window.location.href = `/product.html?id=${card.dataset.id}`; }
      }
    });
  }

  // ── Arrancar ─────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
