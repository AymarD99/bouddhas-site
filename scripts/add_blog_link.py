#!/usr/bin/env python3
"""Ajoute le lien 'Blog' dans le header de toutes les pages (navbar dupliqué par fichier)."""
import pathlib, glob, re

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
files = glob.glob(str(ROOT/"*.html")) + glob.glob(str(ROOT/"blog/*.html"))

link = '<a href="/blog.html">Blog</a>'
count = 0
for f in files:
    p = pathlib.Path(f)
    html = p.read_text(encoding="utf-8")
    if 'href="/blog.html">Blog' in html:
        continue  # déjà présent
    # Insérer après la ligne Méditation dans le navbar
    pat = re.compile(r'(<a href="/meditation">Méditation</a>)')
    if pat.search(html):
        html = pat.sub(r'\1\n        ' + link, html, count=1)
        p.write_text(html, encoding="utf-8")
        count += 1
    # aussi gérer les cas où c'est <a href="/meditation">Méditation</a> sans saut
    elif '<a href="/meditation">Méditation</a>' in html:
        html = html.replace('<a href="/meditation">Méditation</a>',
                           '<a href="/meditation">Méditation</a>\n        ' + link, 1)
        p.write_text(html, encoding="utf-8")
        count += 1

print(f"✅ Lien 'Blog' ajouté sur {count} page(s).")
