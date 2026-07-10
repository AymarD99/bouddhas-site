#!/usr/bin/env python3
"""
Maillage interne: garantit >=3 liens uniques vers d'autres articles par page.
Ajoute des liens de secours dans la box E-E-A-T si besoin.
Usage: python3 scripts/internal_linking.py
"""
import re, pathlib, glob

BLOG = pathlib.Path("/Users/aymarmichel/bouddhas-site/blog")
ARTICLES = [p for p in glob.glob(str(BLOG / "*.html")) if not p.endswith(("404.html","panier.html","produit.html","produits.html"))]

def slug(p): return pathlib.Path(p).stem
def title_of(html):
    m = re.search(r"<title>(.*?)</title>", html)
    return m.group(1).split(" | ")[0] if m else slug

def internal_links(html):
    return set(re.findall(r'href="/blog/([a-z0-9-]+)"', html))

# Groupes thématiques pour un maillage pertinent
THEMES = {
    "mantra": ["mantras-bouddhistes","maha-mrityunjaya-mantra","gayatri-mantra","om-namah-shivaya","ganesh-mantra","mediter"],
    "meditation": ["meditation-debutants","meditation-guidee","meditation-zen","meditation-sommeil","mediter","pleine-conscience","mindfulness","espace-meditation-maison"],
    "bouddhisme": ["bouddhisme-debutant","bouddhisme-tibetain","bouddhisme-france","theravada-mahayana-vajrayana","quatre-nobles-verites","noble-octuple-sentier","karma-renaissance","symbole-lotus"],
    "pierres": ["purifier-pierres-naturelles","signification-bracelet-mala","bienfaits-amethyste-lithotherapie","choisir-bracelet-zen","vertus-pierres-naturelles"],
}

def theme_of(s):
    for t, lst in THEMES.items():
        if s in lst: return t
    return "meditation"

added_total = 0
for p in ARTICLES:
    html = pathlib.Path(p).read_text(encoding="utf-8")
    s = slug(p)
    existing = internal_links(html)
    if s in existing: existing.discard(s)
    need = max(0, 3 - len(existing))
    if need == 0:
        continue
    theme = theme_of(s)
    candidates = [x for x in THEMES.get(theme, []) if x != s and x not in existing]
    # enrichir avec d'autres thèmes si besoin
    if len(candidates) < need:
        for t, lst in THEMES.items():
            if t == theme: continue
            for x in lst:
                if x != s and x not in existing and x not in candidates:
                    candidates.append(x)
            if len(candidates) >= need: break
    picks = candidates[:need]
    if not picks:
        continue
    # Insérer dans la box E-E-A-T (avant "🔗 Sources")
    links_html = " · ".join(f'<a href="/blog/{x}" style="color:var(--gold);">{title_of(open(BLOG/f"{x}.html").read())}</a>' for x in picks)
    if "🔗 Sources" in html:
        html = html.replace("🔗 Sources", f"📚 À lire aussi : {links_html}<br>🔗 Sources", 1)
    else:
        html = html.replace("</article>", f'<p style="font-size:0.85rem;color:var(--text-light);margin-top:1rem;">📚 À lire aussi : {links_html}</p></article>', 1)
    pathlib.Path(p).write_text(html, encoding="utf-8")
    added_total += len(picks)
    print(f"  +{len(picks)} liens → {s}: {picks}")

print(f"\n=== {added_total} liens de maillage ajoutés ===")
