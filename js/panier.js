// Panier — stocké dans localStorage (FIX: variantId + quantité + checkout)
let panier = JSON.parse(localStorage.getItem('bouddhas_panier') || '[]');

function majCompteur() {
  const el = document.getElementById('cart-count');
  if (el) el.textContent = panier.length;
}
majCompteur();

function showToast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 2500);
}

// Ajouter au panier — récupère le variantId + quantité
async function addToCart(handle, qty = 1, variantId = null) {
  if (!window.__productsCache) {
    window.__productsCache = await shopify.getProducts(100);
  }
  const p = window.__productsCache.find(x => x.handle === handle);
  if (!p) return;

  // Récupérer le variantId si pas fourni
  if (!variantId) {
    variantId = p.variants?.edges?.[0]?.node?.id || null;
  }

  // Ajouter qty fois le produit
  for (let i = 0; i < qty; i++) {
    panier.push({
      handle,
      variantId,
      title: p.title,
      price: p.priceRange.minVariantPrice.amount,
      img: p.images?.edges?.[0]?.node?.url || ''
    });
  }
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  majCompteur();
  showToast(`✅ "${p.title}" ajouté (${qty})`);
}

// Retirer du panier
function retirerDuPanier(handle) {
  panier = panier.filter(p => p.handle !== handle);
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  majCompteur();
  location.reload();
}

// Modifier la quantité dans le panier
function updateQty(handle, delta) {
  if (delta > 0) {
    const item = panier.find(p => p.handle === handle);
    if (item) {
      panier.push({ ...item });
    }
  } else if (delta < 0) {
    const idx = panier.findIndex(p => p.handle === handle);
    if (idx !== -1) panier.splice(idx, 1);
  }
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  majCompteur();
  location.reload();
}

// Checkout Shopify via cartCreate
async function createShopifyCheckout() {
  if (panier.length === 0) return;

  showToast('🔄 Préparation du checkout...');

  try {
    // Grouper par variantId et sommer les quantités
    const grouped = {};
    for (const p of panier) {
      if (!p.variantId) continue;
      if (!grouped[p.variantId]) grouped[p.variantId] = { merchandiseId: p.variantId, quantity: 0 };
      grouped[p.variantId].quantity += 1;
    }

    const items = Object.values(grouped);
    if (items.length === 0) {
      showToast('❌ Aucun variant disponible pour le checkout');
      return;
    }

    const mutation = `
      mutation {
        cartCreate(input: { lines: [${items.map(i => `{ merchandiseId: "${i.merchandiseId}", quantity: ${i.quantity} }`).join(',')}] }) {
          cart { id checkoutUrl }
          userErrors { field message }
        }
      }
    `;

    const res = await fetch(CONFIG.apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Shopify-Storefront-Access-Token': CONFIG.storefrontToken
      },
      body: JSON.stringify({ query: mutation })
    });
    const data = await res.json();

    if (data.data?.cartCreate?.cart?.checkoutUrl) {
      window.location.href = data.data.cartCreate.cart.checkoutUrl;
    } else {
      const err = data.data?.cartCreate?.userErrors?.[0]?.message || 'Erreur inconnue';
      showToast(`❌ ${err}`);
    }
  } catch (e) {
    showToast(`❌ Erreur: ${e.message}`);
  }
}

// Page panier
document.addEventListener('DOMContentLoaded', () => {
  const items = document.getElementById('cart-items');
  const summary = document.getElementById('cart-summary');
  if (!items) return;

  if (panier.length === 0) {
    items.innerHTML = `
      <div style="text-align:center;padding:4rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">🛒</div>
        <p style="color:var(--text-light);font-size:1.1rem;">Votre panier est vide</p>
        <a href="/produits" class="btn-primary" style="margin-top:1.5rem;">Découvrir la boutique</a>
      </div>`;
    if (summary) summary.style.display = 'none';
    return;
  }

  // Grouper par handle
  const grouped = {};
  panier.forEach(p => {
    if (!grouped[p.handle]) grouped[p.handle] = { ...p, qty: 0 };
    grouped[p.handle].qty++;
  });

  let total = 0;
  items.innerHTML = Object.values(grouped).map(p => {
    const stotal = parseFloat(p.price) * p.qty;
    total += stotal;
    return `
      <div class="cart-item">
        ${p.img ? `<img src="${p.img}" style="width:60px;height:60px;object-fit:cover;border-radius:8px;margin-right:1rem;">` : ''}
        <div style="flex:1;">
          <h4>${p.title}</h4>
          <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.3rem;">
            <button onclick="updateQty('${p.handle}', -1)" style="background:var(--beige);border:none;width:28px;height:28px;border-radius:6px;cursor:pointer;font-weight:700;">−</button>
            <span style="color:var(--text-light);font-size:0.9rem;min-width:30px;text-align:center;">${p.qty}</span>
            <button onclick="updateQty('${p.handle}', 1)" style="background:var(--beige);border:none;width:28px;height:28px;border-radius:6px;cursor:pointer;font-weight:700;">+</button>
          </div>
        </div>
        <div style="text-align:right;">
          <div class="price">${stotal.toFixed(2)} €</div>
          <button onclick="retirerDuPanier('${p.handle}')" style="background:none;border:none;color:#c00;cursor:pointer;font-size:0.8rem;margin-top:0.3rem;">Supprimer</button>
        </div>
      </div>
    `;
  }).join('');

  document.getElementById('cart-total').textContent = `${total.toFixed(2)} €`;
  if (summary) summary.style.display = 'block';

  const btn = document.getElementById('checkout-btn');
  if (btn) {
    btn.onclick = async (e) => {
      e.preventDefault();
      await createShopifyCheckout();
    };
  }
});

// Exposer globalement
window.addToCart = addToCart;
window.retirerDuPanier = retirerDuPanier;
window.updateQty = updateQty;
window.createShopifyCheckout = createShopifyCheckout;
window.showToast = showToast;