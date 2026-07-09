#!/usr/bin/env python3
"""
IMPORTANT: À exécuter UNIQUEMENT après avoir configuré les redirects 301
dans Shopify (ou Netlify) pour les anciens handles.

Ce script régénère des handles FR propres à partir des titres FR des produits
publiés, puis les pousse via Admin API.

⚠️  CHANGER UN HANDLE = ANCIENNE URL 404 SANS REDIRECT.
    Faire un backup + configurer les 301 avant d'exécuter en prod.
"""
import json, subprocess, time, re, unicodedata

ADMIN_TOKEN = "shpat_REPLACE_ME"  # mettre le vrai token
API = "https://my-bouddha-store.myshopify.com/admin/api/2024-07"

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r"[^\w\s-]", "", s.lower())
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:60]

def get_products():
    out, link = [], f"{API}/products.json?fields=id,title,handle&limit=250&published_status=published"
    while link:
        r = subprocess.run(f'curl -s -H "X-Shopify-Access-Token: {ADMIN_TOKEN}" "{link}"', shell=True, capture_output=True, text=True, timeout=30)
        head, _, body = r.stdout.partition("\r\n\r\n")
        if not body: head, _, body = r.stdout.partition("\n\n")
        d = json.loads(body)
        out += d.get("products", [])
        nxt = None
        for line in head.splitlines():
            if line.lower().startswith("link:") and 'rel="next"' in line:
                nxt = line[line.find("<")+1:line.find(">")]
        link = nxt
    return out

def update_handle(pid, handle):
    url = f"{API}/products/{pid}.json"
    data = json.dumps({"product": {"id": pid, "handle": handle}})
    cmd = f'curl -s -X PUT "{url}" -H "Content-Type: application/json" -H "X-Shopify-Access-Token: {ADMIN_TOKEN}" -d \'{data}\''
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return "handle" in r.stdout

if __name__ == "__main__":
    prods = get_products()
    plan = []
    for p in prods:
        new = slugify(p["title"])
        if new and new != p["handle"]:
            plan.append((p["id"], p["handle"], new))
    print(f"{len(plan)} handles à régénérer FR")
    json.dump(plan, open("handles_rename_plan.json", "w"), indent=2)
    print("Plan sauvé dans handles_rename_plan.json — vérifier avant exécution.")
    # Décommenter pour appliquer:
    # for pid, old, new in plan:
    #     update_handle(pid, new); time.sleep(0.5)
