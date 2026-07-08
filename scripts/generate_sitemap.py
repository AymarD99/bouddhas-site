#!/usr/bin/env python3
"""Génère un sitemap.xml complet avec les produits Shopify."""
import json, subprocess, os

STOREFRONT_TOKEN = "a86df8c1a0e19136d077077520e22e07"
API = "https://my-bouddha-store.myshopify.com/api/2024-07/graphql.json"
SITE = "https://bouddhas.fr"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sitemap.xml")

STATIC_PAGES = [
    ("/", "daily", "1.0"),
    ("/produits.html", "daily", "0.9"),
    ("/pierres.html", "weekly", "0.8"),
    ("/contact.html", "monthly", "0.5"),
    ("/a-propos.html", "monthly", "0.6"),
    ("/livraison.html", "monthly", "0.5"),
    ("/faq.html", "monthly", "0.7"),
]

def get_products():
    """Récupère tous les produits publiés depuis Shopify."""
    products = []
    cursor = None
    has_next = True
    while has_next:
        after = f', after: "{cursor}"' if cursor else ''
        query = f'''{{ products(first: 100{after}) {{ pageInfo {{ hasNextPage endCursor }} edges {{ node {{ handle title images(first: 1) {{ edges {{ node {{ url }} }} }} }} }} }} }}'''
        cmd = f'''curl -s -X POST "{API}" -H "Content-Type: application/json" -H "X-Shopify-Storefront-Access-Token: {STOREFRONT_TOKEN}" -d '{json.dumps({"query": query})}' '''
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        data = json.loads(r.stdout)
        if 'errors' in data:
            print(f"❌ Erreur: {data['errors'][0]['message']}")
            break
        conn = data['data']['products']
        for edge in conn['edges']:
            n = edge['node']
            img = n['images']['edges'][0]['node']['url'] if n['images']['edges'] else ''
            products.append({'handle': n['handle'], 'image': img})
        has_next = conn['pageInfo']['hasNextPage']
        cursor = conn['pageInfo']['endCursor']
    return products

def build_sitemap(products):
    urls = []
    for path, freq, prio in STATIC_PAGES:
        urls.append(f'''  <url>
    <loc>{SITE}{path}</loc>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>''')

    for p in products:
        img_tag = f'\n    <image:image>\n      <image:loc>{p["image"]}</image:loc>\n    </image:image>' if p['image'] else ''
        urls.append(f'''  <url>
    <loc>{SITE}/produit/{p['handle']}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>{img_tag}
  </url>''')

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(urls)}
</urlset>'''

if __name__ == "__main__":
    print("🔄 Génération du sitemap...")
    products = get_products()
    print(f"  {len(products)} produits récupérés")
    content = build_sitemap(products)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ sitemap.xml généré: {OUT}")
    print(f"  Total URLs: {len(products) + len(STATIC_PAGES)}")
