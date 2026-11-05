# API da Torre Tecar. Construída a partir da raiz do repositório:
#   docker compose -f deploy/docker-compose.yml build api
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY server/requirements.txt server/requirements.txt
RUN pip install -r server/requirements.txt \
 && useradd --system --uid 10001 --home /app torre

COPY server/ server/
USER torre

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"

# Migrações antes de subir; proxy-headers porque só o Caddy (rede proxy_edge) fala com a API.
CMD ["sh", "-c", "alembic -c server/alembic.ini upgrade head && exec uvicorn server.app.main:create_app --factory --host 0.0.0.0 --port 8000 --workers 1 --proxy-headers --forwarded-allow-ips '*'"]
