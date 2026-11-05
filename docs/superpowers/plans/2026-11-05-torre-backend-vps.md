# Torre Tecar com back-end próprio na VPS — Plano de migração

> Steps usam checkbox (`- [ ]`). Cada fase termina num estado que funciona sozinho e tem caminho de volta.

**Objetivo:** tirar a Torre do GitHub Pages público e colocá-la na VPS com domínio próprio, login de verdade no servidor, banco de dados como fonte da verdade e as rotinas (ASSOBENS, licitações, CNPJá) rodando na própria VPS.

**Arquitetura:** o proxy reverso que já atende Quantica e Radar ganha uma rota nova para a Torre → API Python (FastAPI) com sessões no servidor → PostgreSQL. Um worker agenda as rotinas que já existem em `assobens/` e `licitacoes/`. As páginas HTML atuais continuam, servidas só para quem está logado, e passam a ler da API em vez de arquivos versionados.

**Stack:** Ubuntu 24.04, Docker Compose, proxy existente da VPS, Python 3.12 + FastAPI + SQLAlchemy + Alembic, PostgreSQL 16, Playwright/Chromium (já usado pela rotina ASSOBENS), pytest.

---

## 1. Ponto de partida (levantado em 05/11/2026)

| Item | Hoje | Problema |
|---|---|---|
| Hospedagem | GitHub Pages em `sizervincio-cyber.github.io/TorreTecar`, repositório **público** | Qualquer pessoa baixa a matriz (CNPJ + nome de proprietário) e o perfil de clientes |
| Domínio | **Nenhum domínio próprio** (`cname` vazio no Pages) | O endereço `*.github.io` pertence ao GitHub e não pode apontar para a VPS |
| Login | `miccGate()` no navegador, senha em SHA-256 dentro do HTML | Não protege nada: credenciais e dados estão no código-fonte |
| CRM | `CRM_ROWS` embutido no `Analitycmbb.html` (5.525 cadastros PJ, nomes de vendedores) | Público e só atualiza editando o HTML |
| Dados | Matriz `.xlsx` + JSON em `Analityc share/` versionados a cada sincronização | Git virou banco de dados (`.git` com 50 MB e crescendo); histórico guarda tudo que vazou |
| Rotinas | GitHub Actions: ASSOBENS 3x/dia, licitações a cada hora, CNPJá após a ASSOBENS | Em repositório privado consomem a cota de minutos; dependem do GitHub |
| Estado local | `localStorage`: observações comerciais, contatos do CRM, regras, leads, rascunhos | Cada navegador tem a sua versão; nada é compartilhado nem tem backup |
| Leads do simulador | Google Apps Script + planilha, token no HTML | Token exposto; dados fora do sistema |

**Páginas:** `Analitycmbb.html` (Torre, 2,6 MB, Vue via CDN), `gestao-tecar.html`, `tco-simulador.html`, `trucktest.html` (+ `trucktest-*.js/json`), `simule.html` (público, para clientes, ligado a QR Code).

---

## 2. Arquitetura alvo

```text
                  Internet
                     │  443 (HTTPS automático)
              ┌──────▼──────┐
              │ proxy atual │  torre.<dominio>       → app (login obrigatório)
              │             │  simule.<dominio>      → simule.html + POST /api/leads (público)
              └──────┬──────┘
                     │ rede interna Docker
        ┌────────────┼──────────────┐
  ┌─────▼─────┐ ┌────▼─────┐ ┌──────▼──────┐
  │  api      │ │  worker  │ │  postgres   │
  │ FastAPI   │ │ agenda:  │ │ dados +     │
  │ sessões   │ │ ASSOBENS │ │ auditoria   │
  │ páginas   │ │ licitaç. │ │             │
  │ estáticas │ │ CNPJá    │ │             │
  └───────────┘ └──────────┘ └──────┬──────┘
                                     │ pg_dump diário
                              backup fora da VPS
```

### Decisões e porquês

- **Python/FastAPI:** as três rotinas e os 80+ testes já são Python. A API reaproveita `config`, `normalizer`, `kpi`, `price_analysis` e `cnpja` em vez de reescrever.
- **PostgreSQL:** relações claras (chassi, CNPJ, raiz, conta), consultas que hoje a Torre faz em JavaScript sobre 26 mil linhas, e backup com `pg_dump`.
- **Páginas atuais primeiro, reescrita depois:** a Fase 1 só muda *onde* e *atrás de quê* as páginas rodam. Ninguém fica sem a Torre durante a migração.
- **Login no servidor:** sessão em cookie `HttpOnly`/`Secure`/`SameSite=Lax`, senha com Argon2, bloqueio após tentativas erradas. Os arquivos de dados só saem pela API, para usuário logado.
- **Rotinas na VPS:** mesmo código, agendadas pelo worker. Gravam no banco, não no git. O GitHub fica só com código.
- **Docker Compose:** um `docker compose up -d` sobe tudo; o mesmo arquivo serve para testar no seu computador.

---

### Stack detalhada

| Camada | Escolha | Observação |
|---|---|---|
| Proxy e HTTPS | O Caddy do Radar (`radardispensa-caddy-1`), dono da porta 443 | Só **acrescentamos** uma rota para a Torre; nada do Quantica e do Radar é alterado |
| API | Python 3.12, FastAPI, Uvicorn (1–2 workers), Pydantic v2 | Mesma linguagem das rotinas e dos testes atuais |
| Banco | PostgreSQL 16 em contêiner, configurado para pouca RAM | `shared_buffers` 128 MB, sem porta exposta para fora |
| ORM e migrações | SQLAlchemy 2 + Alembic | Mudanças de tabela versionadas |
| Login | Sessão no servidor (cookie `HttpOnly`), Argon2, token CSRF, limite de tentativas | Sem senha ou hash no HTML |
| Rotinas | Contêiner `worker` com APScheduler (fuso America/Sao_Paulo) sobre a imagem Playwright/Python | Reaproveita `assobens/`, `licitacoes/` e `cnpja.py`; uma rotina por vez |
| Arquivos | Volume `/data` para originais baixados e logs | Fora do git |
| Testes e deploy | pytest + httpx; GitHub Actions constrói a imagem, publica no GHCR privado e a VPS faz `pull` | A VPS não compila nada (economiza CPU/RAM) |
| Backup | `pg_dump` noturno + `rclone` para fora da VPS, além dos snapshots da Hostinger | Restauração testada na Fase 2 |
| Front | As páginas HTML atuais (Vue via CDN) na Fase 1–4; Vite na Fase 5 | Nada para de funcionar durante a migração |

---

## 3. Decisões que dependem de você (antes da Fase 1)

- [ ] **Domínio definitivo.** Registrar um (ex.: `torretecar.com.br` no Registro.br) ou usar um subdomínio da Tecar. O endereço `github.io` não pode ser levado para a VPS.
- [x] **Domínio provisório:** `torre.2-25-95-244.sslip.io` e `simule.2-25-95-244.sslip.io` (resolvem para o IP da VPS sem configurar DNS e aceitam certificado). Se o Let's Encrypt recusar por limite do sslip.io, o plano B é `srv1879027.hstgr.cloud/torre`. Trocar pelo domínio definitivo é só mudar a rota no proxy e o DNS.
- [x] **VPS:** Hostinger KVM 1, Ubuntu 24.04, 50 GB de disco (20 GB usados), memória em 35% de uso, compartilhada com dois sistemas que **devem continuar intactos**: **Quantica Sistema de Gestão** (responde em HTTP na porta 80) e **Radar**. A porta 443 também está ocupada por um proxy (responde 400 a HTTP simples e não tem certificado para o nome `hstgr.cloud`).
- [x] **Levantamento da VPS (05/11/2026):**

| Recurso | Situação |
|---|---|
| CPU / RAM / swap | 1 vCPU · 3,8 GiB (3,0 GiB disponíveis) · swap 2 GiB (526 MiB em uso) |
| Disco | 48 GB, 28 GB livres |
| Porta 80 | `quantica-app` (rede `quantica-net`) |
| Porta 443 | `radardispensa-caddy-1` (`caddy:2-alpine`, rede `radardispensa_radar_net`), na frente de `radardispensa-radar-1:8080` |
| Outros | `quantica-queue`, `quantica-scheduler`, `quantica-db` (Postgres 18), `quantica-redis`; nenhuma porta de banco publicada no host |
| Portas abertas no host | 22, 80, 443 |

- [x] **Integração com o proxy (aprovada em 05/11/2026, com a condição de Torre e Radar continuarem independentes):** a rota da Torre entra no **Caddy do Radar**, dono da 443. O certificado sai pelo desafio TLS-ALPN na própria 443, como já acontece com o Radar. A configuração do Radar fica no repositório `zero-touch-ops` (`product/radardispensa/vps`), montada no contêiner como arquivo somente leitura.
  - **Rede `proxy_edge`, só para o proxy:** nela entram apenas `radardispensa-caddy-1` e `torre-api`. O contêiner `radar`, o banco da Torre e o worker da Torre **não** participam. Nenhum dos dois sistemas alcança o outro.
  - **O Radar não depende da Torre:** `atualizar.sh` e `instalar.sh` do Radar criam `proxy_edge` se ela não existir. Sem a Torre no ar, os nomes dela respondem 502 e o Radar segue normal.
  - **Mudança preparada em PR rascunho:** [zero-touch-ops#2](https://github.com/sizervincio-cyber/zero-touch-ops/pull/2), com o bloco abaixo, o `caddy` na rede `proxy_edge` e a criação da rede nos scripts.

```text
torre.2-25-95-244.sslip.io, simule.2-25-95-244.sslip.io {
	encode zstd gzip
	reverse_proxy torre-api:8000
}
```

  - **Quando aplicar:** só depois que `torre-api` estiver rodando na Fase 1. Merge do PR e `./atualizar.sh` do Radar. O `caddy` do Radar é recriado por causa da rede nova: alguns segundos sem HTTPS no Radar, em horário de pouco uso. O contêiner `radar` não é recriado.
  - **Para desfazer:** reverter o commit no `zero-touch-ops` e rodar `./atualizar.sh` de novo.
- [ ] **Firewall da Hostinger está com 0 regras:** liberar só 22, 80 e 443 (são as únicas portas usadas hoje).
- [ ] **Orçamento de recursos da Torre:** Postgres 256 MB, API 256 MB, worker até 768 MB só durante a rotina ASSOBENS (Chromium), CPU do worker limitada a 0,5. Com 1 vCPU, as rotinas rodam uma por vez e fora dos horários de pico, se for o caso.
- [ ] **Usuários iniciais** e perfis: quem vê tudo, quem vê só a própria carteira, quem vê só simulação (hoje existe o perfil `sim`).
- [ ] **Destino do backup:** outro provedor/bucket (Backblaze B2, S3, Google Drive da empresa).
- [ ] **Validação jurídica/LGPD:** a exposição pública da matriz já ocorreu; vale registrar a correção e avaliar se a ASSOBENS precisa ser informada.

---

## 4. Fases

### Fase 0 — Preparação (sem mudança para o usuário)

- [ ] Conferir para onde aponta o QR Code `QR - Simulador TCO Tecar.svg` (se for `github.io/TorreTecar/simule.html`, os impressos dependem do redirecionamento da Fase 1).
- [x] Criar a estrutura no repositório: *(feito em 05/11/2026: `server/`, `deploy/`, `tests/test_servidor.py`)*

```text
server/
  app/main.py            FastAPI: rotas, sessão, páginas estáticas
  app/auth.py            login, Argon2, perfis, bloqueio por tentativas
  app/db.py              engine SQLAlchemy
  app/models.py          tabelas
  app/routers/*.py       /api/... por domínio
  migrations/            Alembic
  worker/scheduler.py    agenda as rotinas existentes
  Dockerfile
deploy/
  docker-compose.yml     api, worker, postgres (projeto "torre", sem portas públicas)
  proxy-torre.conf       rota a acrescentar no proxy existente (formato conforme o proxy)
  .env.example           variáveis (sem segredos)
  backup.sh              pg_dump + envio para fora da VPS
tests/server/            testes da API
```

- [ ] `.env` só na VPS: `DATABASE_URL`, `SESSION_SECRET`, `ASSOBENS_USER/PASSWORD`, `CNPJA_API_KEY`, `BACKUP_*`. Nunca no git.

### Fase 1 — Torre na VPS com login real (fecha a exposição)

Meta: o mesmo sistema de hoje, no domínio novo, só para quem faz login. É a fase mais urgente.

- [x] Regras de convivência (valem para todas as fases): *(aplicadas no `deploy/docker-compose.yml`)*
  - projeto Compose próprio (`torre`), rede Docker própria e **Postgres próprio**: não usar banco, volume nem rede do Quantica ou do Radar;
  - contêineres da Torre sem portas públicas: escutam só em `127.0.0.1` ou na rede do proxy;
  - limites de CPU e memória em todos os contêineres da Torre;
  - a única mudança fora da Torre é **acrescentar** uma rota no proxy, validada antes (`nginx -t` / `caddy validate` / teste de rótulos do Traefik) e aplicada com *reload*, nunca *restart*;
  - snapshot da Hostinger antes de cada mudança no proxy ou no firewall.
- [ ] Endurecer a VPS sem afetar os outros sistemas: firewall liberando 22, 80, 443 **e qualquer porta que Quantica e Radar usem** (pelo levantamento), `fail2ban`, `unattended-upgrades`. SSH só por chave e usuário sem root, combinados com você antes.
- [ ] DNS: registro A de `torre.<dominio>` e `simule.<dominio>` para o IP da VPS. O Caddy do Radar emite o certificado pelo desafio TLS-ALPN na 443.
- [x] API mínima: `/login`, `/logout`, sessão, tabela `usuarios` com perfis `admin`, `gestor`, `vendedor`, `simulacao`.
- [x] Servir `Analitycmbb.html`, `gestao-tecar.html`, `tco-simulador.html`, `trucktest*` e `Analityc share/**` **somente com sessão válida**; sem sessão, redireciona para `/login`. *(lista fechada em `server/app/site.py`; perfil `simulacao` recebe 403 nos dados)*
- [ ] Remover o `miccGate()` e as senhas embutidas; o perfil vem do servidor. *(Parcial: servido pela VPS, o gate cede ao `window.TORRE_SERVER` injetado pelo servidor; o gate e os hashes só saem do HTML depois da virada, porque o GitHub Pages ainda depende deles.)*
- [x] `simule.<dominio>` público, com `POST /api/leads` (validação, limite por IP, campo-armadilha anti-robô). Tabela `leads` substitui o Apps Script. *(sem o campo-armadilha por enquanto: validação, limite de 10 envios/hora por IP e 32 KB)*
- [x] Rotinas ainda no GitHub Actions nesta fase: um passo de deploy copia os arquivos atualizados para a VPS (ou a VPS faz `git pull` agendado). *(contêiner `atualiza-dados`, `git pull` a cada 10 min)*
- [ ] **Virada:**
  1. Testar o domínio novo com 2–3 usuários.
  2. Renomear o repositório atual para `torre-tecar` e torná-lo **privado** (o Pages dele sai do ar).
  3. Criar um repositório público novo chamado `TorreTecar` só com `index.html` e `simule.html` redirecionando para o domínio novo: o link antigo e o QR continuam funcionando.
  4. Trocar as senhas (os hashes antigos ficaram públicos).
- [ ] Caminho de volta: o repositório renomeado continua inteiro; reativar o Pages devolve a versão anterior.

**Pronto quando:** `curl` sem login na matriz devolve 401/302; login funciona no celular; QR antigo abre o simulador novo.

### Fase 2 — Banco de dados e rotinas na VPS

Meta: Postgres vira a fonte da verdade e o git deixa de guardar dados.

- [ ] Tabelas (Alembic):
  - `emplacamentos` (chassi PK, data, modelo, tração, marca, segmento, subsegmento, placa, concessionário, cidade, UF, AOP, anos, terreno, documento, tipo, proprietário)
  - `empresas_cnpja` (cnpj PK, campos de `resumo_empresa`, consultado_em)
  - `crm_clientes`, `crm_responsaveis` (hoje `CRM_ROWS`/`CRM_RESP` no HTML)
  - `precos_historico`, `equivalencias_mb`, `tracao_modelos`
  - `licitacoes_*` (espelhando `Analityc share/licitacoes/*.json`)
  - `sync_runs`, `status_rotinas`
- [ ] Script de carga inicial a partir da matriz `.xlsx`, JSONs e CSV atuais, com conferência de totais (mesma conferência ASSOBENS × Torre que existe hoje).
- [ ] Adaptar `assobens.importer` e `licitacoes` para gravar no banco (manter a escrita em arquivo atrás de uma opção, para comparar por uma semana).
- [ ] Worker com os mesmos horários: ASSOBENS 08h/12h/17h, licitações de hora em hora, CNPJá após a ASSOBENS. Alerta por e-mail quando uma rotina falhar duas vezes seguidas.
- [ ] Desligar os workflows de sincronização do GitHub Actions e parar os commits `data: …`.
- [ ] Backup diário (`pg_dump` + arquivos originais baixados) para fora da VPS, com 30 dias de retenção. **Testar uma restauração** antes de dar a fase por pronta.

**Pronto quando:** uma semana de rotinas rodando só na VPS, totais batendo com a ASSOBENS, restauração testada.

### Fase 3 — A Torre lê da API e o estado fica no servidor

Meta: fim do "cada navegador tem a sua versão".

- [ ] Endpoints que devolvem **o mesmo formato** dos arquivos atuais, para trocar só a URL no front:
  - `GET /api/emplacamentos` (no lugar da matriz `.xlsx`; paginado ou em formato compacto)
  - `GET /api/kpis`, `/api/top10`, `/api/precos/top10`, `/api/precos/historico`, `/api/status`
  - `GET /api/empresas` (cadastro CNPJá), `GET /api/licitacoes/...`
  - `GET /api/crm` (no lugar de `CRM_ROWS` embutido; remove o CRM do HTML)
- [ ] Migrar o que hoje é `localStorage`, com importação única do que cada usuário já tem no navegador:

| Chave atual | Vira |
|---|---|
| `micc_obs_comercial` | `observacoes_comerciais` (por raiz, autor, data) |
| `micc_crm_contacts` | `contatos` (por CNPJ, visível conforme o perfil) |
| `micc_rules` | `regras` (globais, editadas por admin) |
| `tecar-tco-leads` | `leads` (já criada na Fase 1) |
| `micc_pinned_hash`, `micc_shareview`, `micc_nav_open` | preferências do usuário (podem ficar no navegador) |

- [ ] Importação do CRM e da tabela de gestão (`gestao-tecar.html`) feita uma vez no servidor por um admin, em vez de em cada navegador.
- [ ] Log de auditoria: quem acessou, exportou CSV ou editou observação.

**Pronto quando:** duas pessoas em computadores diferentes veem a mesma observação comercial; o HTML não contém mais CNPJ nem nome de cliente.

### Fase 4 — Permissões por carteira

- [ ] Vendedor vê só as contas em que é responsável no CRM (mais o whitespace da casa, se decidido); gestor vê a casa; diretoria vê tudo.
- [ ] Filtro aplicado **na API**, não só na tela.
- [ ] Tela de administração de usuários (criar, desativar, trocar perfil, redefinir senha).

### Fase 5 — Modernizar o front (opcional, depois de estável)

- [ ] Quebrar o `Analitycmbb.html` (2,6 MB) em app Vite + Vue com módulos (Mercado, Carteira, Preços, Licitações, Leads), bibliotecas instaladas em vez de CDN.
- [ ] Cálculos pesados (agregações da carteira, KPIs) passam para consultas SQL na API.
- [ ] Reaproveitar os planos já escritos em `docs/superpowers/plans/` (Sales Intelligence, Estoque e Rentabilidade) sobre essa base.

---

## 5. Entrega contínua

- [ ] GitHub Actions no repositório privado: testes (`pytest`) a cada push; na `main`, build das imagens e deploy na VPS por SSH com chave dedicada (`docker compose pull && up -d` + migrações Alembic).
- [ ] Ambiente de teste opcional: `teste.<dominio>` com cópia anonimizada do banco.
- [ ] Healthcheck `GET /api/health` monitorado por um serviço externo de uptime.

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Chromium/Playwright na VPS falhar no login ASSOBENS (IP de datacenter, captcha) | Testar na Fase 2 com a rotina ainda ativa no GitHub; manter o agendador Windows (`scripts/assobens_agendador_windows.ps1`) como plano B |
| VPS cair | Backup fora da VPS + `docker compose` reproduz tudo em outra máquina em menos de 1 hora |
| QR impresso apontar para o endereço antigo | Repositório público `TorreTecar` só com redirecionamentos |
| Pouca RAM (KVM 1 compartilhada com Quantica e Radar) | Limitar memória dos contêineres; rotinas não rodam em paralelo; medir o pico do Chromium na Fase 2 |
| Novo deploy do Radar sobrescrever o Caddyfile e derrubar a rota da Torre | Bloco da Torre em arquivo próprio com `import`, combinado com quem mantém o Radar; monitor de uptime avisa na hora |
| Afetar Quantica ou Radar | Nenhum contêiner, volume ou rede deles é tocado; rota nova no proxy validada antes e aplicada com *reload*; snapshot antes; teste de Quantica e Radar logo após cada mudança |
| Dados já expostos no histórico do git | Repositório privado na Fase 1; avaliar limpeza de histórico (BFG/`git filter-repo`) com cuidado, porque reescreve todos os commits |
