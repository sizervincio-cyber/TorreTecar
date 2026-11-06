#!/usr/bin/env bash
# Liga o OAuth 2.1 do MCP somente leitura para o ChatGPT. Idempotente: a chave só é gerada na primeira vez.
#  - gera o par de chaves ES256 (privada: só a API assina tokens; pública: o MCP só verifica);
#  - grava no deploy/.env: TORRE_OAUTH_ISSUER, TORRE_MCP_RESOURCE_URL, TORRE_OAUTH_PRIVATE_KEY, TORRE_OAUTH_PUBLIC_KEY;
#  - reconstrói e sobe a API (migração 0002 roda sozinha) e o MCP.
# Uso: ./oauth-chatgpt.sh --piloto SEU_LOGIN [--painel https://torre.<dominio>] [--mcp https://mcp.<dominio>/mcp] [--nova-chave]
#      ./oauth-chatgpt.sh --liberar      (fim do piloto: todos os perfis admin/gestor/vendedor podem conectar)
#      ./oauth-chatgpt.sh --desligar     (tira o OAuth; o Codex continua com o token fixo)
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || { echo "deploy/.env não existe; rode ./instalar.sh antes."; exit 1; }
PAINEL="https://torre.2-25-95-244.sslip.io"
MCP="https://mcp.2-25-95-244.sslip.io/mcp"
NOVA=0
PILOTO=""
define() { sed -i "/^$1=/d" .env; printf '%s=%s\n' "$1" "$2" >> .env; }
while [ $# -gt 0 ]; do
  case "$1" in
    --painel) PAINEL="${2%/}"; shift 2 ;;
    --mcp) MCP="${2%/}"; shift 2 ;;
    --nova-chave) NOVA=1; shift ;;
    --piloto) PILOTO="${2:?informe os logins}"; shift 2 ;;
    --liberar)
      sed -i '/^TORRE_OAUTH_LOGINS_PILOTO=/d' .env
      docker compose up -d --force-recreate api
      echo "Piloto encerrado: perfis admin, gestor e vendedor podem conectar o ChatGPT."; exit 0 ;;
    --desligar)
      sed -i -E '/^TORRE_(OAUTH_ISSUER|MCP_RESOURCE_URL|OAUTH_PRIVATE_KEY|OAUTH_PUBLIC_KEY)=/d' .env
      docker compose up -d --force-recreate api
      if grep -qE '^TORRE_MCP_TOKENS_SHA256=.+' .env; then docker compose --profile mcp up -d --force-recreate mcp
      else docker compose --profile mcp stop mcp >/dev/null 2>&1 || true; fi
      echo "OAuth desligado: o ChatGPT perdeu o acesso; o Codex (token fixo) não muda."; exit 0 ;;
    *) echo "opção desconhecida: $1"; exit 1 ;;
  esac
done
[ -n "$PILOTO" ] || grep -qE '^TORRE_OAUTH_LOGINS_PILOTO=.+' .env || {
  echo "Ligue primeiro em piloto: ./oauth-chatgpt.sh --piloto SEU_LOGIN (depois de validar: --liberar)."; exit 1; }
case "$PAINEL$MCP" in *http://*) echo "Use https:// nos dois endereços."; exit 1 ;; esac

# 1) Constrói ANTES de mexer no .env: se o build falhar, nada muda e a API em execução segue como estava.
docker network inspect proxy_edge >/dev/null 2>&1 || docker network create proxy_edge >/dev/null
docker compose --profile mcp build api mcp

# 2) Só agora grava a configuração nova.
if [ -n "$PILOTO" ]; then define TORRE_OAUTH_LOGINS_PILOTO "$PILOTO"; echo "Piloto: só $PILOTO recebe acesso do ChatGPT."; fi
if [ "$NOVA" = 1 ] || ! grep -qE '^TORRE_OAUTH_PRIVATE_KEY=.+' .env; then
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  openssl ecparam -name prime256v1 -genkey -noout -out "$TMP/ec.pem"
  openssl pkcs8 -topk8 -nocrypt -in "$TMP/ec.pem" -out "$TMP/priv.pem"
  openssl ec -in "$TMP/ec.pem" -pubout -out "$TMP/pub.pem" 2>/dev/null
  define TORRE_OAUTH_PRIVATE_KEY "$(base64 -w0 "$TMP/priv.pem")"
  define TORRE_OAUTH_PUBLIC_KEY "$(base64 -w0 "$TMP/pub.pem")"
  echo "Par de chaves ES256 gerado."
fi
define TORRE_OAUTH_ISSUER "$PAINEL"
define TORRE_MCP_RESOURCE_URL "$MCP"
chmod 600 .env

# 3) Sobe com a configuração nova (--force-recreate: a API velha nunca continua com a lista antiga).
docker compose --profile mcp up -d --force-recreate api mcp

# 4) Chave nova: derruba também os refresh tokens guardados (senão eles ganhariam access tokens novos).
if [ "$NOVA" = 1 ]; then
  for _ in $(seq 1 30); do docker compose exec -T api python -m server.app.cli oauth-revogar --todos && break; sleep 2; done
fi

cat <<TXT

OAuth do ChatGPT ligado.
  Servidor de autorização: $PAINEL/.well-known/oauth-authorization-server
  MCP (cole no ChatGPT):   $MCP
Validar (deste servidor ou de qualquer máquina):
  ./validar-mcp.sh $PAINEL $MCP
Conferir:
  curl -s $PAINEL/.well-known/oauth-authorization-server
  curl -s ${MCP%/mcp}/.well-known/oauth-protected-resource/mcp
  curl -si -X POST $MCP | grep -i www-authenticate     # deve citar resource_metadata
TXT
