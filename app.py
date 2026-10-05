#!/usr/bin/env python3
"""Inspirational Quotes — tiny zero-dependency web app.

Serves a single-page quote UI plus a /api/quote JSON endpoint.
Runs anywhere Python 3.8+ runs; deployment target: Railway.
"""
import json
import os
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTES_FILE = os.path.join(BASE_DIR, "quotes.json")

with open(QUOTES_FILE, encoding="utf-8") as fh:
    QUOTES = json.load(fh)


class QuotesHandler(BaseHTTPRequestHandler):
    server_version = "QuotesApp/1.0"

    def _respond(self, status, body, content_type):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status, payload):
        self._respond(status, json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8")

    def do_GET(self):
        path = self.path.split("?", 1)[0].rstrip("/") or "/"

        if path == "/health":
            self._json(200, {"status": "ok", "quotes": len(QUOTES)})
            return

        if path == "/api/quote":
            index = None
            if "?" in self.path:
                for part in self.path.split("?", 1)[1].split("&"):
                    if part.startswith("i="):
                        try:
                            index = int(part[2:]) % len(QUOTES)
                        except ValueError:
                            index = None
            quote = QUOTES[index] if index is not None else random.choice(QUOTES)
            self._json(200, {"text": quote["text"], "author": quote["author"], "total": len(QUOTES)})
            return

        if path == "/api/quotes":
            self._json(200, {"quotes": QUOTES, "total": len(QUOTES)})
            return

        if path == "/":
            try:
                with open(os.path.join(BASE_DIR, "index.html"), "rb") as fh:
                    self._respond(200, fh.read(), "text/html; charset=utf-8")
            except OSError:
                self._respond(500, "index.html ontbreekt", "text/plain; charset=utf-8")
            return

        self._respond(404, "Niet gevonden", "text/plain; charset=utf-8")

    def do_HEAD(self):
        self.do_GET()

    def log_message(self, fmt, *args):
        print("[quotes] %s - %s" % (self.address_string(), fmt % args), flush=True)


def main():
    port = int(os.environ.get("PORT", "3000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), QuotesHandler)
    print("Inspirational Quotes draait op http://0.0.0.0:%d (%d quotes)" % (port, len(QUOTES)), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
