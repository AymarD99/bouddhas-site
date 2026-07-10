#!/Users/aymarmichel/.hermes/hermes-agent/venv/bin/python
"""
Récupère les mots-clés Ubersuggest pour un lot de thématiques (batch économique).
Sort: data/keywords_batch.json  (utilisé par daily_content_pipeline.py)

NOTE (2026-07-10): le module `mcp` n'est PAS dans le python système mais dans le
venv Hermes (~/.hermes/hermes-agent/venv). Pour lancer ce script:
  ~/.hermes/hermes-agent/venv/bin/python scripts/ubersuggest_batch.py
Le shebang ci-dessus pointe déjà vers ce venv.

STRATÉGIE :
- Cibler la "spiritualité pratique" (symboles, tatouages, animaux totems, pierres,
  lune, infini, protection) = fort volume + faible difficulté (SD < 30).
- Utilise `match_keywords` (renvoie SD réel) au lieu de `keyword_suggestions` (SD null).
- Filtrer par search_difficulty (sd) : un site DA 4 ne peut pas ranker sur SD > 30.
- Quota rationné : ~18 seeds x 2 appels = 36 appels/jour max.

Usage: python3 scripts/ubersuggest_batch.py
"""
import asyncio, json, os, pathlib, datetime
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

HERMES = pathlib.Path(os.path.expanduser("~/.hermes"))
TOKEN = json.load(open(HERMES / "mcp-tokens/ubersuggest.json"))["access_token"]
URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Thématiques "spiritualité pratique" (fort volume, faible difficulté) — mix bouddhiste appliqué
SEEDS = [
    "symbole bouddhiste", "signification bouddhisme", "bouddhisme tatouage",
    "animal totem", "pierre spirituelle", "signification lune", "yin yang signification",
    "ganesha signification", "symbole infini", "symbole de protection",
    "mantras bouddhistes", "méditation pleine conscience", "zen bouddhisme",
    "chakra signification", "mala bouddhiste", "fleur de lotus signification",
    "mandala signification", "bouddha signification",
]

# Mots déclencheurs = "spiritualité pratique" (bonus de score + SD estimé si inconnu)
PRACTICE_BONUS = ["signification", "symbole", "tatouage", "totem", "pierre", "lune",
                  "infini", "protection", "ganesha", "yin", "lotus", "mandala", "mala",
                  "chakra", "mantra", "méditation", "zen", "bouddha", "karma", "âme"]

MAX_SD = 40          # Seuil difficulté : au-delà, un DA 4 ne peut pas ranker (élargi de 30)
MIN_VOLUME = 10      # Filtre faible volume (Ubersuggest FR donne souvent 10-100)
MAX_VOLUME = 50000   # Cap anti-anomalie (ex: "infini symbol" 246k = erreur API)

async def call(session, name, args):
    try:
        res = await session.call_tool(name, args)
        for c in res.content:
            if hasattr(c, "text"):
                return c.text
    except Exception as e:
        return json.dumps({"error": str(e)[:150]})
    return "{}"

def score_kw(kw, volume, competition, sd):
    # Score de base = volume / concurrence
    base = volume / (competition + 0.01)
    bonus = 1.0
    for b in PRACTICE_BONUS:
        if b in kw:
            bonus += 0.15  # +15% par mot "spiritualité pratique" présent
    # Pénalité si difficulté élevée (on ne sait pas si on peut ranker)
    if sd is not None and sd > MAX_SD:
        bonus *= 0.3
    return base * bonus

async def main():
    out = {"generated": datetime.datetime.now().isoformat(), "keywords": {}}
    async with streamablehttp_client(URL, headers=HEADERS) as (r, w, _), ClientSession(r, w) as s:
        await s.initialize()
        for kw in SEEDS:
            print(f"→ {kw}...")
            ov = await call(s, "keyword_overview", {"keyword": kw, "location": "fr", "language": "fr"})
            # match_keywords renvoie le SD réel (keyword_suggestions renvoie sd=null)
            mk = await call(s, "match_keywords", {"keywords": [kw], "language": "fr", "locId": 2250, "sortby": "-search_volume"})
            # Si quota épuisé → message clair (pas "0 cible" silencieux)
            if "daily reports limit" in mk or "403" in mk:
                print(f"  ⚠️ Quota Ubersuggest atteint (100/jour) pour '{kw}' — réessaie demain")
                out["keywords"][kw] = {"error": "quota_depasse"}
                continue
            out["keywords"][kw] = {"overview": ov, "match": mk}
    # Parse pour extraire les top suggestions (volume, concurrence, difficulté)
    ranked = []
    for kw, data in out["keywords"].items():
        try:
            d = json.loads(data["match"])
            results = d.get("suggestions", [])
            for r in results:
                if not isinstance(r, dict):
                    continue
                kwr = (r.get("keyword") or "").lower().strip()
                if not kwr:
                    continue
                vol = r.get("volume", 0) or 0
                if vol < MIN_VOLUME or vol > MAX_VOLUME:
                    continue
                comp = r.get("competition", 1) or 1
                sd = r.get("sd")
                # SD inconnu mais mot "spiritualité pratique" → on estime facile (15)
                if sd is None:
                    sd = 15 if any(b in kwr for b in PRACTICE_BONUS) else 40
                if sd > MAX_SD:
                    continue
                ranked.append({
                    "keyword": kwr,
                    "volume": vol,
                    "competition": comp,
                    "sd": sd,
                    "score": round(score_kw(kwr, vol, comp, sd), 2),
                })
        except Exception:
            pass
    # Tri: score décroissant (volume/concurrence + bonus spiritualité pratique)
    ranked.sort(key=lambda x: x["score"], reverse=True)
    # Dédupliquer par mot-clé
    seen = set()
    dedup = []
    for r in ranked:
        if r["keyword"] in seen:
            continue
        seen.add(r["keyword"])
        dedup.append(r)
    out["ranked_targets"] = dedup[:30]
    path = pathlib.Path("/Users/aymarmichel/bouddhas-site/data/keywords_batch.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"✅ {len(dedup)} cibles triées (SD<{MAX_SD}, vol {MIN_VOLUME}-{MAX_VOLUME}) → {path}")

asyncio.run(main())
