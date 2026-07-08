// Recherche
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  if (!searchInput) return;

  let products = [];
  let timeout = null;

  shopify.getProducts(200).then(p => { products = p; });

  searchInput.addEventListener('input', () => {
    clearTimeout(timeout);
    const q = searchInput.value.trim().toLowerCase();
    if (q.length < 2) { 
      searchResults.style.display = 'none'; 
      searchResults.innerHTML = '';
      return; 
    }

    timeout = setTimeout(() => {
      const matches = products.filter(p => 
        p.title.toLowerCase().includes(q) ||
        (p.productType && p.productType.toLowerCase().includes(q)) ||
        (p.tags && p.tags.some(t => t.toLowerCase().includes(q)))
      ).slice(0, 8);

      if (matches.length === 0) {
        searchResults.innerHTML = '<div style="padding:1rem;color:var(--text-light);text-align:center;">Aucun résultat</div>';
      } else {
        searchResults.innerHTML = matches.map(p => `
          <a href="/produit/${p.handle}" class="search-item" style="display:flex;align-items:center;gap:1rem;padding:0.8rem;text-decoration:none;color:inherit;border-bottom:1px solid var(--beige);transition:background 0.2s;">
            <img src="${p.images?.edges?.[0]?.node?.url || ''}" style="width:45px;height:45px;object-fit:cover;border-radius:8px;">
            <div>
              <div style="font-weight:600;font-size:0.95rem;">${p.title}</div>
              <div style="color:var(--gold-dark);font-size:0.9rem;">${shopify.formatPrice(p.priceRange.minVariantPrice.amount)}</div>
            </div>
          </a>
        `).join('');
      }
      searchResults.style.display = 'block';
    }, 300);
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-box')) {
      searchResults.style.display = 'none';
    }
  });
});