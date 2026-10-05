FROM python:3.12-slim

WORKDIR /app

COPY app.py quotes.json index.html ./

ENV PORT=3000
EXPOSE 3000

CMD ["python3", "app.py"]
