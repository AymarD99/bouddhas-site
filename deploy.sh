#!/bin/bash
# Déploiement Bouddhas.fr sur Netlify (1 commande)
# Prérequis: netlify CLI installé (brew install netlify-cli)
# Ce script pousse le repo et déploie en prod. Coût: ~15 credits Netlify (1 seul déploi).

set -e
cd "$(dirname "$0")"

echo "📦 Commit des changements locaux..."
git add -A
git commit -m "🌅 Déploiement: titres FR produits, blog, sitemap, 404, netlify.toml" || echo "(rien à commiter)"
git push origin main

echo "🚀 Déploiement Netlify (prod)..."
netlify deploy --prod --dir .

echo "✅ Fait. Vérifie https://bouddhas.fr"
