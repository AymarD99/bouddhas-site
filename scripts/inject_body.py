#!/usr/bin/env python3
"""
Injecte un corps d'article enrichi (qualité maximale) dans un fichier publié,
en GARDANT: header, navbar, image existante, H1, intro, box E-E-A-T (après </article>).
Usage: python3 scripts/inject_body.py data/bodies_mantras.json
"""
import json, re, pathlib, sys

BLOG = pathlib.Path("/Users/aymarmichel/bouddhas-site/blog")
bodies = json.load(open(sys.argv[1], encoding="utf-8"))

for slug, new_body in bodies.items():
    p = BLOG / f"{slug}.html"
    if not p.exists():
        print(f"  ⚠️  {slug}: fichier absent"); continue
    html = p.read_text(encoding="utf-8")

    # 1) Récupérer H1 + image + intro (tout ce qui précède le 1er <h2>)
    head_match = re.search(r'(<h1>.*?</h1>\s*<p class="article-intro">.*?</p>)', html, re.S)
    if not head_match:
        print(f"  ⚠️  {slug}: H1/intro introuvables"); continue
    header_block = head_match.group(1)

    # 2) Récupérer l'image (balise <img ...> qui suit l'intro)
    img_match = re.search(r'(<div style="margin:1\.5rem 0 2rem;">\s*<img[^>]+></div>)', html, re.S)
    img_block = img_match.group(1) if img_match else ""

    # 3) Isoler la box E-E-A-T + footer (tout ce qui suit </article>)
    tail_match = re.search(r'(</article>.*)$', html, re.S)
    tail = tail_match.group(1) if tail_match else "</article>"

    # 4) Recomposer
    new_html = html[:html.index("<h1>")]  # tout avant le H1 (head, nav...)
    new_html += header_block + "\n" + img_block + "\n" + new_body + "\n" + tail

    p.write_text(new_html, encoding="utf-8")
    print(f"  ✅ {slug}: corps enrichi injecté ({len(new_body)} car.)")

print("=== Injection terminée ===")
