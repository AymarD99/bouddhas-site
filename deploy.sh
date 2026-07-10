#!/usr/bin/env bash
# Déploiement Netlify MANUEL (0 crédit) — repo GitHub DÉCONNECTÉ
# Usage: bash deploy.sh
# Prérequis: NETLIFY_AUTH_TOKEN dans ~/.hermes/.env (ou export)
set -e
cd "$(dirname "$0")"

# Charger le token depuis .env si présent
if [ -f ~/.hermes/.env ]; then
  export $(grep -E "^NETLIFY_AUTH_TOKEN=" ~/.hermes/.env | xargs)
fi

if [ -z "$NETLIFY_AUTH_TOKEN" ]; then
  echo "❌ NETLIFY_AUTH_TOKEN manquant. Ajoute-le dans ~/.hermes/.env"
  exit 1
fi

echo "🚀 Déploiement MANUEL en prod (0 crédit, upload direct)..."
netlify deploy --prod --dir . --auth "$NETLIFY_AUTH_TOKEN"

echo "✅ Terminé. Vérifie https://bouddhas.fr"
