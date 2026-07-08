// Accueil — produits avec badge Nouveau
document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('product-grid');
  if (!grid) return;

  try {
    const products = await shopify.getProducts(12);
    grid.innerHTML = products.map(p => {
      const img = p.images?.edges?.[0]?.node?.url || 'https://placehold.co/400x400/FDF8F0/C9A96E?text=Bouddhas';
      const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
      const isNew = shopify.isNew(p.createdAt);
      return `
        <div class="product-card">
          <div class="image-wrap">
            ${isNew ? '<span style="position:absolute;top:12px;right:12px;background:var(--gold);color:var(--white);padding:0.3rem 0.8rem;border-radius:20px;font-size:0.75rem;font-weight:700;letter-spacing:0.5px;z-index:2;">NOUVEAU</span>' : ''}
            <a href="/produit/${p.handle}">
              <img src="${img}" alt="${p.title}" loading="lazy">
            </a>
          </div>
          <div class="product-info">
            <a href="/produit/${p.handle}" style="text-decoration:none;color:inherit;">
              <h3>${p.title}</h3>
            </a>
            ${p.productType ? `<div style="color:var(--text-light);font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;">${p.productType}</div>` : ''}
            <div class="price">${price}</div>
            <button class="btn-add" onclick="addToCart('${p.handle}')">Ajouter au panier</button>
          </div>
        </div>
      `;
    }).join('');
  } catch (e) {
    grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">✨ ${e.message}</div>`;
  }
});

// Cache produits pour le panier
window.__productsCache = null;

async function addToCart(handle) {
  if (!window.__productsCache) {
    window.__productsCache = await shopify.getProducts(100);
  }
  const p = window.__productsCache.find(x => x.handle === handle);
  if (!p) return;

  let panier = JSON.parse(localStorage.getItem('bouddhas_panier') || '[]');
  panier.push({ 
    handle, 
    title: p.title, 
    price: p.priceRange.minVariantPrice.amount,
    img: p.images?.edges?.[0]?.node?.url || ''
  });
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  updateCartCount();
  showToast(`✅ "${p.title}" ajouté`);
}

function updateCartCount() {
  const panier = JSON.parse(localStorage.getItem('bouddhas_panier') || '[]');
  const el = document.getElementById('cart-count');
  if (el) el.textContent = panier.length;
}

function toast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 2500);
}

updateCartCount();