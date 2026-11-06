# Torre Tecar: MCP somente leitura no ChatGPT (e no Codex)

## 1. TL;DR

- **A MCP existente foi reaproveitada, não reescrita.** As mesmas 11 ferramentas do Codex, com os mesmos nomes e o mesmo endpoint `https://mcp.<dominio>/mcp` (Streamable HTTP). O token fixo do Codex continua valendo.
- **O que faltava para o ChatGPT era a autenticação.** O ChatGPT não usa o token fixo do Codex; ele descobre e faz OAuth sozinho. O painel da Torre virou o **servidor de autorização OAuth 2.1** (DCR + PKCE S256), usando o **login que já existe**. O MCP só verifica o token com a **chave pública**.
- **Somente leitura em camadas técnicas, não por prompt.** O processo do MCP não tem credencial de banco, lê as bases de um volume `:ro`, roda com o sistema de arquivos `read_only` e aceita só `POST /mcp`. O catálogo é fechado (13 ferramentas de leitura) e o token tem um único escopo, `torre.read`.
- **Evidência:** 178 testes passando (20 novos). Um teste ponta a ponta sobre HTTP real com o **cliente OAuth oficial do SDK MCP** fez descoberta, DCR, PKCE, login, consentimento, token e consultas em dados reais.
- **Pendente de ação humana (3 itens, seção 11):** publicar a rota `mcp.` no Caddy, rodar `./oauth-chatgpt.sh` na VPS e cadastrar o conector na conta do ChatGPT. A conexão com o ChatGPT real **não foi testada** daqui porque não há acesso à conta.

## 2. Diagnóstico da MCP atual

| Componente | Estado encontrado | Compatível com ChatGPT? | Ação tomada |
|---|---|---|---|
| Servidor MCP | `mcp_torre/` (SDK `mcp` 2.3, `MCPServer`), 11 ferramentas | Sim | **Reutilizado** |
| Transporte | Streamable HTTP sem estado em `/mcp`, resposta JSON | Sim | Mantido; só `POST` passa (GET/PUT/DELETE: 405) |
| Tools | 11 de leitura, `readOnlyHint` etc. corretos | Sim, mas sem `outputSchema` | `structuredContent` + `outputSchema`; `search`/`fetch` adicionados |
| Erros | `ErroConsulta` virava "Error executing tool X" (o modelo não via o motivo) | Ruim para os dois | **Corrigido**: mensagem útil, sem traceback |
| Autenticação | Bearer fixo (SHA-256 no servidor), 401 com `WWW-Authenticate: Bearer` sem metadados | **Não** (o ChatGPT precisa de OAuth descobrível) | OAuth 2.1 no painel + verificação JWT no MCP |
| Descoberta | Sem `/.well-known` | **Não** | RFC 9728 no MCP e RFC 8414 no painel |
| Endpoint HTTPS | Contêiner `mcp` no perfil Compose; rota `mcp.` no Caddy do RadarDispensa **pendente** (PR externo) | Depende da rota | Sem mudança de infra; ação humana |
| Segurança | FS `read_only`, `cap_drop ALL`, volume `:ro`, Host check, 120/min | Boa base | Limite por usuário, 413, 504, auditoria, lista fechada de caminhos |
| Codex | Testado pelo usuário | Preservar | Token fixo intacto + teste de regressão |

**Grafo e menor conjunto de mudanças**

```
ChatGPT ──POST /mcp──> Caddy (TLS) ──> torre-mcp:8000
   │                                     ├ Portao (mcp_torre/auth.py): /health, /.well-known, só POST /mcp,
   │                                     │   Bearer: torre_* (Codex, SHA-256) | JWT ES256 (iss, aud, exp, scope, perfil)
   │                                     ├ SDK MCP (Host check, JSON-RPC, schemas)
   │                                     └ 13 ferramentas -> consultas.py -> dados.py -> arquivos :ro
   └──OAuth──> Caddy ──> torre-api:8000 (painel)
                           /.well-known/oauth-authorization-server, /oauth/register|authorize|token|revoke
                           login existente (Argon2, sessão) -> consentimento -> tabelas oauth_* (Postgres)
```

O único nó novo é o servidor de autorização dentro do painel, que já tinha identidade, sessão, banco e tela de login. Criar um IdP novo ou dar banco ao MCP seria pior: o MCP continua sem nenhuma credencial de escrita.

## 3. Matriz de alterações

| Arquivo | Tipo | Por quê |
|---|---|---|
| `mcp_torre/auth.py` | novo | Portão único Codex + OAuth: verificação JWT ES256 (só chave pública), RFC 9728, `WWW-Authenticate` com `resource_metadata`, 401/403, lista fechada de caminhos e métodos, limite por usuário, 413, 504, log de auditoria |
| `mcp_torre/server.py` | alterado | Usa o portão; `structured_output`; erros de validação legíveis; limite de 200 caracteres por argumento; `search` e `fetch`; configuração por ambiente |
| `mcp_torre/consultas.py` | alterado (só acréscimo) | `pesquisar()` e `detalhar()` reaproveitando `cliente_360` e as licitações |
| `server/app/oauth.py` | novo | Servidor de autorização OAuth 2.1 |
| `server/app/models.py` + `migrations/0002` | alterado / novo | Tabelas `oauth_clientes`, `oauth_codigos`, `oauth_refresh` (só hashes) |
| `server/app/config.py`, `main.py` | alterado | Configuração por ambiente; rotas OAuth antes da rota genérica |
| `server/app/auth.py` | alterado | Desativar o usuário ou trocar senha/perfil também revoga o OAuth |
| `server/app/cli.py` | alterado | `oauth-clientes`, `oauth-revogar --login X` / `--todos` |
| `deploy/docker-compose.yml` | alterado | Variáveis OAuth: chave privada **só** na API, pública **só** no MCP |
| `deploy/oauth-chatgpt.sh` | novo | Gera as chaves ES256, grava o `.env`, sobe API e MCP; `--desligar` |
| `deploy/atualizar.sh`, `mcp-token.sh` | alterado | MCP sobe também só com OAuth; revogar os tokens do Codex não derruba o ChatGPT |
| `requirements` (server, mcp_torre) | alterado | `pyjwt[crypto]` |
| `tests/test_mcp_chatgpt.py` | novo | 20 testes (seção 8) |

Nada foi alterado em `instaladores/` (o Codex usa o mesmo URL e o mesmo token).

## 4. Endpoint

- MCP: `https://mcp.2-25-95-244.sslip.io/mcp` (valor padrão do `oauth-chatgpt.sh`; trocar com `--mcp` quando o domínio mudar). **Fica no ar só depois da rota no Caddy (ação humana 1).**
- Protected Resource Metadata: `https://mcp.<dominio>/.well-known/oauth-protected-resource/mcp` (também na raiz `/.well-known/oauth-protected-resource`).
- Servidor de autorização: `https://torre.<dominio>/.well-known/oauth-authorization-server`.
- Nenhum domínio está fixo na lógica: tudo vem de `TORRE_OAUTH_ISSUER`, `TORRE_MCP_RESOURCE_URL` e `TORRE_MCP_HOSTS`.

## 5. Autenticação e autorização

| Item | Implementação |
|---|---|
| Fluxo | OAuth 2.1 Authorization Code + **PKCE S256 obrigatório** (`plain` recusado) |
| Registro do cliente | Dynamic Client Registration (RFC 7591). `redirect_uri` **só da lista** `TORRE_OAUTH_REDIRECT_URIS` (padrão: callbacks do ChatGPT). Métodos `none`, `client_secret_post`, `client_secret_basic`. 10 registros por hora por IP |
| Identidade | Login da Torre (Argon2, bloqueio de tentativas). Tela de consentimento com CSRF amarrado à sessão, `X-Frame-Options: DENY` e CSP `frame-ancestors 'none'` |
| Access token | JWT ES256, 30 min, `iss`, `aud` = URL do MCP (RFC 8707), `sub`, `login`, `perfil`, `scope=torre.read`, `client_id`, `jti` |
| Refresh token | 30 dias, opaco (só o hash no banco), **rotação** e **detecção de reuso**: um token velho reapresentado revoga a família inteira |
| Perfis | `admin`, `gestor`, `vendedor` (`TORRE_MCP_PERFIS`). `simulacao` (que no painel já não vê dados) recebe `access_denied`. O MCP confere o perfil de novo no token |
| Revogação | `cli desativar/senha/perfil` e `oauth-revogar` apagam os refresh tokens; endpoint RFC 7009. O access token já emitido vale até vencer (máx. 30 min) |
| Segredos | Chave privada só no `deploy/.env` (chmod 600) e só no contêiner `api`. O MCP recebe só a chave pública. Nenhum token vai para log ou resposta |
| Codex | Token fixo `torre_...` inalterado (o ChatGPT não reutiliza esse token) |

**Isolamento por registro (IDOR):** hoje o painel mostra as mesmas bases a todos os perfis com acesso a dados, e a separação por carteira é a Fase 4 do roadmap. O MCP espelha exatamente isso: não dá a ninguém mais do que o painel já mostra. O `principal` (usuário, perfil) já chega a cada requisição em `scope["state"]`, pronto para filtrar por carteira quando a Fase 4 existir.

## 6. Catálogo de ferramentas

Todas com `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false` (só bases internas). Todas com `inputSchema` e `outputSchema` (objeto), resposta em `structuredContent` + texto, limite de 500 linhas e de 200 caracteres por argumento de texto.

| Ferramenta | Função | Parâmetros principais |
|---|---|---|
| `status_dados` | Data e tamanho de cada base | (nenhum) |
| `resumo_emplacamentos` | Totais por até 3 dimensões + share MB | `agrupar_por`, `top`, período, marca, UF, AOP, cidade, segmento, subsegmento, tração, modelo, proprietário, CNPJ, concessionário, tipo de pessoa |
| `comparar_periodos` | Período A x B: variação % e p.p. | `a_ini`, `a_fim`, `b_ini`, `b_fim`, `agrupar_por`, filtros |
| `buscar_emplacamentos` | Registros (placa, chassi, CNPJ), exige filtro | `limite` ≤ 500, filtros, placa, chassi |
| `cliente_360` | Ficha do cliente por CNPJ/raiz/nome | `cnpj_ou_nome`, `limite_veiculos` |
| `carteira_por_responsavel` | Carteira do CRM por vendedor, `total_sem_duplicar` | `casa`, `responsavel` |
| `buscar_crm` | Contas do CRM | `texto`, `responsavel`, `casa`, `temperatura`, `limite` |
| `buscar_licitacoes` | Compras públicas PNCP (GO, MT, TO) | `texto`, `uf`, `municipio`, `orgao`, `ano`, `situacao`, `somente_abertas`, `limite` |
| `itens_licitacoes` | Itens, vencedores e quantidade por marca | `base`, `segmento`, `texto`, `uf`, `ano`, `vencedor_contem`, `limite` |
| `precos` | Histórico de preços e Top 10 com gap MB | `modelo_contem`, `marca`, `grupo_contem`, `desde`, `limite` |
| `indicadores_assobens` | KPIs consolidados ASSOBENS | (nenhum) |
| `search` *(novo)* | Busca clientes e licitações (padrão search/fetch do ChatGPT) | `query` → `{results:[{id,title,url}]}`, até 20 |
| `fetch` *(novo)* | Documento completo de um resultado | `id` (`cliente:<raiz>` ou `licitacao:<id>`) → `{id,title,text,url,metadata}` |

Mapa das ferramentas sugeridas no pedido: `torre_get_capabilities`/`overview` = `status_dados` + `indicadores_assobens`; `emplacamentos` = `resumo_emplacamentos`/`buscar_emplacamentos`; `market_share` = `resumo_emplacamentos` (share por grupo); `compare_periods` = `comparar_periodos`; `search`/`fetch` = novos. **Não existe base de "simulações comerciais"** no servidor (os simuladores rodam no navegador; os leads do simulador ficam em `leads`, dado pessoal fora do escopo). Por isso não foi criada `torre_get_simulacoes`. Os nomes antigos foram mantidos para não quebrar o Codex e a skill `torre-relatorios`.

## 7. Auditoria somente leitura (por que escrever é tecnicamente impossível)

1. **Catálogo:** 13 ferramentas, todas consultas puras. Ferramenta inexistente (`executar_sql`) → erro. Não há SQL nem comando arbitrário.
2. **Autorização:** o único escopo que existe é `torre.read`. Um token com qualquer outro escopo recebe 403.
3. **Backend:** o portão só deixa passar `POST /mcp`, `/health` e `GET /.well-known/*`. Qualquer outro caminho dá 404 e qualquer outro método dá 405.
4. **Persistência:** o contêiner `mcp` **não tem credencial de banco** (nem variável, nem rede `interno` onde está o Postgres). Prova estática nos testes: o pacote `mcp_torre` não importa SQLAlchemy, psycopg, sqlite3, subprocess, cliente HTTP, socket ou shutil, e não abre arquivo para escrita.
5. **Infraestrutura:** volume `..:/srv/site:ro`, `read_only: true`, `tmpfs /tmp` 16 MB, `cap_drop: ALL`, `no-new-privileges`, usuário sem privilégio (uid 10002) e só a rede `proxy_edge`.
6. **Efeitos colaterais permitidos:** só no painel, nas tabelas `oauth_*` (estado de autenticação). Teste: o fluxo OAuth não altera `usuarios` nem `leads`. O `ultimo_login` é o comportamento do login que já existia.

A anotação `readOnlyHint` é só declaração: a garantia vem dos itens 3 a 5.

## 8. Evidências de testes

```
python -m pytest -q   ->   178 passed, 1 failed
```
A falha (`test_sync_job::test_sem_credenciais_configuradas`) já existia antes da mudança: falta o Playwright no ambiente de teste. Não tem relação com o MCP.

`tests/test_mcp_chatgpt.py` (20 testes):
- **Compatibilidade:** descoberta RFC 8414 e RFC 9728; `WWW-Authenticate` com `resource_metadata`; initialize, tools/list e tools/call com o token OAuth; schemas de entrada e saída; regressão do Codex com OAuth ligado e desligado.
- **OAuth:** fluxo completo; rotação de refresh e reuso que revoga a família; código de uso único e queimado na 1ª tentativa; PKCE errado; cliente confidencial exigindo segredo (post e basic); `resource` de outro servidor (`invalid_target`); OAuth desligado sem configuração; host público `simule.` sem OAuth.
- **Red team:** redirect fora da lista (domínio parecido, http, `../`, userinfo, fragmento); cliente ou redirect desconhecido nunca redireciona; CSRF forjado (403); perfil `simulacao` (`access_denied`); usuário desativado perde o refresh; tokens sem assinatura, de outra chave, vencidos, de outro `aud`, de emissor falso, sem `sub`, `alg=none`, HS256 com a chave pública, escopo de escrita e perfil `simulacao` no token; limite por usuário (429); argumento de 5.000 caracteres; ids maliciosos no `fetch`; erro sem traceback.
- **Imutabilidade:** hash SHA-256 de todos os arquivos das bases antes e depois de chamar **todas** as 13 ferramentas, com 9 cargas adversariais cada (SQL injection, path traversal, `$(rm -rf /)`, prompt injection, byte nulo, template). Resultado: estado idêntico.

**Ponta a ponta sobre HTTP real** (painel e MCP com uvicorn, bases reais do repositório, cliente OAuth oficial do SDK MCP):
```
authorize -> /oauth/authorize | params: client_id, code_challenge, code_challenge_method, redirect_uri, resource, response_type, scope, state
1. initialize: Torre Tecar | protocolo 2025-11-25
2. tools/list: 13 ferramentas, todas readOnlyHint: True
3. status_dados: 26846 linhas, 2020-01-03 a 2026-11-04
4. resumo GO 2025+: 1845 emplac., share MB 45.58 %
5. search: 20 resultados   6. fetch: ficha do cliente (1911 chars)
7. ferramenta inexistente: isError=True
8. token: escopo torre.read | 1800 s | refresh: sim | client_id via DCR
log: {"quem":"usuario:1","login":"ana","tipo":"oauth","acao":"tools/call:search","status":200,...}   (sem token, sem argumentos)
```

**Bugs encontrados e corrigidos durante os ciclos:** mensagem de validação engolida pelo SDK (afetava o Codex); saída sem `structuredContent` (anotações em string com `from __future__`); comparação de data com e sem fuso no SQLite ao limpar tokens vencidos.

## 9. Conectar no ChatGPT (procedimento para o usuário)

> A documentação da OpenAI (`developers.openai.com`, `help.openai.com`) estava bloqueada pela rede deste ambiente. Os passos abaixo seguem a especificação MCP e o comportamento conhecido do ChatGPT. **Confira os nomes de menu na tela atual**, porque a OpenAI muda a interface com frequência.

1. **Elegibilidade:** conectores MCP personalizados ficam no ChatGPT **web**, em planos com modo desenvolvedor ou conectores personalizados (Plus/Pro e workspaces Business/Enterprise/Edu, nos quais o **administrador** precisa liberar). O app mobile usa conectores já instalados, mas não cadastra conectores novos.
2. No chatgpt.com: **Configurações → Apps/Conectores (ou Plugins) → Avançado → Modo desenvolvedor: ligado**.
3. **Criar / Adicionar servidor MCP personalizado:**
   - Nome: `Torre Tecar — Read Only`
   - Descrição: `Consultas somente leitura às bases comerciais da Torre Tecar`
   - URL do servidor MCP: `https://mcp.2-25-95-244.sslip.io/mcp`
   - Autenticação: **OAuth**, deixando vazios client ID e secret: o ChatGPT faz o registro dinâmico sozinho.
   - Marcar "confio neste aplicativo" e clicar em Criar.
4. O ChatGPT abre a **tela de login da Torre**. Entre com o seu usuário e clique em **Permitir leitura**.
5. Confira as 13 ferramentas listadas e teste: *"Use a Torre Tecar e diga até quando vão as bases"*, *"Share Mercedes-Benz em extrapesados GO 2025 x 2026"*, *"Pesquise o cliente J R Transportes"*.

**Por modalidade:** no chat com modo desenvolvedor, todas as 13 ferramentas ficam disponíveis. Em pesquisa aprofundada e conhecimento da empresa, o ChatGPT usa `search` e `fetch`. No Codex, o token fixo continua igual (`instaladores/`). No **ChatGPT Work** e no mobile, o suporte depende da liberação do workspace e precisa ser validado na conta.

**Se o callback for recusado** ("redirect_uri fora da lista"): veja no log da API o `redirect_uri` que o ChatGPT enviou e acrescente-o em `TORRE_OAUTH_REDIRECT_URIS` no `deploy/.env` (itens separados por vírgula; um item terminado em `/` aceita o caminho abaixo). Depois rode `docker compose up -d api`.

## 10. Implantação e rollback (VPS)

```bash
cd /opt/torre/repo/deploy
./atualizar.sh                                   # código novo; a API aplica a migração 0002 sozinha
./oauth-chatgpt.sh --piloto SEU_LOGIN            # chaves ES256 + .env + sobe api e mcp, só para você
#   domínio novo: ./oauth-chatgpt.sh --painel https://torre.NOVO --mcp https://mcp.NOVO/mcp
#   e TORRE_MCP_HOSTS=mcp.NOVO,torre-mcp:8000 no .env

# Conferir (9 checagens; com TORRE_MCP_TOKEN também valida o Codex)
TORRE_MCP_TOKEN=torre_... ./validar-mcp.sh https://torre.2-25-95-244.sslip.io https://mcp.2-25-95-244.sslip.io/mcp
docker compose --profile mcp logs --tail 50 mcp    # linhas "torre-mcp.auditoria"

# Operação
docker compose exec api python -m server.app.cli oauth-clientes
docker compose exec api python -m server.app.cli oauth-revogar --login fulano   # ou --todos
```

**Rollback, do mais leve ao mais completo:**
1. Só desligar o ChatGPT: `./oauth-chatgpt.sh --desligar`. O Codex continua.
2. Revogar todos os acessos e trocar a chave: `cli oauth-revogar --todos` e depois `./oauth-chatgpt.sh --nova-chave`.
3. Código anterior: `git -C .. checkout <commit anterior> && ./atualizar.sh`. As tabelas `oauth_*` podem ficar (não são lidas pela versão anterior). Para removê-las: `docker compose exec api alembic -c server/alembic.ini downgrade 0001`.

Não há porta nova no host, mudança de domínio nem alteração no RadarDispensa ou na Quântica.

## 10.1 Liberação controlada (piloto → todos)

| Fase | O que fazer | Critério para avançar |
|---|---|---|
| 0. Deploy | `./atualizar.sh` e `./oauth-chatgpt.sh --piloto SEU_LOGIN` | `./validar-mcp.sh` com **9 OK** (inclui o Codex com o seu token) |
| 1. Piloto | Só `SEU_LOGIN` recebe token; qualquer outro usuário recebe "acesso negado" ao tentar conectar | Uma consulta completa no ChatGPT: conectar → login → Permitir → *"até quando vão as bases"* → *"share MB extrapesados GO 2025 x 2026"* → *"pesquise o cliente X"* e abrir o resultado. Os números batem com a Torre e aparecem as linhas `torre-mcp.auditoria` com o seu login no log |
| 2. Liberação | `./oauth-chatgpt.sh --liberar` (recria só a API, em segundos) | Usuários `admin`, `gestor` e `vendedor` conectam; `simulacao` continua sem acesso |
| Volta | `./oauth-chatgpt.sh --piloto SEU_LOGIN` de novo (os outros perdem o refresh na hora e o access token em até 30 min) ou `--desligar` | |

O piloto é aplicado na autorização, na troca do código e no refresh, por isso tirar alguém da lista corta o acesso no próximo refresh. Testado em `test_piloto_so_libera_os_logins_da_lista_e_corta_o_refresh`.

## 10.2 Codex: o que muda

Nada no uso. Mesmo URL (`https://mcp.<dominio>/mcp`), mesmo token `torre_...`, mesmas 11 ferramentas com os mesmos nomes e argumentos, e os instaladores e a skill `torre-relatorios` intactos. O piloto e o OAuth não se aplicam ao token fixo. Diferenças percebidas: as respostas trazem também `structuredContent`, os erros de validação agora dizem o motivo (antes vinha só "Error executing tool") e há duas ferramentas a mais (`search` e `fetch`). No deploy, o contêiner `mcp` é recriado e fica alguns segundos fora do ar. Evidência: teste `test_codex_token_fixo_continua_funcionando` (com OAuth ligado e desligado) e o `validar-mcp.sh` com o token do Codex.

## 11. Ações humanas pendentes

| # | Ação | Quem | Por quê |
|---|---|---|---|
| 1 | Publicar `mcp.2-25-95-244.sslip.io → torre-mcp:8000` no Caddyfile do RadarDispensa (PR no `zero-touch-ops`), sem remover o cabeçalho `Authorization`, e rodar `./atualizar.sh` de lá | Admin da VPS | Repositório e infraestrutura fora do alcance desta sessão |
| 2 | `./atualizar.sh`, `./oauth-chatgpt.sh --piloto SEU_LOGIN` e `./validar-mcp.sh` na VPS | Admin da VPS | Gera a chave privada lá (ela nunca passa pelo repositório) |
| 3 | Cadastrar o conector no ChatGPT (seção 9), fazer a consulta do piloto (10.1) e só então `--liberar` | Usuário com conta elegível | Sem acesso à conta ChatGPT daqui: **conexão real pendente de teste** |

## 12. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| A OpenAI mudar o `redirect_uri` do callback | Lista configurável por `.env`, sem deploy de código |
| Access token vale até 30 min após a revogação | TTL curto (`TORRE_OAUTH_ACCESS_MIN`); para corte imediato, `--nova-chave` invalida todos |
| Dados de registros (nomes, objetos de licitação) com texto malicioso (prompt injection) | O servidor não tem ação a executar; as instruções do MCP dizem que o texto das bases é dado; o catálogo é só leitura |
| Domínio sslip.io provisório | Tudo por variável; troca com `--painel` e `--mcp`. O ChatGPT precisará de um conector novo com o URL novo |
| Mesmo acesso para todos os perfis com dados | Igual ao painel hoje; o filtro por carteira entra na Fase 4 (o principal já chega ao MCP) |
| CIMD (Client ID Metadata Documents) não implementado | O ChatGPT faz DCR. Se um dia exigir CIMD, o caminho é aceitar `client_id` em URL de domínio na lista |
