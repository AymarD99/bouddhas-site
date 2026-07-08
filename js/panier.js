// Panier — stocké dans localStorage
let panier = JSON.parse(localStorage.getItem('bouddhas_panier') || '[]');
let productsCache = null;

function majCompteur() {
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

async function addToCart(handle) {
  if (!productsCache) {
    productsCache = await shopify.getProducts(100);
  }
  const p = productsCache.find(x => x.handle === handle);
  if (!p) return;
  
  panier.push({ handle, title: p.title, price: p.priceRange.minVariantPrice.amount });
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  MiseCompteur();
  toast(`✅ "${p.title}" ajouté au panier`);
}

async function addToCartFromDetail(variantId, title, price) {
  panier.push({ handle: variantId, title, price });
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  MiseCompteur();
  toast(`✅ "${title}" ajouté au panier`);
}

// Page panier
document.addEventListener('DOMContentLoaded', () => {
  MiseCompteur();
  
  const items = document.getElementById('cart-items');
  const summary = document.getElementById('cart-summary');
  if (!items) return;

  if (panier.length === 0) {
    items.innerHTML = '<div style="text-align:center;padding:3rem;color:var(--text-light);">Votre panier est vide</div>';
    if (summary) summary.style.display = 'none';
    return;
  }

  // Grouper par produit
  const grouped = {};
  panier.forEach(p => {
    if (!grouped[p.handle]) grouped[p.handle] = { ...p, qty: 0 };
    grouped[p.handle].qty++;
  });

  let total = 0;
  items.innerHTML = Object.values(grouped).map(item => {
    total += parseFloat(item.price) * item.qty;
    return `
      <div class="cart-item">
        <div>
          <h4>${item.title}</h4>
          <div style="color:var(--text-light);font-size:0.9rem;">Quantité: ${item.qty}</div>
        </div>
        <div>
          <div class="price">${(parseFloat(item.price) * item.qty).toFixed(2)} €</div>
          <button onclick="removeFromCart('${item.handle}')" style="background:none;border:none;color:#c00;cursor:pointer;font-size:0.85rem;">Supprimer</button>
        </div>
      </div>
    `;
  }).join('');

  document.getElementById('cart-total').textContent = `${total.toFixed(2)} €`;
  if (summary) summary.style.display = 'block';

  // Configurer le bouton checkout
  const checkoutBtn = document.getElementById('checkout-btn');
  if (checkoutBtn) {
    checkoutBtn.href = `https://my-bouddha-store.myshopify.com/checkout`;
    checkoutBtn.target = '_blank';
  }
});

function removeFromCart(handle) {
  const idx = panier.findLastIndex(p => p.handle === handle);
  if (idx !== -1) panier.splice(idx, 1);
  localStorage.setItem('bouddhas_panier', JSON.stringify(panier));
  location.reload();
}

// Pour la compatibilité avec l'ancien code
window.addToCart = addToCart;
window.addToCartFromDetail = addToCartFromDetail;
window.removeFromCart = removeFromCart;