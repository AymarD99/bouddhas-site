#!/usr/bin/env python3
"""Retire toutes les mentions explicites 'affiliation' du site (footer + textes visibles).
Remplace par 'Média indépendant' (cohérent avec le reste du site)."""
import pathlib, glob

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
pages = ["a-propos.html", "comparatif-bracelets.html", "comparatifs.html",
         "formations.html", "index.html"]

# Remplacements (visibles à l'écran)
repl = [
    ("Site d'affiliation indépendant", "Média indépendant"),
    ("est un site d'affiliation", "est un média indépendant"),
    ("site d'affiliation", "média indépendant"),
    ("liens d'affiliation", "liens de partenariat"),
    ("partenariat d'affiliation", "partenariat commercial"),
    ("affiliation)", "partenariat)"),
    ("Formations en affiliation", "Formations recommandées"),
    ("avec liens d'affiliation", "avec liens de partenariat"),
    (" Sélection indépendante avec liens d'affiliation", ""),
    ("Les liens d'affiliation éventuels sont clairement signalés. Indépendance garantie.",
     "Notre sélection est indépendante et sourcée. Indépendance garantie."),
]

for name in pages:
    p = ROOT / name
    if not p.exists():
        continue
    h = p.read_text(encoding="utf-8")
    before = h
    for a, b in repl:
        h = h.replace(a, b)
    if h != before:
        p.write_text(h, encoding="utf-8")
        print(f"✅ {name}: mentions 'affiliation' retirées")
    else:
        print(f"   {name}: rien à changer")
