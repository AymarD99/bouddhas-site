#!/usr/bin/env python3
"""
build_css.py — Génère css/style.min.css à partir de css/style.css.

Usage: python3 build_css.py
Minification basique (retire commentaires + espaces inutiles).
À lancer après chaque modif de style.css pour que le site (qui charge
style.min.css) reflète les changements.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "css" / "style.css"
DST = ROOT / "css" / "style.min.css"


def minify(css: str) -> str:
    # 1. Retire commentaires /* ... */
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    # 2. Retire espaces autour de { } : ; , > ~ + (et dans les sélecteurs)
    css = re.sub(r"\s*([{}:;,])\s*", r"\1", css)
    # 3. Retire espaces autour des opérateurs de combinaison
    css = re.sub(r"\s*([>~+])\s*", r"\1", css)
    # 4. Retire espaces en début/fin de lignes et lignes vides
    css = re.sub(r"\n\s*", " ", css)
    css = re.sub(r"\s{2,}", " ", css)
    css = css.strip()
    return css


def main():
    if not SRC.exists():
        print(f"❌ Source introuvable: {SRC}")
        return 1
    out = minify(SRC.read_text())
    DST.write_text(out)
    print(f"✅ {SRC.name} ({SRC.stat().st_size} B) -> {DST.name} ({DST.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
