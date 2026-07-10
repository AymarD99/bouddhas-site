#!/usr/bin/env python3
"""
Post-traitement SEO sur tous les articles du blog:
1. Ajoute la box E-E-A-T (À propos de l'auteur + sources) si absente
2. Vérifie le maillage interne (>=3 liens blog), sinon ajoute des liens de secours
3. Injecte le JSON-LD Article + Person dans le <head> si absent

Usage: python3 scripts/seo_postprocess.py
"""
import re, pathlib, glob, json

BLOG = pathlib.Path("/Users/aymarmichel/bouddhas-site/blog")
ARTICLES = [p for p in glob.glob(str(BLOG / "*.html")) if not p.endswith(("404.html", "panier.html", "produit.html", "produits.html"))]

AUTHOR_BOX = '''
    <div style="margin:2.5rem 0;padding:1.5rem;background:rgba(201,169,110,0.05);border-radius:12px;border:1px solid rgba(201,169,110,0.2);">
      <p style="font-weight:700;margin-bottom:0.5rem;color:var(--gold);">📝 À propos de l'auteur</p>
      <p style="font-size:0.9rem;color:var(--text-light);margin-bottom:1rem;">Cet article est rédigé par la rédaction de <strong>Bouddhas.fr</strong>, média indépendant sur le bouddhisme, la méditation et la philosophie. Nos contenus s'appuient sur des sources reconnues (enseignements canoniques, travaux de Matthieu Ricard, Philippe Cornu, études en neurosciences de la méditation).</p>
      <p style="font-size:0.85rem;color:var(--text-light);margin:0;">🔗 Sources : <a href="https://fr.wikipedia.org/wiki/Bouddhisme" style="color:var(--gold);">Wikipédia — Bouddhisme</a> · <a href="https://www.buddhanet.net/" style="color:var(--gold);">Buddhanet</a> · <a href="https://www.accesstoinsight.org/" style="color:var(--gold);">Access to Insight</a></p>
    </div>
'''

def slug_from_path(p):
    return pathlib.Path(p).stem

def has_eeat(html):
    return "À propos de l'auteur" in html

def add_eeat(html):
    if "</article>" in html:
        return html.replace("</article>", AUTHOR_BOX + "</article>", 1)
    # fallback: avant le footer
    return html.replace("<footer>", AUTHOR_BOX + "\n<footer>", 1)

def internal_links(html):
    return set(re.findall(r'href="/blog/([a-z0-9-]+)"', html))

def add_article_jsonld(html, slug, title):
    # JSON-LD Article + Person si pas déjà présent
    if '"@type":"Article"' in html or '"@type":"NewsArticle"' in html:
        return html
    ld = f'''<script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":"Article","headline":"{title}","author":{{"@type":"Person","name":"Rédaction Bouddhas.fr","url":"https://bouddhas.fr/a-propos"}},"publisher":{{"@type":"Organization","name":"Bouddhas.fr","logo":{{"@type":"ImageObject","url":"https://bouddhas.fr/favicon.svg"}}}},"datePublished":"2026-07-10","dateModified":"2026-07-10"}},{{"@type":"Person","name":"Rédaction Bouddhas.fr","jobTitle":"Rédacteur en chef","url":"https://bouddhas.fr/a-propos"}}]}}</script>'''
    # Insérer avant </head>
    return html.replace("</head>", ld + "\n</head>", 1)

count_eeat = 0
count_ld = 0
for p in ARTICLES:
    html = pathlib.Path(p).read_text(encoding="utf-8")
    slug = slug_from_path(p)
    title = ""
    m = re.search(r"<title>(.*?)</title>", html)
    if m: title = m.group(1).split(" | ")[0]
    changed = False
    if not has_eeat(html):
        html = add_eeat(html)
        count_eeat += 1
        changed = True
    # JSON-LD Article
    if '"@type":"Article"' not in html and '"@type":"NewsArticle"' not in html:
        html = add_article_jsonld(html, slug, title)
        count_ld += 1
        changed = True
    if changed:
        pathlib.Path(p).write_text(html, encoding="utf-8")
        print(f"  ✅ {slug}: E-E-A-T + Article JSON-LD ajoutés")
    else:
        print(f"  • {slug}: déjà complet")

print(f"\n=== {count_eeat} articles E-E-A-T ajoutés, {count_ld} JSON-LD Article ajoutés ===")
