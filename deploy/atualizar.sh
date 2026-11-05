#!/usr/bin/env bash
# Atualiza a Torre Tecar para a versão mais recente do repositório (banco e usuários são mantidos).
set -euo pipefail
cd "$(dirname "$0")"
git -C .. pull --ff-only
docker network inspect proxy_edge >/dev/null 2>&1 || docker network create proxy_edge >/dev/null
# O MCP (perfil "mcp") só entra quando já existe token no .env (ver ./mcp-token.sh).
PERFIS=""
grep -qE '^TORRE_MCP_TOKENS_SHA256=.+' .env 2>/dev/null && PERFIS="--profile mcp"
docker compose $PERFIS build
docker compose $PERFIS up -d
docker compose $PERFIS ps
