#!/usr/bin/env bash
# Gera um token de acesso ao MCP da Torre (Codex), guarda só o SHA-256 no deploy/.env e sobe o contêiner mcp.
# O token aparece UMA vez: copie para o instalador do Codex no seu computador.
# Uso: ./mcp-token.sh            (acrescenta um token; os anteriores continuam valendo)
#      ./mcp-token.sh --revogar  (apaga todos os tokens e derruba o MCP)
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || { echo "deploy/.env não existe; rode ./instalar.sh antes."; exit 1; }

if [ "${1:-}" = "--revogar" ]; then
  sed -i '/^TORRE_MCP_TOKENS_SHA256=/d' .env
  if grep -qE '^TORRE_OAUTH_PUBLIC_KEY=.+' .env; then
    docker compose --profile mcp up -d --force-recreate mcp >/dev/null   # ChatGPT (OAuth) continua; Codex sai
    echo "Tokens do Codex revogados. O MCP segue no ar só para o ChatGPT (OAuth)."
  else
    docker compose --profile mcp stop mcp >/dev/null 2>&1 || true
    echo "Tokens revogados e MCP parado."
  fi
  exit 0
fi

TOKEN="torre_$(openssl rand -hex 24)"
HASH="$(printf '%s' "$TOKEN" | sha256sum | cut -d' ' -f1)"
ATUAL="$(grep -E '^TORRE_MCP_TOKENS_SHA256=' .env | cut -d= -f2- || true)"
sed -i '/^TORRE_MCP_TOKENS_SHA256=/d' .env
printf 'TORRE_MCP_TOKENS_SHA256=%s\n' "${ATUAL:+$ATUAL,}$HASH" >> .env
chmod 600 .env

docker network inspect proxy_edge >/dev/null 2>&1 || docker network create proxy_edge >/dev/null
docker compose --profile mcp build mcp
docker compose --profile mcp up -d mcp

cat <<TXT

MCP da Torre no ar (contêiner torre-mcp). Seu token (guarde agora; ele não aparece de novo):

  $TOKEN

No seu computador, rode o instalador do Codex e cole este token quando ele pedir.
TXT
