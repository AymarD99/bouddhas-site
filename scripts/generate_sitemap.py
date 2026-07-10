#!/usr/bin/env python3
"""
generate_sitemap.py — Génère sitemap.xml pour bouddhas.fr (site d'AFFILIATION).

Plus de Shopify/e-commerce. Le sitemap ne contient QUE:
  - Pages statiques (index, blog, a-propos, etc.)
  - Articles de blog (blog/*.html)
Scan automatique — aucune URL en dur (sauf la racine).

Usage: python3 scripts/generate_sitemap.py
"""
import os, pathlib, glob

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
SITEMAP = ROOT / "sitemap.xml"
BLOG = ROOT / "blog"

# Pages statiques à la racine (priorité décroissante)
STATIC_PAGES = [
    ("/", "daily", "1.0"),
    ("/blog", "weekly", "0.9"),
    ("/meditation", "weekly", "0.8"),
    ("/bouddhisme", "weekly", "0.8"),
    ("/culture", "weekly", "0.7"),
    ("/philosophie", "weekly", "0.7"),
    ("/guides", "weekly", "0.7"),
    ("/comparatifs", "weekly", "0.7"),
    ("/comparatif-bracelets", "weekly", "0.6"),
    ("/formations", "weekly", "0.6"),
    ("/glossaire", "weekly", "0.6"),
    ("/faq", "monthly", "0.6"),
    ("/a-propos", "monthly", "0.5"),
    ("/contact", "monthly", "0.5"),
]

def main():
    urls = []
    for path, freq, prio in STATIC_PAGES:
        urls.append(f'''  <url>
    <loc>https://bouddhas.fr{path}</loc>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>''')
    # Articles de blog (scan auto)
    articles = sorted(glob.glob(str(BLOG / "*.html")))
    for a in articles:
        slug = pathlib.Path(a).stem
        urls.append(f'''  <url>
    <loc>https://bouddhas.fr/blog/{slug}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>''')
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''
    SITEMAP.write_text(content, encoding="utf-8")
    print(f"✅ sitemap.xml généré: {len(urls)} URLs ({len(articles)} articles de blog + {len(STATIC_PAGES)} pages statiques)")

if __name__ == "__main__":
    main()
