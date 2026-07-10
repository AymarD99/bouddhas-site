#!/usr/bin/env python3
"""Supprime le doublon Contact (.cart-link) du header sur toutes les pages."""
import pathlib, glob

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
files = glob.glob(str(ROOT/"*.html")) + glob.glob(str(ROOT/"blog/*.html"))
count = 0
for f in files:
    p = pathlib.Path(f)
    html = p.read_text(encoding="utf-8")
    if 'class="cart-link"' in html:
        html = html.replace('<a href="/contact" class="cart-link">✉️ Contact</a>', '')
        html = html.replace("<a href=\"/contact\" class=\"cart-link\">✉️ Contact</a>", "")
        p.write_text(html, encoding="utf-8")
        count += 1
print(f"✅ Doublon Contact supprimé sur {count} page(s).")
