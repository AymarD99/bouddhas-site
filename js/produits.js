// Page boutique — chargement avec filtre catégorie
document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('product-grid');
  if (!grid) return;

  // Lire le paramètre categorie dans l'URL
  const params = new URLSearchParams(window.location.search);
  const categorie = params.get('categorie');

  try {
    const products = await shopify.getProducts(100);
    
    // Filtrer par catégorie si spécifié
    const filtres = categorie 
      ? products.filter(p => p.productType === categorie)
      : products;

    if (filtres.length === 0) {
      grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">Aucun produit trouvé dans cette catégorie.</div>`;
      return;
    }

    grid.innerHTML = filtres.map(p => {
      const img = p.images?.edges?.[0]?.node?.url || 'https://placehold.co/400x400/FDF8F0/C4A265?text=Bouddhas';
      const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
      const handle = p.handle;
      return `
        <div class="product-card">
          <a href="/produit/${handle}">
            <img src="${img}" alt="${p.title}" loading="lazy">
          </a>
          <div class="product-info">
            <a href="/produit/${handle}" style="text-decoration:none;color:inherit;">
              <h3>${p.title}</h3>
            </a>
            ${p.productType ? `<div style="color:var(--gold-dark);font-size:0.85rem;margin-bottom:0.3rem;">${p.productType}</div>` : ''}
            <div class="price">${price}</div>
            <button class="btn-add" onclick="addToCart('${handle}')">Ajouter au panier</button>
          </div>
        </div>
      `;
    }).join('');
  } catch (e) {
    grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">Erreur: ${e.message}</div>`;
  }
});