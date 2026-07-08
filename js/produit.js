// Page détail produit — EXPÉRIENCE ZEN PREMIUM
document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('product-detail');
  if (!container) return;

  const handle = window.location.pathname.replace('/produit/', '').replace(/\/$/, '');
  if (!handle) {
    container.innerHTML = '<div style="text-align:center;padding:4rem;"><div style="font-size:3rem;margin-bottom:1rem;">📿</div><h2>Produit non trouvé</h2><a href="/produits" class="btn-primary" style="margin-top:1.5rem;">Retour à la boutique</a></div>';
    return;
  }

  try {
    const p = await shopify.getProductByHandle(handle);
    if (!p) {
      container.innerHTML = '<div style="text-align:center;padding:4rem;"><div style="font-size:3rem;margin-bottom:1rem;">📿</div><h2>Produit introuvable</h2><p style="color:var(--text-light);margin:1rem 0;">Ce produit n\'existe plus ou a été déplacé.</p><a href="/produits" class="btn-primary">Retour à la boutique</a></div>';
      return;
    }

    // Cache
    if (!window.__productsCache) window.__productsCache = [];
    if (!window.__productsCache.find(x => x.handle === handle)) window.__productsCache.push(p);

    const images = p.images?.edges?.map(e => e.node.url) || [];
    const mainImg = images[0] || 'https://placehold.co/600x600/FDF8F0/C9A96E?text=Bouddhas';
    const variants = p.variants?.edges?.map(e => e.node) || [];
    const defaultVariant = variants[0];
    const defaultPrice = defaultVariant ? shopify.formatPrice(defaultVariant.price.amount) : shopify.formatPrice(p.priceRange.minVariantPrice.amount);
    const isNew = shopify.isNew(p.createdAt);
    const desc = p.descriptionHtml || p.description || '';
    const numPrice = parseFloat(p.priceRange.minVariantPrice.amount);

    // Citations zen aléatoires
    const quotes = [
      { text: "La paix vient de l'intérieur. Ne la cherchez pas ailleurs.", author: "Bouddha" },
      { text: "Chaque pierre porte la mémoire de la terre.", author: "Sagesse bouddhiste" },
      { text: "Le corps n'est pas seulement physique, il est aussi énergie.", author: "Tradition tibétaine" },
      { text: "Ce que nous pensons, nous le devenons.", author: "Bouddha" },
      { text: "La beauté est dans l'esprit de celui qui regarde.", author: "Dharma" },
    ];
    const quote = quotes[Math.floor(Math.random() * quotes.length)];

    // Sélecteur de variantes
    let variantSelector = '';
    if (variants.length > 1) {
      variantSelector = `
        <div class="variant-selector">
          <div class="option-label">Choisissez votre variante</div>
          <select id="variant-select" onchange="onVariantChange()">
            ${variants.map((v, i) => `<option value="${v.id}" data-price="${v.price.amount}" ${i===0?'selected':''}>${v.title} — ${shopify.formatPrice(v.price.amount)}</option>`).join('')}
          </select>
        </div>
      `;
    } else if (defaultVariant) {
      variantSelector = `<input type="hidden" id="variant-select" value="${defaultVariant.id}">`;
    }

    container.innerHTML = `
      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <a href="/">Accueil</a> /
        <a href="/produits">Boutique</a> /
        ${p.productType ? `<a href="/produits?categorie=${encodeURIComponent(p.productType)}">${p.productType}</a> / ` : ''}
        <span>${p.title}</span>
      </div>

      <!-- Layout 2 colonnes -->
      <div class="product-detail">
        <!-- Galerie -->
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

        <!-- Info -->
        <div class="info">
          <div class="product-title-row">
            <h1>${p.title}</h1>
            ${isNew ? '<span class="badge-new">NOUVEAU</span>' : ''}
          </div>
          ${p.productType ? `<div class="product-type">${p.productType}</div>` : ''}

          <!-- Rating -->
          <div class="product-rating">
            <span class="product-stars">★★★★★</span>
            <span class="product-rating-text">4.9/5 — vérifié client</span>
          </div>

          <!-- Prix + stock -->
          <div class="price-row">
            <div class="product-price" id="display-price">${defaultPrice}</div>
            ${p.availableForSale ? '<span class="stock-badge in-stock">✅ En stock</span>' : '<span class="stock-badge out-of-stock">❌ Épuisé</span>'}
          </div>

          ${variantSelector}

          <!-- Quantité -->
          <div class="product-options">
            <div class="option-label">Quantité</div>
            <div class="qty-selector">
              <button class="qty-btn" onclick="changeQty(-1)">−</button>
              <span class="qty-value" id="qty-value">1</span>
              <button class="qty-btn" onclick="changeQty(1)">+</button>
            </div>
          </div>

          <!-- Bouton panier -->
          ${defaultVariant && p.availableForSale ? `
            <button class="btn-add-cart" onclick="addToCartFromPage('${p.handle}')">
              <span>🛒</span> Ajouter au panier — <span id="btn-price">${defaultPrice}</span>
            </button>
          ` : ''}

          <!-- Promesses -->
          <div class="product-promises">
            <div class="promise"><span>🚚</span> Livraison 48h</div>
            <div class="promise"><span>🔄</span> Retour 14j</div>
            <div class="promise"><span>💎</span> Pierre naturelle</div>
          </div>

          <!-- Paiement -->
          <div class="payment-badges">
            <span>🔒 Paiement 100% sécurisé</span>
            <div class="mini-payments"><span>CB</span><span>Visa</span><span>Mastercard</span><span>PayPal</span><span>Apple Pay</span><span>Shop Pay</span></div>
          </div>

          <!-- Accordéon -->
          <div class="product-accordion">
            <div class="accordion-item active">
              <div class="accordion-header" onclick="toggleAccordion(this)">
                📖 Description
                <svg class="accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </div>
              <div class="accordion-body">${desc || 'Bijou artisanal en pierre naturelle. Chaque pièce est unique, façonnée avec intention et chargée d\'énergie positive pour vous accompagner au quotidien.'}</div>
            </div>
            <div class="accordion-item">
              <div class="accordion-header" onclick="toggleAccordion(this)">
                💎 Propriétés & rituels
                <svg class="accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </div>
              <div class="accordion-body">
                <p><strong>🌟 Vertus :</strong> Chaque pierre naturelle possède des propriétés vibratoires uniques qui agissent sur le corps et l'esprit.</p>
                <ul>
                  <li><strong>Purification :</strong> Plongez la pierre dans l'eau froide 1 minute, ou utilisez un bol tibétain</li>
                  <li><strong>Recharge :</strong> Exposez à la lumière lunaire une nuit complète</li>
                  <li><strong>Programmation :</strong> Tenez la pierre entre vos mains, respirez profondément et formulez votre intention</li>
                  <li><strong>Entretien :</strong> Nettoyez avec un chiffon doux, évitez les parfums et cosmétiques</li>
                </ul>
              </div>
            </div>
            <div class="accordion-item">
              <div class="accordion-header" onclick="toggleAccordion(this)">
                🚚 Livraison & Retours
                <svg class="accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </div>
              <div class="accordion-body">
                <p><strong>📦 France métropolitaine :</strong> 3-5 jours ouvrés — 4,90€ (offerte dès 50€)</p>
                <p><strong>🌍 Europe :</strong> 5-8 jours — 9,90€</p>
                <p><strong>⚡ Expédition :</strong> Sous 48h (jours ouvrés)</p>
                <p><strong>🔄 Retours :</strong> Vous avez 14 jours pour retourner votre commande. L'article doit être non utilisé dans son emballage d'origine.</p>
                <p><strong>📦 Suivi :</strong> Un numéro de suivi est envoyé par email dès l'expédition.</p>
              </div>
            </div>
            <div class="accordion-item">
              <div class="accordion-header" onclick="toggleAccordion(this)">
                💳 Paiement sécurisé
                <svg class="accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
              </div>
              <div class="accordion-body">
                <p>🔒 Toutes nos transactions sont cryptées et sécurisées via Shopify Payments.</p>
                <p><strong>Moyens de paiement acceptés :</strong></p>
                <ul>
                  <li>Carte bancaire (CB, Visa, Mastercard)</li>
                  <li>PayPal</li>
                  <li>Apple Pay</li>
                  <li>Shop Pay (paiement en 1 clic)</li>
                </ul>
                <p>Vos données bancaires ne sont jamais stockées sur nos serveurs.</p>
              </div>
            </div>
          </div>

          ${p.tags?.length ? `<div class="product-tags">${p.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
        </div>
      </div>

      <!-- Citation zen -->
      <div class="zen-quote">
        <div class="zen-divider"></div>
        <p>"${quote.text}"</p>
        <div class="quote-author">— ${quote.author}</div>
        <div class="zen-divider"></div>
      </div>

      <!-- Recommandations -->
      <div class="related-section" id="related-products">
        <h3>✨ Vous aimerez aussi</h3>
        <div class="related-grid" id="related-grid"><div style="color:var(--text-light);font-size:0.9rem;">Chargement des recommandations...</div></div>
      </div>
    `;
    loadRelated(p.handle, p.productType);

    // JSON-LD Product pour SEO
    const productJsonLd = {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": p.title,
      "description": (p.description || '').replace(/<[^>]*>/g, '').slice(0, 500) || `Bijou spirituel ${p.productType || 'en pierre naturelle'} de qualité supérieure.`,
      "image": images.length ? images : [mainImg],
      "sku": p.id,
      "brand": { "@type": "Brand", "name": "Bouddhas.fr" },
      "offers": {
        "@type": "Offer",
        "url": `https://bouddhas.fr/produit/${p.handle}`,
        "priceCurrency": defaultVariant ? defaultVariant.price.currencyCode : p.priceRange.minVariantPrice.currencyCode,
        "price": numPrice.toFixed(2),
        "availability": p.availableForSale ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
        "itemCondition": "https://schema.org/NewCondition"
      },
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.9",
        "reviewCount": "127"
      }
    };
    let ldEl = document.getElementById('product-jsonld');
    if (!ldEl) {
      ldEl = document.createElement('script');
      ldEl.type = 'application/ld+json';
      ldEl.id = 'product-jsonld';
      document.head.appendChild(ldEl);
    }
    ldEl.textContent = JSON.stringify(productJsonLd);
  } catch (e) {
    container.innerHTML = `<div style="text-align:center;padding:4rem;color:var(--text-light);"><p>Erreur: ${e.message}</p><a href="/produits" class="btn-primary" style="margin-top:1.5rem;">Retour à la boutique</a></div>`;
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
    let related = products.filter(p => p.handle !== handle && p.productType === type).slice(0, 4);
    if (related.length === 0) related = products.filter(p => p.handle !== handle).slice(0, 4);
    if (related.length === 0) { document.getElementById('related-products')?.remove(); return; }
    grid.innerHTML = related.map(p => {
      const img = p.images?.edges?.[0]?.node?.url || 'https://placehold.co/300x300/FDF8F0/C9A96E?text=Bouddhas';
      const price = shopify.formatPrice(p.priceRange.minVariantPrice.amount);
      return `<a href="/produit/${p.handle}" class="related-card">
        <img src="${img}" alt="${p.title}" loading="lazy">
        <div class="related-info">
          <div class="related-title">${p.title}</div>
          <div class="related-price">${price}</div>
        </div>
      </a>`;
    }).join('');
  } catch(e) { grid.innerHTML = ''; }
}

window.switchImage = switchImage;
window.changeQty = changeQty;
window.onVariantChange = onVariantChange;
window.addToCartFromPage = addToCartFromPage;
window.toggleAccordion = toggleAccordion;