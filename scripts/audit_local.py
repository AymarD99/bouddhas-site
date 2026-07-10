#!/usr/bin/env python3
"""Scan local du site pour confirmer les 6 problèmes Ubersuggest par les données."""
import glob, re

files = glob.glob("*.html") + glob.glob("blog/*.html")
report = {"no_h1": [], "no_meta_desc": [], "short_title": [], "dup_title": [], "thin_content": []}
titles = []

for f in files:
    try:
        html = open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    # H1
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if not h1 or not h1[0].strip():
        report["no_h1"].append(f)
    # Meta description
    md = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', html, re.I)
    if not md or not md.group(1).strip():
        report["no_meta_desc"].append(f)
    # Title
    t = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    title_txt = t.group(1).strip() if t else ""
    if len(title_txt) < 30:
        report["short_title"].append((f, len(title_txt), title_txt))
    if title_txt:
        titles.append((f, title_txt.lower()))
    # Word count
    txt = re.sub(r"<script.*?</script>", "", html, flags=re.S | re.I)
    txt = re.sub(r"<style.*?</style>", "", txt, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    words = len(txt.split())
    if words < 300:
        report["thin_content"].append((f, words))

# Dup titles
from collections import Counter
tc = Counter([t for _, t in titles])
dups = {t: c for t, c in tc.items() if c > 1}
report["dup_title"] = [(f, t) for f, t in titles if t in dups]

for k, v in report.items():
    print(f"=== {k} ({len(v)}) ===")
    if k == "dup_title":
        for f, t in v:
            print(f"  {f} :: {t}")
    elif k == "short_title":
        for f, n, t in v:
            print(f"  {f} ({n}c) :: {t[:60]}")
    elif k == "thin_content":
        for f, n in v:
            print(f"  {f} ({n} mots)")
    else:
        for f in v:
            print(f"  {f}")
    print()
