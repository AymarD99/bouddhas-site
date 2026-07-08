#!/usr/bin/env python3
"""
Synchronisation Shopify → Site statique.
- Régénère le sitemap.xml avec les produits publiés
- Vérifie l'intégrité des produits (prix, images, variantes)
- Signale les anomalies dans un fichier de log

À exécuter en cron (ex: tous les jours à 3h du matin).
"""
import json, subprocess, os
from datetime import datetime

# Config
STOREFRONT_TOKEN = "a86df8c1a0e19136d077077520e22e07"
API = "https://my-bouddha-store.myshopify.com/api/2024-07/graphql.json"
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP_PATH = os.path.join(SITE_DIR, "sitemap.xml")
LOG_PATH = os.path.join(SITE_DIR, "scripts", "sync_log.txt")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

def shopify(query, variables=None):
    payload = {"query": query}
    if variables: payload["variables"] = variables
    cmd = f'''curl -s -X POST "{API}" -H "Content-Type: application/json" -H "X-Shopify-Storefront-Access-Token: {STOREFRONT_TOKEN}" -d '{json.dumps(payload)}' '''
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)

def get_all_products():
    """Récupère tous les produits publiés avec pagination."""
    products = []
    cursor = None
    page = 0
    while True:
        after = f', after: "{cursor}"' if cursor else ''
        query = (
            "{ products(first: 100" + after + ") {"
            " pageInfo { hasNextPage endCursor }"
            " edges { node {"
            " handle title availableForSale"
            " images(first: 1) { edges { node { url } } }"
            " variants(first: 1) { edges { node { price { amount } availableForSale } } }"
            " } } } }"
        )
        data = shopify(query)
        if 'errors' in data:
            log(f"❌ ERREUR API: {data['errors'][0]['message']}")
            break
        conn = data['data']['products']
        for edge in conn['edges']:
            n = edge['node']
            variants = n['variants']['edges']
            price = variants[0]['node']['price']['amount'] if variants else '0'
            img = n['images']['edges'][0]['node']['url'] if n['images']['edges'] else None
            products.append({
                'handle': n['handle'],
                'title': n['title'],
                'available': n['availableForSale'],
                'price': float(price),
                'has_image': bool(img),
                'has_variant': bool(variants)
            })
        page += 1
        if not conn['pageInfo']['hasNextPage'] or page > 50:
            break
        cursor = conn['pageInfo']['endCursor']
    return products

def generate_sitemap(products):
    """Génère le sitemap.xml."""
    STATIC = [
        ("/", "daily", "1.0"),
        ("/produits.html", "daily", "0.9"),
        ("/pierres.html", "weekly", "0.8"),
        ("/blog.html", "weekly", "0.7"),
        ("/contact.html", "monthly", "0.5"),
        ("/a-propos.html", "monthly", "0.6"),
        ("/livraison.html", "monthly", "0.5"),
        ("/faq.html", "monthly", "0.7"),
    ]
    urls = []
    for path, freq, prio in STATIC:
        urls.append(f'''  <url>
    <loc>https://bouddhas.fr{path}</loc>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>''')
    for p in products:
        urls.append(f'''  <url>
    <loc>https://bouddhas.fr/produit/{p['handle']}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>''')
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''
    with open(SITEMAP_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    log("🔄 Début synchronisation Shopify")
    products = get_all_products()
    log(f"  {len(products)} produits récupérés")
    no_img = [p for p in products if not p['has_image']]
    no_price = [p for p in products if p['price'] == 0]
    no_var = [p for p in products if not p['has_variant']]
    if no_img: log(f"  ⚠ {len(no_img)} produits sans image")
    if no_price: log(f"  ⚠ {len(no_price)} produits sans prix")
    if no_var: log(f"  ⚠ {len(no_var)} produits sans variante")
    generate_sitemap(products)
    log(f"  ✅ sitemap.xml généré ({len(products) + 8} URLs)")
    log("✅ Synchronisation terminée")

if __name__ == "__main__":
    main()
