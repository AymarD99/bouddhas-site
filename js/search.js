// Recherche locale (média) — sans Shopify
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  if (!searchInput) return;

  // Index local des pages du média
  const pages = [
    { t: "Bouddhisme", u: "/bouddhisme", d: "Histoire, écoles, maîtres" },
    { t: "Méditation", u: "/meditation", d: "Débuter, techniques, pleine conscience" },
    { t: "Philosophie", u: "/philosophie", d: "Karma, compassion, éveil" },
    { t: "Culture", u: "/culture", d: "Symboles, temples, pays" },
    { t: "Guides", u: "/guides", d: "Espace, quotidien, bien-être" },
    { t: "Glossaire", u: "/glossaire", d: "50 termes bouddhistes" },
    { t: "FAQ", u: "/faq", d: "30 questions fréquentes" },
    { t: "À propos", u: "/a-propos", d: "Ligne éditoriale" },
    { t: "Blog", u: "/blog", d: "Articles et guides" },
    { t: "Méditation débutants", u: "/blog/meditation-debutants", d: "5 minutes par jour" },
    { t: "Bracelet mala", u: "/blog/signification-bracelet-mala", d: "Signification et origine" },
    { t: "Améthyste", u: "/blog/bienfaits-amethyste-lithotherapie", d: "Bienfaits lithothérapie" },
    { t: "Pierres naturelles", u: "/blog/vertus-pierres-naturelles", d: "Vertus et guide" },
    { t: "Purifier pierres", u: "/blog/purifier-pierres-naturelles", d: "Nettoyer ses pierres" },
    { t: "Choisir bracelet zen", u: "/blog/choisir-bracelet-zen", d: "Guide d'achat" },
    { t: "Symboles bouddhistes", u: "/blog/symboles-bouddhistes-sens", d: "Lotus, mandala, om" }
  ];

  let timeout = null;
  searchInput.addEventListener('input', () => {
    clearTimeout(timeout);
    const q = searchInput.value.trim().toLowerCase();
    if (q.length < 2) {
      searchResults.style.display = 'none';
      searchResults.innerHTML = '';
      return;
    }
    timeout = setTimeout(() => {
      const matches = pages.filter(p =>
        p.t.toLowerCase().includes(q) || p.d.toLowerCase().includes(q)
      ).slice(0, 8);
      if (matches.length === 0) {
        searchResults.innerHTML = '<div style="padding:1rem;color:var(--text-light);text-align:center;">Aucun résultat</div>';
      } else {
        searchResults.innerHTML = matches.map(p => `
          <a href="${p.u}" class="search-item" style="display:flex;align-items:center;gap:1rem;padding:0.8rem;text-decoration:none;color:inherit;border-bottom:1px solid var(--beige);transition:background 0.2s;">
            <div>
              <div style="font-weight:600;font-size:0.95rem;">${p.t}</div>
              <div style="color:var(--gold-dark);font-size:0.85rem;">${p.d}</div>
            </div>
          </a>
        `).join('');
      }
      searchResults.style.display = 'block';
    }, 200);
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-box')) {
      searchResults.style.display = 'none';
    }
  });
});
