#!/usr/bin/env python3
"""Bouw quotes.json uit echte, openbare bronnen.

Geen verzonnen quotes: alles komt uit bestaande open datasets.
Bronnen:
  1. dwyl/quotes      (GPL-2 op de repo; de quotes zelf zijn publiek domein)
  2. mubaris/motivate (MIT)

Draai:  python3 build_quotes.py
Uit:    quotes.json  +  verslag op stdout
"""
import json
import os
import re
import unicodedata
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "quotes.json")

SOURCES = [
    {
        "name": "dwyl/quotes",
        "url": "https://raw.githubusercontent.com/dwyl/quotes/master/quotes.json",
        "license": "GPL-2 (repo) / publiek domein (de citaten)",
    },
    {
        "name": "mubaris/motivate",
        "url": "https://raw.githubusercontent.com/mubaris/motivate/master/motivate/data_unique/unique_quotes.json",
        "license": "MIT",
    },
]

MIN_LEN = 20          # korter dan dit is geen bruikbare quote
MAX_LEN = 400         # langer dan dit past niet in een Short
JUNK_AUTHORS = {"", "unknown", "author unknown", "n/a", "none"}


def norm(text: str) -> str:
    """Normaliseer voor ontdubbeling: kleine letters, alleen alfanumeriek."""
    folded = unicodedata.normalize("NFKD", text.lower())
    return re.sub(r"[^a-z0-9]", "", folded)


def tidy(text: str) -> str:
    """Schoon de quote op zonder de inhoud te veranderen."""
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip('"').strip()


def fetch(source: dict):
    """Haal één bron op en geef (quote, auteur)-paren terug."""
    req = urllib.request.Request(
        source["url"], headers={"User-Agent": "quotes-app-builder/2.0"}
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    if isinstance(raw, dict):
        raw = raw.get("data") or raw.get("quotes") or []

    pairs = []
    for row in raw:
        text = row.get("text") or row.get("quote") or ""
        author = row.get("author") or ""
        if isinstance(author, str):
            author = author.replace(", type.fit", "").strip()
        pairs.append((tidy(text), author.strip() if isinstance(author, str) else ""))
    return pairs


def main():
    seen = {}          # genormaliseerde tekst -> record
    per_source = {}

    for source in SOURCES:
        try:
            pairs = fetch(source)
        except Exception as exc:                       # netwerkstoring: bron overslaan
            print("  ! %-20s overgeslagen: %s" % (source["name"], exc))
            continue

        added = 0
        for text, author in pairs:
            if not (MIN_LEN <= len(text) <= MAX_LEN):
                continue
            if author.lower() in JUNK_AUTHORS:
                author = "Onbekend"
            key = norm(text)
            if not key or key in seen:
                continue
            seen[key] = {
                "text": text,
                "author": author,
                "source": source["name"],
            }
            added += 1

        per_source[source["name"]] = added
        print("  %-20s %5d records -> %5d uniek nieuw" % (source["name"], len(pairs), added))

    quotes = sorted(seen.values(), key=lambda q: (q["author"].lower(), q["text"]))

    if len(quotes) < 900:
        raise SystemExit("FOUT: slechts %d unieke quotes, minimum is 900." % len(quotes))

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(quotes, fh, ensure_ascii=False, indent=1)

    print()
    print("Totaal unieke quotes : %d" % len(quotes))
    print("Unieke auteurs       : %d" % len({q["author"] for q in quotes}))
    print("Weggeschreven naar   : %s (%.1f KB)" % (OUT, os.path.getsize(OUT) / 1024))
    for name, n in per_source.items():
        print("  bijdrage %-20s %d" % (name, n))


if __name__ == "__main__":
    main()
