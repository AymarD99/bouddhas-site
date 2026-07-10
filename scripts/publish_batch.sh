#!/usr/bin/env bash
# Pipeline de publication batch (local uniquement, 0 déploiement ici)
# Usage: bash scripts/publish_batch.sh
cd /Users/aymarmichel/bouddhas-site
DRAFTS=$(ls blog/_drafts/*.html 2>/dev/null)
if [ -z "$DRAFTS" ]; then echo "Aucun draft"; exit 0; fi
for f in $DRAFTS; do
  slug=$(basename "$f" .html)
  title=$(grep -m1 '<h1>' "$f" | sed 's/<[^>]*>//g')
  desc="Guide complet sur $(echo $title | tr 'A-Z' 'a-z'), bienfaits et pratique. Média indépendant bouddhisme & méditation."
  echo "=== Publication: $slug ==="
  python3 scripts/post_article.py \
    --slug "$slug" \
    --title "$title" \
    --desc "$desc" \
    --prompt "$slug spiritual calm" \
    --category "meditation" \
    --html-file "$f" 2>&1 | tail -2
done
echo "✅ Batch publié (local). Déployer séparément."
