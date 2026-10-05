#!/usr/bin/env python3
"""Inspirerende Quotes — zero-dependency web app.

Serveert een donkere quote-UI plus JSON-endpoints.
Dataset: echte quotes uit openbare bronnen (zie build_quotes.py).
Draait overal waar Python 3.8+ draait; deployment target: Railway.
"""
import json
import os
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTES_FILE = os.path.join(BASE_DIR, "quotes.json")

with open(QUOTES_FILE, encoding="utf-8") as fh:
    QUOTES = json.load(fh)

INDEX_HTML = os.path.join(BASE_DIR, "index.html")


class QuotesHandler(BaseHTTPRequestHandler):
    server_version = "QuotesApp/2.0"

    # ---------- helpers ----------
    def _respond(self, status, body, content_type):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status, payload):
        self._respond(
            status,
            json.dumps(payload, ensure_ascii=False),
            "application/json; charset=utf-8",
        )

    @staticmethod
    def _int_param(params, name, default=None):
        try:
            return int(params[name][0])
        except (KeyError, ValueError, IndexError):
            return default

    # ---------- routes ----------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        params = parse_qs(parsed.query)

        if path in ("/health", "/api/health"):
            self._json(200, {"status": "ok", "quotes": len(QUOTES), "authors": self._author_count()})
            return

        if path == "/api/quotes":
            self._json(200, {"quotes": QUOTES, "total": len(QUOTES)})
            return

        if path == "/api/stats":
            self._json(200, {"total_quotes": len(QUOTES), "total_authors": self._author_count()})
            return

        if path == "/api/authors":
            self._json(200, {"authors": self._authors()})
            return

        if path in ("/api/quote", "/api/quote/random"):
            self._send_one(params)
            return

        if path == "/":
            try:
                with open(INDEX_HTML, "rb") as fh:
                    self._respond(200, fh.read(), "text/html; charset=utf-8")
            except OSError:
                self._respond(500, "index.html ontbreekt", "text/plain; charset=utf-8")
            return

        self._respond(404, "Niet gevonden", "text/plain; charset=utf-8")

    def do_HEAD(self):
        self.do_GET()

    def _author_count(self):
        return len({q["author"] for q in QUOTES})

    def _authors(self):
        seen = {}
        for q in QUOTES:
            seen[q["author"]] = seen.get(q["author"], 0) + 1
        return [
            {"name": name, "count": count}
            for name, count in sorted(seen.items(), key=lambda kv: (-kv[1], kv[0].lower()))
        ]

    def _send_one(self, params):
        """Eén quote. `i` = index (voor vorige/volgende), `author` = filter, anders random."""
        pool = QUOTES
        author = params.get("author", [None])[0]
        if author:
            pool = [q for q in pool if q["author"] == author]
            if not pool:
                pool = QUOTES

        index = self._int_param(params, "i")
        if index is not None:
            index %= len(pool)
        else:
            index = random.randrange(len(pool))

        quote = pool[index]
        self._json(
            200,
            {
                "text": quote["text"],
                "author": quote["author"],
                "index": index,
                "total": len(QUOTES),
                "pool": len(pool),
                "authors": self._author_count(),
            },
        )

    def log_message(self, fmt, *args):
        print("[quotes] %s - %s" % (self.address_string(), fmt % args), flush=True)


def main():
    port = int(os.environ.get("PORT", "3000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), QuotesHandler)
    print(
        "Inspirational Quotes draait op http://0.0.0.0:%d (%d quotes, %d auteurs)"
        % (port, len(QUOTES), len({q["author"] for q in QUOTES})),
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
