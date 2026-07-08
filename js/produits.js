// Page boutique — grille + filtres + tri (FIX: ajout tri)
document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('product-grid');
  if (!grid) return;

  const params = new URLSearchParams(window.location.search);
  const categorie = params.get('categorie');

  try {
    const products = await shopify.getProducts(100);
    window.__productsCache = products;
    
    // Récupérer les types uniques pour les filtres
    const types = [...new Set(products.map(p => p.productType).filter(Boolean))].sort();
    
    let filtered = categorie 
      ? products.filter(p => p.productType === categorie)
      : products;

    // Fonction de tri
    function sortProducts(list, sortBy) {
      switch(sortBy) {
        case 'price-asc': return [...list].sort((a,b) => parseFloat(a.priceRange.minVariantPrice.amount) - parseFloat(b.priceRange.minVariantPrice.amount));
        case 'price-desc': return [...list].sort((a,b) => parseFloat(b.priceRange.minVariantPrice.amount) - parseFloat(a.priceRange.minVariantPrice.amount));
        case 'newest': return [...list].sort((a,b) => new Date(b.createdAt) - new Date(a.createdAt));
        case 'name': return [...list].sort((a,b) => a.title.localeCompare(b.title));
        default: return list;
      }
    }

    // Barre de tri + filtres
    const toolbar = document.getElementById('product-toolbar');
    if (toolbar) {
      toolbar.innerHTML = `
        <div style="display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between;margin-bottom:2rem;">
          <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
            <button class="filter-btn ${!categorie?'active':''}" onclick="window.location.href='/produits'">Tous</button>
            ${types.slice(0, 8).map(t => `<button class="filter-btn ${categorie===t?'active':''}" onclick="window.location.href='/produits?categorie=${encodeURIComponent(t)}'">${t}</button>`).join('')}
          </div>
          <select id="sort-select" onchange="renderProducts()" style="padding:0.5rem 1rem;border:2px solid var(--beige);border-radius:8px;font-size:0.9rem;cursor:pointer;">
            <option value="newest">Nouveautés</option>
            <option value="price-asc">Prix croissant</option>
            <option value="price-desc">Prix décroissant</option>
            <option value="name">Nom (A-Z)</option>
          </select>
        </div>
      `;
    }

    // Fonction de rendu
    window.renderProducts = function() {
      const sortBy = document.getElementById('sort-select')?.value || 'newest';
      const sorted = sortProducts(filtered, sortBy);

      if (sorted.length === 0) {
        grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">Aucun produit dans cette catégorie</div>`;
        return;
      }

      grid.innerHTML = sorted.map(p => {
        const img = p.images?.edges?.[0]?.node?.url || 'https://placehold.co/400x400/FDF8F0/C9A96E?text=Bouddhas';
        const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
        const isNew = shopify.isNew(p.createdAt);
        return `
          <div class="product-card">
            <div class="image-wrap">
              ${isNew ? '<span style="position:absolute;top:12px;right:12px;background:var(--gold);color:var(--white);padding:0.3rem 0.8rem;border-radius:20px;font-size:0.75rem;font-weight:700;">NOUVEAU</span>' : ''}
              <a href="/produit/${p.handle}">
                <img src="${img}" alt="${p.title}" loading="lazy">
              </a>
            </div>
            <div class="product-info">
              <a href="/produit/${p.handle}" style="text-decoration:none;color:inherit;">
                <h3>${p.title}</h3>
              </a>
              ${p.productType ? `<div style="color:var(--text-light);font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">${p.productType}</div>` : ''}
              <div class="price">${price}</div>
              ${p.availableForSale 
                ? `<button class="btn-add" onclick="addToCart('${p.handle}')">Ajouter au panier</button>`
                : `<button class="btn-add" style="background:var(--text-light);" disabled>Rupture</button>`
              }
            </div>
          </div>
        `;
      }).join('');
    };

    renderProducts();
  } catch (e) {
    grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">Erreur: ${e.message}</div>`;
  }
});