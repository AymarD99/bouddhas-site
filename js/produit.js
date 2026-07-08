// Page détail produit
document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('product-detail');
  if (!container) return;

  const handle = window.location.pathname.replace('/produit/', '');
  if (!handle) {
    container.innerHTML = '<div style="text-align:center;padding:4rem;">Produit non trouvé</div>';
    return;
  }

  try {
    const p = await shopify.getProductByHandle(handle);
    if (!p) {
      container.innerHTML = '<div style="text-align:center;padding:4rem;">Produit introuvable</div>';
      return;
    }

    const images = p.images?.edges?.map(e => e.node.url) || [];
    const mainImg = images[0] || 'https://placehold.co/600x600/FDF8F0/C9A96E?text=Bouddhas';
    const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
    const isNew = shopify.isNew(p.createdAt);

    container.innerHTML = `
      <div class="product-detail">
        <div>
          <img class="main-image" src="${mainImg}" alt="${p.title}" id="main-img">
          ${images.length > 1 ? `
            <div class="thumbs">
              ${images.map(url => `<img src="${url}" onclick="document.getElementById('main-img').src=this.src">`).join('')}
            </div>
          ` : ''}
        </div>
        <div class="info">
          <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.5rem;">
            <h1>${p.title}</h1>
            ${isNew ? '<span style="background:var(--gold);color:var(--white);padding:0.25rem 0.8rem;border-radius:20px;font-size:0.75rem;font-weight:700;">NOUVEAU</span>' : ''}
          </div>
          ${p.productType ? `<div style="color:var(--text-light);font-size:0.85rem;text-transform:uppercase;letter-spacing:2px;margin-bottom:0.5rem;">${p.productType}</div>` : ''}
          <div class="price">${price}</div>
          <div style="margin-bottom:1.5rem;">
            ${p.availableForSale 
              ? '<span style="color:#2e7d32;font-size:0.9rem;">✅ En stock</span>' 
              : '<span style="color:#c62828;font-size:0.9rem;">❌ Épuisé</span>'}
          </div>
          <div class="description">${p.descriptionHtml || p.description || ''}</div>
          
          ${p.variants?.edges?.[0]?.node && p.availableForSale ? `
            <button class="btn-primary" onclick="addToCart('${p.handle}')" style="width:100%;margin-top:1rem;">
              Ajouter au panier — ${price}
            </button>
          ` : ''}

          ${p.tags?.length ? `
            <div style="margin-top:2rem;padding-top:1.5rem;border-top:1px solid var(--beige);">
              <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
                ${p.tags.map(t => `<span style="background:var(--beige);padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;color:var(--text-light);">${t}</span>`).join('')}
              </div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div style="text-align:center;padding:4rem;color:var(--text-light);">Erreur: ${e.message}</div>`;
  }
});