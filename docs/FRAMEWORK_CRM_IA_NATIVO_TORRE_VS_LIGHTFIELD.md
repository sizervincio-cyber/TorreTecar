# Torre CRM: framework e stack para um CRM nativo em IA igual ou superior ao Lightfield

> Versão 1.0 · 07/11/2026 · Escopo: vendas de caminhões e ônibus Mercedes-Benz da Tecar (Goiânia e Anápolis)

---

## 1) TL;DR

- **O que o Lightfield é:** um CRM que se monta sozinho. Lê e-mail, agenda, Slack, LinkedIn e gravações de reunião, guarda tudo sem esquema fixo (primeiro o dado bruto, depois a estrutura) e põe agentes de IA para preparar reuniões, diagnosticar negócio parado, montar cadência e escrever follow-up. A demo é feita com o workspace já montado com os dados do próprio cliente.
- **Onde ele é fraco para nós:** foi feito para startup americana de SaaS que vende por e-mail e Zoom. Não tem WhatsApp como canal principal, não conhece o funil de concessionária (test-drive, avaliação de usado, financiamento Banco Mercedes-Benz/FINAME, faturamento direto, implemento, entrega técnica), não conversa com o portal CIMBB da montadora e cobra em dólar (US$ 999 a 1.999 por mês no workspace, mais créditos).
- **Nossa tese:** copiar a arquitetura dele (captura automática + grafo de contexto + agentes) e ganhar em quatro frentes onde ele não joga: **WhatsApp primeiro, verticalização de concessionária pesada, dados que já temos (TCO, licitações, ASSOBENS, estoque) e custo em real rodando no nosso VPS.**
- **Stack recomendada:** evoluir o que já existe no repositório (FastAPI + Postgres 16 + servidor MCP), somando pgvector, fila de jobs, API de LLM com roteamento de modelo, transcrição de áudio e um front Next.js. Nada de reescrever do zero.

---

## 2) Diagnóstico: como o Lightfield funciona

### 2.1 Produto

| Camada | Como funciona no Lightfield | Fonte |
|---|---|---|
| Captura | Conecta e-mail e agenda e puxa até 2 anos de histórico em minutos. Também Slack, LinkedIn, gravador de reunião próprio, data warehouse | Getting started, SaaStr |
| Modelo de dados | "Schema-less": guarda o não estruturado primeiro. Quando você cria um campo novo, ele reprocessa o histórico e preenche retroativamente, com proveniência (de qual e-mail ou call veio o valor) | Reviews, Trust Center |
| Grafo de contexto | Contas, contatos, oportunidades e interações ligados entre si. Pessoas e agentes têm a mesma leitura e escrita | Trust Center |
| Agentes | Prep de reunião, resumo pós-call, diagnóstico de deal parado (compara com ganhos e perdidos: "nos ganhos o TI entrou cedo, aqui não"), busca de ICP em empresas novas, cadência de outbound, e-mail de reativação | SaaStr (demo ao vivo do CEO) |
| Workflows | Builder com passos de agente, gatilho por webhook e chamadas HTTP | Trust Center |
| Chat / Q&A | Pergunta em linguagem natural sobre a base. Expõe servidor MCP para Claude/ChatGPT consultarem e agirem no CRM | Reviews |
| Migração | Agente de importação: sobe o CSV do HubSpot/Salesforce, ele propõe o mapeamento, você confirma. Ordem: contas, contatos, oportunidades. Sync bidirecional para conviver com o CRM antigo | Blog e página Migration |
| Segurança | SOC 2 Type II, HIPAA/BAA, criptografia em repouso, TLS, RBAC. ISO 27001 "em breve" | trust.lightfield.app |

### 2.2 Fluxo do "Book a Demo"

1. Formulário curto (nome, e-mail corporativo, empresa, tamanho do time, CRM atual).
2. Agendamento direto na agenda do time de vendas.
3. Na call, o workspace é montado **ao vivo com os dados do prospect** (conecta e-mail e agenda, o CRM aparece populado). Esse é o momento "uau": o cliente vê os próprios negócios organizados sem digitar nada.
4. Pós-venda: engenheiros "forward-deployed" acompanham a migração (cerca de 2 h para sair de Zoho/HubSpot e 30 a 45 min de treinamento, segundo o próprio CEO).

**Lição de produto:** a demo não mostra o software, mostra o cliente dentro do software. Vamos replicar isso com o vendedor da Tecar: no primeiro login ele vê a carteira dele já montada a partir do WhatsApp e da agenda.

### 2.3 Canal do YouTube (@ltfld-app)

Vídeos identificados: "Lightfield Demo: The AI-native CRM" (começa pelo **seller cockpit**, a tela do vendedor), "Lightfield platform overview", "Zero to One: Why We Built Lightfield" (história do fundador) e demos ao vivo em eventos SaaStr ("o CRM que se monta no palco e destrava um deal em 3 minutos"). O padrão de conteúdo é: dor da digitação, CRM se montando sozinho, agente resolvendo um caso real em minutos.

> Limitação: o acesso direto ao lightfield.com e ao YouTube foi bloqueado pela rede deste ambiente. A análise usa páginas indexadas do próprio Lightfield (lightfield.app, support, trust center, blog), cobertura da SaaStr e reviews de terceiros. Os preços mudaram mais de uma vez em 2026 e devem ser confirmados na página oficial.

### 2.4 Modelo de negócio (referência)

- Starter US$ 89 por usuário/mês (até 3), Pro US$ 999/mês por workspace (5 seats de captura, viewers ilimitados), Growth US$ 1.999/mês (10 seats), Enterprise sob consulta. Seat extra de captura US$ 200/mês.
- Créditos de IA: 10 por item ingerido (e-mail, reunião, mensagem), 15 por 30 min gravados, 20 por reunião processada (prep + resumo).
- Fundadores do Tome (Keith Peiris e Henri Liriani). Série A de US$ 47 mi liderada pela a16z.

**Para a Tecar com 10 vendedores:** cerca de US$ 1.999 a 2.999/mês, ou R$ 11 a 17 mil/mês (câmbio de R$ 5,60), sem WhatsApp e sem nada de concessionária.

---

## 3) Red team: o que pode dar errado ao copiar o Lightfield

| Premissa fraca | Por que quebra | Correção |
|---|---|---|
| "Basta ler e-mail e agenda" | Vendedor de caminhão vende no WhatsApp, no telefone e no pátio. E-mail é 10% da conversa | WhatsApp e ligações são a fonte nº 1 |
| "Schema-less resolve tudo" | Sem campos fortes não dá para fechar meta, comissão nem falar com o CIMBB | Híbrido: núcleo estruturado (proposta, modelo, valor, etapa) + camada flexível JSONB com proveniência |
| "O agente envia sozinho" | Mensagem errada para frotista grande queima relacionamento de anos e pode violar LGPD | Agente rascunha, humano aprova. Envio automático só em cadências de baixo risco já aprovadas |
| "Ler o WhatsApp pessoal do vendedor" | Risco trabalhista e LGPD, e o vendedor sai e leva a carteira | Número corporativo por vendedor via API oficial (Cloud API) ou dispositivo da empresa, com termo de consentimento e política escrita |
| "Construir tudo de uma vez" | Projeto de 12 meses morre antes de gerar valor | MVP em 6 semanas com 1 loja e 3 vendedores, medir adoção antes de escalar |
| "LLM é barato" | Reprocessar 2 anos de conversas de 10 vendedores custa caro se usar o modelo topo em tudo | Roteamento: modelo rápido para extração, modelo topo só para diagnóstico e redação |
| "VPS atual aguenta" | Postgres hoje roda com 256 MB. Embeddings e transcrição não cabem | Subir o VPS (8 GB RAM) ou separar worker de IA |

---

## 4) Blue team: framework Torre CRM (modelo C.O.R.E.)

Quatro camadas. Cada uma tem um resultado medível.

```
 FONTES                      C · CAPTURA            O · ORGANIZAÇÃO              R · RACIOCÍNIO            E · EXECUÇÃO
 WhatsApp Cloud API  ─┐      conectores +           grafo de contexto            agentes com ferramentas   cockpit do vendedor
 Ligações (gravação) ─┤      normalização em        (conta, contato, frota,      e memória                 cadências e tarefas
 E-mail / Agenda     ─┼────▶ "eventos" brutos ────▶ oportunidade, proposta) ────▶ prep, diagnóstico,  ────▶ painel do gerente
 Portal CIMBB        ─┤      com proveniência       + campos extraídos por IA     próxima ação, previsão    sync CIMBB / MCP
 Licitações/ASSOBENS ─┤                             + busca vetorial                                       (humano aprova)
 Estoque / TCO       ─┘
```

### C · Captura (zero digitação)

- **Evento** é a unidade de tudo: mensagem, ligação, e-mail, reunião, visita, proposta, nota de voz. Cada evento guarda texto, autor, horário, canal e link para a origem.
- Conectores na ordem de valor: WhatsApp, agenda Google, e-mail, telefonia (gravação + transcrição), CIMBB, bases internas que já existem no repositório (licitações, ASSOBENS, simulador TCO, estoque).
- Nota de voz no app ("acabei de sair da Transportadora X, querem 3 Actros 2651 para março") vira evento estruturado. Isso é melhor que o Lightfield para quem vive na estrada.

### O · Organização (grafo de contexto híbrido)

- **Núcleo estruturado** (tabelas Postgres): Conta, Contato, Frota (placa, modelo, ano, km), Oportunidade, Proposta, Veículo do estoque, Vendedor, Loja.
- **Camada flexível**: `atributos JSONB` com proveniência por campo `{valor, evento_origem, confiança, extraído_em}`. Campo novo dispara backfill sobre o histórico, como no Lightfield.
- **Resolução de entidades**: casar "Zé da Transcerrado", "José Silva" e o CNPJ da Transcerrado na mesma conta (regras + LLM + confirmação humana quando a confiança for baixa).
- **Busca**: pgvector para semântica + full-text do Postgres para nome, placa e CNPJ.

### R · Raciocínio (agentes)

| Agente | Gatilho | Entrega | Diferencial vs Lightfield |
|---|---|---|---|
| Prep de visita | 1 h antes do compromisso | Resumo da conta, frota atual, idade média, última proposta, objeções, TCO sugerido | Usa frota e TCO, não só e-mails |
| Pós-contato | Fim de ligação ou conversa | Resumo, próxima ação, atualização de etapa (sugestão) | Funciona em WhatsApp e áudio |
| Deal parado | Oportunidade sem evento há N dias | Diagnóstico comparando com ganhos e perdidos + rascunho de mensagem | Padrões de concessionária (aprovação de crédito, implemento, prazo de entrega) |
| Renovação de frota | Diário | Lista de contas com caminhões acima de X anos ou km, ordenada por potencial | Não existe no Lightfield |
| Radar de licitações | Nova licitação compatível | Alerta ao vendedor da região com edital e proposta-base | Integra o módulo `licitacoes` atual |
| Copiloto do gerente | Pergunta livre | "Quais propostas acima de R$ 1 mi estão paradas em Anápolis?" com links para evidências | Também via MCP no ChatGPT/Claude (já temos `mcp_torre`) |
| Importação | Upload de planilha ou export | Mapeamento proposto, confirmação, carga | Igual ao Lightfield |

Regras dos agentes: toda afirmação cita o evento de origem, toda escrita no CRM é sugestão até o vendedor aceitar (ou regra explícita de autoaprovação), log de auditoria de cada ação.

### E · Execução (onde o vendedor trabalha)

- **Cockpit do vendedor** (mobile primeiro): agenda do dia com prep pronto, fila de "próximas ações" priorizada, rascunhos para aprovar com um toque, nota de voz.
- **Painel do gerente**: funil por loja e vendedor, previsão ponderada, deals em risco, aderência (atividades por oportunidade).
- **Sync CIMBB**: lança atividades e atualizações de proposta no portal da montadora (aproveitando a rotina que já existe hoje), fim da digitação dupla.
- **MCP**: o servidor `mcp_torre` passa a expor leitura e escrita do CRM.

---

## 5) Stack recomendada

Princípio: **estender o que já roda** (FastAPI, Postgres 16, Alembic, Docker Compose, Caddy, MCP) e somar só o necessário.

| Camada | Escolha | Por quê | Alternativa |
|---|---|---|---|
| Backend / API | **FastAPI + SQLAlchemy 2 + Alembic** (já existe em `server/`) | Time já domina, Python é a língua das libs de IA | NestJS (só se o time virar TS) |
| Banco | **Postgres 16 + pgvector + pg_trgm** | Um banco só para relacional, JSONB, vetor e busca textual. Menos peças | Qdrant separado se passar de ~5 mi vetores |
| Fila e jobs | **Redis + Arq** (ou Dramatiq) | Ingestão, transcrição e agentes rodam fora da requisição | Celery (mais pesado) |
| Orquestração de agentes | **SDK nativo do provedor de LLM com tool use** + funções Python próprias | Menos abstração, mais controle e custo previsível | LangGraph se os fluxos ficarem muito ramificados |
| LLM | **Claude** com roteamento: Haiku para extração e classificação em massa, Sonnet para resumo e rascunho, Opus para diagnóstico e perguntas complexas. Prompt caching ligado | Qualidade em português e uso de ferramentas. Roteamento corta custo | Modelo aberto (Llama/Qwen) via vLLM só para extração, se o volume explodir |
| Embeddings | Modelo multilíngue (ex.: Voyage multilingual ou `bge-m3` local) | Português e nomes próprios | |
| Transcrição | **Whisper large-v3 (faster-whisper)** em worker com GPU sob demanda, ou API de transcrição | Áudio de WhatsApp e ligações em pt-BR | Deepgram/AssemblyAI |
| WhatsApp | **WhatsApp Cloud API oficial (Meta)** com webhook | Legal, estável, sem risco de banimento | BSP como Twilio/360dialog. **Evitar** bibliotecas não oficiais |
| E-mail e agenda | Google Workspace API (Gmail + Calendar) com OAuth e push (Pub/Sub) | Captura em tempo real | Microsoft Graph se houver Outlook |
| Telefonia | URA/PABX em nuvem com gravação e webhook (ex.: Twilio, Zenvia ou o PABX atual se tiver API) | Ligação vira evento | |
| Frontend | **Next.js 15 + React + Tailwind + shadcn/ui**, PWA instalável no celular | Cockpit mobile sem loja de apps | Manter HTML single-file só para páginas públicas (TCO, simule) |
| Tempo real | Server-Sent Events do FastAPI | Simples, sem infraestrutura extra | WebSocket |
| Auth | O `auth.py`/`oauth.py` atuais (Argon2 + JWT) + RBAC por loja e papel | Já existe | Keycloak se precisar de SSO |
| Observabilidade de IA | **Langfuse** self-hosted (traces, custo por agente, avaliação) | Saber quanto cada agente custa e erra | Arize Phoenix |
| Infra | Docker Compose no VPS atual, **com upgrade para 8 GB RAM / 4 vCPU**. Worker de transcrição separado | Custo baixo, controle dos dados no Brasil | Kubernetes só acima de 100 usuários |
| Backup e segurança | `deploy/backup.sh` atual + criptografia de disco, segredos fora do repositório, logs de auditoria, DPO e base legal LGPD documentada | Requisito para dados de clientes | |

**Custo mensal estimado (10 vendedores, 2 lojas):** VPS R$ 300 a 600, LLM R$ 1.500 a 3.500 (com roteamento e cache), WhatsApp Cloud API R$ 300 a 800 (conversas iniciadas pela empresa), transcrição R$ 200 a 500. **Total: R$ 2,5 a 5,5 mil/mês**, contra R$ 11 a 17 mil do Lightfield sem os recursos de concessionária.

---

## 6) Comparativo: Lightfield vs Torre CRM

| Critério | Lightfield | Torre CRM (meta) |
|---|---|---|
| Captura e-mail/agenda | Sim | Sim |
| Captura WhatsApp | Não | **Sim, canal principal** |
| Ligações e notas de voz | Gravador de reunião | **Ligações + áudio WhatsApp + nota de voz** |
| Esquema flexível com backfill | Sim | Sim (JSONB + proveniência) |
| Objetos de concessionária (frota, usado, financiamento, implemento) | Não | **Sim** |
| Integração com montadora (CIMBB) | Não | **Sim** |
| Licitações, TCO, ASSOBENS, estoque | Não | **Sim, já existem no repositório** |
| Agentes de prep, diagnóstico, cadência | Sim | Sim |
| MCP | Sim | Sim (`mcp_torre`) |
| Dados hospedados no Brasil / LGPD | Nos EUA | **No nosso VPS** |
| Certificação SOC 2 | Sim | Não (não é necessária para uso interno) |
| Custo para 10 vendedores | R$ 11 a 17 mil/mês | **R$ 2,5 a 5,5 mil/mês** |

---

## 7) Plano recomendado (roadmap)

| Fase | Semanas | Entrega | Critério de saída |
|---|---|---|---|
| 0. Fundação | 1 a 2 | pgvector, Redis + worker, tabela `eventos`, núcleo Conta/Contato/Frota/Oportunidade, Langfuse | Migrations rodando, teste de ingestão de 10 mil eventos |
| 1. Captura | 3 a 5 | WhatsApp Cloud API, Google Calendar/Gmail, nota de voz com transcrição, importação de planilhas e do CIMBB | 3 vendedores piloto com 100% das conversas no CRM |
| 2. Organização | 5 a 6 | Extração de entidades, resolução de duplicados, busca semântica | Precisão ≥ 90% em amostra de 200 eventos revisados |
| 3. Agentes v1 | 6 a 8 | Prep de visita, pós-contato, deal parado, copiloto do gerente | ≥ 60% dos rascunhos aceitos sem edição grande |
| 4. Cockpit | 7 a 9 | PWA do vendedor + painel do gerente | Uso diário por 80% dos pilotos |
| 5. Vertical | 9 a 12 | Renovação de frota, radar de licitações, TCO no prep, sync CIMBB de volta | Atividades no CIMBB lançadas sem digitação |
| 6. Escala | 12+ | Todas as lojas, cadências com autoaprovação, previsão de vendas | Metas de KPI abaixo |

---

## 8) KPIs e fórmulas

| KPI | Fórmula | Meta em 90 dias |
|---|---|---|
| Taxa de captura | eventos registrados automaticamente ÷ total de interações | ≥ 85% |
| Tempo de digitação | horas/semana do vendedor no CRM (pesquisa + log) | −70% |
| Velocidade do funil | dias médios do primeiro contato ao faturamento | −15% |
| Deals reativados | oportunidades paradas > 21 dias que voltam a andar ÷ total paradas | ≥ 25% |
| Aceite de rascunho | rascunhos aprovados ÷ gerados | ≥ 60% |
| Conversão | propostas ganhas ÷ propostas emitidas | +3 p.p. |
| Custo de IA por vendedor | gasto LLM + transcrição ÷ vendedores ativos | ≤ R$ 350/mês |
| ROI | (margem bruta incremental − custo total do sistema) ÷ custo total | > 5x no ano 1 |

Referência de impacto: com ticket médio de R$ 800 mil por caminhão e margem de 6%, **um caminhão a mais por mês** gera cerca de R$ 48 mil de margem, o que paga o sistema cerca de 10 vezes.

---

## 9) Checklist de arranque

- [ ] Aprovar orçamento e piloto (1 loja, 3 vendedores)
- [ ] Números corporativos de WhatsApp por vendedor e conta Meta Business verificada
- [ ] Política de uso e termo LGPD assinados pelos vendedores
- [ ] Upgrade do VPS (8 GB RAM) e chave de API do LLM em segredo do ambiente
- [ ] Export das planilhas e do CIMBB para carga inicial
- [ ] Definir as 8 etapas do funil e os campos obrigatórios do núcleo
- [ ] Montar conjunto de 200 conversas reais anonimizadas para avaliar os agentes
- [ ] Escolher PABX/telefonia com API de gravação

## 10) Próximos passos

1. Validar este framework com a diretoria comercial (30 min).
2. Rodar a Fase 0 no repositório (`server/`): migrations de `eventos` e núcleo, pgvector e worker.
3. Abrir o piloto de WhatsApp com 1 vendedor em 2 semanas.

## 11) Riscos e mitigação

| Risco | Impacto | Mitigação |
|---|---|---|
| Vendedor não adota | Alto | Começar pelo que poupa trabalho (prep e resumo automáticos), nada de campo obrigatório novo |
| Alucinação do agente | Alto | Citação obrigatória da fonte, humano aprova escrita, avaliação contínua no Langfuse |
| LGPD e dados pessoais | Alto | Base legal documentada, retenção definida, acesso por papel, dados no Brasil |
| Mudança de regra da API do WhatsApp | Médio | Usar só API oficial, camada de canal isolada |
| Custo de LLM fora de controle | Médio | Roteamento de modelo, cache, orçamento por agente com alerta |
| Dependência de uma pessoa no time técnico | Médio | Documentação no repositório, testes automatizados, deploy por script |

---

## Fontes

- [Lightfield: home](https://lightfield.com/) · [Book a Demo](https://lightfield.app/book-demo) · [Migration](https://lightfield.app/migration) · [Agentic data import](https://lightfield.app/blog/agentic-data-import-in-lightfield) · [Getting started](https://support.lightfield.app/articles/5111978357-getting-started-with-lightfield) · [Pricing (support)](https://support.lightfield.app/articles/9815515424-how-lightfield-s-pricing-works) · [Trust Center](https://trust.lightfield.app/) · [HubSpot vs Lightfield](https://lightfield.com/alternatives/hubspot)
- [SaaStr: AI App of the Week](https://www.saastr.com/saastr-ai-app-of-the-week-lightfield-the-ai-native-crm-that-killed-tomes-25-million-users-to-build-something-better/) · [SaaStr: demo ao vivo do CEO](https://www.saastr.com/watching-an-ai-native-crm-run-the-full-gtm-loop-live-lightfield-ceo-keith-peiris-demos-a-stalled-deal-an-automation-and-ten-new-prospects/) · [SaaStr: CRM montado no palco](https://www.saastr.com/lightfield-just-assembled-a-working-crm-live-on-stage-then-unstuck-a-stalled-deal-in-3-minutes/)
- YouTube: [Lightfield Demo](https://www.youtube.com/watch?v=2dBrqwp1tK4) · [Platform overview](https://www.youtube.com/watch?v=tU3GnxiDfdU) · [Zero to One](https://www.youtube.com/watch?v=Idmapqa9vYk) · [Review de terceiro](https://www.youtube.com/watch?v=iIfRnNI3APc)
- Reviews: [Carly](https://www.usecarly.com/blog/lightfield-crm/) · [Fluid CRM](https://fluidcrm.io/blog/lightfield-crm/) · [Ahoy pricing index](https://ahoy.ai/ai-native-crm/pricing-index/lightfield/) · [MakerStack](https://makerstack.co/reviews/lightfield-review/) · [AI Agent Index](https://theaiagentindex.com/agents/lightfield)
