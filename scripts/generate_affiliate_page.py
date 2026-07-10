#!/usr/bin/env python3
"""
generate_affiliate_page.py — Génère une page produit d'AFFILIATION pour bouddhas.fr.

Site d'affiliation (pas e-commerce): 1 page /produit/SLUG.html par produit partenaire.
Template SEO + maillage interne vers articles de blog existants.
Aucun produit réel pour l'instant — script prêt à l'emploi quand tu auras les liens.

Usage:
  python3 scripts/generate_affiliate_page.py --slug bracelet-meditation-amazon \
      --title "Bracelet de méditation" --desc "..." --partner-url "https://amzn.to/XXX" \
      --category "bijoux" --related "meditation-debutants,meditation-zen,pierres-spirituelles"
"""
import argparse, pathlib, re, sys, json

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
BLOG = ROOT / "blog"
PROD = ROOT / "produit"
DATA = ROOT / "data"

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def existing_articles():
    return [pathlib.Path(p).stem for p in BLOG.glob("*.html")]

def build_html(slug, title, desc, partner_url, category, related):
    # Maillage: liens vers articles existants (ou liens par défaut si related vide)
    if related:
        rel = [r.strip() for r in related.split(",")]
    else:
        rel = ["meditation-debutants", "meditation-zen", "pierres-spirituelles", "bouddhisme-debutant"]
    # Filtre pour ne garder que les articles qui existent VRAIMENT
    exist = set(existing_articles())
    liens = [r for r in rel if r in exist][:3]
    if not liens:
        liens = ["meditation-debutants", "meditation-zen", "pierres-spirituelles"]
    maillage = "\n".join(
        f'        <li><a href="/blog/{l}.html">{l.replace("-", " ").capitalize()}</a></li>'
        for l in liens
    )
    html = f'''<!-- TITLE: {title} — avis et où l'acheter (affiliation) -->
<!-- DESC: {desc[:150]} -->
<h1>{title}</h1>
<p class="article-intro">Découvrez {title.lower()}, un objet qui soutient votre pratique spirituelle. Notre avis honnête et transparent.</p>

<h2>Description</h2>
<p>{desc}</p>

<h2>Bienfaits</h2>
<ul>
  <li>Soutient la pratique de la méditation</li>
  <li>Matériaux naturels et éthiques</li>
  <li>Esthétique en accord avec vos valeurs</li>
</ul>

<h2>Comment l'utiliser</h2>
<p>Intégrez cet objet dans votre routine quotidienne, avec présence et non-attachment.</p>

<h2>Pour qui ?</h2>
<p>Idéal pour les pratiquants cherchant à approfondir leur cheminement personnel.</p>

<h2>Notre posture d'affiliation</h2>
<p><em>commerce équitable, transparence:</em> bouddhas.fr est un site d'affiliation. Si vous achetez via notre lien, nous percevons une commission sans surcoût pour vous. Nous ne recommandons que des produits alignés avec nos valeurs.</p>

<h2>Articles liés</h2>
<ul>
{maillage}
</ul>

<div class="affiliate-cta">
  <a href="{partner_url}" rel="nofollow noopener" target="_blank" class="btn-affiliate">Voir le produit chez notre partenaire →</a>
</div>'''
    return html

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--desc", required=True)
    ap.add_argument("--partner-url", required=True)
    ap.add_argument("--category", default="bijoux")
    ap.add_argument("--related", default="")
    args = ap.parse_args()

    slug = slugify(args.slug)
    html = build_html(slug, args.title, args.desc, args.partner_url, args.category, args.related)
    PROD.mkdir(exist_ok=True)
    out = PROD / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    print(f"✅ Page affiliation générée: produit/{slug}.html")
    print(f"   Maillage: {len([l for l in args.related.split(',') if l.strip()])} lien(s) cible(s)")
    # Historique pour éviter doublons
    DATA.mkdir(exist_ok=True)
    hist = DATA / "affiliate_pages.json"
    data = json.load(open(hist)) if hist.exists() else {"pages": []}
    if slug not in [p["slug"] for p in data["pages"]]:
        data["pages"].append({"slug": slug, "title": args.title, "category": args.category})
        json.dump(data, open(hist, "w"), ensure_ascii=False, indent=2)
        print(f"✅ Ajouté à affiliate_pages.json ({len(data['pages'])} pages)")

if __name__ == "__main__":
    main()
