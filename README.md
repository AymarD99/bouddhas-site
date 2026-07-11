# Bouddhas — Boutique Spirituelle Headless

Site e-commerce headless utilisant la Storefront API Shopify.

## Tech
- HTML/CSS/JS pur
- Storefront API GraphQL
- Shopify Checkout
- Netlify (déploiement)

## Déploiement
Déployer sur Netlify en connectant ce repo GitHub.

## 🔄 Pipeline SEO quotidien (autonome)

`scripts/daily_content_pipeline.py` tourne 1×/jour (cron 20h) :
1. Recherche Ubersuggest (batch `data/keywords_batch.json`, quota 100/jour)
2. Sélection 5-10 mots-clés non couverts (fort volume / faible concurrence)
3. Rédaction via OpenRouter (poolside/laguna)
4. Publication locale (`post_article.py`)
5. Maillage interne + E-E-A-T
6. **1 SEUL déploiement Netlify** (économise tokens)

### 🛡️ Garde-fous anti-casse (2026-07-10)
- **Qualité** : refus si <800 mots ou >1200 mots (UX > SEO, pas de suroptimisation), <5 H2, title/desc manquants
- **Anti-cannibalisme** : 1 article/thème max (dédoublonnage sémantique)
- **Vérif HTTP** : après déploiement, `curl https://bouddhas.fr` → alerte si ≠ 200
- **Deploy conditionnel** : si 0 nouvel article → pas de déploiement (économie token)
- **Batch Ubersuggest** : doit tourner via venv Hermes (`~/.hermes/hermes-agent/venv/bin/python`) car module `mcp` absent du python système

### ⚠️ Quota Ubersuggest
Compte limité à 100 rapports/jour. Si `ubersuggest_batch.py` retourne 0 cible → quota atteint, réessaie demain. Le batch du jour reste utilisable.

## 📁 Structure
```
blog/              # Articles générés
scripts/           # Pipeline SEO, ubersuggest_batch, post_article
data/              # keywords_batch.json (mots-clés ciblés)
deploy.sh          # Déploiement Netlify (--prod)
css/               # style.min.css (47KB volontaire, dupliqué)
```

## 🤖 Orchestration double exécuteur (Hermes + OpenCode + MiMo)

Hermes est le **super-orchestrateur**. Deux exécuteurs agents travaillent en parallèle :
- **OpenCode** (`localhost:4096`, GLM-5.2 NIM) → tâches réfléchies (SEO, contenu, affiliation)
- **MiMo-Code** (`localhost:4097`, canal **gratuit** `mimo/mimo-auto`) → tâches code rapides (CSS, fixes, scripts)

### Agents
| Exécuteur | Agents |
|-----------|--------|
| OpenCode | bouddhas-seo, bouddhas-css, bouddhas-data, calendrier, bouddhas-affiliation |
| MiMo | bouddhas-css, sub-mobile, sub-desktop, bouddhas-seo, bouddhas-data |

### Watchdogs
- `scripts/opencode_wrapper.sh` (cron 5min) → relance OpenCode si down
- `scripts/mimo_watchdog.sh` (cron 5min) → relance MiMo si down

### Règle stricte
Tout travail est fait en **branche locale** + **preview screenshot** avant déploiement (jamais de push prod sans validation humaine).
