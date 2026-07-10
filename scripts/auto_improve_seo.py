#!/usr/bin/env python3
"""
auto_improve_seo.py — Amélioration SEO auto hebdomadaire (Hermes → OpenCode).

Trouve le article de blog le plus faible (moins de 1200 mots, sans FAQ, ou peu de H2)
et demande a l'agent bouddhas-seo (OpenCode) de l'ameliorer EN LOCAL (branche).
Jamais deploye — l'humain verifie en local puis merge si OK.

Regle UX: max 1200 mots (eviter suroptimisation). Ton bouddhiste calme.
Usage: python3 scripts/auto_improve_seo.py
"""
import glob, os, re, subprocess, pathlib, json, datetime

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
BLOG = ROOT / "blog"
OPENCODE = ROOT / "scripts"  # pas utilise direct, on appelle opencode run

def score_article(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    body = re.sub(r"<[^>]+>", " ", txt)
    mots = len(re.findall(r"\w+", body))
    h2 = len(re.findall(r"<h2", txt, re.I))
    faq = "faq" in txt.lower() or "questions fr" in txt.lower()
    liens = len(re.findall(r'href="/blog/', txt))
    # Score faiblesse: moins de mots = plus faible, sans FAQ = +penalite
    weakness = 0
    if mots < 1200: weakness += (1200 - mots)
    if not faq: weakness += 200
    if h2 < 5: weakness += (5 - h2) * 30
    if liens < 3: weakness += (3 - liens) * 20
    return weakness, mots, h2, faq, liens

def main():
    arts = sorted(glob.glob(str(BLOG / "*.html")))
    scored = []
    for a in arts:
        w, m, h, f, l = score_article(a)
        scored.append((w, os.path.basename(a), m, h, f, l))
    scored.sort(reverse=True)
    if not scored:
        print("Aucun article a ameliorer"); return
    top = scored[0]
    print(f"Article le plus faible: {top[1]} (score faiblesse {top[0]})")
    print(f"  mots={top[2]} h2={top[3]} faq={top[4]} liens={top[5]}")
    if top[0] < 50:
        print("✅ Tous les articles sont deja bons (faiblesse < 50). Rien a faire.")
        return
    slug = pathlib.Path(top[1]).stem
    branch = f"seo-auto-{slug[:20]}-{datetime.date.today().strftime('%Y%m%d')}"
    desc = f"""Ameliore l'article blog/{top[1]} pour le SEO, EN LOCAL (branche {branch}), NE PAS deployer.
Regles STRICTES UX (eviter suroptimisation):
- LONGUEUR MAX 1200 mots (viser 900-1100). Pas de contenu gonfle.
- Garde le ton bouddhiste calme et naturel. Pas de mots-cles forces.
- Ajoute sections utiles (h2) si manquantes, et une FAQ courte (3 questions).
- 3 liens internes vers articles existants (meditation, pierres, bouddhisme).
- NE MODIFIE PAS le CSS global (variables --gold, design dore/noir).
- Francais. Rapport des changements en commentaire en tete du fichier."""
    print(f"\nLancement OpenCode (agent bouddhas-seo) sur branche {branch}...")
    try:
        p = subprocess.run(
            ["opencode", "run", "-m", "nim/z-ai/glm-5.2", "--agent", "bouddhas-seo"],
            input=desc, capture_output=True, text=True, timeout=550
        )
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = 124
        print("⏱️ Agent a depasse le temps (lent). Verifie la branche manuellement plus tard.")
    print(f"Agent termine (rc={rc}). Branche {branch} prete en local.")
    print(f"Verif locale: ouvre blog/{top[1]} puis merge si OK (gh pr create).")

if __name__ == "__main__":
    main()
