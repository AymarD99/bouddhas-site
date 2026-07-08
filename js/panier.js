// Panier — stocké dans localStorage
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

// Ajouter depuis les pages
async function addToCart(handle) {
  if (!window.__productsCache) {
    window.__productsCache = await shopify.getProducts(100);
  }
  const p = window.__productsCache.find(x => x.handle === handle);
  if (!p) return;

  panier.push({
    handle,
    variantId: p.variants?.edges?.[0]?.node?.id || null,
    title: p.title,
    price: p.priceRange.minVariantPrice.amount,
    img: p.images?.edges?.[0]?.node?.url || ''
  });
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  majCompteur();
  showToast(`✅ "${p.title}" ajouté`);
}

// Créer un checkout Shopify via API Storefront
async function createShopifyCheckout() {
  if (panier.length === 0) return;

  showToast('🔄 Préparation du checkout...');

  try {
    // Récupérer les variants IDs
    const items = [];
    for (const p of panier) {
      if (p.variantId) {
        items.push({ merchandiseId: p.variantId, quantity: 1 });
      }
    }

    if (items.length === 0) {
      showToast('❌ Impossible de préparer la commande');
      return;
    }

    const mutation = `
      mutation {
        cartCreate(input: { lines: [${items.map(i => `{ merchandiseId: "${i.merchandiseId}", quantity: ${i.quantity} }`).join(',')}] }) {
          cart {
            id
            checkoutUrl
          }
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
      const url = data.data.cartCreate.cart.checkoutUrl;
      // Ouvrir le checkout
      window.location.href = url;
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
          <div style="color:var(--text-light);font-size:0.9rem;">Qté: ${p.qty}</div>
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

  // Bouton checkout
  const btn = document.getElementById('checkout-btn');
  if (btn) {
    btn.onclick = async (e) => {
      e.preventDefault();
      await createShopifyCheckout();
    };
  }
});

function retirerDuPanier(handle) {
  const idx = panier.findLastIndex(p => p.handle === handle);
  if (idx !== -1) panier.splice(idx, 1);
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  location.reload();
}

// Exposer globalement
window.addToCart = addToCart;
window.retirerDuPanier = retirerDuPanier;
window.createShopifyCheckout = createShopifyCheckout;