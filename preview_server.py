#!/usr/bin/env python3
# Serveur de preview local exposé sur le réseau (0.0.0.0)
# Rewrite URLs sans .html (comme Netlify)
import http.server, socketserver, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8077
ROOT = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)
    def translate_path(self, path):
        p = super().translate_path(path)
        if os.path.exists(p + ".html"):
            return p + ".html"
        return p
    def end_headers(self):
        # Cache: fonts/images/CSS/JS = 1 an, HTML = pas de cache
        ext = self.path.split('.')[-1].lower()
        if ext in ('woff2','jpg','jpeg','png','css','js','ico'):
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        else:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

# 0.0.0.0 = écoute sur toutes les interfaces (réseau local)
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Preview Bouddhas.fr → http://0.0.0.0:{PORT}/")
    print(f"Réseau local → http://192.168.0.31:{PORT}/")
    httpd.serve_forever()
