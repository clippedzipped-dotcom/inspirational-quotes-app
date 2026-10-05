# Inspirerende Quotes — app

Een kleine web-app die inspirerende quotes toont. Gebouwd met **Gemini**, gehost op **Railway**.

## Wat het doet
- `/` — donkere single-page UI met grote typografie en een knop voor de volgende quote
- `/api/quote` — geeft één willekeurige quote als JSON
- `/api/quotes` — alle 25 quotes als JSON
- `/health` — healthcheck

## Lokaal draaien
```bash
python3 app.py          # -> http://localhost:3000
```

## Op Railway zetten
Het project bevat een `Dockerfile` en `railway.json`, dus Railway bouwt het zonder extra configuratie.

**Optie A — via de Railway CLI** (aanbevolen; vraagt één keer je login):
```bash
npm install -g @railway/cli
railway login
railway init          # kies "Empty Project", naam: inspirational-quotes
railway up            # upload + deploy
railway domain        # geeft de publieke https-URL
```

**Optie B — via GitHub** (geen CLI nodig):
1. Zet deze map in een GitHub-repo
2. Railway → New Project → Deploy from GitHub repo
3. Railway detecteert de Dockerfile en deployt
4. Settings → Networking → Generate Domain

## Bestanden
| Bestand | Doel |
|---|---|
| `app.py` | webserver, geen dependencies (Python stdlib) |
| `quotes.json` | 25 quotes (tekst + auteur) |
| `index.html` | de UI |
| `Dockerfile` | build-image voor Railway |
| `railway.json` | Railway build/deploy-config |

## Quote toevoegen
Zet een regel bij in `quotes.json`:
```json
{ "text": "Jouw quote hier.", "author": "Naam" }
```
