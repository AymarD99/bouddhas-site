// Page boutique — grille + filtres
document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('product-grid');
  if (!grid) return;

  const params = new URLSearchParams(window.location.search);
  const categorie = params.get('categorie');

  try {
    const products = await shopify.getProducts(100);
    const filtres = categorie 
      ? products.filter(p => p.productType === categorie)
      : products;

    if (filtres.length === 0) {
      grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">Aucun produit dans cette catégorie</div>`;
      return;
    }

    grid.innerHTML = filtres.map(p => {
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
  } catch (e) {
    grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">Erreur: ${e.message}</div>`;
  }
});