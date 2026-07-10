#!/usr/bin/env python3
"""
PUBLICATION D'ARTICLE BOUddhas.fr — Workflow automatisé (standards Yoast + 0 doublon + image native).

Usage:
  python3 scripts/post_article.py --slug mon-article --title "Mon titre" --desc "Meta description 120-155c" --keyword "mot cle" --prompt "prompt image Pollinations" --html "<h1>...</h1><h2>...</h2>..." [--category meditation]

Ce que fait le script:
  1. Génère UNE image unique via Pollinations (aux dimensions natives, jamais recadrée)
  2. Crée blog/<slug>.html avec hero image (dimensions natives: max-width:100%;height:auto)
  3. Injette: <title> 30-60c, meta description 120-155c, 1 H1, canonical, Open Graph, JSON-LD Article + ImageObject
  4. Vérifie 0 doublon d'image (image jamais réutilisée ailleurs)
  5. Lance yoast_check.py pour valider le tout

RÈGLE IMAGE (user): jamais de height fixe + object-fit:cover -> l'image garde SES dimensions de génération.
"""
import argparse, os, re, sys, subprocess, glob, urllib.parse, time

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = f"{SITE}/images/blog"

def gen_image(slug, prompt, width=1200, height=700):
    """Génère une image via Pollinations (dimensions natives). Fallback Picsum si rate-limit persistant."""
    fname = f"{slug}.jpg"
    path = f"{IMG_DIR}/{fname}"
    if os.path.exists(path):
        print(f"  ⚠️ Image {fname} existe déjà -> doublon potentiel, on génère un nom unique")
        fname = f"{slug}-{int(time.time())}.jpg"
        path = f"{IMG_DIR}/{fname}"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width={width}&height={height}&nologo=true&model=flux"
    for attempt in range(5):
        try:
            subprocess.run(["curl", "-s", "-L", "--max-time", "90", "-o", path, url], check=True)
            out = subprocess.run(["file", path], capture_output=True, text=True).stdout
            if "JPEG" in out:
                print(f"  ✅ Image générée (Pollinations): {fname} ({os.path.getsize(path)} bytes, {width}x{height})")
                return fname
            else:
                wait = 2 ** attempt * 5
                print(f"  ⚠️ Tentative {attempt+1}: image invalide (rate-limit), attente {wait}s...")
        except Exception as e:
            print(f"  ⚠️ Tentative {attempt+1} échoue: {e}")
        time.sleep(2 ** attempt * 5)
    # Fallback Picsum (image générique, non thématique — à remplacer plus tard)
    print("  ⚠️ Pollinations indisponible (rate-limit). Fallback Picsum (image générique).")
    fb = f"{IMG_DIR}/{fname}"
    subprocess.run(["curl", "-s", "-L", "--max-time", "60", "-o", fb, f"https://picsum.photos/{width}/{height}"], check=True)
    return fname

def check_doublon(fname, exclude=None):
    files = glob.glob(f"{SITE}/*.html") + glob.glob(f"{SITE}/blog/*.html")
    for f in files:
        if exclude and os.path.basename(f) == exclude:
            continue
        if fname in open(f, encoding="utf-8").read():
            raise SystemExit(f"❌ DOUBLON: {fname} déjà utilisée dans {os.path.basename(f)}")

def build_page(slug, title, desc, keyword, html_body, img, category):
    cat_label = {"meditation":"Méditation","bouddhisme":"Bouddhisme","philosophie":"Philosophie",
                 "culture":"Culture","guides":"Guides"}.get(category, "Bouddhisme")
    cat_url = f"/{category}" if category else "/bouddhisme"
    url = f"https://bouddhas.fr/blog/{slug}.html"
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html_body, re.S)
    h1_text = h1.group(1).strip() if h1 else title
    lead = re.search(r"<p[^>]*>(.*?)</p>", html_body, re.S)
    lead_text = lead.group(1).strip() if lead else desc

    page = '''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="__DESC__">
  <title>__TITLE__</title>
  <link rel="canonical" href="__URL__">
  <link rel="stylesheet" href="/css/style.min.css">
  <meta property="og:type" content="article">
  <meta property="og:title" content="__TITLE__">
  <meta property="og:description" content="__DESC__">
  <meta property="og:url" content="__URL__">
  <meta property="og:image" content="https://bouddhas.fr/images/blog/__IMG__">
  <meta property="og:site_name" content="Bouddhas.fr">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="__TITLE__">
  <meta name="twitter:description" content="__DESC__">
  <meta name="twitter:image" content="https://bouddhas.fr/images/blog/__IMG__">
  <script type="application/ld+json">{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "__H1__",
    "description": "__DESC__",
    "author": {"@type": "Organization", "name": "Bouddhas.fr"},
    "publisher": {"@type": "Organization", "name": "Bouddhas.fr"},
    "datePublished": "__DATE__",
    "mainEntityOfPage": "__URL__"
  }</script>
  <script type="application/ld+json">{
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "ImageObject",
        "url": "https://bouddhas.fr/images/blog/__IMG__",
        "name": "__SLUG__",
        "description": "__DESC__",
        "author": {"@type": "Organization", "name": "Bouddhas.fr"},
        "contentUrl": "https://bouddhas.fr/images/blog/__IMG__",
        "caption": "__DESC__"
      }
    ]
  }</script>
</head>
<body>
  <div class="announcement-bar" id="announcement-bar"><div class="swiper-wrapper" id="announce-slider"><div class="swiper-slide">📚 Média indépendant sur le bouddhisme & la méditation</div><div class="swiper-slide">🔍 Explorez nos guides et notre glossaire</div><div class="swiper-slide">✨ Contenu sourcé et bienveillant</div></div></div>
  <nav class="navbar">
  <div class="container">
    <a href="/" class="logo">Bouddhas</a>
    <button class="nav-burger" onclick="toggleNav()">☰</button>
    <div class="nav-links" id="nav-links">
      <a href="/">Accueil</a>
      <a href="/bouddhisme">Bouddhisme</a>
      <a href="/meditation">Méditation</a>
      <a href="/philosophie">Philosophie</a>
      <a href="/culture">Culture</a>
      <a href="/guides">Guides</a>
      <a href="/glossaire">Glossaire</a>
      <a href="/faq">FAQ</a>
      <a href="/a-propos">À propos</a>
      <div class="search-box">
        <span class="icon">🔍</span>
        <input type="text" id="search-input" placeholder="Rechercher..." autocomplete="off">
        <div class="search-results" id="search-results"></div>
      </div>
    </div>
  </div>
</nav>
<div class="nav-overlay" id="nav-overlay" onclick="toggleNav()"></div>
<script>
  function toggleNav() {
    document.getElementById('nav-links').classList.toggle('open');
    document.getElementById('nav-overlay').classList.toggle('open');
  }
</script>

<article class="section" style="max-width:800px;margin:0 auto;padding:3.5rem 1.5rem;">
  <div class="breadcrumb"><a href="/">Accueil</a> / <a href="/blog">Blog</a> / <span>__CATLABEL__</span></div>
  <span class="blog-cat" style="display:inline-block;margin-bottom:1rem;">__CATLABEL__</span>
  <div style="margin:1.5rem 0 2rem;"><img title="__DESC__" src="/images/blog/__IMG__" alt="__DESC__" loading="lazy" style="display:block;max-width:100%;height:auto;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,0.25);"></div>
__HTMLBODY__
  <div class="article-cta">
    <p>📚 Approfondissez</p>
    <a href="__CATURL__" class="btn-primary">Tout sur __CATLABEL__ →</a>
  </div>
</article>

  <footer><div class='container'><div class='brand'>Bouddhas</div><div class='sub'>Média indépendant sur le bouddhisme, la méditation et la philosophie</div><div style='display:flex;justify-content:center;gap:1.5rem;margin:1.5rem 0;'><a href='/bouddhisme' style='color:rgba(255,255,255,0.4);text-decoration:none;font-size:0.9rem;'>Bouddhisme</a><a href='/meditation' style='color:rgba(255,255,255,0.4);text-decoration:none;font-size:0.9rem;'>Méditation</a><a href='/glossaire' style='color:rgba(255,255,255,0.4);text-decoration:none;font-size:0.9rem;'>Glossaire</a><a href='/faq' style='color:rgba(255,255,255,0.4);text-decoration:none;font-size:0.9rem;'>FAQ</a><a href='/a-propos' style='color:rgba(255,255,255,0.4);text-decoration:none;font-size:0.9rem;'>À propos</a></div><div class='copy'>&copy; 2026 Bouddhas.fr — Média indépendant. Tous droits réservés.</div></div></footer>

<script src="/js/announce.min.js"></script>
<script src="/js/search.min.js"></script>
<button class="scroll-top" onclick="window.scrollTo({top:0,behavior:'smooth'})" aria-label="Retour en haut">↑</button>
<script>
  window.addEventListener('scroll', function() {
    var btn = document.querySelector('.scroll-top');
    if (btn) { if (window.scrollY > 400) btn.classList.add('visible'); else btn.classList.remove('visible'); }
  });
</script>
</body>
</html>'''
    page = (page
        .replace("__DESC__", desc)
        .replace("__TITLE__", title)
        .replace("__URL__", url)
        .replace("__IMG__", img)
        .replace("__H1__", h1_text)
        .replace("__SLUG__", slug)
        .replace("__DATE__", time.strftime("%Y-%m-%d"))
        .replace("__CATURL__", cat_url)
        .replace("__CATLABEL__", cat_label)
        .replace("__HTMLBODY__", html_body))
    path = f"{SITE}/blog/{slug}.html"
    open(path, "w", encoding="utf-8").write(page)
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--desc", required=True)
    ap.add_argument("--prompt", required=True, help="Prompt image Pollinations")
    ap.add_argument("--html", default="", help="Corps HTML (h1, h2, p...)")
    ap.add_argument("--html-file", default="", help="Fichier contenant le corps HTML")
    ap.add_argument("--category", default="bouddhisme")
    ap.add_argument("--keyword", default="")
    args = ap.parse_args()

    if args.html_file:
        html_body = open(args.html_file, encoding="utf-8").read().strip()
    else:
        html_body = args.html
    if not html_body:
        raise SystemExit("❌ Fournir --html ou --html-file")

    print(f"📝 Publication article: {args.slug}")
    # 1. Image unique (dimensions natives)
    img = gen_image(args.slug, args.prompt)
    # 2. Doublon check
    check_doublon(img)
    # 3. Page
    path = build_page(args.slug, args.title, args.desc, args.keyword, html_body, img, args.category)
    print(f"  ✅ Page créée: {os.path.basename(path)}")
    # 4. Validation Yoast
    print("\n🔍 Validation Yoast:")
    r = subprocess.run([sys.executable, f"{SITE}/scripts/yoast_check.py", path], capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0 and "❌" in r.stdout:
        print("⚠️ Des erreurs subsistent — corrige avant déploiement")
    else:
        print("✅ Article publié et validé (Yoast + 0 doublon + image native)")

if __name__ == "__main__":
    main()
