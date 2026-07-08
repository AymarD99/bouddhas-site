// Page boutique — grille premium + filtres dynamiques + tri + animations
document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('product-grid');
  if (!grid) return;

  const params = new URLSearchParams(window.location.search);
  const categorie = params.get('categorie');

  try {
    const products = await shopify.getProducts(100);
    window.__productsCache = products;
    
    const types = [...new Set(products.map(p => p.productType).filter(Boolean))].sort();
    let filtered = categorie ? products.filter(p => p.productType === categorie) : products;

    function sortProducts(list, sortBy) {
      switch(sortBy) {
        case 'price-asc': return [...list].sort((a,b) => parseFloat(a.priceRange.minVariantPrice.amount) - parseFloat(b.priceRange.minVariantPrice.amount));
        case 'price-desc': return [...list].sort((a,b) => parseFloat(b.priceRange.minVariantPrice.amount) - parseFloat(a.priceRange.minVariantPrice.amount));
        case 'newest': return [...list].sort((a,b) => new Date(b.createdAt) - new Date(a.createdAt));
        case 'name': return [...list].sort((a,b) => a.title.localeCompare(b.title));
        default: return list;
      }
    }

    const toolbar = document.getElementById('product-toolbar');
    if (toolbar) {
      toolbar.innerHTML = `
        <div class="shop-toolbar">
          <div class="shop-filters">
            <button class="filter-btn ${!categorie?'active':''}" onclick="window.location.href='/produits'">Tous (${products.length})</button>
            ${types.slice(0, 8).map(t => {
              const count = products.filter(p => p.productType === t).length;
              return `<button class="filter-btn ${categorie===t?'active':''}" onclick="window.location.href='/produits?categorie=${encodeURIComponent(t)}'">${t} (${count})</button>`;
            }).join('')}
          </div>
          <div class="shop-sort">
            <span class="sort-label">Trier par :</span>
            <select id="sort-select" onchange="renderProducts()" class="sort-select">
              <option value="newest">Nouveautés</option>
              <option value="price-asc">Prix croissant</option>
              <option value="price-desc">Prix décroissant</option>
              <option value="name">Nom (A-Z)</option>
            </select>
          </div>
        </div>
        ${categorie ? `<div class="shop-current"><h1>${categorie}</h1><p>${filtered.length} produit(s) dans cette catégorie</p></div>` : ''}
      `;
    }

    window.renderProducts = function() {
      const sortBy = document.getElementById('sort-select')?.value || 'newest';
      const sorted = sortProducts(filtered, sortBy);

      if (sorted.length === 0) {
        grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:4rem;color:var(--text-light);">
          <div style="font-size:3rem;margin-bottom:1rem;">🔍</div>
          <p>Aucun produit dans cette catégorie</p>
          <a href="/produits" class="btn-primary" style="margin-top:1.5rem;">Voir tous les produits</a>
        </div>`;
        return;
      }

      grid.innerHTML = sorted.map(p => {
        const img = p.images?.edges?.[0]?.node?.url || 'https://placehold.co/400x400/FDF8F0/C9A96E?text=Bouddhas';
        const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
        const isNew = shopify.isNew(p.createdAt);
        const numPrice = parseFloat(p.priceRange.minVariantPrice.amount);
        const hasPromo = numPrice > 0 && numPrice < 30;
        
        return `
          <div class="product-card">
            <div class="image-wrap">
              ${isNew ? '<span style="position:absolute;top:12px;right:12px;background:var(--gold);color:var(--white);padding:0.3rem 0.8rem;border-radius:20px;font-size:0.7rem;font-weight:700;letter-spacing:0.5px;z-index:2;">NOUVEAU</span>' : ''}
              ${hasPromo && !isNew ? '<span class="badge-sale">PROMO</span>' : ''}
              <a href="/produit/${p.handle}">
                <img src="${img}" alt="${p.title}" loading="lazy">
              </a>
              <div class="quick-view">
                <a href="/produit/${p.handle}" style="color:white;text-decoration:none;">👁️ Voir le produit</a>
              </div>
            </div>
            <div class="product-info">
              <a href="/produit/${p.handle}" style="text-decoration:none;color:inherit;">
                <h3>${p.title}</h3>
              </a>
              ${p.productType ? `<div style="color:var(--text-light);font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">${p.productType}</div>` : ''}
              <div class="price">${price}</div>
              ${p.availableForSale 
                ? `<button class="btn-add" onclick="addToCart('${p.handle}')">Ajouter au panier</button>`
                : `<button class="btn-add" style="background:var(--text-light);" disabled>Rupture de stock</button>`
              }
            </div>
          </div>
        `;
      }).join('');
      
      // Animate cards
      grid.querySelectorAll('.product-card').forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
          card.style.transition = 'all 0.5s ease';
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, i * 50);
      });
    };

    renderProducts();
  } catch (e) {
    grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">Erreur: ${e.message}</div>`;
  }
});