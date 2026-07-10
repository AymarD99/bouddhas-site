#!/usr/bin/env python3
"""
Corrige les titles + meta descriptions des articles auto-générés (trop courts/génériques).
Usage: python3 scripts/fix_seo_titles.py
"""
import json, pathlib, re, urllib.request, urllib.error

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
BLOG = ROOT / "blog"

KEY = open(pathlib.Path.home()/".hermes/.env").read()
OR = re.search(r"OPENROUTER_API_KEY=([^\n]+)", KEY).group(1).strip()

# Articles auto à corriger (slug -> (title 40-60c, desc 120-155c))
TARGETS = {
    "bajrang-baan": (
        "Le Bajrang Baan : signification, bienfaits et récitation",
        "Découvrez le Bajrang Baan, puissant mantra de Hanuman. Signification, bienfaits spirituels et guide de récitation pour renforcer courage et protection au quotidien."
    ),
    "hare-krishna-hare-hare": (
        "Hare Krishna Hare Hare : le mantra de dévotion expliqué",
        "Tout sur le Hare Krishna Hare Hare : origine, signification sanskrite et bienfaits de ce mantra de dévotion. Guide pratique pour la récitation quotidienne."
    ),
    "mahamitujay-mantra": (
        "Maha Mrityunjaya Mantra : signification et bienfaits",
        "Le Maha Mrityunjaya Mantra expliqué : traduction, signification du mantra de guérison et bienfaits pour apaiser le corps et l'esprit. Récitation et conseils."
    ),
    "google-breathing-exercise": (
        "Le Google Breathing Exercise : technique de respiration",
        "Le Google Breathing Exercise (réduction du stress 4-4-4-4) expliqué : comment pratiquer cette respiration carrée pour calmer le stress en quelques minutes."
    ),
    "cinq-preceptes": (
        "Les 5 préceptes bouddhistes : guide éthique complet",
        "Les 5 préceptes bouddhistes expliqués simplement : non-violence, justesse, maîtrise, parole vraie et clarté. Leur sens profond et application dans la vie quotidienne."
    ),
}

def gen_seo(slug):
    return TARGETS.get(slug, (None, None))

for slug, kw in TARGETS.items():
    f = BLOG/f"{slug}.html"
    if not f.exists():
        print(f"  ⚠️ {slug} introuvable, skip"); continue
    html = f.read_text(encoding="utf-8")
    title, desc = gen_seo(slug)
    if not title:
        print(f"  ⚠️ Génération échouée pour {slug}"); continue
    # Remplacer title (toutes les variantes)
    html = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")', fr'\1{title}\2', html)
    if desc:
        html = re.sub(r'(<meta name="description" content=")[^"]*(")', fr'\1{desc}\2', html)
        html = re.sub(r'(<meta property="og:description" content=")[^"]*(")', fr'\1{desc}\2', html)
    # Mettre à jour le H1 aussi si c'est le titre générique
    html = re.sub(r"<h1[^>]*>[^<]*</h1>", f"<h1>{title}</h1>", html, count=1)
    f.write_text(html, encoding="utf-8")
    print(f"  ✅ {slug}: title='{title}' | desc={len(desc)}c")
print("Terminé.")
