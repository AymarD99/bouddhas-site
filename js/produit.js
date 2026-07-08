// Page détail produit — version PREMIUM (FIX: variantes + quantité + variantId)
document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('product-detail');
  if (!container) return;

  const handle = window.location.pathname.replace('/produit/', '').replace(/\/$/, '');
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

    // Mettre en cache
    if (!window.__productsCache) window.__productsCache = [];
    if (!window.__productsCache.find(x => x.handle === handle)) {
      window.__productsCache.push(p);
    }

    const images = p.images?.edges?.map(e => e.node.url) || [];
    const mainImg = images[0] || 'https://placehold.co/600x600/FDF8F0/C9A96E?text=Bouddhas';
    const variants = p.variants?.edges?.map(e => e.node) || [];
    const defaultVariant = variants[0];
    const defaultPrice = defaultVariant ? shopify.formatPrice(defaultVariant.price.amount) : shopify.formatPrice(p.priceRange.minVariantPrice.amount);
    const isNew = shopify.isNew(p.createdAt);
    const desc = p.descriptionHtml || p.description || '';

    // Construire le sélecteur de variantes
    let variantSelector = '';
    if (variants.length > 1) {
      variantSelector = `
        <div class="product-options">
          <div class="option-label">Variante :</div>
          <select id="variant-select" onchange="onVariantChange()" style="padding:0.6rem 1rem;border:2px solid var(--beige);border-radius:8px;font-size:0.9rem;cursor:pointer;min-width:200px;">
            ${variants.map((v, i) => `<option value="${v.id}" data-price="${v.price.amount}" ${i===0?'selected':''}>${v.title} — ${shopify.formatPrice(v.price.amount)}</option>`).join('')}
          </select>
        </div>
      `;
    } else if (defaultVariant) {
      variantSelector = `<input type="hidden" id="variant-select" value="${defaultVariant.id}">`;
    }

    container.innerHTML = `
      <div class="product-detail">
        <div class="gallery-wrap">
          <div class="gallery-main">
            <img src="${mainImg}" alt="${p.title}" id="main-img" class="gallery-img">
          </div>
          ${images.length > 1 ? `
            <div class="gallery-thumbs">
              ${images.map((url, i) => `<div class="gallery-thumb ${i===0?'active':''}" onclick="switchImage(this, '${url}')"><img src="${url}" alt=""></div>`).join('')}
            </div>
          ` : ''}
        </div>
        <div class="info">
          <div class="breadcrumb">
            <a href="/">Accueil</a> / 
            ${p.productType ? `<a href="/produits?categorie=${p.productType}">${p.productType}</a> / ` : ''}
            <span>${p.title}</span>
          </div>
          <div class="product-title-row">
            <h1>${p.title}</h1>
            ${isNew ? '<span class="badge-new">NOUVEAU</span>' : ''}
          </div>
          ${p.productType ? `<div class="product-type">${p.productType}</div>` : ''}
          <div class="price-row">
            <div class="product-price" id="display-price">${defaultPrice}</div>
            ${p.availableForSale ? '<span class="stock-badge in-stock">✅ En stock</span>' : '<span class="stock-badge out-of-stock">❌ Épuisé</span>'}
          </div>
          ${variantSelector}
          <div class="product-options">
            <div class="option-label">Quantité :</div>
            <div class="qty-selector">
              <button class="qty-btn" onclick="changeQty(-1)">−</button>
              <span class="qty-value" id="qty-value">1</span>
              <button class="qty-btn" onclick="changeQty(1)">+</button>
            </div>
          </div>
          ${defaultVariant && p.availableForSale ? `
            <button class="btn-add-cart" onclick="addToCartFromPage('${p.handle}')">
              <span>🛒</span> Ajouter au panier — <span id="btn-price">${defaultPrice}</span>
            </button>
          ` : ''}
          <div class="payment-badges">
            <span>🔒 Paiement sécurisé</span>
            <div class="mini-payments"><span>CB</span><span>Visa</span><span>MC</span><span>PayPal</span><span>Apple Pay</span></div>
          </div>
          <div class="product-promises">
            <div class="promise"><span>🚚</span> Livraison offerte dès 50€</div>
            <div class="promise"><span>🔄</span> Retour sous 14 jours</div>
            <div class="promise"><span>💎</span> Pierre naturelle authentique</div>
          </div>
          <div class="product-accordion">
            <div class="accordion-item active">
              <div class="accordion-header" onclick="toggleAccordion(this)">
                📖 Description
                <svg class="accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </div>
              <div class="accordion-body">${desc || 'Bijou artisanal en pierre naturelle. Chaque pièce est unique.'}</div>
            </div>
            <div class="accordion-item">
              <div class="accordion-header" onclick="toggleAccordion(this)">
                💎 Propriétés de la pierre
                <svg class="accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </div>
              <div class="accordion-body">
                <p>Chaque pierre naturelle possède des vertus uniques.</p>
                <ul style="margin-top:0.8rem;padding-left:1.2rem;line-height:2;">
                  <li><strong>Purification :</strong> Eau froide 1 min</li>
                  <li><strong>Recharge :</strong> Lumière lunaire</li>
                  <li><strong>Programmation :</strong> Formulez votre intention</li>
                </ul>
              </div>
            </div>
            <div class="accordion-item">
              <div class="accordion-header" onclick="toggleAccordion(this)">
                🚚 Livraison & Retours
                <svg class="accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </div>
              <div class="accordion-body">
                <p><strong>France :</strong> 3-5 jours — 4,90€ (offert dès 50€)</p>
                <p><strong>Europe :</strong> 5-8 jours — 9,90€</p>
                <p>✅ Retours sous 14 jours</p>
              </div>
            </div>
            <div class="accordion-item">
              <div class="accordion-header" onclick="toggleAccordion(this)">
                💳 Paiement sécurisé
                <svg class="accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </div>
              <div class="accordion-body">
                <p>🔒 Transactions cryptées via Shopify.</p>
                <p>CB, Visa, Mastercard, PayPal, Apple Pay, Shop Pay.</p>
              </div>
            </div>
          </div>
          ${p.tags?.length ? `<div class="product-tags">${p.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
          <div class="related-section" id="related-products">
            <h3>✨ Vous aimerez aussi</h3>
            <div class="related-grid" id="related-grid"><div style="color:var(--text-light);font-size:0.9rem;">Chargement...</div></div>
          </div>
        </div>
      </div>
    `;
    loadRelated(p.handle, p.productType);
  } catch (e) {
    container.innerHTML = `<div style="text-align:center;padding:4rem;color:var(--text-light);">Erreur: ${e.message}</div>`;
  }
});

function switchImage(el, url) {
  document.getElementById('main-img').src = url;
  document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
}

let qty = 1;
function changeQty(delta) {
  qty = Math.max(1, qty + delta);
  document.getElementById('qty-value').textContent = qty;
}

function onVariantChange() {
  const select = document.getElementById('variant-select');
  const selectedOption = select.options[select.selectedIndex];
  const price = shopify.formatPrice(selectedOption.dataset.price);
  document.getElementById('display-price').textContent = price;
  document.getElementById('btn-price').textContent = price;
}

// addToCart avec variantId + quantité depuis la page produit
async function addToCartFromPage(handle) {
  const select = document.getElementById('variant-select');
  const variantId = select ? select.value : null;
  await addToCart(handle, qty, variantId);
}

function toggleAccordion(header) {
  const item = header.closest('.accordion-item');
  const isOpen = item.classList.contains('active');
  document.querySelectorAll('.accordion-item').forEach(i => i.classList.remove('active'));
  if (!isOpen) item.classList.add('active');
}

async function loadRelated(handle, type) {
  const grid = document.getElementById('related-grid');
  if (!grid) return;
  try {
    const products = await shopify.getProducts(50);
    const related = products.filter(p => p.handle !== handle && p.productType === type).slice(0, 4);
    if (related.length === 0) { document.getElementById('related-products')?.remove(); return; }
    grid.innerHTML = related.map(p => {
      const img = p.images?.edges?.[0]?.node?.url || '';
      const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
      return `<a href="/produit/${p.handle}" class="related-card"><img src="${img}" alt="${p.title}"><div class="related-info"><div class="related-title">${p.title}</div><div class="related-price">${price}</div></div></a>`;
    }).join('');
  } catch(e) { grid.innerHTML = ''; }
}

window.switchImage = switchImage;
window.changeQty = changeQty;
window.onVariantChange = onVariantChange;
window.addToCartFromPage = addToCartFromPage;
window.toggleAccordion = toggleAccordion;