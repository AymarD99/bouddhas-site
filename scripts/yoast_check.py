#!/usr/bin/env python3
"""Vérifie que chaque article/blog respecte les standards SEO type Yoast.
Usage: python3 scripts/yoast_check.py [fichier.html]
Si aucun fichier: vérifie tous les articles de blog/ + pages média.
"""
import re, os, sys, glob

site = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_file(path):
    h = open(path, encoding="utf-8").read()
    issues = []
    base = os.path.basename(path)

    # 1. <title> 30-60 chars (Yoast: ~50-60)
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    if not m:
        issues.append("❌ Pas de <title>")
    else:
        t = m.group(1).strip()
        if len(t) < 30 or len(t) > 60:
            issues.append(f"⚠️ <title> {len(t)} car. (idéal 30-60): {t}")

    # 2. meta description 120-155 chars
    m = re.search(r'<meta name="description" content="(.*?)"', h, re.S)
    if not m:
        issues.append("❌ Pas de meta description")
    else:
        d = m.group(1).strip()
        if len(d) < 120 or len(d) > 155:
            issues.append(f"⚠️ meta description {len(d)} car. (idéal 120-155): {d[:50]}...")

    # 3. 1 seul H1
    h1 = re.findall(r"<h1", h)
    if len(h1) != 1:
        issues.append(f"❌ {len(h1)} balise(s) H1 (doit être 1)")

    # 4. Structure H2/H3 présente
    if not re.search(r"<h2", h):
        issues.append("⚠️ Pas de H2 (structure recommandée)")

    # 5. 1 image unique + alt+title
    imgs = re.findall(r'<img[^>]*>', h)
    if len(imgs) == 0:
        issues.append("❌ Aucune image")
    else:
        for i, tag in enumerate(imgs):
            if 'alt=' not in tag:
                issues.append(f"❌ img #{i+1}: pas de alt")
            if 'title=' not in tag:
                issues.append(f"⚠️ img #{i+1}: pas de title")
        # doublon image inter-pages
        srcs = re.findall(r'src="/images/blog/([^"]+)"', h)
        for s in set(srcs):
            files = glob.glob(f"{site}/*.html") + glob.glob(f"{site}/blog/*.html")
            occ = sum(1 for f in files if f != path and s in open(f, encoding="utf-8").read())
            if occ > 0:
                issues.append(f"❌ image '{s}' utilisée sur une AUTRE page (doublon)")

    # 6. JSON-LD ImageObject unique + canonique
    if '"ImageObject"' not in h:
        issues.append("❌ Pas de JSON-LD ImageObject")
    elif h.count('"ImageObject"') > 1:
        issues.append("❌ Plusieurs ImageObject (doublon JSON-LD)")
    if 'rel="canonical"' not in h:
        issues.append("⚠️ Pas de canonical URL")

    # 7. Open Graph
    if 'property="og:image"' not in h and 'og:title' not in h:
        issues.append("⚠️ Pas d'Open Graph (og:title/og:image)")

    return issues

def main():
    if len(sys.argv) > 1:
        targets = [sys.argv[1]]
    else:
        targets = glob.glob(f"{site}/blog/*.html") + glob.glob(f"{site}/*.html")
    total = 0
    for t in targets:
        if not os.path.exists(t):
            continue
        iss = check_file(t)
        if iss:
            print(f"\n📄 {os.path.basename(t)}:")
            for i in iss:
                print("  " + i)
            total += len(iss)
        else:
            print(f"✅ {os.path.basename(t)}: SEO OK (Yoast)")
    print(f"\n=== {total} point(s) à corriger ===")

if __name__ == "__main__":
    main()
