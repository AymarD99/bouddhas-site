#!/usr/bin/env python3
"""Déplace le contenu hors <main> (entre </main> et <footer) à l'INTERIEUR de <main>
(juste AVANT </main>). Version corrigée."""
import pathlib, re

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
pages = ["comparatifs.html", "comparatif-bracelets.html", "formations.html",
         "a-propos.html", "guides.html"]

for name in pages:
    p = ROOT / name
    html = p.read_text(encoding="utf-8")
    m = re.search(r"(</main>)(.*?)(<footer)", html, re.S)
    if not m:
        print(f"{name}: rien à déplacer")
        continue
    outside = m.group(2).strip()
    if not outside:
        print(f"{name}: vide")
        continue
    # Reconstruit: tout ce qui est avant </main> + outside + </main> + <footer + reste
    new = html[:m.start()] + "\n\n  " + outside + "\n\n  " + "</main>" + html[m.end():]
    p.write_text(new, encoding="utf-8")
    print(f"✅ {name}: {len(outside)} car. déplacés DANS <main> (avant </main>)")
