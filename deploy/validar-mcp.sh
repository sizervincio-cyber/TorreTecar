#!/usr/bin/env bash
# Validação externa do MCP da Torre depois do deploy (não altera nada; só GET/POST de leitura).
# Uso: ./validar-mcp.sh https://torre.<dominio> https://mcp.<dominio>/mcp
#      TORRE_MCP_TOKEN=torre_... ./validar-mcp.sh ...   (também testa o Codex: initialize, tools/list e uma consulta)
set -uo pipefail
PAINEL="${1:?painel}"; MCP="${2:?url do mcp}"; BASE="${MCP%/mcp}"
ok=0; falhou=0
passo() { if [ "$2" = 0 ]; then echo "  OK   $1"; ok=$((ok+1)); else echo "  FALHA $1 ${3:-}"; falhou=$((falhou+1)); fi; }
J='Content-Type: application/json'; A='Accept: application/json, text/event-stream'

echo "== Torre MCP: $MCP"
m="$(curl -fsS --max-time 15 "$PAINEL/.well-known/oauth-authorization-server")"
echo "$m" | tr -d ' ' | grep -qF '"code_challenge_methods_supported":["S256"]' && echo "$m" | grep -q '"registration_endpoint"'
passo "metadados do servidor de autorização (RFC 8414, S256, DCR)" $?
r="$(curl -fsS --max-time 15 "$BASE/.well-known/oauth-protected-resource/mcp")"
r1="$(echo "$r" | tr -d ' ')"
echo "$r1" | grep -qF "\"resource\":\"$MCP\"" && echo "$r1" | grep -qF "\"authorization_servers\":[\"$PAINEL\"]"
passo "protected resource metadata (RFC 9728) aponta para o painel" $? "$r"
h="$(curl -sS --max-time 15 -o /dev/null -D - -X POST -H "$J" -H "$A" -d '{}' "$MCP")"
echo "$h" | grep -qE '^HTTP/[0-9.]+ 401' && echo "$h" | grep -qi "www-authenticate: Bearer resource_metadata=\"$BASE/.well-known/oauth-protected-resource/mcp\""
passo "sem token: 401 com WWW-Authenticate resource_metadata" $?
c="$(curl -sS --max-time 15 -o /dev/null -w '%{http_code}' -X POST -H 'Authorization: Bearer eyJhbGciOiJub25lIn0.e30.' -H "$J" -H "$A" -d '{}' "$MCP")"
[ "$c" = 401 ]; passo "token forjado (alg none): 401" $? "($c)"
c="$(curl -sS --max-time 15 -o /dev/null -w '%{http_code}' -X DELETE "$MCP")"
[ "$c" = 405 ]; passo "métodos de escrita HTTP bloqueados (DELETE: 405)" $? "($c)"
c="$(curl -sS --max-time 15 -o /dev/null -w '%{http_code}' -H "$A" "$PAINEL/oauth/authorize?client_id=x")"
[ "$c" = 400 ]; passo "cliente OAuth desconhecido não redireciona (400)" $? "($c)"

if [ -n "${TORRE_MCP_TOKEN:-}" ]; then
  T="Authorization: Bearer $TORRE_MCP_TOKEN"
  i="$(curl -sS --max-time 30 -X POST -H "$T" -H "$J" -H "$A" "$MCP" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"validar","version":"1"}}}')"
  echo "$i" | grep -q '"Torre Tecar"'; passo "Codex: initialize" $?
  l="$(curl -sS --max-time 30 -X POST -H "$T" -H "$J" -H "$A" "$MCP" -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}')"
  n="$(echo "$l" | tr -d ' ' | grep -o '"readOnlyHint":true' | wc -l)"
  [ "$n" = 13 ]; passo "Codex: 13 ferramentas, todas readOnlyHint" $? "($n)"
  s="$(curl -sS --max-time 60 -X POST -H "$T" -H "$J" -H "$A" "$MCP" -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"status_dados","arguments":{}}}')"
  echo "$s" | grep -q '"structuredContent"' && echo "$s" | tr -d ' ' | grep -q '"isError":false'
  passo "Codex: status_dados com dados reais" $?
  echo "$s" | grep -o '"linhas":[0-9]*' | head -1 | sed 's/^/       /'
fi
echo "== $ok OK, $falhou falha(s)"
[ "$falhou" = 0 ]
