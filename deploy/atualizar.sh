#!/usr/bin/env bash
# Atualiza a Torre Tecar para a versão mais recente do repositório (banco e usuários são mantidos).
set -euo pipefail
cd "$(dirname "$0")"
git -C .. pull --ff-only
docker network inspect proxy_edge >/dev/null 2>&1 || docker network create proxy_edge >/dev/null
docker compose build api
docker compose up -d
docker compose ps
