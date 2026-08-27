# Estoque e Calculadora de Rentabilidade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar um front-end Tecar funcional, móvel e auditável que sincroniza estoque somente leitura do Google Sheets e calcula rentabilidade pelas regras do XLS.

**Architecture:** Um único HTML autocontido mantém a abertura por clique e facilita hospedagem estática. Dois scripts internos isolam o motor financeiro e o importador de estoque, permitindo testes com `node:test` por extração dos blocos de script; a camada de interface consome apenas as APIs públicas desses motores.

**Tech Stack:** HTML5, CSS responsivo, JavaScript ES2020 sem dependências, Web Storage, Fetch API, Intl, Node.js test runner.

---

## Estrutura de arquivos

- `tecar_estoque_rentabilidade.html`: aplicação final autocontida, contendo marcação, estilos, motores de domínio, estoque de contingência e controladores da interface.
- `tests/helpers/load-html-script.cjs`: extrai e executa um script identificado dentro do HTML final.
- `tests/rentabilidade.test.cjs`: casos de ouro e limites do motor financeiro.
- `tests/estoque.test.cjs`: parsing, validação, normalização e deduplicação do estoque.
- `tests/interface.test.cjs`: verificações estruturais de acessibilidade, responsividade e segurança.
- `package.json`: comandos locais de teste sem dependências de terceiros.
- `INSTRUCOES_TECAR_RENTABILIDADE.md`: publicação da planilha, configuração, execução e contingência.

### Task 1: Harness de testes e contrato do motor financeiro

**Files:**
- Create: `package.json`
- Create: `tests/helpers/load-html-script.cjs`
- Create: `tests/rentabilidade.test.cjs`
- Create: `tecar_estoque_rentabilidade.html`

- [ ] **Step 0: Criar o comando de testes sem dependências**

```json
{
  "name": "tecar-estoque-rentabilidade",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "test": "node --test tests/*.test.cjs"
  }
}
```

- [ ] **Step 1: Criar o carregador de scripts internos do HTML**

```js
// tests/helpers/load-html-script.cjs
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function loadHtmlScript(scriptId, extraContext = {}) {
  const htmlPath = path.resolve(__dirname, '..', '..', 'tecar_estoque_rentabilidade.html');
  const html = fs.readFileSync(htmlPath, 'utf8');
  const pattern = new RegExp(`<script[^>]+id=["']${scriptId}["'][^>]*>([\\s\\S]*?)<\\/script>`);
  const match = html.match(pattern);
  if (!match) throw new Error(`Script ${scriptId} não encontrado`);
  const context = { window: {}, console, Intl, URL, ...extraContext };
  vm.createContext(context);
  vm.runInContext(match[1], context, { filename: `${scriptId}.js` });
  return context.window;
}

module.exports = { loadHtmlScript };
```

- [ ] **Step 2: Criar os primeiros testes financeiros, antes da implementação**

```js
// tests/rentabilidade.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const { loadHtmlScript } = require('./helpers/load-html-script.cjs');

const { TecarProfitability } = loadHtmlScript('tecar-profitability-engine');

test('Anápolis reproduz o caso preenchido no XLS', () => {
  const result = TecarProfitability.calculate({
    scenario: 'anapolis_go', cost: 291970.47, ipi: 0, sale: 330000,
    freight: 3992.45, delivery: 0, licensing: 0, accessories: 0,
    other: 0, factoryBonus: 0, variableBonus: 0
  });
  assert.ok(Math.abs(result.margin - 17885.74) <= 0.02);
  assert.ok(Math.abs(result.marginPct - 5.42) <= 0.01);
  assert.ok(Math.abs(result.commissionTotal - 1335.31) <= 0.02);
});

test('venda zero não produz Infinity ou NaN', () => {
  const result = TecarProfitability.calculate({ scenario: 'aparecida_go', cost: 100000, sale: 0 });
  assert.equal(result.marginPct, null);
  assert.equal(result.commissionPct, null);
  assert.ok(Number.isFinite(result.margin));
});

test('comissão fora do fundo não fica negativa por padrão', () => {
  const result = TecarProfitability.calculate({ scenario: 'aparecida_go', cost: 300000, sale: 200000 });
  assert.equal(result.commissionOutside, 0);
});

test('combinação sem regra exige cenário conhecido', () => {
  assert.throws(
    () => TecarProfitability.resolveScenario('PALMAS', 'MATO GROSSO'),
    /cenário não mapeado/i
  );
});
```

- [ ] **Step 3: Executar e observar a falha esperada**

Run: `node --test tests/rentabilidade.test.cjs`

Expected: FAIL com `Script tecar-profitability-engine não encontrado`.

- [ ] **Step 4: Criar o esqueleto do HTML e o motor financeiro mínimo**

O HTML deve declarar um script clássico com `id="tecar-profitability-engine"` e publicar:

```js
window.TecarProfitability = Object.freeze({
  SCENARIOS,
  resolveScenario,
  calculate,
  formatMoney,
  formatPercent
});
```

Os cenários serão constantes imutáveis:

```js
const SCENARIOS = Object.freeze({
  aparecida_go: { icmsCredit: 7, icmsDebit: 9, fund: 3, general: 0, financial: 0, saleCharge: 2.2, reduction: 3.94, creditOut: 0, protege: 0, target: 3, commissionNf: 0.2, commissionFund: 2.5, delivery: 385.90 },
  anapolis_go: { icmsCredit: 7, icmsDebit: 9, fund: 3, general: 0, financial: 0.5, saleCharge: 1, reduction: 3.94, creditOut: 0, protege: 0, target: 3, commissionNf: 0.2, commissionFund: 2.5, delivery: 385.90 },
  mato_grosso_local: { icmsCredit: 7, icmsDebit: 12, fund: 3, general: 2.59, financial: 0, saleCharge: 2.2, reduction: 0, creditOut: 0, protege: 0, target: 3, commissionNf: 0.3, commissionFund: 2.5, delivery: 385.90 },
  tocantins_local: { icmsCredit: 7, icmsDebit: 8, fund: 3, general: 2.6, financial: 1, saleCharge: 1.2, reduction: 0, creditOut: 0, protege: 0, target: 3, commissionNf: 0.3, commissionFund: 2.5, delivery: 0 },
  aparecida_tocantins: { icmsCredit: 7, icmsDebit: 12, fund: 3, general: 0, financial: 0, saleCharge: 2.2, reduction: 0, creditOut: 4, protege: 15, target: 6, commissionNf: 0.2, commissionFund: 2.5, delivery: 0 },
  goias_mato_grosso: { icmsCredit: 7, icmsDebit: 12, fund: 3, general: 2.6, financial: 0, saleCharge: 3.5, reduction: 0, creditOut: 4, protege: 15, target: 6, commissionNf: 0.2, commissionFund: 2.5, delivery: 0 }
});
```

`calculate()` deve normalizar ausências para zero, rejeitar valores não finitos e devolver créditos, débitos, margem, meta, preço mínimo e comissões no mesmo objeto.

```js
function calculate(raw = {}) {
  const rules = SCENARIOS[raw.scenario];
  if (!rules) throw new Error('Cenário de rentabilidade inválido');
  const amount = (value) => {
    const parsed = Number(value ?? 0);
    if (!Number.isFinite(parsed)) throw new TypeError('Valor financeiro inválido');
    return parsed;
  };
  const rate = (key) => amount(raw.rates?.[key] ?? rules[key]) / 100;
  const cost = amount(raw.cost);
  const ipi = amount(raw.ipi);
  const sale = amount(raw.sale);
  const costWithIpi = cost + ipi;
  const freight = amount(raw.freight);
  const delivery = amount(raw.delivery);
  const licensing = amount(raw.licensing);
  const accessories = amount(raw.accessories);
  const other = amount(raw.other);
  const factoryBonus = amount(raw.factoryBonus);
  const variableBonus = amount(raw.variableBonus);
  const icmsCredit = costWithIpi * rate('icmsCredit');
  const fund = costWithIpi * rate('fund');
  const creditOut = sale * rate('creditOut');
  const totalCredits = sale + icmsCredit + fund + creditOut + factoryBonus + variableBonus;
  const icmsDebit = sale * rate('icmsDebit');
  const reduction = Math.max(0, costWithIpi - icmsCredit) * rate('reduction');
  const general = sale * rate('general');
  const financial = sale * rate('financial');
  const saleCharge = sale * rate('saleCharge');
  const protege = creditOut * rate('protege');
  const operational = freight + delivery + licensing + accessories + other;
  const totalDebits = costWithIpi + icmsDebit + reduction + general + financial + saleCharge + protege + operational;
  const margin = totalCredits - totalDebits;
  const marginPct = sale > 0 ? margin / sale * 100 : null;
  const withoutFund = margin - fund;
  const withoutFundPct = sale > 0 ? withoutFund / sale * 100 : null;
  const outsideBase = raw.allowNegativeCommission ? withoutFund : Math.max(0, withoutFund);
  const commissionFund = fund * rate('commissionFund');
  const commissionOutside = outsideBase * 0.05;
  const commissionInvoice = sale * rate('commissionNf');
  const commissionTotal = commissionFund + commissionOutside + commissionInvoice;
  const commissionPct = sale > 0 ? commissionTotal / sale * 100 : null;
  const variableCredit = 1 + rate('creditOut');
  const variableDebit = rate('icmsDebit') + rate('general') + rate('financial') + rate('saleCharge') + rate('creditOut') * rate('protege');
  const coefficient = variableCredit - variableDebit - rate('target');
  const fixedCredits = icmsCredit + fund + factoryBonus + variableBonus;
  const fixedDebits = costWithIpi + reduction + operational;
  const minimumSale = coefficient > 0 ? Math.max(0, (fixedDebits - fixedCredits) / coefficient) : null;
  return {
    cost, ipi, sale, costWithIpi, icmsCredit, fund, creditOut,
    factoryBonus, variableBonus, totalCredits, icmsDebit, reduction,
    general, financial, saleCharge, protege, operational, totalDebits,
    margin, marginPct, withoutFund, withoutFundPct,
    targetPct: rules.target, distanceToTarget: marginPct === null ? null : marginPct - rules.target,
    minimumSale, commissionFund, commissionOutside, commissionInvoice,
    commissionTotal, commissionPct
  };
}
```

- [ ] **Step 5: Executar os testes financeiros**

Run: `node --test tests/rentabilidade.test.cjs`

Expected: PASS nos quatro testes.

- [ ] **Step 6: Commit**

```bash
git add package.json tecar_estoque_rentabilidade.html tests/helpers/load-html-script.cjs tests/rentabilidade.test.cjs
git commit -m "feat: add audited profitability engine"
```

### Task 2: Importador e sincronização de estoque defensivos

**Files:**
- Modify: `tecar_estoque_rentabilidade.html`
- Create: `tests/estoque.test.cjs`

- [ ] **Step 1: Escrever testes de parsing e validação**

```js
// tests/estoque.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const { loadHtmlScript } = require('./helpers/load-html-script.cjs');
const { TecarStock } = loadHtmlScript('tecar-stock-engine');

const csv = [
  'Nº,Casa,Modelo,Variante,UP,Cor,Ano,NF,Pagamento,Faturamento fábrica,Chassi,Campanha,Margem 5%,Margem 10%,Permanência,Valor NF,ICMS,Frete,Fundo fixo,Fundo variável,Bônus,Despesa,Pneus,Cliente,Status,Casa venda,Data reserva,Dias reserva,Vencimento fábrica,Dias,Vencido',
  '1,APARECIDA,ACTROS 2653 S/36,9042T,UPI,BRANCO 9147,26/27,A PRODUZIR,,,1677545263,"R$ 900.000,00","R$ 932.500,00","R$ 980.000,00",FABRICA,"R$ 859.972,34","R$ 60.198,06","R$ 5.000,00",3%,"R$ 12.899,59","R$ 25.799,17",,,LIBERADO,LIBERADO,,,,0,0'
].join('\n');

test('converte moeda e percentual brasileiros', () => {
  assert.equal(TecarStock.parseMoney('R$ 859.972,34'), 859972.34);
  assert.equal(TecarStock.parseRate('3%'), 0.03);
});

test('mapeia CSV por cabeçalho, não só por posição', () => {
  const rows = TecarStock.parseCsv(csv);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].chassis, '1677545263');
  assert.equal(rows[0].sale5, 932500);
});

test('rejeita estrutura sem campos críticos', () => {
  assert.throws(() => TecarStock.parseCsv('Modelo,Cor\nACTROS,Branco'), /campos obrigatórios/i);
});

test('deduplica chassi preservando a última linha válida', () => {
  const row = TecarStock.parseCsv(csv)[0];
  const result = TecarStock.deduplicate([{ ...row, sale5: 1 }, { ...row, sale5: 2 }]);
  assert.equal(result.length, 1);
  assert.equal(result[0].sale5, 2);
});
```

- [ ] **Step 2: Executar e observar a falha**

Run: `node --test tests/estoque.test.cjs`

Expected: FAIL com `Script tecar-stock-engine não encontrado`.

- [ ] **Step 3: Implementar o motor de estoque**

O script `id="tecar-stock-engine"` deve expor:

```js
window.TecarStock = Object.freeze({
  REQUIRED_FIELDS,
  parseCsv,
  parseMoney,
  parseRate,
  parseExcelDate,
  deduplicate,
  validateRows,
  sanitizeSpreadsheetText
});
```

O parser deve:

- analisar aspas, vírgulas, quebras de linha e aspas duplicadas segundo CSV;
- normalizar cabeçalhos removendo acentos e espaços;
- limitar a entrada a 5 MB e 10.000 linhas;
- rejeitar carga sem casa, modelo, chassi, valor NF, preço de referência e status;
- descartar linhas vazias e preservar números como números;
- remover caracteres de controle dos textos;
- deduplicar por chassi.

O mapeamento deve ser explícito e auditável:

```js
const COLUMN_ALIASES = Object.freeze({
  number: ['n', 'nº', 'numero'], house: ['casa'], model: ['modelo'],
  variant: ['variante'], year: ['ano'], invoice: ['nf'], chassis: ['chassi'],
  campaign: ['campanha'], sale5: ['margem 5%', 'margem 5'],
  sale10: ['margem 10%', 'margem 10'], location: ['permanencia'],
  invoiceValue: ['valor nf'], icmsValue: ['icms'], freight: ['frete'],
  fixedFund: ['fundo fixo'], variableFund: ['fundo variavel'],
  factoryBonus: ['bonus'], expense: ['despesa'], client: ['cliente'],
  status: ['status'], saleHouse: ['casa venda'], daysInStock: ['dias'], overdueDays: ['vencido']
});

function sanitizeSpreadsheetText(value) {
  return String(value ?? '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').trim();
}

function parseMoney(value) {
  const text = sanitizeSpreadsheetText(value).replace(/R\$|\s/g, '');
  if (!text) return 0;
  const normalized = text.includes(',') ? text.replace(/\./g, '').replace(',', '.') : text;
  const parsed = Number(normalized.replace(/[^0-9.-]/g, ''));
  return Number.isFinite(parsed) ? parsed : 0;
}

function parseRate(value) {
  const parsed = parseMoney(value);
  return String(value ?? '').includes('%') ? parsed / 100 : parsed > 1 ? parsed / 100 : parsed;
}
```

- [ ] **Step 4: Implementar o coordenador de sincronização**

```js
async function syncStock({ url, timeoutMs = 12000, fetchImpl = fetch }) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl(url, { method: 'GET', cache: 'no-store', signal: controller.signal });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const text = await response.text();
    const rows = TecarStock.parseCsv(text);
    TecarStock.validateRows(rows);
    return rows;
  } finally {
    clearTimeout(timer);
  }
}
```

O aplicativo deve salvar no cache apenas após todo o pipeline passar.

- [ ] **Step 5: Executar todos os testes de domínio**

Run: `node --test tests/rentabilidade.test.cjs tests/estoque.test.cjs`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tecar_estoque_rentabilidade.html tests/estoque.test.cjs
git commit -m "feat: add defensive stock synchronization"
```

### Task 3: Interface móvel de estoque

**Files:**
- Modify: `tecar_estoque_rentabilidade.html`
- Create: `tests/interface.test.cjs`

- [ ] **Step 1: Escrever verificações estruturais da interface**

```js
// tests/interface.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('tecar_estoque_rentabilidade.html', 'utf8');

test('declara viewport e idioma', () => {
  assert.match(html, /<html[^>]+lang="pt-BR"/);
  assert.match(html, /name="viewport"[^>]+width=device-width/);
});

test('possui navegação e regiões de status acessíveis', () => {
  assert.match(html, /aria-label="Navegação principal"/);
  assert.match(html, /aria-live="polite"/);
  assert.match(html, /id="stock-view"/);
  assert.match(html, /id="calculator-view"/);
});

test('inclui proteção contra movimento excessivo e impressão', () => {
  assert.match(html, /prefers-reduced-motion/);
  assert.match(html, /@media print/);
});

test('não contém segredo ou operação de escrita remota', () => {
  assert.doesNotMatch(html, /AIza[0-9A-Za-z_-]{20,}/);
  assert.doesNotMatch(html, /method\s*:\s*['"](?:POST|PUT|PATCH|DELETE)/i);
});
```

- [ ] **Step 2: Executar e observar as falhas da interface ainda incompleta**

Run: `node --test tests/interface.test.cjs`

Expected: pelo menos um FAIL por estrutura ausente.

- [ ] **Step 3: Implementar o layout de estoque aprovado**

O HTML deve conter:

```html
<main id="stock-view" class="view is-active">
  <header class="app-header">...</header>
  <section class="stock-toolbar" aria-label="Filtros do estoque">...</section>
  <section class="stock-kpis" aria-label="Resumo do estoque">...</section>
  <section id="stock-results" aria-live="polite">...</section>
</main>

<nav class="mobile-nav" aria-label="Navegação principal">
  <button data-view="stock" aria-current="page">Estoque</button>
  <button data-view="calculator">Simulação</button>
</nav>
```

Direção visual: industrial refinado Mercedes-Benz, fundo grafite, superfícies em preto fosco, tipografia clara, acento azul técnico, estados verde/âmbar/vermelho e composição densa sem parecer planilha.

- [ ] **Step 4: Implementar renderização responsiva**

- Até 767 px: cartões, filtros em chips roláveis, painel de detalhe em folha inferior e navegação fixa.
- A partir de 768 px: tabela com cabeçalho fixo e painel lateral.
- Nenhum elemento deve exigir largura maior que 320 px.
- Botões e campos devem ter altura mínima de 44 px no modo toque.

- [ ] **Step 5: Implementar busca, filtros e seleção**

```js
function getFilteredStock(rows, filters) {
  const query = normalize(filters.query);
  return rows.filter((vehicle) => {
    const haystack = normalize([
      vehicle.model, vehicle.variant, vehicle.chassis, vehicle.invoice,
      vehicle.color, vehicle.client, vehicle.house, vehicle.location
    ].join(' '));
    return (!query || haystack.includes(query)) &&
      (!filters.house || vehicle.house === filters.house) &&
      (!filters.status || normalize(vehicle.status) === normalize(filters.status)) &&
      (!filters.model || vehicle.model === filters.model) &&
      (!filters.minimumAge || vehicle.daysInStock >= filters.minimumAge);
  });
}
```

- [ ] **Step 6: Executar testes**

Run: `node --test tests/*.test.cjs`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add tecar_estoque_rentabilidade.html tests/interface.test.cjs
git commit -m "feat: build responsive stock experience"
```

### Task 4: Interface e integração da calculadora

**Files:**
- Modify: `tecar_estoque_rentabilidade.html`
- Modify: `tests/rentabilidade.test.cjs`
- Modify: `tests/interface.test.cjs`

- [ ] **Step 1: Adicionar teste de preenchimento vindo do estoque**

```js
test('converte veículo do estoque em entradas da simulação', () => {
  const input = TecarProfitability.fromStock({
    house: 'APARECIDA', model: 'ACTROS 2653 S/36', chassis: '1677545263',
    invoiceValue: 859972.34, sale5: 932500, freight: 5000,
    fixedFund: 0.03, variableFund: 12899.59, factoryBonus: 25799.17,
    expense: 'Baú de alumínio · custo informado R$ 39.000,00'
  }, 'GOIÁS');
  assert.equal(input.scenario, 'aparecida_go');
  assert.equal(input.sale, 932500);
  assert.equal(input.accessories, 39000);
});
```

- [ ] **Step 2: Executar e observar a falha**

Run: `node --test tests/rentabilidade.test.cjs`

Expected: FAIL com `TecarProfitability.fromStock is not a function`.

- [ ] **Step 3: Implementar `fromStock()` e o formulário**

```html
<main id="calculator-view" class="view" hidden>
  <form id="profitability-form" novalidate>
    <section class="vehicle-reference">...</section>
    <section class="deal-fields">...</section>
    <details class="advanced-rules"><summary>Regras auditadas</summary>...</details>
  </form>
  <aside class="profitability-result" aria-live="polite">...</aside>
</main>
```

Campos monetários usarão `inputmode="decimal"`; origem será somente leitura; destino será obrigatório; valores do estoque terão botão individual de restauração.

- [ ] **Step 4: Implementar atualização instantânea e memória de cálculo**

Cada alteração válida chama `TecarProfitability.calculate()`. A memória deve exibir a soma explícita de:

```js
const breakdown = {
  credits: [sale, icmsCredit, fund, creditOut, factoryBonus, variableBonus],
  debits: [costWithIpi, icmsDebit, reduction, general, financial, saleCharge, protege, operational],
  commission: [commissionFund, commissionOutside, commissionInvoice]
};
```

- [ ] **Step 5: Implementar semáforo de margem**

- Margem abaixo de zero: crítica.
- Margem entre zero e meta: atenção.
- Margem igual ou acima da meta: saudável.
- Venda zero: incompleta, sem percentual inventado.

- [ ] **Step 6: Executar testes**

Run: `node --test tests/*.test.cjs`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add tecar_estoque_rentabilidade.html tests/rentabilidade.test.cjs tests/interface.test.cjs
git commit -m "feat: integrate stock profitability workflow"
```

### Task 5: Persistência, exportação e estados de contingência

**Files:**
- Modify: `tecar_estoque_rentabilidade.html`
- Modify: `tests/interface.test.cjs`
- Create: `INSTRUCOES_TECAR_RENTABILIDADE.md`

- [ ] **Step 1: Adicionar testes estáticos dos controles operacionais**

```js
test('expõe sincronização, cache e ações da simulação', () => {
  for (const id of ['sync-stock', 'sync-status', 'save-simulation', 'copy-summary', 'print-summary']) {
    assert.match(html, new RegExp(`id=["']${id}["']`));
  }
  assert.match(html, /localStorage/);
});
```

- [ ] **Step 2: Implementar cache versionado**

```js
const CACHE_KEYS = Object.freeze({
  stock: 'tecar_stock_cache_v1',
  simulation: 'tecar_profitability_simulation_v1',
  settings: 'tecar_profitability_settings_v1'
});

function saveStockCache(rows, source) {
  localStorage.setItem(CACHE_KEYS.stock, JSON.stringify({
    version: 1,
    savedAt: new Date().toISOString(),
    source,
    rows
  }));
}
```

- [ ] **Step 3: Implementar estados remotos sem perda de dados**

Na abertura, renderizar cache/fallback antes do `fetch`. Em erro, manter as linhas renderizadas e atualizar somente o componente `sync-status`. Em esquema incompatível, informar que a carga foi rejeitada.

- [ ] **Step 4: Implementar copiar e imprimir**

O resumo copiado deve conter veículo, chassi, origem, destino, cenário, venda, margem, percentual, preço mínimo, comissão e data. A impressão deve ocultar busca, filtros e navegação, mostrando a memória de cálculo e aviso `Simulação comercial — confirmar regras fiscais vigentes`.

- [ ] **Step 5: Documentar uso e publicação somente leitura**

`INSTRUCOES_TECAR_RENTABILIDADE.md` deve explicar:

1. Abrir a planilha Google.
2. Usar `Arquivo → Compartilhar → Publicar na Web`.
3. Publicar somente a aba de estoque como CSV.
4. Manter republicação automática habilitada.
5. Colar a URL publicada no campo administrativo do aplicativo ou na constante `REMOTE_STOCK_URL`.
6. Abrir `tecar_estoque_rentabilidade.html` ou hospedá-lo em serviço estático HTTPS.
7. Confirmar o selo `Atualizado` antes de usar dados recém-alterados.

- [ ] **Step 6: Executar testes**

Run: `node --test tests/*.test.cjs`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add tecar_estoque_rentabilidade.html tests/interface.test.cjs INSTRUCOES_TECAR_RENTABILIDADE.md
git commit -m "feat: add offline resilience and simulation export"
```

### Task 6: Verificação funcional e visual

**Files:**
- Modify: `tecar_estoque_rentabilidade.html` only if verification exposes a defect
- Modify: `tests/*.test.cjs` only when a verified edge case needs a regression test

- [ ] **Step 1: Executar a suíte completa**

Run: `node --test tests/*.test.cjs`

Expected: todos os testes PASS, nenhum teste ignorado.

- [ ] **Step 2: Executar inspeções estáticas de segurança**

Run: `rg -n "innerHTML\s*=.*(?:client|model|chassis|expense)|eval\(|new Function|AIza|method\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)" tecar_estoque_rentabilidade.html`

Expected: nenhuma ocorrência insegura; `innerHTML` permitido somente em templates que passam valores por `escapeHtml()`.

- [ ] **Step 3: Servir localmente para teste**

Run: `python -m http.server 4173`

Expected: servidor disponível em `http://127.0.0.1:4173/tecar_estoque_rentabilidade.html`.

- [ ] **Step 4: Testar os breakpoints**

Validar em 320 × 568, 360 × 800, 390 × 844, 768 × 1024, 1024 × 768 e 1440 × 900:

- ausência de rolagem horizontal;
- cartões/tabela legíveis;
- filtros operantes;
- painel de detalhe acessível;
- navegação inferior sem cobrir ações;
- formulário com teclado decimal no celular;
- resultado e memória de cálculo sem corte.

- [ ] **Step 5: Executar caso completo**

1. Selecionar um ACTROS liberado de Aparecida.
2. Abrir simulação com destino Goiás.
3. Confirmar preenchimento de NF, venda 5%, frete, bônus e fundo.
4. Trocar preço para campanha e depois restaurar margem 5%.
5. Alterar destino para Tocantins e confirmar cenário/meta de 6%.
6. Copiar resumo e verificar conteúdo.
7. Recarregar e verificar persistência.
8. Desligar a rede e confirmar uso do cache.

- [ ] **Step 6: Conferir impressão**

Expected: uma composição A4 com identificação, entradas, resultado, memória e aviso; sem navegação ou filtros.

- [ ] **Step 7: Commit de correções verificadas, se houver**

```bash
git add tecar_estoque_rentabilidade.html tests
git commit -m "fix: harden mobile profitability experience"
```

- [ ] **Step 8: Verificar o estado final do repositório**

Run: `git status --short`

Expected: somente arquivos preexistentes do usuário permanecem não rastreados; nenhum arquivo da entrega fica pendente.
