# Rotina ASSOBENS → Torre Tecar

Rotina autônoma, idempotente e auditável que baixa o relatório analítico de emplacamentos do
BI ASSOBENS (Veículos Novos Área Operacional → VEÍCULOS → Excel), atualiza a matriz que a Torre
já lê, recalcula os KPIs existentes e captura o Comparativo de Preços para os 10 modelos mais
vendidos de cada segmento.

## Arquitetura (aderente ao projeto: site estático, sem backend)

| Camada | Onde | O quê |
|---|---|---|
| Robô | `assobens/` (Python + Playwright) | login, navegação, download, parse, normalização, validação, upsert, KPIs, preços |
| "Banco" | `Analityc share/` (versionado) | `consolidado_emplacamentos_2020_2026.xlsx` (matriz, chave única CHASSI) + `assobens/*.json`, `precos_historico.csv` |
| Histórico/auditoria | git + `Analityc share/assobens/sync_runs.json` + artefatos do Actions | cada execução, hash do arquivo, contagens, erros |
| Scheduler | `.github/workflows/assobens-sync.yml` | `0 11,15,20 * * *` UTC = **08/12/17 America/Sao_Paulo**; `workflow_dispatch` = "Atualizar ASSOBENS agora" |
| Alternativa local | `scripts/assobens_agendador_windows.ps1` | Agendador do Windows 08/12/17 no fuso do sistema |
| Frontend | `Analitycmbb.html` → Importações → card **ASSOBENS** | última/próxima atualização, status, registros, preços, mensagem de falha |

Serviços (um módulo cada): `auth` (AssobensAuthenticationService), `browser` (AssobensBrowserService),
`emplacamentos_downloader`, `price_downloader`, `parser` (AssobensSpreadsheetParser), `normalizer`,
`validator`, `importer` (upsert + publicação atômica), `kpi` (AssobensKpiService),
`price_analysis` (AssobensPriceAnalysisService + PriceHistory), `sync_job` (AssobensSyncJob), `runlog`.

## Credenciais

Somente por ambiente: `ASSOBENS_USER` e `ASSOBENS_PASSWORD`.

- Local: crie `.env` na raiz (já ignorado pelo git) com as duas linhas `ASSOBENS_USER=` / `ASSOBENS_PASSWORD=`.
- GitHub Actions: *Settings → Secrets and variables → Actions → New repository secret* (os dois nomes acima).
- Logs redigem senha, token JWT, cookies e headers (`logutil.redact`). O token do BI nunca é devolvido pelos serviços.

## Como o robô funciona

1. `portal.assobens.org.br/wp-login.php` (WordPress): preenche por *label* ("Nome de usuário ou endereço de e-mail", "Senha"), clica "Acessar". Login válido = `#login_error` ausente **e** `body.logged-in`/`#wpadminbar`/link do BI presente.
2. Segue o link do portal para `bi-assobens.com.br/?ssotoken=…` (SSO → rota `/sso/:token`); sessão válida = `localStorage._pbiAssobens` com JWT. Fallback: login direto no BI (o BI responde 403 pedindo o portal quando o acesso é unificado).
3. Menu **Veículos Novos Área Operacional** (a rota `/dashboard` direta dá 404 na Netlify — navegação sempre pelo menu). O relatório é **Power BI embutido** (report `82a1f474…`, página `81f800ed…`).
4. Dentro do iframe: opção **VEÍCULOS** → ícone **Excel** → download (`storage/app/assobens/AAAA/MM/DD/HHMM_emplacamentos.xlsx`). Região MB e Distrito não são tocados (ficam "Todos"; o estado é apenas registrado no log).
5. Parser por **nome de cabeçalho** (aliases em `parser.ALIASES`; posição das colunas é irrelevante). Colunas de contato/endereço (`C_TELEFONE*`, `C_EMAIL`, `C_NO_LOGR`, `C_NU_CEP`…) nunca saem do arquivo bruto.
6. Normalização: data ISO, CNPJ formatado, PF mascarada (`***.***.***-**`/`***`), marca unificada com o rótulo da matriz (`MERCEDES-BENZ`→`M.BENZ`, `VOLKSWAGEN`→`VW`…), texto sem espaços ocultos.
7. Validações antes de publicar: soma por fabricante = total; share total = 100%; MB calculado × informado (quando houver); sem negativos; arquivo vazio; mudança de estrutura; **queda > 50%** vs execução anterior (bloqueia a publicação, status `partial`); gate de qualidade da Torre (≥ 75).
8. **UPSERT por CHASSI** na matriz; publicação atômica (`os.replace`) com backup da anterior em `storage/app/assobens/backup/`. Mesmo arquivo duas vezes = 0 inseridos/0 atualizados; valor alterado no ASSOBENS = registro atualizado, nunca duplicado.
9. KPIs recalculados da matriz vigente (`kpis.json`), ranking de modelos por subsegmento nos últimos 12 meses → **Top 10** (`top10_segmentos.json`).
10. Comparativo de Preços (Power BI `512302d7…`): leitura da tabela acessível ou "Exportar dados" do visual → `precos_historico.csv` (append-only; mesma data com preço diferente atualiza) → `precos_top10.json` com gap R$/% usando **só** `equivalencias_mb.json` (vazio ⇒ `equivalente_mb = null`, "equivalência não cadastrada").
11. Auditoria em `sync_runs.json` (id, started/finished, status, source, file_name, file_hash, rows_downloaded/valid/imported/updated/rejected, error_message, executed_by, trigger_type, steps) e `status.json` para a Torre.
12. Falhas: 3 tentativas na etapa de navegador (30 s, 2 min); login recusado não repete; screenshot + JSON (timestamp, URL, etapa) em `storage/logs/assobens/errors/`; status `failed` mantém a última base válida.

## DE/PARA ASSOBENS → matriz → KPI da Torre

| ASSOBENS (relatório) | Matriz | KPI existente na Torre |
|---|---|---|
| Marca / MARCA_COMPLETA | MARCA | Total Mercado, Total Mercedes-Benz (`M.BENZ`), Market Share MB, share por fabricante |
| Data Emplacamento / DATA_COMPLETA | DATA EMPLACAMENTO | por ano, por mês, últimos 12 meses, evolução, sazonalidade |
| SubSegmento | SUBSEGMENTO | segmento comercial (LEVES/MEDIOS/SEMIPESADOS/EXTRAPESADOS) |
| Segmento | SEGMENTO | família (1.0-CAMINHOES) |
| Tração | TRAÇÃO | mix por tração |
| Modelo | MODELO | ranking de modelos, Top 10 |
| Município / Estado | CIDADE / UF | território, geointeligência |
| Desc. Área Operacional / Área Operacional | DEALER AOP / AOP | área operacional |
| CPF ou CNPJ / Tipo de Pessoa / Nome do Proprietário | CPFCNPJPROPRIETARIO / TIPOCNPJPROPRIETARIO / NOMEPROPRIETARIO | clientes, classificação MBB, recorrência |
| Combustível, Grupo, Versão, Região MB, Distrito, Tipo Veículo (se vierem) | colunas extras preservadas | ainda sem KPI (a Torre ignora colunas desconhecidas) |

Nenhum KPI foi criado ou duplicado: a Torre continua calculando tudo a partir da matriz.

## Comandos

```bash
python -m assobens sync --trigger manual            # sincronização completa (navegador headless)
python -m assobens sync --trigger manual --headed   # navegador visível (depuração)
python -m assobens importar caminho/arquivo.xlsx    # importa um Excel já baixado, sem navegador
python -m assobens discover                         # login + screenshot + árvore de acessibilidade dos relatórios
python -m assobens kpis                             # recalcula kpis/top10/precos_top10 da matriz atual
python -m assobens status                           # status.json
python -m pytest -q tests                           # testes
```

Dependências: `pip install -r requirements-assobens.txt && python -m playwright install chromium`.

## Primeira execução em produção (obrigatória antes de ligar a agenda)

1. Configurar os dois secrets no GitHub (ou `.env` local).
2. `python -m assobens discover` → conferir em `storage/logs/assobens/` se a opção **VEÍCULOS** e o ícone **Excel** foram
   localizados; ajustar `assobens/selectors.json` se necessário (candidatos são tentados em ordem).
3. `python -m assobens sync --trigger manual` (ou *Actions → ASSOBENS sync → Run workflow*).
4. Conferir contra o portal: Total Mercado, Total MB, Share MB, ranking de fabricantes, subsegmentos, Top 10, preços (`kpis.json`, `top10_segmentos.json`, `precos_top10.json`).
5. Só então criar a variável de repositório `ASSOBENS_SCHEDULER_ENABLED=true` (*Settings → Secrets and variables → Actions → Variables*): a agenda 08/12/17 passa a rodar. A execução manual funciona independentemente dessa variável.

## Premissas documentadas

- Sem credenciais em mãos nesta implementação, os localizadores **dentro do Power BI** (aba VEÍCULOS, ícone Excel, tabela de preços)
  foram escritos a partir do código público do BI e de padrões do Power BI embutido; ficam em `selectors.json` e se confirmam na primeira execução autenticada (`discover`).
- O endpoint interno `GET /v1/dados/excel` (usado pela página *Enriquecimento – Baixar dados*) existe, mas o próprio BI avisa que
  esse relatório "não deve ser considerado para fins de market share" e ele não traz Tração/Terreno; por isso a fonte principal é o Excel do relatório Power BI.
- Repositório público: PF mascarada e colunas de contato nunca publicadas, como na matriz atual.
- Cron do GitHub é UTC; Brasil sem horário de verão desde 2019 ⇒ 11/15/20 UTC = 08/12/17 São Paulo (testado em `tests/test_scheduler_tz.py`).
