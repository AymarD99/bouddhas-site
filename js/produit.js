// Page détail produit
document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('product-detail');
  if (!container) return;

  // Lire le handle depuis l'URL : /produit/le-handle
  const handle = window.location.pathname.replace('/produit/', '');
  if (!handle) {
    container.innerHTML = '<div style="text-align:center;padding:3rem;">Produit non trouvé</div>';
    return;
  }

  try {
    const p = await shopify.getProductByHandle(handle);
    if (!p) {
      container.innerHTML = '<div style="text-align:center;padding:3rem;">Produit introuvable</div>';
      return;
    }

    const images = p.images?.edges?.map(e => e.node.url) || [];
    const mainImg = images[0] || 'https://placehold.co/600x600/FDF8F0/C4A265?text=Bouddhas';
    const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
    const variantId = p.variants?.edges?.[0]?.node?.id || null;

    container.innerHTML = `
      <div class="product-detail">
        <div>
          <img src="${mainImg}" alt="${p.title}" style="width:100%;border-radius:15px;">
          <div style="display:flex;gap:0.5rem;margin-top:1rem;">
            ${images.slice(1, 4).map(url => `<img src="${url}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;cursor:pointer;" onclick="this.parentElement.previousElementSibling.src=this.src">`).join('')}
          </div>
        </div>
        <div class="info">
          <h1>${p.title}</h1>
          ${p.productType ? `<div style="color:var(--gold-dark);margin-bottom:0.5rem;">${p.productType}</div>` : ''}
          <div class="price">${price}</div>
          ${p.availableForSale ? '<div style="color:green;margin-bottom:1rem;">✅ En stock</div>' : '<div style="color:#c00;margin-bottom:1rem;">❌ Rupture de stock</div>'}
          <div class="description">${p.descriptionHtml || p.description || ''}</div>
          
          ${variantId ? `
            <button class="btn-primary" onclick="addToCartFromDetail('${variantId}','${p.title.replace(/'/g,"\\'")}','${p.priceRange.minVariantPrice.amount}')" style="width:100%;margin-top:1.5rem;">
              Ajouter au panier
            </button>
          ` : ''}

          <div style="margin-top:2rem;padding-top:1.5rem;border-top:1px solid var(--beige);">
            ${p.tags?.length ? `<div style="display:flex;gap:0.5rem;flex-wrap:wrap;">${p.tags.map(t => `<span style="background:var(--beige);padding:0.3rem 0.8rem;border-radius:15px;font-size:0.85rem;">#${t}</span>`).join('')}</div>` : ''}
          </div>
        </div>
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-light);">Erreur: ${e.message}</div>`;
  }
});