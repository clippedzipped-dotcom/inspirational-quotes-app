# Inspirerende Quotes — app

Een web-app met inspirerende quotes. Gebouwd met **Gemini**, gehost op **Railway**.

De dataset komt uit echte, openbare bronnen (geen verzonnen quotes) en wordt
**tijdens de Docker-build** opgehaald. Daarom staat er geen dataset van honderden
kilobytes in deze repo: de `quotes.json` die hier staat is alleen de noodvangst.

## Endpoints
| Route | Wat het geeft |
|---|---|
| `/` | donkere single-page UI, teller, auteur-filter, vorige/volgende |
| `/api/quote` | één quote (`?i=` index, `?author=` filter, anders willekeurig) |
| `/api/quotes` | de volledige dataset als JSON |
| `/api/authors` | alle auteurs met hun aantal quotes |
| `/api/stats` | aantal quotes en auteurs |
| `/health` | healthcheck |

## Dataset
`build_quotes.py` haalt twee onafhankelijke open datasets op, ontdubbelt op
genormaliseerde tekst en weigert te schrijven onder de 900 unieke quotes.

| Bron | Records | Licentie |
|---|---|---|
| [dwyl/quotes](https://github.com/dwyl/quotes) | 1.655 | GPL-2 op de repo; de citaten zelf zijn publiek domein |
| [mubaris/motivate](https://github.com/mubaris/motivate) | 2.335 | MIT |

Uitkomst van de laatste build: **3.745 unieke quotes · 1.862 auteurs**.

## Lokaal draaien
```bash
python3 build_quotes.py     # optioneel: dataset (her)bouwen
python3 app.py              # -> http://localhost:3000
```

## Op Railway
De repo bevat een `Dockerfile` en `railway.json`. De service is aan deze GitHub-repo
gekoppeld: **een push naar `main` start automatisch een nieuwe deploy.**
`build_quotes.py` draait mee in de build; mislukt dat (netwerk), dan blijft de
seed-dataset actief en faalt de deploy niet.

## Bestanden
| Bestand | Doel |
|---|---|
| `app.py` | webserver, geen dependencies (Python stdlib) |
| `build_quotes.py` | bouwt de dataset uit de openbare bronnen |
| `quotes.json` | noodvangst-dataset (wordt bij de build vervangen) |
| `index.html` | de UI |
| `Dockerfile` | build-image voor Railway |
| `railway.json` | Railway build/deploy-config |
