FROM python:3

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

HEALTHCHECK --interval=1m --timeout=5s CMD curl -f http://localhost:8080/ || exit 1

CMD ["python", "sync.py"]
