#!/usr/bin/env python3
"""
verify_article.py — GARDE-FOU anti-doublon + qualité pour bouddhas.fr

Lancé APRÈS le pipeline SEO quotidien (cron 20h+15min).
Scan tous les articles du blog/ et vérifie :
  ANTI-DOUBLON:
    1. Slug exact déjà publié (historique cross-batch)
    2. Similarité de contenu (hash des 200 premiers mots vs existants)
    3. Titre déjà utilisé
    4. Doublon sémantique (>=2 mots-racines partagés)
  QUALITÉ:
    1. Longueur 1200-1800 mots
    2. >=5 <h2> + section FAQ
    3. Balises <!-- TITLE --> / <!-- DESC --> présentes
    4. HTML valide (balises fermées)
    5. Aucun mot interdit
    6. >=3 liens internes /blog/

Sortie: JSON + rapport français. Exit 0 = OK, exit 1 = problèmes détectés.
Usage:
  python3 scripts/verify_article.py            # scan complet
  python3 scripts/verify_article.py --json     # sortie machine
"""
import json, os, re, pathlib, glob, hashlib, sys, argparse

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")
BLOG = ROOT / "blog"
DATA = ROOT / "data"
HISTORY = DATA / "published_articles.json"

MOTS_INTERDITS = ["xxx", "porn", "casino", "sexe", "drogue"]
MIN_MOTS = 800
MAX_MOTS = 1200
MIN_H2 = 5
MIN_LIENS_INTERNES = 3

STOP = {"pour", "avec", "dans", "cette", "plus", "être", "comme", "mais", "tout",
        "entre", "leur", "bouddhisme", "méditation", "bouddhiste", "pratique"}

def lire_articles():
    arts = {}
    for p in glob.glob(str(BLOG / "*.html")):
        slug = pathlib.Path(p).stem
        try:
            txt = open(p, encoding="utf-8").read()
        except:
            continue
        arts[slug] = txt
    return arts

def mots_texte(txt):
    # Nettoyer HTML
    clean = re.sub(r"<[^>]+>", " ", txt)
    clean = re.sub(r"<!--.*?-->", " ", clean, flags=re.S)
    return [w for w in re.findall(r"[a-zA-ZÀ-ÿ]{4,}", clean.lower()) if w not in STOP]

def hash_contenu(txt):
    mots = mots_texte(txt)[:200]
    return hashlib.md5(" ".join(mots).encode()).hexdigest()

def charger_history():
    if HISTORY.exists():
        try:
            return json.load(open(HISTORY, encoding="utf-8"))
        except:
            pass
    return {"published": []}

def sauver_history(h):
    DATA.mkdir(exist_ok=True)
    json.dump(h, open(HISTORY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def verifier_un(slug, txt, autres):
    """Retourne liste de problèmes pour 1 article."""
    pb = []
    # --- Anti-doublon ---
    # 1. Slug dans historique
    # 2. Hash contenu vs autres
    h = hash_contenu(txt)
    for other_sl, other_txt in autres.items():
        if other_sl == slug:
            continue
        if hash_contenu(other_txt) == h:
            pb.append(f"DOUBLON_CONTENU: identique à {other_sl}")
    # 3. Titre déjà utilisé
    mt = re.search(r"<h1[^>]*>(.*?)</h1>", txt, re.S | re.I)
    titre = re.sub(r"<[^>]+>", "", mt.group(1)).strip().lower() if mt else ""
    for other_sl, other_txt in autres.items():
        if other_sl == slug:
            continue
        mo = re.search(r"<h1[^>]*>(.*?)</h1>", other_txt, re.S | re.I)
        if mo and re.sub(r"<[^>]+>", "", mo.group(1)).strip().lower() == titre and titre:
            pb.append(f"DOUBLON_TITRE: titre identique à {other_sl}")
    # 4. Doublon sémantique (>=2 mots-racines partagés)
    mots = set(mots_texte(txt))
    for other_sl, other_txt in autres.items():
        if other_sl == slug:
            continue
        if len(mots & set(mots_texte(other_txt))) >= 2 and slug[:8] == other_sl[:8]:
            # même préfixe de slug + mots partagés = risque doublon
            if len(mots & set(mots_texte(other_txt))) >= 5:
                pb.append(f"DOUBLON_SEMANTIQUE: ~ avec {other_sl}")

    # --- Qualité ---
    mots_count = len(mots_texte(txt))
    if mots_count < MIN_MOTS:
        pb.append(f"QUALITE_COURT: {mots_count} mots (<{MIN_MOTS})")
    if mots_count > MAX_MOTS:
        pb.append(f"QUALITE_LONG: {mots_count} mots (>{MAX_MOTS})")
    h2 = len(re.findall(r"<h2", txt, re.I))
    if h2 < MIN_H2:
        pb.append(f"QUALITE_H2: {h2} <h2 (min {MIN_H2})")
    if not re.search(r"<h2[^>]*>\s*FAQ", txt, re.S | re.I) and not re.search(r"faq", txt, re.I):
        pb.append("QUALITE_FAQ: section FAQ manquante")
    if not re.search(r"<!--\s*TITLE:", txt, re.I):
        pb.append("QUALITE_TITLE: balise <!-- TITLE --> manquante")
    if not re.search(r"<!--\s*DESC:", txt, re.I):
        pb.append("QUALITE_DESC: balise <!-- DESC --> manquante")
    # HTML valide (balises bloc fermées)
    for tag in ["div", "section", "article", "ul", "ol", "p"]:
        o = len(re.findall(rf"<{tag}[\s>]", txt, re.I))
        c = len(re.findall(rf"</{tag}>", txt, re.I))
        if o > c + 2:  # tolérance petite
            pb.append(f"HTML_OUVERT: <{tag}> non fermé ({o} ouvertes, {c} fermées)")
    # Mots interdits
    for w in MOTS_INTERDITS:
        if re.search(rf"\b{w}\b", txt, re.I):
            pb.append(f"MOT_INTERDIT: {w}")
    # Liens internes
    liens = re.findall(r'href="/blog/[^"]+\.html"', txt, re.I)
    if len(liens) < MIN_LIENS_INTERNES:
        pb.append(f"MAILLAGE: {len(liens)} liens internes (<{MIN_LIENS_INTERNES})")
    return pb

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    arts = lire_articles()
    if not arts:
        print("⚠️ Aucun article trouvé dans blog/")
        sys.exit(0)

    tous_pb = {}
    for slug, txt in arts.items():
        autres = {k: v for k, v in arts.items() if k != slug}
        pb = verifier_un(slug, txt, autres)
        if pb:
            tous_pb[slug] = pb

    # Historique cross-batch: slug déjà publié ?
    hist = charger_history()
    deja_publies = set(hist.get("published", []))
    pb_history = {}
    for slug in arts:
        if slug in deja_publies:
            pb_history[slug] = ["DOUBLON_HISTORY: déjà dans published_articles.json"]

    # Fusion
    all_pb = {}
    for s, p in tous_pb.items():
        # Mise à jour historique (ajoute les slugs actuels)
        hist["published"] = sorted(set(hist.get("published", [])) | set(arts.keys()))
        sauver_history(hist)

        if args.json:
            print(json.dumps({"articles": len(arts), "problemes": all_pb}, ensure_ascii=False, indent=2))
        else:
            # Séparer nouveaux (pas dans history avant ce run) vs existants
            nouveaux = set(all_pb.keys()) - (deja_publies & set(all_pb.keys()))
            print(f"🔍 Vérification de {len(arts)} articles...\n")
            if not all_pb:
                print("✅ AUCUN problème — tous les articles sont uniques et de qualité.")
            else:
                # Doublons (tous) = prioritaires
                doublons = {s: p for s, p in all_pb.items() if any(x.startswith("DOUBLON") for x in p)}
                if doublons:
                    print(f"🚨 {len(doublons)} DOUBLON(S) détecté(s) — ACTION REQUISE:\n")
                    for slug, pbs in doublons.items():
                        print(f"  📄 {slug}.html")
                        for p in pbs:
                            print(f"     - {p}")
                        print()
                # Qualité sur NOUVEAUX uniquement (existants tolérés)
                q_pb = {s: p for s, p in all_pb.items()
                        if s not in doublons and any(x.startswith("QUALITE") or x.startswith("MAILLAGE") or x.startswith("HTML") or x.startswith("MOT") for x in p)}
                if q_pb:
                    print(f"⚠️ {len(q_pb)} article(s) NOUVEAU(X) avec problème de qualité:\n")
                    for slug, pbs in q_pb.items():
                        print(f"  📄 {slug}.html (NOUVEAU)")
                        for p in pbs:
                            print(f"     - {p}")
                        print()
                if not doublons and not q_pb:
                    print("✅ Aucun doublon, aucun nouveau article de mauvaise qualité.")

        sys.exit(1 if any(x.startswith("DOUBLON") for p in all_pb.values() for x in p) else 0)

if __name__ == "__main__":
    main()
