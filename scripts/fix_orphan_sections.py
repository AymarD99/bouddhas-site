#!/usr/bin/env python3
"""Répare les pages enrichies: déplace les sections <h2>/<p> injectées HORS <main>
vers l'intérieur de <main> (juste avant <div class="lire-aussi">)."""
import pathlib, re

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
for f in ["philosophie.html", "culture.html"]:
    p = ROOT / f
    html = p.read_text(encoding="utf-8")
    # Extrait le bloc hors-main: entre </main> et <footer
    m = re.search(r"</main>\s*(<h2>.*?</h2>\s*<p>.*?</p>\s*)+<footer", html, re.S)
    if not m:
        print(f"{f}: rien à déplacer")
        continue
    block = m.group(0).replace("</main>", "").replace("<footer", "<footer")
    # Le bloc à déplacer = tout entre </main> et <footer
    start = html.index("</main>") + len("</main>")
    end = html.index("<footer")
    outside = html[start:end].strip()
    # Retire le bloc hors-main
    html = html[:start] + "\n" + html[end:]
    # Insère avant <div class="lire-aussi">
    anchor = '<div class="lire-aussi">'
    if anchor in html:
        html = html.replace(anchor, outside + "\n\n  " + anchor, 1)
        p.write_text(html, encoding="utf-8")
        print(f"✅ {f}: sections déplacées dans <main> (avant 'À lire aussi')")
    else:
        print(f"⚠️ {f}: anchor lire-aussi introuvable")
