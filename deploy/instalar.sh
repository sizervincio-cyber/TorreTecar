#!/usr/bin/env bash
# Instala a Torre Tecar no VPS sem tocar no RadarDispensa nem na Quântica.
# Uso (como root, com o repositório em /opt/torre/repo):  cd /opt/torre/repo/deploy && ./instalar.sh
set -euo pipefail
cd "$(dirname "$0")"
say(){ printf '\n== %s\n' "$*"; }

command -v docker >/dev/null && docker compose version >/dev/null || { echo "Docker/Compose não encontrado."; exit 1; }

say "1/4 Rede do proxy (proxy_edge)"
docker network inspect proxy_edge >/dev/null 2>&1 || docker network create proxy_edge >/dev/null
echo "ok"

say "2/4 Segredos (deploy/.env)"
if [ ! -f .env ]; then
  printf 'POSTGRES_PASSWORD=%s\n' "$(openssl rand -hex 24)" > .env
  chmod 600 .env
  echo "criado"
else
  echo "já existe; mantido"
fi
mkdir -p ssh

say "3/4 Construindo e subindo (projeto Docker 'torre')"
docker compose build api
docker compose up -d

say "4/4 Esperando a API responder"
ok=0; for _ in $(seq 1 30); do
  if docker compose exec -T api python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=3)" 2>/dev/null; then ok=1; break; fi
  sleep 2
done
docker compose ps
[ "$ok" = 1 ] || { echo "A API não respondeu. Veja: docker compose logs --tail 60 api db"; exit 1; }

cat <<'TXT'

Torre instalada. Próximos passos:
  1) Criar o primeiro usuário (a senha é pedida no terminal):
       docker compose exec api python -m server.app.cli criar --login SEU_LOGIN --perfil admin --nome "Seu Nome"
  2) Testar pela rede do proxy, antes de publicar:
       docker run --rm --network proxy_edge curlimages/curl -s http://torre-api:8000/api/health
  3) Publicar: merge do PR do zero-touch-ops e ./atualizar.sh do RadarDispensa (ver deploy/README.md).
TXT
