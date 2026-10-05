FROM python:3.12-slim

WORKDIR /app

# quotes.json dat hier wordt meegekopieerd is de NOODVANGST (kleine seed).
# De volledige set (~3.700 quotes) wordt hieronder tijdens de build opgehaald
# uit de openbare bronnen, zodat er geen grote dataset in de repo hoeft.
COPY app.py build_quotes.py index.html quotes.json ./

RUN python3 build_quotes.py \
    || echo "WAARSCHUWING: bronnen onbereikbaar tijdens build - seed-dataset blijft actief"

ENV PORT=3000
EXPOSE 3000

CMD ["python3", "app.py"]
