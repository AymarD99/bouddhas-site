#!/usr/bin/env python3
"""Injecte les données structurées JSON-LD sur toutes les pages HTML."""
import os, glob, json

SITE = "https://bouddhas.fr"
PAGES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Organization (commun à toutes les pages)
ORG_JSONLD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Bouddhas.fr",
    "url": SITE,
    "logo": f"{SITE}/images/logo.png",
    "description": "Boutique en ligne de bouddhas, pierres naturelles, bijoux spirituels et objets de décoration zen.",
    "sameAs": [
        "https://www.instagram.com/bouddhas.fr",
        "https://www.facebook.com/bouddhas.fr"
    ],
    "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+33-6-83-81-07-29",
        "contactType": "customer service",
        "areaServed": "FR",
        "availableLanguage": "French"
    }
}

# WebSite avec SearchAction
WEBSITE_JSONLD = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Bouddhas.fr",
    "url": SITE,
    "potentialAction": {
        "@type": "SearchAction",
        "target": f"{SITE}/produits.html?q={{search_term_string}}",
        "query-input": "required name=search_term_string"
    }
}

def breadcrumb_for(page):
    """Retourne le BreadcrumbList pour une page donnée."""
    mapping = {
        "index.html": [("Accueil", "/")],
        "produits.html": [("Accueil", "/"), ("Boutique", "/produits.html")],
        "produit.html": [("Accueil", "/"), ("Boutique", "/produits.html"), ("Produit", "/produit.html")],
        "panier.html": [("Accueil", "/"), ("Panier", "/panier.html")],
        "contact.html": [("Accueil", "/"), ("Contact", "/contact.html")],
        "a-propos.html": [("Accueil", "/"), ("À propos", "/a-propos.html")],
        "livraison.html": [("Accueil", "/"), ("Livraison", "/livraison.html")],
        "faq.html": [("Accueil", "/"), ("FAQ", "/faq.html")],
        "pierres.html": [("Accueil", "/"), ("Pierres naturelles", "/pierres.html")],
    }
    items = mapping.get(page, [("Accueil", "/")])
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": f"{SITE}{url}"
            }
            for i, (name, url) in enumerate(items)
        ]
    }

def inject_jsonld(html, jsonld_list):
    """Injecte une ou plusieurs balises JSON-LD avant </head>."""
    scripts = "\n".join(
        f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False, indent=2)}</script>'
        for d in jsonld_list
    )
    if "</head>" in html:
        html = html.replace("</head>", f"  <!-- JSON-LD Structured Data -->\n  {scripts}\n</head>", 1)
    return html

# Traiter chaque page
results = []
for page in ["index.html", "produits.html", "produit.html", "panier.html",
             "contact.html", "a-propos.html", "livraison.html", "faq.html", "pierres.html"]:
    path = os.path.join(PAGES_DIR, page)
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Éviter doublons
    if "application/ld+json" in html:
        results.append(f"  ⏭  {page}: déjà présent")
        continue

    jsonld_list = [ORG_JSONLD, WEBSITE_JSONLD, breadcrumb_for(page)]
    html = inject_jsonld(html, jsonld_list)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    results.append(f"  ✅ {page}: Organization + WebSite + BreadcrumbList ajoutés")

print("=== DONNÉES STRUCTURÉES INJECTÉES ===")
for r in results:
    print(r)
