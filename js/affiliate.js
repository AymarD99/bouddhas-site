// ============================================================
//  CONFIGURATION AFFILIATION — Bouddhas.fr
//  Remplir les ID ci-dessous avec tes identifiants réels.
//  Laisser vide = bouton masqué automatiquement.
// ============================================================

const AFFILIATE = {
  // AliExpress Portals : votre tracking ID (ex: "metaframe0")
  aliexpress: {
    enabled: true,
    trackingId: "VOTRE_ID_ALIEXPRESS",   // ← REMPLIR
    // Construit l'URL d'affiliation depuis un ID produit AliExpress
    build: (product) => {
      const aid = product.aliId || "";
      const base = aid
        ? `https://fr.aliexpress.com/item/${aid}.html`
        : "https://fr.aliexpress.com/";
      return `https://portals.aliexpress.com/affiportals/web/landing.htm?trackingId=${AFFILIATE.aliexpress.trackingId}&url=${encodeURIComponent(base)}`;
    }
  },

  // CJdropshipping : votre ID d'affilié (embed dans le lien produit CJ)
  cj: {
    enabled: true,
    affId: "VOTRE_ID_CJ",               // ← REMPLIR
    build: (product) => {
      const pid = product.cjProductUrl || "";
      const url = pid || "https://cjdropshipping.com/";
      return pid.includes("?")
        ? `${pid}&aff=${AFFILIATE.cj.affId}`
        : `${pid}?aff=${AFFILIATE.cj.affId}`;
    }
  },

  // Amazon Partenaires FR : votre tag (ex: "bouddhas-21")
  amazon: {
    enabled: true,
    tag: "VOTRE_TAG_AMAZON",            // ← REMPLIR
    // Recherche Amazon (pas de lien produit direct sans ASIN)
    build: (product) => {
      const q = encodeURIComponent(product.title || "bouddha bracelet");
      return `https://www.amazon.fr/s?k=${q}&tag=${AFFILIATE.amazon.tag}`;
    }
  }
};

// ============================================================
//  GÉNÉRATION DES BOUTONS (retourne HTML)
// ============================================================
function affiliateButtons(product) {
  const btns = [];

  if (AFFILIATE.aliexpress.enabled && AFFILIATE.aliexpress.trackingId !== "VOTRE_ID_ALIEXPRESS") {
    btns.push(`<a class="btn-affil btn-ali" href="${AFFILIATE.aliexpress.build(product)}" target="_blank" rel="sponsored nofollow">🛒 Voir sur AliExpress</a>`);
  }
  if (AFFILIATE.cj.enabled && AFFILIATE.cj.affId !== "VOTRE_ID_CJ") {
    btns.push(`<a class="btn-affil btn-cj" href="${AFFILIATE.cj.build(product)}" target="_blank" rel="sponsored nofollow">✨ Voir sur CJ</a>`);
  }
  if (AFFILIATE.amazon.enabled && AFFILIATE.amazon.tag !== "VOTRE_TAG_AMAZON") {
    btns.push(`<a class="btn-affil btn-ama" href="${AFFILIATE.amazon.build(product)}" target="_blank" rel="sponsored nofollow">📦 Comparer sur Amazon</a>`);
  }

  // Fallback si aucun ID configuré : message discret (à retirer en prod)
  if (btns.length === 0) {
    return `<a class="btn-affil btn-placeholder" href="/contact" style="background:var(--text-light);">🔧 Boutons à configurer</a>`;
  }
  return `<div class="affil-buttons">${btns.join("")}</div>`;
}
