# Tecar Sales Intelligence — MVP operacional frontend-only

**Data:** 2 de agosto de 2026  
**Status:** design aprovado em conversa; aguardando revisão final do documento  
**Escopo:** MVP operacional parcial (opção B)

## 1. Objetivo

Criar uma aplicação web local-first para transformar a planilha de emplacamentos da Tecar e a carteira de grandes frotas de Matheus em uma ferramenta de inteligência comercial. O MVP deve ler o Excel real no navegador, consolidar clientes, calcular market share e prioridade, exibir clientes em um mapa, recomendar linhas Mercedes-Benz e manter dados de CRM no IndexedDB.

O MVP não terá backend. O arquivo Excel selecionado pelo usuário permanecerá inalterado. A base processada e os registros comerciais serão locais ao dispositivo.

## 2. Evidências da base inicial

A análise da aba `Export` do arquivo `EMPLACAMENTOS 01.08.2021 Á 30.07.xlsx` encontrou:

- 22.506 linhas recebidas e 22.504 emplacamentos válidos;
- período de 2 de agosto de 2021 a 23 de julho de 2026;
- 22.504 chassis e placas únicos, sem duplicidades detectadas nesses campos;
- 3.976 CNPJs completos e 3.762 raízes de CNPJ;
- 3.981 nomes empresariais originais e 3.905 nomes normalizados;
- 12 marcas e market share Mercedes-Benz geral de 16,9%;
- 15.471 emplacamentos em GO, com 16,7% Mercedes-Benz;
- 2.972 emplacamentos no DF, com 31,1% Mercedes-Benz;
- 1.508 emplacamentos em TO, com 2,3% Mercedes-Benz;
- share Mercedes-Benz de 11,2% em rodoviário, 18,3% em distribuição e 34,2% em fora de estrada;
- endereço, cidade, UF e CEP praticamente completos, mas nenhuma coordenada geográfica;
- 20.287 registros sem email e 1.479 sem telefone principal, portanto esses campos não podem ser tratados como contatos comerciais validados.

A carteira recebida possui 74 linhas e 72 nomes únicos. A comparação inicial identificou 63 correspondências diretas por nome normalizado, uma candidata provável e oito casos que precisam de revisão manual. As correspondências seguras representam 1.191 emplacamentos, dos quais 49 são Mercedes-Benz, um share de 4,1%.

Oportunidades evidentes incluem Transmasut (325 emplacamentos, nenhum Mercedes-Benz), Paganini (81, nenhum Mercedes-Benz), Mahnic Operadora (62, dois Mercedes-Benz) e Margil (62, nove Mercedes-Benz).

## 3. Escopo do MVP

### Incluído

- importar a planilha XLSX real no navegador;
- validar estrutura e qualidade mínima;
- processar a planilha em Web Worker;
- normalizar nomes, CNPJ, marca, modelo, datas e endereços;
- consolidar empresas pela raiz do CNPJ;
- relacionar a carteira de Matheus com revisão manual de casos incertos;
- calcular market share, segmentação e scores;
- exibir dashboard, mapa, carteira e Cliente 360;
- recomendar uma linha Mercedes-Benz com evidências;
- cadastrar contatos, interações, tarefas, oportunidades, observações e próximas ações;
- persistir a base de trabalho e o CRM no IndexedDB;
- salvar tema, filtros e preferências não sensíveis;
- oferecer temas claro e escuro;
- funcionar sem backend.

### Fora do escopo

- geração do Excel oficial versionado;
- importação incremental mensal com comparação antes/depois;
- migrações completas do schema oficial de 20 abas;
- autenticação corporativa;
- sincronização entre dispositivos;
- edição simultânea;
- backend, API privada ou banco de dados em servidor;
- envio automático de WhatsApp;
- sobrescrita do Excel de origem.

## 4. Arquitetura

### Stack

- Vue 3;
- TypeScript;
- Vite;
- Pinia para estado da interface;
- SheetJS para leitura de XLSX;
- Web Worker para importação e cálculos pesados;
- IndexedDB com Dexie;
- Google Maps JavaScript API e Geocoding API;
- Apache ECharts;
- Vitest para regras unitárias;
- Playwright para fluxos críticos, se estiver disponível no ambiente;
- Salesforce Lightning Design System como linguagem de componentes, espaçamento, estados, acessibilidade e tokens visuais.

### Fluxo de dados

```text
Excel selecionado
  -> validação de estrutura
  -> Web Worker de leitura e normalização
  -> consolidação por CNPJ raiz
  -> motor de regras e indicadores
  -> confirmação do usuário
  -> IndexedDB
  -> Dashboard / Mapa / Carteira / Cliente 360 / CRM
```

A nova importação somente substitui a base analítica local após validação e confirmação. Entidades de CRM são relacionadas por IDs estáveis e preservadas quando a base analítica é atualizada.

### Limites de módulos

- `import`: seleção, leitura, progresso, cancelamento e diagnóstico do arquivo;
- `normalization`: funções puras de nomes, CNPJ, marcas, modelos, datas e endereços;
- `commercial-rules`: consolidação, share, segmentação, score, eventos e recomendações;
- `repositories`: interfaces de leitura/gravação independentes da interface;
- `storage`: implementação IndexedDB/Dexie;
- `maps`: geocodificação, cache de coordenadas e marcadores;
- `crm`: contatos, interações, tarefas e oportunidades;
- `analytics`: seletores e agregações consumidos pelas telas;
- `ui`: componentes Lightning, navegação, temas e acessibilidade.

Componentes Vue não conterão regras comerciais críticas.

## 5. Modelo local

O IndexedDB conterá, no mínimo:

- `imports`: metadados, arquivo, período, status, totais e diagnósticos;
- `clients`: empresa consolidada por raiz do CNPJ;
- `establishments`: matrizes e filiais;
- `registrations`: emplacamentos normalizados;
- `portfolioMatches`: nome recebido, cliente correspondente, confiança e validação manual;
- `geocodes`: endereço normalizado, latitude, longitude, precisão, data e status;
- `contacts`;
- `interactions`;
- `tasks`;
- `opportunities`;
- `notes`;
- `settings` apenas para preferências não sensíveis.

IDs serão UUIDs. Números de linha do Excel não serão IDs permanentes.

## 6. Correspondência e consolidação

- CNPJ válido e sua raiz são a chave primária de consolidação;
- nomes normalizados apoiam a vinculação da carteira;
- correspondências exatas e inequivocamente normalizadas podem ser automáticas;
- correspondências aproximadas são apenas sugestões;
- nenhuma sugestão aproximada é confirmada silenciosamente;
- os oito casos incertos da carga inicial aparecem em uma fila de revisão;
- a identidade exibida é a da matriz preferencial;
- filiais aparecem no Cliente 360, mas o mapa exibe um marcador por cliente consolidado.

## 7. Segmentação comercial

O período padrão é a janela completa carregada, com filtros de data disponíveis.

- **Conquistar:** nenhum emplacamento Mercedes-Benz no período filtrado;
- **Explorar:** possui Mercedes-Benz, mas a marca não é líder isolada;
- **Manter:** Mercedes-Benz é a marca líder isolada;
- empate entre Mercedes-Benz e qualquer concorrente resulta em **Explorar**.

A classificação sempre mostra contagens, share e marca líder que justificam o resultado.

## 8. Scoring

O score geral varia de 0 a 100 e é composto por:

- 40% potencial: volume e frequência de compras;
- 30% espaço competitivo: participação das outras marcas;
- 20% momento de compra: recência e padrão entre eventos;
- 10% aderência: compatibilidade entre aplicação atual e linhas Mercedes-Benz.

Os componentes são normalizados e exibidos separadamente. A ordenação de prioridade pode ser aplicada dentro de Conquistar, Explorar ou Manter para evitar comparações distorcidas entre objetivos diferentes.

O score não representa probabilidade estatística de fechamento; é uma regra comercial versionada e explicável.

## 9. Recomendação Mercedes-Benz

A regra considera segmento, subsegmento, tração, potência, motorização, modelos mais comprados e aplicação econômica.

- Accelo: operações leves e distribuição urbana;
- Atego: distribuição e semipesados;
- Axor: rodoviário e aplicações robustas intermediárias;
- Actros: pesados rodoviários e longa distância;
- Arocs: fora de estrada, construção e aplicações severas.

A recomendação é indicativa. A tela deve mostrar os fatores usados e um link para a página oficial do modelo/linha quando disponível.

## 10. Mapa e geocodificação

O mapa utiliza Google Maps JavaScript API e Geocoding API. Cada cliente consolidado possui um marcador baseado no endereço da matriz.

- a chave não será commitada nem embutida em arquivo distribuído;
- a configuração será local ao dispositivo;
- a interface orientará a restringir a chave por domínio e por API;
- resultados de geocodificação serão armazenados em cache local;
- a precisão retornada será registrada;
- falha de geocodificação gera estado de revisão, não coordenada inventada;
- mapa indisponível não bloqueia as outras telas.

Filtros do mapa: segmento comercial, segmento veicular, subsegmento, marca líder, score, cidade, UF, gestor e status de abordagem.

## 11. Experiência e telas

### Central de comando

Layout A aprovado: KPIs, mapa resumido e ranking de prioridades na mesma tela.

KPIs principais: clientes, emplacamentos, share Mercedes-Benz, Conquistar, Explorar, Manter, clientes em janela de compra, oportunidades e tarefas vencidas.

### Mapa

Mapa completo com um marcador por cliente, filtros, legenda, busca e painel lateral resumido. O clique abre o resumo e o acesso ao Cliente 360.

### Carteira Matheus

Tabela pesquisável com 72 nomes únicos iniciais, status de correspondência, volume, share, marca líder, segmento comercial, score, última compra, próxima ação e responsável.

### Cliente 360

Resumo, histórico de cinco anos, evolução, marcas, modelos, potência, eventos de compra, matriz/filiais, recomendação Mercedes-Benz, contatos, interações, tarefas, oportunidades e próxima ação.

### CRM local

Formulários e listas para contatos, interações, tarefas, oportunidades, observações, status e próxima ação. Toda alteração recebe data e ID estável.

### Importar Excel

Selecionar arquivo, validar estrutura, mostrar progresso, exibir qualidade e impacto, solicitar confirmação e somente então promover para base local ativa.

### Configurações

Chave do Google Maps, tema claro/escuro, preferências, informações da base carregada e limpeza controlada dos dados locais.

## 12. Linguagem visual

- Salesforce Lightning Design System como base;
- barra superior azul-marinho e menu lateral compacto;
- azul Lightning para ações e navegação;
- vermelho para Conquistar, âmbar para Explorar e verde para Manter;
- densidade adequada para análise comercial sem sacrificar legibilidade;
- marca Tecar e Mercedes-Benz aplicadas com discrição;
- temas claro e escuro com os mesmos significados semânticos;
- contraste, foco visível, rótulos e navegação por teclado.

## 13. Erros e segurança local

- arquivo inválido não substitui a base ativa;
- importação pode ser cancelada;
- a última base válida permanece disponível até confirmação;
- falhas mostram motivo e ação recomendada;
- dados sensíveis de CRM não ficam no LocalStorage;
- a aplicação avisa que os dados estão apenas no dispositivo;
- limpeza local exige confirmação explícita;
- a chave Google Maps deve ser restrita, pois chaves usadas no frontend são observáveis pelo navegador;
- nenhuma mensagem afirma que um arquivo foi salvo ou uma geocodificação foi concluída antes da confirmação real.

## 14. Testes

Testes unitários cobrem:

- normalização e validação de CNPJ;
- extração da raiz;
- normalização de nomes, marcas e modelos;
- consolidação de matriz e filiais;
- deduplicação;
- segmentação, inclusive empate como Explorar;
- componentes do score e score final;
- recomendação de produto e suas evidências;
- correspondência segura e fila de revisão.

Testes de integração cobrem:

- importação da planilha real com 22.504 registros válidos;
- persistência e restauração do IndexedDB;
- preservação de CRM em nova importação;
- agregações e filtros;
- falha de mapa sem bloquear o restante do sistema.

Fluxos de interface cobrem importação, dashboard, mapa, Cliente 360, cadastro de CRM, tema claro/escuro e estados de erro.

## 15. Critérios de aceite

O MVP estará aceito quando:

1. executar sem backend;
2. importar no navegador a planilha inicial real;
3. confirmar 22.504 registros válidos para a carga inicial;
4. manter a base original inalterada;
5. consolidar clientes por raiz do CNPJ;
6. permitir revisar correspondências incertas da carteira;
7. calcular market share e as três segmentações com evidências;
8. calcular score explicável;
9. exibir dashboard, mapa, carteira e Cliente 360;
10. recomendar linha Mercedes-Benz com justificativa;
11. persistir CRM local no IndexedDB;
12. preservar CRM ao reimportar dados analíticos;
13. alternar entre temas claro e escuro;
14. continuar funcional, exceto pelo mapa, quando a chave Google Maps estiver ausente ou inválida;
15. passar nos testes unitários e de integração definidos para o MVP;
16. funcionar nos fluxos principais em Chrome e Edge e ser responsivo para consulta em telas menores.

