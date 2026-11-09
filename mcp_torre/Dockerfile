# MCP somente leitura da Torre Tecar (Codex). Construído a partir da raiz do repositório:
#   docker compose -f deploy/docker-compose.yml --profile mcp build mcp
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY mcp_torre/requirements.txt mcp_torre/requirements.txt
RUN pip install -r mcp_torre/requirements.txt \
 && useradd --system --uid 10002 --home /app torre-mcp

COPY precos_comerciais/ precos_comerciais/
COPY mcp_torre/ mcp_torre/
USER torre-mcp

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"
CMD ["python", "-m", "mcp_torre.server"]
