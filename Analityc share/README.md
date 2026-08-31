# Market Intelligence Command Center

Painel de inteligência de mercado para caminhões pesados (rede Mercedes-Benz / Tecar),
construído como um único arquivo HTML autocontido.

## Arquivos

| Arquivo | Papel |
|---|---|
| `../Analitycmbb.html` | Aplicação completa, na **raiz do repositório** (Vue 3 + Chart.js + amCharts 5 + Leaflet + Cytoscape) |
| `EMPLACAMENTO - ANÁLISE PERFIL CLIENTES.xlsx` | Matriz fonte — 2.357 emplacamentos, jan–ago/2026 |
| `capa.jpg` | Imagem de fundo da tela de acesso |

O HTML fica na raiz para produzir uma URL curta no GitHub Pages; os dados continuam
nesta pasta e são referenciados por caminho relativo (`Analityc share/…`).

## Como rodar

O arquivo abre direto no navegador, mas para que a planilha seja lida como **fonte viva**
é preciso servi-lo por HTTP a partir da **raiz do repositório** (o `fetch` do XLSX não
funciona sob `file://`):

```bash
python -m http.server 8755
```

Depois abra <http://localhost:8755/Analitycmbb.html>.

## Acesso

O painel abre numa tela de login (`Tecarmbb` / `Actros2653`), lembrada por sessão do
navegador. **Isso não é um controle de segurança**: a verificação roda no navegador e tanto
as credenciais quanto os dados estão no código-fonte da página. Serve para organizar o
acesso e evitar navegação casual, não para proteger a informação.

No carregamento o painel tenta, nesta ordem:

1. ler o XLSX ao lado do HTML e ativá-lo se o hash mudou;
2. restaurar o último snapshot importado do IndexedDB;
3. cair no snapshot embutido no próprio HTML.

Para atualizar os dados, basta **salvar a planilha por cima e recarregar a página** —
ou usar a tela *Importações* para subir outra matriz (validação de schema + gate de
qualidade ≥ 75/100 antes de substituir a matriz ativa).

A matriz importada pela tela fica **fixada** (`micc_pinned_hash` em localStorage) e tem
precedência sobre a planilha do servidor, inclusive ao recarregar. A tela *Importações*
mostra qual fonte está ativa e permite voltar para a planilha do servidor.

### Correção de data no import

Planilha salva com locale en-US converte as datas ambíguas (dia ≤ 12) em data real lendo
`dd/mm` como `mm/dd`, e deixa as demais como texto. O SheetJS então entrega as convertidas com
ano de dois dígitos, que o parser rejeitava — os registros entravam **sem data**. Na base
2020–2026 isso atingia 6.676 de 26.092 (25,6%).

O import detecta a mistura dos dois formatos, relê as convertidas como `dd/mm/aa` (o primeiro
campo exibido é o dia verdadeiro) e normaliza tudo para ISO. Só aplica quando nenhum valor
recuperado fica inválido; caso contrário não altera nada. O resultado é declarado na tela
*Data Quality*, com a contagem exata. **Para eliminar a causa**, exporte a coluna de data como
texto ou no formato ISO `aaaa-mm-dd`.

## Telas

**Decisão** — Control Tower · Mercado · Território · Geointeligência
**Cliente** — Classificação MBB · Clientes · Customer 360 · Recorrência · Sazonalidade · Oportunidades
**Comercial** — Participação Comercial · Responsáveis
**Diagnóstico** — Concorrência · Licitações · Graph Explorer · Sensibilidade · Data Quality
**Governança** — Importações · Regras

## Classificação MBB — R1 a W2

As faixas oficiais Mercedes-Benz **não foram alteradas**. A nomenclatura analítica foi
expandida em duas subclasses por classe oficial, com ordem de exibição fixa `R1 → W2`
(nunca alfabética):

| Classe oficial | Classe analítica | Código | Faixa |
|---|---|---|---:|
| Retail | Retail Base | `R1` | 1–2 |
| Retail | Retail Plus | `R2` | 3–4 |
| Middle | Middle Core | `M1` | 5–14 |
| Middle | Middle Large | `M2` | 15–49 |
| Wholesale | Wholesale Key | `W1` | 50–299 |
| Wholesale | Wholesale Strategic | `W2` | 300+ |

**Métrica de classificação:** volume *anualizado* de emplacamentos do cliente **na janela de
classificação** — exatamente a mesma métrica que o sistema já usava para o perfil comercial.
Nenhuma métrica foi substituída: emplacamentos, frota, compras históricas e YTD seguem como
métricas próprias e independentes.

**Critério de classificação** (`rules.classMode`, padrão `ativos`): o denominador de tempo é
explícito e selecionável em *Regras*, porque numa base multianual a escolha muda tudo.

| Critério | Como lê o volume | Distribuição na base 2020–2026 |
|---|---|---|
| `ativos` (padrão) | total ÷ anos em que o cliente comprou | R1 3.293 · R2 264 · M1 156 · M2 41 · W1 9 · **NA 0** |
| `pico` | maior volume num único ano | R1 3.038 · R2 390 · M1 251 · M2 64 · W1 18 · W2 2 |
| `cobertura` | total ÷ anos da base inteira | **89% em NA** — não usar em base multianual |
| `janela` | volume dos últimos 12 meses | 80% em NA (os inativos no período) |

Dividir pela cobertura inteira dilui o porte: em 6,64 anos um cliente com 6 caminhões resulta
em 0,90 — abaixo de 1, portanto sem classificação. Por isso o padrão é a **média por ano
ativo**, que é a leitura operacional de “volume médio por ano”: mede a intensidade de compra
quando o cliente compra. O balde agregado de PF não identificada nunca é classificado — é um
rótulo com muitos clientes reais, não uma conta.

## Migração de classe

A classe é recalculada **ano a ano**, pelo volume de cada ano-calendário, e comparada entre
dois períodos. Responde não “qual o porte do cliente” mas **como o porte mudou**: quem subiu,
quem desceu, quem manteve, quem entrou e quem parou de comprar. Inclui matriz de transição
(diagonal = manteve, acima = subiu, abaixo = desceu) e a lista das contas ordenada pela maior
variação de volume.

O padrão compara os dois últimos anos **completos** — o ano corrente costuma estar parcial e
compará-lo faria a carteira inteira aparentar queda.

## Tração

Quando a matriz traz a coluna de tração, ela vira dimensão de análise e filtro global: share
por tração nas duas leituras, líder de cada configuração e whitespace. Tração é proxy direto
de aplicação — 6X4 e 8X4 concentram fora de estrada e carga pesada, 4X2 e 6X2 concentram
rodoviário e distribuição.

A faixa é aplicada como intervalo semiaberto `[min, max+1)`: para qualquer valor inteiro o
resultado é idêntico à tabela oficial. Volume ausente, zero, negativo ou não numérico → `NA`.

A classe **não é persistida** — é recalculada em runtime a partir da matriz, portanto
snapshots antigos continuam válidos sem migração nem regravação. `classifyCustomerRange()`
é a fonte única da verdade; o perfil comercial (`VAREJO` / `REGIONAL` / `FROTISTA` /
`SETOR PÚBLICO` / …) continua existindo como dimensão separada e complementar.

## Share of Trucks × Share of Clients

Toda participação no painel declara o denominador. Um seletor global alterna as duas
perspectivas em todas as telas onde participação faz sentido:

```
Share of Trucks  = emplacamentos da marca ÷ emplacamentos do universo filtrado
Share of Clients = clientes únicos que compraram a marca
                   ÷ clientes únicos compradores do universo filtrado
```

**Share of Clients mede penetração e não é aditivo.** Um cliente que comprou Mercedes-Benz,
Volvo e Scania no mesmo período é contado nas três marcas, então a soma entre marcas pode
ultrapassar 100% — isso não é erro. Na base atual a soma é ≈ 110%; o excesso sobre 100% é a
medida de clientes multimarca.

A identidade do cliente usa o mesmo Entity Resolution do resto do sistema
(`CNPJ raiz → CNPJ completo → CPF → chave tratada`). Emplacamento nunca é contado como
cliente e filiais da mesma raiz são um único cliente. O balde agregado de PF não
identificada representa muitos clientes reais sob um único rótulo: permanece integralmente
no denominador de *Trucks* e é excluído da contagem de clientes únicos, para não inflar
artificialmente nenhuma penetração.

Métricas derivadas e vizinhas, mantidas semanticamente separadas:

- **Depth Index** = Share of Trucks ÷ Share of Clients. `> 1` volume proporcionalmente maior
  que a presença em clientes; `≈ 1` equilíbrio; `< 1` presença ampla com baixo volume
  relativo. Nunca lido isoladamente.
- **Clientes exclusivos** = clientes que compraram somente aquela marca ÷ clientes
  compradores. É métrica distinta e não substitui Share of Clients.
- **Share of Wallet** (Customer 360) = unidades MB do cliente ÷ unidades totais daquele
  cliente. Mede profundidade *dentro* de uma conta, não penetração no mercado.
- **Whitespace Clients** = clientes compradores em que a Mercedes-Benz não tem participação,
  complementando o Whitespace Volume.

A tela *Data Quality* executa uma suíte determinística a cada renderização (43 asserções
sobre o universo filtrado) cobrindo as fronteiras exatas das faixas, valores inválidos,
identidade do cliente e consistência dos dois denominadores.

## Camada comercial — Participação

Segunda planilha (`enriquecimento_clientes_Prime.xlsx`, 3.299 linhas) cruzada por **CHASSI**
em **LEFT JOIN**. Ela **não é fonte de mercado**: nunca altera marca, modelo, data, cliente,
território, classe MBB nem o denominador de Share of Trucks / Share of Clients. Emplacamentos
continua sendo a *source of truth*.

Auditoria do cruzamento: **98,2% de match** (2.314 de 2.357 emplacamentos), **zero** chassi
duplicado, **zero** conflito de marca ou modelo. As 985 linhas órfãs da Participação são Van
(699) e Ônibus (274) — não pertencem ao mercado de caminhões — mais 12 caminhões fora da base.
Emplacamento sem correspondência é classificado como **Não informado**, nunca como “Sem
participação”: tratá-lo como ausência de participação distorceria cobertura e captura.

### Três dimensões que não se confundem

```
Market Share            quanto do mercado comprou Mercedes-Benz
Commercial Coverage     quanto desse mercado foi trabalhado comercialmente
Unit Capture Rate       quando participamos, quanto capturamos
```

```
Commercial Coverage   = (Venda + Com participação) ÷ (Venda + Com + Sem)
Coverage Completeness = unidades com status conhecido ÷ total de emplacamentos
Unit Capture Rate     = Venda ÷ (Venda + Com participação)
Client Coverage       = clientes com Venda ou Com participação ÷ clientes com status conhecido
```

“Não informado” fica **fora** do denominador de cobertura e é reportado à parte, para que baixa
qualidade da planilha não se disfarce de baixa cobertura.

**Unidade não é oportunidade.** Um chassi é uma unidade, não necessariamente uma negociação
independente — um cliente pode ter comprado 50 caminhões numa única negociação. Por isso a
métrica se chama *Unit Capture Rate* e nunca “taxa de conversão”, e as perdas são lidas como
“50 unidades associadas ao motivo Preço”, nunca “50 negociações perdidas”.

**Motivos têm duas leituras obrigatórias**: unidades e clientes únicos. “744 unidades / 155
clientes” distingue perda pulverizada de perda concentrada numa conta grande. A taxonomia é
normalizada e o texto original do motivo é sempre preservado.

**O campo `Tipo`** aparece exclusivamente nas unidades “Sem participação” (727 de 727): ele
qualifica *por que não participamos* (Dentro da Carteira Com/Sem Visita, Fora da Carteira), e
não o tipo de cliente. **`Invasão`** tem 0,8% de preenchimento — preservado como RAW e marcado
como não mapeado, sem interpretação.

### Market Share ≠ Participação Comercial

Das 409 Mercedes-Benz emplacadas, **374 (91,4%) são venda nossa** e 35 chegaram ao mercado por
outro canal da marca. Nenhuma linha “Venda” é de outra marca. O Share of Trucks segue contando
as 409, porque mede o produto no mercado; a captura conta as 374, porque mede a atuação
comercial. É a evidência direta de que as duas dimensões medem coisas diferentes.

### Responsável comercial

`Responsável` é o que a planilha declara — **não está comprovado** que corresponde a quem
fechou a venda. Um cliente pode ter mais de um responsável (6 de 710 casos), por isso as
métricas são por **unidade** e a contagem de clientes significa “clientes tocados”, não
carteira exclusiva; a soma de clientes por responsável pode superar o total da equipe.

A dimensão canônica resolve aliases de grafia (`Camila Cavaliere` = `Camila da Silva
Cavaliere`). Nomes são exibidos abreviados (primeiro nome + inicial). Não há ranking por
volume de venda: o gráfico Cobertura × Captura usa a **mediana da equipe** como corte, nunca
50% arbitrário, e considera apenas responsáveis com ao menos 10 unidades de status conhecido.

## Conceitos analíticos

- **Whitespace** = volume total observado − volume Mercedes-Benz. É o volume que a conta
  comprovadamente comprou de outras marcas.
- **Marca dominante** = marca com o maior número de veículos observados na entidade.
- **Spill-in** = emplacamento feito no território de um AOP por concessionário cuja base é
  outro AOP. Inferido por heurística (AOP modal do dealer), não por cadastro mestre —
  parametrizável na tela *Regras* e testável na tela *Sensibilidade*.
- **Opportunity Score** = soma ponderada e explicável de volume, whitespace, recorrência,
  janela de recompra, território e multimarca. O componente de crescimento pesa zero
  enquanto não houver histórico multianual.

## Geolocalização

A matriz atual **não possui CEP nem latitude/longitude**. A camada geográfica resolve cada
registro na melhor precisão disponível, sempre declarada:

`coordenada original` → `CEP geocodificado` → `centroide do município` → `centroide do AOP`

Hoje a granularidade efetiva é o **município** (116 municípios, centroides de sede derivados
do IBGE). O motor de CEP — normalização, cache em IndexedDB, provider plugável e fila com
pausar/cancelar — já está implementado e passa a operar sozinho assim que a matriz trouxer
uma coluna de CEP. Coordenadas derivadas de CEP ou centroide são **aproximadas**, nunca o
endereço exato do estabelecimento.

## Privacidade

O número do CNPJ é **pseudonimizado**: cada raiz real foi trocada por uma raiz sintética de
forma determinística, preservando o agrupamento de clientes (724 raízes), a distinção de
filiais e os dígitos verificadores válidos. O XLSX com os CNPJs reais e o mapa reverso ficam
fora do repositório, protegidos pelo `.gitignore`.

> **Atenção — a camada comercial reverte a pseudonimização.** A planilha de Participação traz
> o CNPJ real e, a pedido explícito, ele foi importado. Como o cruzamento é por chassi, isso
> permite reconstruir o mapa entre a raiz sintética e o CNPJ verdadeiro de toda a base de
> clientes. **Esta versão não deve ir para um repositório público**: torne o repositório
> privado ou gere uma variante sem a coluna `CNPJ_Participacao` antes de publicar.

Razão social, chassi, placa e o comportamento de compra por cliente **permanecem como no
original**. Como o nome da empresa identifica o cliente de forma mais direta que o CNPJ, a
pseudonimização do documento reduz pouco a exposição: em repositório público, este conteúdo
é informação comercial identificável e indexável.
