#!/usr/bin/env python3
"""
PIPELINE QUOTIDIEN AUTONOME (1 déploiement/jour, économe tokens Netlify)
1. Recherche Ubersuggest (1 batch/jour, quota rationné)
2. Sélection de 5-10 mots-clés non couverts (fort volume / faible concurrence)
3. Rédaction de chaque corps d'article (qualité maximale) via OpenRouter hy3:free
4. Publication locale (post_article.py)
5. Maillage interne + E-E-A-T (scripts existants)
6. 1 SEUL déploiement Netlify (deploy.sh)

Usage: python3 scripts/daily_content_pipeline.py
"""
import json, os, re, pathlib, glob, subprocess, sys, urllib.request, urllib.error, argparse

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
BLOG = ROOT / "blog"
DATA = ROOT / "data"
SCRIPTS = ROOT / "scripts"
DATA.mkdir(exist_ok=True)

# --- 1. Recherche Ubersuggest (1 batch/jour) ---
print("🔍 [1/6] Recherche Ubersuggest (batch unique)...")
subprocess.run([sys.executable, str(SCRIPTS/"ubersuggest_batch.py")], cwd=str(ROOT))

# --- 2. Sélection des cibles ---
parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=8, help="Nombre max d'articles/jour")
args, _ = parser.parse_known_args()

def existing_slugs():
    slugs = set()
    for p in glob.glob(str(BLOG/"*.html")):
        slugs.add(pathlib.Path(p).stem)
    return slugs

def is_duplicate(sl, covered):
    # Doublon exact
    if sl in covered: return True
    # Doublon approximatif: si un slug couvert est sous-chaine du mot-clé ou inverse
    for c in covered:
        if c in sl or sl in c:
            return True
    return False

def slugify(kw):
    return re.sub(r'[^a-z0-9]+','-',kw.lower()).strip('-')

print("🎯 [2/6] Sélection des cibles...")
d = json.load(open(DATA/"keywords_batch.json"))
targets = d.get("ranked_targets", [])
covered = existing_slugs()
chosen = []
for t in targets:
    kw = t["keyword"].lower().strip()
    sl = slugify(kw)
    # Éviter doublons (exacts + approximatifs) + mots trop courts/génériques
    if is_duplicate(sl, covered): continue
    if len(kw) < 4: continue
    if any(b in kw for b in ["xxx","porn","casino"]): continue
    chosen.append((sl, kw, t.get("volume",0), t.get("competition",1)))
    if len(chosen) >= args.limit: break  # max /jour (fourchette 5-10)
if not chosen:
    print("  ⚠️ Aucune nouvelle cible (tout est couvert). Pas de déploiement pour éviter un token Netlify inutile.")
    sys.exit(0)
print(f"  → {len(chosen)} cibles: {[c[1] for c in chosen]}")

# --- 3. Rédaction via OpenRouter (hy3:free) ---
print("✍️  [3/6] Rédaction des articles (qualité maximale)...")
KEY = open(pathlib.Path.home()/".hermes/.env").read()
import re as _re
m = _re.search(r"OPENROUTER_API_KEY=([^\n]+)", KEY)
OR_KEY = m.group(1).strip() if m else ""

def rediger(kw, volume):
    prompt = f"""Tu es un expert SEO senior. Rédige un article de blog en français (FR) sur le sujet : "{kw}".
L'article doit viser la qualité maximale (meilleur que le top 10 Google).
Contraintes STRICTES de format (réponds UNIQUEMENT en HTML, sans balise <html>/<head>/<body>, sans bloc de code markdown) :
- Une phrase d'intro <p class="article-intro"> qui répond DIRECTEMENT à l'intention de recherche
- Plusieurs <h2> (au moins 5) : définition, origine, pratique concrète, bienfaits, FAQ
- Des <h3> si utile
- Paragraphes courts, listes <ul>/<ol> pour la lisibilité
- Une section <h2>FAQ</h2> avec 2-3 questions/réponses
- Une section <h2>Articles liés</h2> avec 3 liens <a href="/blog/SLUG.html"> vers des articles existants (méditation-debutants, meditation-guidee, mantras-bouddhistes, bouddhisme-debutant, meditation-zen, meditation-pleine-conscience)
- Ton humain, professionnel, français impeccable, aucune faute
- Ne JAMAIS inventer de faits ; si source nécessaire, cite Wikipédia/Buddhanet
- Longueur : 1200-1800 mots
Volume recherche visé : {volume}. Adapte la profondeur."""
    models = ["poolside/laguna-m.1:free", "google/gemma-4-26b-a4b-it:free", "meta-llama/llama-3.3-70b-instruct:free"]
    for attempt in range(3):
        for mdl in models:
            body = {
                "model": mdl,
                "messages": [{"role":"user","content": prompt}],
                "temperature": 0.7, "max_tokens": 4000
            }
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(body).encode(),
                headers={"Authorization":f"Bearer {OR_KEY}","Content-Type":"application/json"})
            try:
                resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
                txt = resp.get("choices",[{}])[0].get("message",{}).get("content")
                if not txt:
                    continue
                # Nettoyer les éventuels blocs markdown
                txt = txt.strip()
                if txt.startswith("```"):
                    txt = re.sub(r"^```[a-z]*\n?|\n?```$", "", txt, flags=re.S)
                return txt
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    continue  # try next model
                print(f"    ⚠️ HTTP {e.code} {kw}")
            except Exception as e:
                print(f"    ⚠️ Erreur {kw}: {str(e)[:100]}")
    print(f"    ⚠️ Tous modèles échoués pour {kw}")
    return None

# --- 4. Publication locale ---
print("📝 [4/6] Publication locale (post_article.py)...")
created = 0
for sl, kw, vol, comp in chosen:
    print(f"  → {kw}...")
    body = rediger(kw, vol)
    if not body:
        print(f"    ⚠️ Rédaction échouée, skip"); continue
    draft = BLOG/"_drafts"/f"{sl}.html"
    draft.parent.mkdir(exist_ok=True)
    draft.write_text(f"<h1>{kw.capitalize()}</h1>\n{body}", encoding="utf-8")
    # Publication
    r = subprocess.run([sys.executable, str(SCRIPTS/"post_article.py"),
        "--slug", sl, "--title", kw.capitalize(),
        "--desc", f"Guide complet sur {kw} : signification, bienfaits et pratique. Média indépendant bouddhisme & méditation.",
        "--prompt", f"{sl} spiritual calm", "--category", "meditation",
        "--html-file", str(draft)], cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode != 0:
        print(f"    ⚠️ Échec publication {sl}: {r.stderr[-200:]}")
        draft.unlink(missing_ok=True)
        continue
    draft.unlink(missing_ok=True)
    created += 1

# --- 5. Maillage + E-E-A-T ---
print("🔗 [5/6] Maillage interne + E-E-A-T...")
subprocess.run([sys.executable, str(SCRIPTS/"seo_postprocess.py")], cwd=str(ROOT))
subprocess.run([sys.executable, str(SCRIPTS/"internal_linking.py")], cwd=str(ROOT))

# --- 6. 1 SEUL déploiement (uniquement si des articles ont été créés) ---
if created == 0:
    print("⚠️ Aucun article créé → PAS de déploiement (économise token Netlify).")
    sys.exit(0)
print(f"🚀 [6/6] Déploiement unique Netlify ({created} article(s) créé(s))...")
subprocess.run(["bash", str(ROOT/"deploy.sh")], cwd=str(ROOT))
print("\n✅ PIPELINE TERMINÉ — 1 déploiement effectué pour tout le lot.")
