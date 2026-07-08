document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('product-grid');
  if (!grid) return;

  try {
    const products = await shopify.getProducts(12);
    grid.innerHTML = products.map(p => {
      const img = p.images?.edges?.[0]?.node?.url || 'https://placehold.co/400x400/FDF8F0/C4A265?text=Bouddhas';
      const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
      const handle = p.handle;
      return `
        <div class="product-card">
          <a href="/produit.html?handle=${handle}">
            <img src="${img}" alt="${p.title}" loading="lazy">
          </a>
          <div class="product-info">
            <a href="/produit.html?handle=${handle}" style="text-decoration:none;color:inherit;">
              <h3>${p.title}</h3>
            </a>
            <div class="price">${price}</div>
            <button class="btn-add" onclick="addToCart('${p.title}')">Ajouter au panier</button>
          </div>
        </div>
      `;
    }).join('');
  } catch (e) {
    grid.innerHTML = `<div class="loading">Erreur de chargement: ${e.message}</div>`;
  }
});

async function addToCart(title) {
  // Simple notification pour le MVP
  alert(`"${title}" ajouté au panier ! (Fonctionnalité paiement à venir via Shopify Checkout)`);
}
