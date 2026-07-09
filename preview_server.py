#!/usr/bin/env python3
# Serveur de preview local — rewrite URLs sans .html (comme Netlify)
# Usage: python3 preview_server.py [port]
import http.server, socketserver, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
ROOT = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def translate_path(self, path):
        # Essaie .html si la route n'existe pas
        p = super().translate_path(path)
        if not os.path.exists(p) and not os.path.isdir(p):
            if os.path.exists(p + ".html"):
                return p + ".html"
        return p

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"Preview Bouddhas.fr → http://127.0.0.1:{PORT}/")
    httpd.serve_forever()
