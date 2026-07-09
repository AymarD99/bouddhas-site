# Bouddhas.fr — Plan SEO & Content Factory (local, non déployé)

> Généré pendant la session de nuit 2026-07-10. Tout reste en environnement local.

## État du site (00h00 → en cours)
- 12 articles de blog (7 originaux + 5 nouveaux)
- 13 pages média (accueil, 5 fondamentaux, glossaire, faq, guides, culture, a-propos, contact, blog, comparatifs, formations, comparatif-bracelets)
- 0 doublon d'image, 0 lien cassé, SEO technique 100/100
- Maillage interne : 3 liens "À lire aussi" par article

## Veille concurrentielle (FR)
- Marché FR peu concentré : pas de géant type "Bouddha Bouddhisme" dominant (eux ~10-30k vis/mois estimé)
- Concurrents principaux : bouddha-bouddhisme.com (blog actif), bouddha-power.com, carnets-du-bouddhisme.com (annuaire)
- Leurs points faibles : FAQ basiques (8-12 questions), peu de guides "comment faire" pratiques, contenu souvent traduit/non natif
- OPPORTUNITÉ : contenu FR natif + approfondi + E-E-A-T (sources, auteur, dates)

## Mots-clés à fort potentiel (longue traîne, faible concurrence FR)
1. différence theravada mahayana vajrayana → cluster Bouddhisme
2. méditation pleine conscience sommeil stress débutant → cluster Méditation
3. mantras bouddhistes signification om mani → cluster Culture (déjà fait)
4. pierres bouddha lithothérapie citrine quartz rose → cluster Guides (à étendre)
5. bouddhisme pour débutant par où commencer → cluster Bouddhisme
6. comment méditer le matin routine → cluster Méditation
7. symbole lotus signification bouddhisme → cluster Culture
8. noble octuple sentier expliqué → cluster Philosophie

## Clusters prioritaires (roadmap)
- P1 Bouddhisme : theravada-mahayana-vajrayana, bouddhisme-debutant, histoire-bouddha
- P1 Méditation : meditation-sommeil, meditation-pleine-conscience, routine-matinale
- P2 Culture : symbole-lotus, festivals-bouddhistes, temples-famous
- P2 Guides : citrine-quartz-rose, purifier-espace, yoga-bouddhiste
- P3 Philosophie : noble-octuple-sentier, sunyata-vide, interdependance

## Décisions
- Header/footer des articles doivent matcher l'architecture actuelle (.announcement-bar/.navbar) → script post_article.py corrigé
- Images : Pollinations en rate-limit persistant (error 1033) → fallback placeholder local (gen_placeholder.py), à remplacer quand l'API revient
- Popup newsletter : désactivé (code commenté), réactivable

## Outils créés
- scripts/post_article.py (corrigé : header/footer actuels, retry Pollinations 5x + fallback Picsum)
- scripts/gen_placeholder.py (fallback image local or/noir + titre)
- scripts/yoast_check.py (validation SEO)

## Prochaines priorités
1. Publier 3-5 articles des clusters P1 (theravada, meditation-sommeil, bouddhisme-debutant)
2. Enrichir la FAQ (30 → 40+ questions)
3. Remplacer les placeholders par de vraies images Pollinations (quand API libre)
4. Soumettre sitemap dans Search Console (action utilisateur)
