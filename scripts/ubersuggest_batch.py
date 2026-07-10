#!/usr/bin/env python3
"""
Récupère les mots-clés Ubersuggest pour un lot de thématiques (batch économique).
Sort: data/keywords_batch.json  (utilisé par content_pipeline.py)
Usage: python3 scripts/ubersuggest_batch.py
"""
import asyncio, json, os, pathlib, datetime
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

HERMES = pathlib.Path(os.path.expanduser("~/.hermes"))
TOKEN = json.load(open(HERMES / "mcp-tokens/ubersuggest.json"))["access_token"]
URL = "https://ubersuggest-mcp.neilpatelapi.com/mcp"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Thématiques à cibler (rotation quotidienne possible via argv)
SEEDS = ["bouddhisme", "méditation", "bouddha", "mantra", "pleine conscience", "mindfulness"]

async def call(session, name, args):
    try:
        res = await session.call_tool(name, args)
        for c in res.content:
            if hasattr(c, "text"):
                return c.text
    except Exception as e:
        return json.dumps({"error": str(e)[:150]})
    return "{}"

async def main():
    out = {"generated": datetime.datetime.now().isoformat(), "keywords": {}}
    async with streamablehttp_client(URL, headers=HEADERS) as (r, w, _), ClientSession(r, w) as s:
        await s.initialize()
        for kw in SEEDS:
            print(f"→ {kw}...")
            ov = await call(s, "keyword_overview", {"keyword": kw, "location": "fr", "language": "fr"})
            sug = await call(s, "keyword_suggestions", {"keywords": [kw], "location": "fr", "language": "fr"})
            out["keywords"][kw] = {"overview": ov, "suggestions": sug}
    # Parse pour extraire les top suggestions (volume, concurrence)
    ranked = []
    for kw, data in out["keywords"].items():
        try:
            d = json.loads(data["suggestions"])
            for r in d.get("results", []):
                if isinstance(r, dict) and r.get("volume", 0) and r.get("volume") > 100:
                    ranked.append({
                        "keyword": r["keyword"],
                        "volume": r["volume"],
                        "competition": r.get("competition", 1),
                    })
        except Exception:
            pass
    # Tri: volume décroissant, concurrence croissante (facilité)
    ranked.sort(key=lambda x: (x["volume"] / (x["competition"] + 0.01)), reverse=True)
    out["ranked_targets"] = ranked[:30]
    path = pathlib.Path("/Users/aymarmichel/bouddhas-site/data/keywords_batch.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"✅ {len(ranked)} cibles triées → {path}")

asyncio.run(main())
