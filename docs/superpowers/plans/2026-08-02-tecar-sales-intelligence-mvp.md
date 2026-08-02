# Tecar Sales Intelligence MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um MVP Vue 3 frontend-only que importe a planilha real da Tecar, gere inteligência comercial explicável, exiba dashboard/mapa/Cliente 360 e persista CRM no IndexedDB.

**Architecture:** A aplicação separa domínio puro, importação em Web Worker, persistência Dexie e componentes Vue. Todos os indicadores são derivados de entidades normalizadas; o Google Maps é um adaptador opcional e nunca bloqueia o restante da experiência.

**Tech Stack:** Vue 3, TypeScript, Vite, Pinia, Vue Router, SheetJS, Dexie, Google Maps JavaScript API, Apache ECharts, Vitest, Vue Test Utils, fake-indexeddb e Playwright.

---

## Estrutura de arquivos

```text
package.json                         dependências e comandos
vite.config.ts                       Vite + Vitest
tsconfig.app.json                    TypeScript da aplicação
src/main.ts                          bootstrap Vue
src/App.vue                          shell raiz
src/router/index.ts                  rotas
src/styles/tokens.css                tokens SLDS e temas
src/styles/base.css                  estilos globais
src/components/AppShell.vue          barra superior e menu
src/components/StatCard.vue          KPI reutilizável
src/components/SegmentBadge.vue      Conquistar/Explorar/Manter
src/domain/types.ts                  entidades e contratos
src/domain/normalization.ts          normalização pura
src/domain/segmentation.ts           segmentação comercial
src/domain/scoring.ts                score explicável
src/domain/recommendation.ts         recomendação Mercedes
src/domain/portfolio-matching.ts     correspondência segura
src/import/schema.ts                 colunas e validação
src/import/parse-workbook.ts         XLSX para registros normalizados
src/import/import.worker.ts          processamento fora da UI
src/import/worker-client.ts          cliente tipado do worker
src/storage/db.ts                    schema Dexie
src/storage/repositories.ts          repositórios locais
src/maps/google-maps.ts              loader e geocodificação
src/maps/geocode-service.ts          cache e estados de erro
src/stores/app.ts                    estado global e importação
src/stores/filters.ts                filtros analíticos
src/analytics/selectors.ts           KPIs, rankings e séries
src/views/DashboardView.vue          central de comando A
src/views/ImportView.vue             fluxo de importação
src/views/MapView.vue                mapa e filtros
src/views/PortfolioView.vue          carteira Matheus
src/views/Client360View.vue          cliente e CRM
src/views/SettingsView.vue           chave e tema
src/features/crm/ContactForm.vue     contato
src/features/crm/InteractionForm.vue interação
src/features/crm/TaskForm.vue        tarefa
src/features/crm/OpportunityForm.vue oportunidade
src/**/*.test.ts                     testes unitários/integrados
e2e/import-and-crm.spec.ts           fluxo de ponta a ponta
```

## Task 1: Scaffold e shell Lightning

**Files:**
- Create: `package.json`
- Create: `vite.config.ts`
- Create: `src/main.ts`
- Create: `src/App.vue`
- Create: `src/router/index.ts`
- Create: `src/styles/tokens.css`
- Create: `src/styles/base.css`
- Create: `src/components/AppShell.vue`
- Test: `src/components/AppShell.test.ts`

- [ ] **Step 1: Criar o projeto Vite e instalar dependências**

Run:

```powershell
npm init -y
npm install vue-router@4 pinia dexie xlsx echarts uuid
npm install vue@3
npm install -D vite @vitejs/plugin-vue typescript vue-tsc vitest @vitest/coverage-v8 @vue/test-utils jsdom fake-indexeddb playwright eslint prettier @types/google.maps
npm pkg set scripts.dev="vite" scripts.build="vue-tsc -b && vite build" scripts.test="vitest"
```

Expected: `package.json` criado na raiz sem alterar a planilha, logos ou documentos existentes.

- [ ] **Step 2: Escrever o teste que exige navegação e alternância de tema**

```ts
// src/components/AppShell.test.ts
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { describe, expect, it } from 'vitest'
import AppShell from './AppShell.vue'

describe('AppShell', () => {
  it('exibe a navegação comercial e alterna o tema', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div />' } }],
    })
    const wrapper = mount(AppShell, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain('Central de comando')
    expect(wrapper.text()).toContain('Mapa')
    await wrapper.get('[data-testid="theme-toggle"]').trigger('click')
    expect(document.documentElement.dataset.theme).toBe('dark')
  })
})
```

- [ ] **Step 3: Rodar o teste e confirmar RED**

Run: `npm test -- src/components/AppShell.test.ts`

Expected: FAIL porque `AppShell.vue` ainda não existe.

- [ ] **Step 4: Implementar shell, rotas vazias e tokens**

```ts
// vite.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
export default defineConfig({ plugins: [vue()], test: { environment: 'jsdom', globals: true, setupFiles: [] } })
```

```json
// tsconfig.json
{ "files": [], "references": [{ "path": "./tsconfig.app.json" }] }
```

```json
// tsconfig.app.json
{
  "compilerOptions": {
    "target": "ES2023", "lib": ["ESNext", "DOM", "WebWorker"], "module": "ESNext",
    "moduleResolution": "Bundler", "strict": true, "jsx": "preserve", "types": ["vitest/globals", "google.maps"],
    "skipLibCheck": true, "allowImportingTsExtensions": true, "noEmit": true
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "e2e/**/*.ts", "vite.config.ts"]
}
```

```ts
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/tokens.css'
import './styles/base.css'
document.documentElement.dataset.theme = localStorage.getItem('tecar-theme') ?? 'light'
createApp(App).use(createPinia()).use(router).mount('#app')
```

```ts
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
const EmptyView = { template: '<section><h1>Em construção</h1></section>' }
export default createRouter({ history: createWebHistory(), routes: [
  { path: '/', component: EmptyView }, { path: '/mapa', component: EmptyView },
  { path: '/carteira', component: EmptyView }, { path: '/importar', component: EmptyView },
  { path: '/configuracoes', component: EmptyView },
] })
```

```vue
<!-- src/App.vue -->
<script setup lang="ts">import AppShell from './components/AppShell.vue'</script>
<template><AppShell /></template>
```

```css
/* src/styles/base.css */
* { box-sizing: border-box; }
body { margin: 0; background: var(--color-bg); color: var(--color-text); font-family: "Salesforce Sans", "Segoe UI", sans-serif; }
.topbar { position: fixed; inset: 0 0 auto; height: 3rem; padding: .75rem 1rem; background: var(--color-brand-deep); color: white; z-index: 10; }
.sidebar { position: fixed; inset: 3rem auto 0 0; width: 13rem; display: grid; align-content: start; gap: .25rem; padding: .75rem; background: var(--color-surface); border-right: 1px solid var(--color-border); }
.sidebar a, .sidebar button { padding: .65rem; color: inherit; text-align: left; background: transparent; border: 0; border-radius: var(--radius); }
.content { min-height: 100vh; margin-left: 13rem; padding: 4.5rem 1.5rem 1.5rem; }
```

```css
/* src/styles/tokens.css */
:root {
  --color-brand: #0b5cab;
  --color-brand-deep: #032d60;
  --color-bg: #f3f3f3;
  --color-surface: #ffffff;
  --color-text: #181818;
  --color-border: #c9c9c9;
  --color-conquistar: #ba0517;
  --color-explorar: #dd7a01;
  --color-manter: #2e844a;
  --radius: 0.25rem;
  --shadow: 0 1px 3px rgb(0 0 0 / 16%);
}

:root[data-theme='dark'] {
  --color-bg: #0f1720;
  --color-surface: #181f27;
  --color-text: #f3f3f3;
  --color-border: #52606d;
}
```

```vue
<!-- src/components/AppShell.vue -->
<script setup lang="ts">
import { ref } from 'vue'
const dark = ref(document.documentElement.dataset.theme === 'dark')
function toggleTheme() {
  dark.value = !dark.value
  document.documentElement.dataset.theme = dark.value ? 'dark' : 'light'
  localStorage.setItem('tecar-theme', dark.value ? 'dark' : 'light')
}
</script>

<template>
  <header class="topbar"><strong>Tecar Sales Intelligence</strong></header>
  <aside class="sidebar" aria-label="Navegação principal">
    <RouterLink to="/">Central de comando</RouterLink>
    <RouterLink to="/mapa">Mapa</RouterLink>
    <RouterLink to="/carteira">Carteira</RouterLink>
    <RouterLink to="/importar">Importar Excel</RouterLink>
    <RouterLink to="/configuracoes">Configurações</RouterLink>
    <button data-testid="theme-toggle" type="button" @click="toggleTheme">Tema</button>
  </aside>
  <main class="content"><RouterView /></main>
</template>
```

- [ ] **Step 5: Rodar teste e build**

Run: `npm test -- src/components/AppShell.test.ts`

Expected: PASS, 1 test.

Run: `npm run build`

Expected: exit 0.

- [ ] **Step 6: Commit**

```powershell
git add package.json package-lock.json vite.config.ts tsconfig*.json index.html src
git commit -m "feat: scaffold Lightning application shell"
```

## Task 2: Tipos, normalização e CNPJ

**Files:**
- Create: `src/domain/types.ts`
- Create: `src/domain/normalization.ts`
- Create: `src/domain/ids.ts`
- Test: `src/domain/normalization.test.ts`
- Test: `src/domain/ids.test.ts`

- [ ] **Step 1: Escrever testes das regras puras**

```ts
// src/domain/normalization.test.ts
import { describe, expect, it } from 'vitest'
import { extractCnpjRoot, normalizeBrand, normalizeCompanyName, normalizeCnpj } from './normalization'

describe('normalization', () => {
  it('preserva zeros à esquerda e extrai a raiz do CNPJ', () => {
    expect(normalizeCnpj('00.038.166/0001-05')).toBe('00038166000105')
    expect(extractCnpjRoot('00.038.166/0001-05')).toBe('00038166')
  })
  it('normaliza empresa sem sufixos jurídicos', () => {
    expect(normalizeCompanyName('Mâhnic Operadora Logística Ltda.')).toBe('MAHNIC OPERADORA LOGISTICA')
  })
  it('unifica a marca Mercedes-Benz', () => {
    expect(normalizeBrand('M.BENZ')).toBe('MERCEDES-BENZ')
  })
})
```

```ts
// src/domain/ids.test.ts
import { expect, it } from 'vitest'
import { stableId } from './ids'
it('gera o mesmo UUID para a mesma chave de origem', () => {
  expect(stableId('client', '00038166')).toBe(stableId('client', '00038166'))
  expect(stableId('client', '00038166')).not.toBe(stableId('registration', '00038166'))
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/domain/normalization.test.ts src/domain/ids.test.ts`

Expected: FAIL com módulo ausente.

- [ ] **Step 3: Implementar tipos e normalização**

```ts
// src/domain/types.ts
export type CommercialSegment = 'CONQUISTAR' | 'EXPLORAR' | 'MANTER'
export type MercedesLine = 'ACCELO' | 'ATEGO' | 'AXOR' | 'ACTROS' | 'AROCS'

export interface Registration {
  id: string
  clientId: string
  cnpj: string
  cnpjRoot: string
  companyName: string
  date: string
  chassis: string
  plate: string
  brand: string
  model: string
  vehicleSegment: string
  subsegment: string
  traction: string
  power: number | null
  city: string
  state: string
  address: string
}

export interface Client {
  id: string
  cnpjRoot: string
  displayName: string
  matrixCnpj: string
  city: string
  state: string
  address: string
  registrationIds: string[]
}
```

```ts
// src/domain/normalization.ts
const LEGAL_SUFFIX = /\b(LTDA|LIMITADA|S\/?A|SA|EIRELI|ME|EPP|UNIPESSOAL)\b/g

export function normalizeCnpj(value: unknown): string {
  return String(value ?? '').replace(/\D/g, '').padStart(14, '0').slice(-14)
}
export function extractCnpjRoot(value: unknown): string {
  return normalizeCnpj(value).slice(0, 8)
}
export function normalizeCompanyName(value: unknown): string {
  return String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase()
    .replace(LEGAL_SUFFIX, ' ').replace(/[^A-Z0-9]+/g, ' ').replace(/\s+/g, ' ').trim()
}
export function normalizeBrand(value: unknown): string {
  const brand = normalizeCompanyName(value)
  return /^(M BENZ|MBENZ|MERCEDES BENZ)$/.test(brand) ? 'MERCEDES-BENZ' : brand
}
```

```ts
// src/domain/ids.ts
import { v5 as uuidv5 } from 'uuid'
const TECAR_NAMESPACE = 'b3e9b3be-3197-4c7f-8a9d-f0a5e9c7e4d1'
export function stableId(kind: 'client' | 'registration', sourceKey: string): string {
  return uuidv5(`${kind}:${sourceKey}`, TECAR_NAMESPACE)
}
```

- [ ] **Step 4: Confirmar GREEN**

Run: `npm test -- src/domain/normalization.test.ts src/domain/ids.test.ts`

Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```powershell
git add src/domain
git commit -m "feat: add truck registration domain normalization"
```

## Task 3: Segmentação e score explicável

**Files:**
- Create: `src/domain/segmentation.ts`
- Create: `src/domain/scoring.ts`
- Test: `src/domain/segmentation.test.ts`
- Test: `src/domain/scoring.test.ts`

- [ ] **Step 1: Escrever testes de Conquistar, Explorar, empate e Manter**

```ts
// src/domain/segmentation.test.ts
import { describe, expect, it } from 'vitest'
import { classifyClient } from './segmentation'

describe('classifyClient', () => {
  it('classifica sem Mercedes como Conquistar', () => {
    expect(classifyClient({ VOLVO: 10, SCANIA: 2 })).toBe('CONQUISTAR')
  })
  it('classifica Mercedes sem liderança ou empatada como Explorar', () => {
    expect(classifyClient({ 'MERCEDES-BENZ': 2, VOLVO: 4 })).toBe('EXPLORAR')
    expect(classifyClient({ 'MERCEDES-BENZ': 4, VOLVO: 4 })).toBe('EXPLORAR')
  })
  it('classifica Mercedes líder isolada como Manter', () => {
    expect(classifyClient({ 'MERCEDES-BENZ': 5, VOLVO: 4 })).toBe('MANTER')
  })
})
```

- [ ] **Step 2: Escrever o teste do score e confirmar RED**

```ts
// src/domain/scoring.test.ts
import { expect, it } from 'vitest'
import { calculateScore } from './scoring'

it('retorna total e componentes auditáveis', () => {
  expect(calculateScore({ potential: 80, competitiveSpace: 100, purchaseTiming: 50, fit: 70 })).toEqual({
    total: 79,
    potential: 32,
    competitiveSpace: 30,
    purchaseTiming: 10,
    fit: 7,
  })
})
```

Run: `npm test -- src/domain/segmentation.test.ts src/domain/scoring.test.ts`

Expected: FAIL com módulos ausentes.

- [ ] **Step 3: Implementar regras mínimas**

```ts
// src/domain/segmentation.ts
import type { CommercialSegment } from './types'
export function classifyClient(counts: Record<string, number>): CommercialSegment {
  const mercedes = counts['MERCEDES-BENZ'] ?? 0
  if (mercedes === 0) return 'CONQUISTAR'
  const competitorMax = Math.max(0, ...Object.entries(counts).filter(([brand]) => brand !== 'MERCEDES-BENZ').map(([, count]) => count))
  return mercedes > competitorMax ? 'MANTER' : 'EXPLORAR'
}
```

```ts
// src/domain/scoring.ts
export interface ScoreInput { potential: number; competitiveSpace: number; purchaseTiming: number; fit: number }
export interface ScoreBreakdown extends ScoreInput { total: number }
const clamp = (value: number) => Math.max(0, Math.min(100, value))
export function calculateScore(input: ScoreInput): ScoreBreakdown {
  const potential = Math.round(clamp(input.potential) * 0.4)
  const competitiveSpace = Math.round(clamp(input.competitiveSpace) * 0.3)
  const purchaseTiming = Math.round(clamp(input.purchaseTiming) * 0.2)
  const fit = Math.round(clamp(input.fit) * 0.1)
  return { total: potential + competitiveSpace + purchaseTiming + fit, potential, competitiveSpace, purchaseTiming, fit }
}
```

- [ ] **Step 4: Confirmar GREEN**

Run: `npm test -- src/domain/segmentation.test.ts src/domain/scoring.test.ts`

Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```powershell
git add src/domain
git commit -m "feat: classify and score fleet clients"
```

## Task 4: Recomendação Mercedes e correspondência de carteira

**Files:**
- Create: `src/domain/recommendation.ts`
- Create: `src/domain/portfolio-matching.ts`
- Test: `src/domain/recommendation.test.ts`
- Test: `src/domain/portfolio-matching.test.ts`

- [ ] **Step 1: Escrever testes de recomendação e segurança do match**

```ts
// src/domain/recommendation.test.ts
import { expect, it } from 'vitest'
import { recommendMercedesLine } from './recommendation'
it('recomenda Actros para pesado rodoviário', () => {
  expect(recommendMercedesLine({ segment: 'PESADOS', subsegment: 'RODOVIARIO', traction: '6X4', power: 540 })).toMatchObject({ line: 'ACTROS' })
})
it('recomenda Arocs para fora de estrada', () => {
  expect(recommendMercedesLine({ segment: 'PESADOS', subsegment: 'FORA-DE-ESTRADA', traction: '6X4', power: 480 })).toMatchObject({ line: 'AROCS' })
})
```

```ts
// src/domain/portfolio-matching.test.ts
import { expect, it } from 'vitest'
import { matchPortfolioName } from './portfolio-matching'
it('confirma apenas nome normalizado exato', () => {
  const candidates = [{ clientId: '1', name: 'MAHNIC OPERADORA LOGISTICA LTDA' }]
  expect(matchPortfolioName('Mâhnic Operadora Logística', candidates).status).toBe('MATCHED')
  expect(matchPortfolioName('Mahnic Transportes', candidates).status).toBe('REVIEW')
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/domain/recommendation.test.ts src/domain/portfolio-matching.test.ts`

Expected: FAIL com módulos ausentes.

- [ ] **Step 3: Implementar regras explicáveis**

```ts
// src/domain/recommendation.ts
import type { MercedesLine } from './types'
export interface VehicleProfile { segment: string; subsegment: string; traction: string; power: number | null }
export function recommendMercedesLine(profile: VehicleProfile): { line: MercedesLine; reasons: string[] } {
  if (profile.subsegment.includes('FORA-DE-ESTRADA')) return { line: 'AROCS', reasons: ['Aplicação fora de estrada'] }
  if (profile.segment === 'PESADOS' && profile.subsegment.includes('RODOVIARIO')) return { line: 'ACTROS', reasons: ['Pesado rodoviário', `Tração ${profile.traction}`] }
  if (profile.segment === 'SEMIPESADOS') return { line: 'ATEGO', reasons: ['Operação semipesada'] }
  if ((profile.power ?? 0) <= 220) return { line: 'ACCELO', reasons: ['Potência e distribuição leve'] }
  return { line: 'AXOR', reasons: ['Aplicação robusta intermediária'] }
}
```

```ts
// src/domain/portfolio-matching.ts
import { normalizeCompanyName } from './normalization'
export interface Candidate { clientId: string; name: string }
export function matchPortfolioName(received: string, candidates: Candidate[]) {
  const key = normalizeCompanyName(received)
  const exact = candidates.find((candidate) => normalizeCompanyName(candidate.name) === key)
  return exact ? { status: 'MATCHED' as const, clientId: exact.clientId, confidence: 1 } : { status: 'REVIEW' as const, clientId: null, confidence: 0 }
}
```

- [ ] **Step 4: Confirmar GREEN e commit**

Run: `npm test -- src/domain/recommendation.test.ts src/domain/portfolio-matching.test.ts`

Expected: PASS, 3 tests.

```powershell
git add src/domain
git commit -m "feat: recommend Mercedes lines and match portfolio safely"
```

## Task 5: Importador XLSX e Web Worker

**Files:**
- Create: `src/import/schema.ts`
- Create: `src/import/parse-workbook.ts`
- Create: `src/import/import.worker.ts`
- Create: `src/import/worker-client.ts`
- Test: `src/import/parse-workbook.test.ts`

- [ ] **Step 1: Escrever teste com workbook XLSX em memória**

```ts
// src/import/parse-workbook.test.ts
import * as XLSX from 'xlsx'
import { expect, it } from 'vitest'
import { parseWorkbook } from './parse-workbook'

it('converte a aba Export em registros normalizados', () => {
  const sheet = XLSX.utils.json_to_sheet([{
    'DATA EMPLACAMENTO': '2026-07-23', CHASSI: 'ABC123', PLACA: 'UJC7E81',
    'CNPJ EMPRESA': '00.038.166/0001-05', 'NOME EMPRESA': 'Banco Central do Brasil',
    MARCA: 'M.BENZ', MODELO: 'M.BENZ/ACTROS 2651S 6X4', SEGMENTO: 'PESADOS',
    SUBSEGMENTO: 'RODOVIARIO', 'TRAÇÃO': '6X4', 'POTÊNCIA': '510',
    'LOG CIDADE': 'BRASILIA', 'LOG ESTADO': 'DF', 'LOG CEP': '70074900',
  }])
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, sheet, 'Export')
  const result = parseWorkbook(workbook)
  expect(result.errors).toEqual([])
  expect(result.registrations[0]).toMatchObject({ cnpjRoot: '00038166', brand: 'MERCEDES-BENZ', power: 510 })
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/import/parse-workbook.test.ts`

Expected: FAIL com `parseWorkbook` ausente.

- [ ] **Step 3: Implementar schema e parser**

```ts
// src/import/schema.ts
export const REQUIRED_COLUMNS = ['DATA EMPLACAMENTO', 'CHASSI', 'PLACA', 'CNPJ EMPRESA', 'NOME EMPRESA', 'MARCA', 'MODELO', 'SEGMENTO', 'SUBSEGMENTO'] as const
export interface ImportError { row: number; field: string; message: string }
```

```ts
// src/import/parse-workbook.ts
import * as XLSX from 'xlsx'
import { extractCnpjRoot, normalizeBrand, normalizeCnpj, normalizeCompanyName } from '../domain/normalization'
import { stableId } from '../domain/ids'
import type { Registration } from '../domain/types'
import { REQUIRED_COLUMNS, type ImportError } from './schema'

export interface ParseResult { registrations: Registration[]; errors: ImportError[] }
export function parseWorkbook(workbook: XLSX.WorkBook): ParseResult {
  const sheet = workbook.Sheets.Export
  if (!sheet) return { registrations: [], errors: [{ row: 0, field: 'Export', message: 'Aba Export ausente' }] }
  const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' })
  const headers = new Set(Object.keys(rows[0] ?? {}))
  const missing = REQUIRED_COLUMNS.filter((column) => !headers.has(column))
  if (missing.length) return { registrations: [], errors: missing.map((field) => ({ row: 1, field, message: 'Coluna obrigatória ausente' })) }
  const errors: ImportError[] = []
  const registrations = rows.flatMap((row, index) => {
    const date = new Date(String(row['DATA EMPLACAMENTO']))
    if (!row.CHASSI || Number.isNaN(date.valueOf())) {
      errors.push({ row: index + 2, field: !row.CHASSI ? 'CHASSI' : 'DATA EMPLACAMENTO', message: 'Registro inválido' })
      return []
    }
    const cnpj = normalizeCnpj(row['CNPJ EMPRESA'])
    return [{
      id: stableId('registration', String(row.CHASSI)), clientId: stableId('client', extractCnpjRoot(cnpj)), cnpj, cnpjRoot: extractCnpjRoot(cnpj),
      companyName: normalizeCompanyName(row['NOME EMPRESA']), date: date.toISOString().slice(0, 10),
      chassis: String(row.CHASSI), plate: String(row.PLACA), brand: normalizeBrand(row.MARCA), model: String(row.MODELO),
      vehicleSegment: String(row.SEGMENTO), subsegment: String(row.SUBSEGMENTO), traction: String(row['TRAÇÃO']),
      power: Number(row['POTÊNCIA']) || null, city: String(row['LOG CIDADE']), state: String(row['LOG ESTADO']),
      address: [row['LOG DESCRICAO'], row['LOG NUMERO'], row['LOG BAIRRO'], row['LOG CIDADE'], row['LOG ESTADO'], row['LOG CEP']].filter(Boolean).join(', '),
    } satisfies Registration]
  })
  return { registrations, errors }
}
```

- [ ] **Step 4: Confirmar GREEN**

Run: `npm test -- src/import/parse-workbook.test.ts`

Expected: PASS, 1 test.

- [ ] **Step 5: Encapsular leitura em worker com progresso**

```ts
// src/import/import.worker.ts
import * as XLSX from 'xlsx'
import { parseWorkbook } from './parse-workbook'
self.onmessage = (event: MessageEvent<ArrayBuffer>) => {
  self.postMessage({ type: 'progress', value: 10 })
  const workbook = XLSX.read(event.data, { type: 'array', cellDates: true })
  self.postMessage({ type: 'progress', value: 55 })
  const result = parseWorkbook(workbook)
  self.postMessage({ type: 'complete', value: 100, result })
}
```

```ts
// src/import/worker-client.ts
export type ImportWorkerEvent =
  | { type: 'progress'; value: number }
  | { type: 'complete'; value: 100; result: import('./parse-workbook').ParseResult }
export function runWorkbookImport(buffer: ArrayBuffer, onProgress: (value: number) => void) {
  return new Promise<import('./parse-workbook').ParseResult>((resolve, reject) => {
    const worker = new Worker(new URL('./import.worker.ts', import.meta.url), { type: 'module' })
    worker.onerror = (event) => { worker.terminate(); reject(new Error(event.message)) }
    worker.onmessage = (event: MessageEvent<ImportWorkerEvent>) => {
      if (event.data.type === 'progress') onProgress(event.data.value)
      if (event.data.type === 'complete') { worker.terminate(); resolve(event.data.result) }
    }
    worker.postMessage(buffer, [buffer])
  })
}
```

- [ ] **Step 6: Commit**

```powershell
git add src/import
git commit -m "feat: import and validate Tecar workbooks in a worker"
```

## Task 6: Consolidação, analytics e validação da planilha real

**Files:**
- Create: `src/analytics/selectors.ts`
- Test: `src/analytics/selectors.test.ts`
- Test: `src/import/real-workbook.test.ts`

- [ ] **Step 1: Escrever teste de consolidação e KPIs**

```ts
// src/analytics/selectors.test.ts
import { expect, it } from 'vitest'
import { buildClientAnalytics, buildClients } from './selectors'
it('consolida filiais por raiz e calcula share', () => {
  const rows = [
    { cnpjRoot: '12345678', cnpj: '12345678000100', brand: 'MERCEDES-BENZ', date: '2026-01-01' },
    { cnpjRoot: '12345678', cnpj: '12345678000200', brand: 'VOLVO', date: '2026-02-01' },
  ]
  expect(buildClientAnalytics(rows as never)).toEqual([{ cnpjRoot: '12345678', total: 2, mercedes: 1, shareMercedes: 0.5, segment: 'EXPLORAR' }])
  expect(buildClients(rows as never)).toHaveLength(1)
})
```

- [ ] **Step 2: Confirmar RED, implementar seletor e confirmar GREEN**

```ts
// src/analytics/selectors.ts
import { classifyClient } from '../domain/segmentation'
import { stableId } from '../domain/ids'
import type { Client, Registration } from '../domain/types'
export function buildClients(rows: Registration[]): Client[] {
  return [...Map.groupBy(rows, (row) => row.cnpjRoot)].map(([cnpjRoot, registrations]) => {
    const matrix = registrations.find((row) => row.cnpj.slice(8, 12) === '0001') ?? registrations[0]
    return { id: stableId('client', cnpjRoot), cnpjRoot, displayName: matrix.companyName, matrixCnpj: matrix.cnpj,
      city: matrix.city, state: matrix.state, address: matrix.address, registrationIds: registrations.map((row) => row.id) }
  })
}
export function buildClientAnalytics(rows: Registration[]) {
  const groups = Map.groupBy(rows, (row) => row.cnpjRoot)
  return [...groups].map(([cnpjRoot, registrations]) => {
    const counts = Object.fromEntries([...Map.groupBy(registrations, (row) => row.brand)].map(([brand, values]) => [brand, values.length]))
    const mercedes = counts['MERCEDES-BENZ'] ?? 0
    return { cnpjRoot, total: registrations.length, mercedes, shareMercedes: mercedes / registrations.length, segment: classifyClient(counts) }
  })
}
```

Run: `npm test -- src/analytics/selectors.test.ts`

Expected: PASS, 1 test.

- [ ] **Step 3: Criar teste da planilha real**

```ts
// src/import/real-workbook.test.ts
import fs from 'node:fs'
import * as XLSX from 'xlsx'
import { expect, it } from 'vitest'
import { parseWorkbook } from './parse-workbook'
it('importa a base inicial da Tecar', () => {
  const bytes = fs.readFileSync('EMPLACAMENTOS 01.08.2021 Á 30.07.xlsx')
  const result = parseWorkbook(XLSX.read(bytes, { type: 'buffer', cellDates: true }))
  expect(result.registrations).toHaveLength(22504)
  expect(result.registrations.filter((row) => row.brand === 'MERCEDES-BENZ')).toHaveLength(3810)
})
```

- [ ] **Step 4: Rodar a validação real**

Run: `npm test -- src/import/real-workbook.test.ts`

Expected: PASS, 22.504 registros e 3.810 Mercedes-Benz.

- [ ] **Step 5: Commit**

```powershell
git add src/analytics src/import/real-workbook.test.ts
git commit -m "feat: consolidate clients and calculate market analytics"
```

## Task 7: IndexedDB e preservação do CRM

**Files:**
- Create: `src/storage/db.ts`
- Create: `src/storage/repositories.ts`
- Test: `src/storage/repositories.test.ts`

- [ ] **Step 1: Escrever teste integrado com fake-indexeddb**

```ts
// src/storage/repositories.test.ts
import 'fake-indexeddb/auto'
import { beforeEach, expect, it } from 'vitest'
import { TecarDb } from './db'
import { replaceAnalyticalBase } from './repositories'
let db: TecarDb
beforeEach(async () => { db = new TecarDb(`test-${crypto.randomUUID()}`) })
it('substitui emplacamentos e preserva contatos', async () => {
  await db.contacts.add({ id: 'contact-1', clientId: 'client-1', name: 'Ana', phone: '62999999999', email: '' })
  await replaceAnalyticalBase(db, [{ id: 'r1', clientId: 'client-1' } as never], [])
  await replaceAnalyticalBase(db, [{ id: 'r2', clientId: 'client-1' } as never], [])
  expect(await db.registrations.count()).toBe(1)
  expect(await db.contacts.get('contact-1')).toMatchObject({ name: 'Ana' })
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/storage/repositories.test.ts`

Expected: FAIL com banco ausente.

- [ ] **Step 3: Implementar schema Dexie e transação**

```ts
// src/storage/db.ts
import Dexie, { type EntityTable } from 'dexie'
import type { Client, Registration } from '../domain/types'
export interface Contact { id: string; clientId: string; name: string; phone: string; email: string }
export interface Interaction { id: string; clientId: string; occurredAt: string; summary: string; nextAction: string }
export interface Task { id: string; clientId: string; title: string; dueDate: string; status: 'OPEN' | 'DONE' }
export interface Opportunity { id: string; clientId: string; title: string; stage: string; quantity: number; estimatedValue: number }
export class TecarDb extends Dexie {
  registrations!: EntityTable<Registration, 'id'>; clients!: EntityTable<Client, 'id'>
  contacts!: EntityTable<Contact, 'id'>; interactions!: EntityTable<Interaction, 'id'>
  tasks!: EntityTable<Task, 'id'>; opportunities!: EntityTable<Opportunity, 'id'>
  constructor(name = 'tecar-sales-intelligence') {
    super(name)
    this.version(1).stores({
      registrations: 'id,clientId,cnpjRoot,date,brand', clients: 'id,cnpjRoot,displayName,state',
      contacts: 'id,clientId', interactions: 'id,clientId,occurredAt', tasks: 'id,clientId,dueDate,status', opportunities: 'id,clientId,stage',
    })
  }
}
export const db = new TecarDb()
```

```ts
// src/storage/repositories.ts
import type { Client, Registration } from '../domain/types'
import type { TecarDb } from './db'
export async function replaceAnalyticalBase(database: TecarDb, registrations: Registration[], clients: Client[]) {
  await database.transaction('rw', database.registrations, database.clients, async () => {
    await database.registrations.clear(); await database.clients.clear()
    await database.registrations.bulkAdd(registrations); await database.clients.bulkAdd(clients)
  })
}
```

- [ ] **Step 4: Confirmar GREEN e commit**

Run: `npm test -- src/storage/repositories.test.ts`

Expected: PASS, CRM preservado.

```powershell
git add src/storage
git commit -m "feat: persist analytical data and CRM in IndexedDB"
```

## Task 8: Store de importação e tela de confirmação

**Files:**
- Create: `src/stores/app.ts`
- Create: `src/views/ImportView.vue`
- Test: `src/views/ImportView.test.ts`

- [ ] **Step 1: Escrever teste do fluxo de confirmação**

```ts
// src/views/ImportView.test.ts
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, expect, it } from 'vitest'
import ImportView from './ImportView.vue'
beforeEach(() => setActivePinia(createPinia()))
it('não promove a base antes da confirmação', async () => {
  const wrapper = mount(ImportView)
  expect(wrapper.find('[data-testid="confirm-import"]').exists()).toBe(false)
  expect(wrapper.text()).toContain('Selecionar planilha')
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/views/ImportView.test.ts`

Expected: FAIL porque a view não existe.

- [ ] **Step 3: Implementar estados e view**

```ts
// src/stores/app.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Registration } from '../domain/types'
import { runWorkbookImport } from '../import/worker-client'
import { buildClients } from '../analytics/selectors'
import { db } from '../storage/db'
import { replaceAnalyticalBase } from '../storage/repositories'
export const useAppStore = defineStore('app', () => {
  const status = ref<'IDLE' | 'READING' | 'REVIEW' | 'READY' | 'ERROR'>('IDLE')
  const progress = ref(0); const pending = ref<Registration[]>([]); const errors = ref<string[]>([])
  async function loadFile(file: File) {
    status.value = 'READING'; progress.value = 0; errors.value = []
    try {
      const result = await runWorkbookImport(await file.arrayBuffer(), (value) => { progress.value = value })
      pending.value = result.registrations; errors.value = result.errors.map((error) => `Linha ${error.row}: ${error.message}`)
      status.value = 'REVIEW'
    } catch (error) { errors.value = [error instanceof Error ? error.message : 'Falha na importação']; status.value = 'ERROR' }
  }
  async function confirmImport() {
    await replaceAnalyticalBase(db, pending.value, buildClients(pending.value))
    pending.value = []; status.value = 'READY'
  }
  return { status, progress, pending, errors, loadFile, confirmImport }
})
```

```vue
<!-- src/views/ImportView.vue -->
<script setup lang="ts">
import { useAppStore } from '../stores/app'
const store = useAppStore()
function selectFile(event: Event) { const file = (event.target as HTMLInputElement).files?.[0]; if (file) void store.loadFile(file) }
</script>
<template>
  <section><h1>Importar Excel</h1><label class="upload">Selecionar planilha<input type="file" accept=".xlsx,.xls" @change="selectFile" /></label>
  <progress v-if="store.status === 'READING'" :value="store.progress" max="100" />
  <p v-if="store.status === 'REVIEW'">{{ store.pending.length.toLocaleString('pt-BR') }} registros válidos</p>
  <button v-if="store.status === 'REVIEW'" data-testid="confirm-import" type="button" @click="store.confirmImport">Confirmar nova base local</button>
  <ul v-if="store.errors.length"><li v-for="error in store.errors" :key="error">{{ error }}</li></ul></section>
</template>
```

- [ ] **Step 4: Confirmar GREEN e commit**

Run: `npm test -- src/views/ImportView.test.ts`

Expected: PASS.

```powershell
git add src/stores src/views/ImportView.vue src/views/ImportView.test.ts
git commit -m "feat: add controlled workbook import flow"
```

## Task 9: Central de comando A e filtros

**Files:**
- Create: `src/stores/filters.ts`
- Create: `src/components/StatCard.vue`
- Create: `src/components/SegmentBadge.vue`
- Create: `src/components/MarketShareChart.vue`
- Create: `src/views/DashboardView.vue`
- Test: `src/views/DashboardView.test.ts`

- [ ] **Step 1: Escrever teste dos KPIs e segmentos**

```ts
// src/views/DashboardView.test.ts
import { mount } from '@vue/test-utils'
import { expect, it } from 'vitest'
import DashboardView from './DashboardView.vue'
it('mostra KPIs, mapa resumido e prioridades', () => {
  const wrapper = mount(DashboardView, { props: { summary: { clients: 72, shareMercedes: 0.169, conquistar: 48, explorar: 17, manter: 7 } } })
  expect(wrapper.text()).toContain('16,9%')
  expect(wrapper.text()).toContain('Conquistar')
  expect(wrapper.text()).toContain('Prioridades de hoje')
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/views/DashboardView.test.ts`

Expected: FAIL porque os componentes não existem.

- [ ] **Step 3: Implementar grid responsivo e seletores Pinia**

```vue
<!-- src/components/StatCard.vue -->
<script setup lang="ts">defineProps<{ label: string; value: string | number; tone?: string }>()</script>
<template><article class="stat-card" :data-tone="tone"><span>{{ label }}</span><strong>{{ value }}</strong></article></template>
```

```vue
<!-- src/components/SegmentBadge.vue -->
<script setup lang="ts">
import type { CommercialSegment } from '../domain/types'
defineProps<{ segment: CommercialSegment }>()
const labels = { CONQUISTAR: 'Conquistar', EXPLORAR: 'Explorar', MANTER: 'Manter' }
</script>
<template><span class="segment-badge" :data-segment="segment">{{ labels[segment] }}</span></template>
```

```vue
<!-- src/views/DashboardView.vue -->
<script setup lang="ts">
import StatCard from '../components/StatCard.vue'
import MarketShareChart from '../components/MarketShareChart.vue'
defineProps<{
  summary?: { clients: number; shareMercedes: number; conquistar: number; explorar: number; manter: number }
  shareHistory?: Array<{ period: string; share: number }>
}>()
</script>
<template><section><h1>Central de comando</h1><div class="stats">
  <StatCard label="Clientes" :value="summary?.clients ?? 0" />
  <StatCard label="Share Mercedes-Benz" :value="`${((summary?.shareMercedes ?? 0) * 100).toFixed(1).replace('.', ',')}%`" />
  <StatCard label="Conquistar" :value="summary?.conquistar ?? 0" tone="conquistar" />
  <StatCard label="Explorar" :value="summary?.explorar ?? 0" tone="explorar" />
  <StatCard label="Manter" :value="summary?.manter ?? 0" tone="manter" />
</div><MarketShareChart :points="shareHistory ?? []" /><div class="dashboard-grid"><article><h2>Mapa de oportunidades</h2></article><article><h2>Prioridades de hoje</h2></article></div></section></template>
```

- [ ] **Step 4: Confirmar GREEN e adicionar ECharts com dados derivados**

Run: `npm test -- src/views/DashboardView.test.ts`

Expected: PASS.

```vue
<!-- src/components/MarketShareChart.vue -->
<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
const props = defineProps<{ points: Array<{ period: string; share: number }> }>()
const host = ref<HTMLElement>(); let chart: echarts.ECharts | undefined
function render() {
  chart?.setOption({ tooltip: { trigger: 'axis' }, xAxis: { type: 'category', data: props.points.map((p) => p.period) },
    yAxis: { type: 'value', min: 0, max: 1, axisLabel: { formatter: (value: number) => `${Math.round(value * 100)}%` } },
    series: [{ type: 'line', smooth: true, data: props.points.map((p) => p.share), color: '#0b5cab' }] })
}
onMounted(() => { chart = echarts.init(host.value!); render() })
watch(() => props.points, render, { deep: true })
onBeforeUnmount(() => chart?.dispose())
</script>
<template><div ref="host" class="chart" role="img" aria-label="Evolução do market share Mercedes-Benz" /></template>
```

- [ ] **Step 5: Commit**

```powershell
git add src/components src/stores/filters.ts src/views/DashboardView.vue src/views/DashboardView.test.ts
git commit -m "feat: build commercial command center dashboard"
```

## Task 10: Google Maps opcional e geocodificação com cache

**Files:**
- Create: `src/maps/google-maps.ts`
- Create: `src/maps/geocode-service.ts`
- Create: `src/views/MapView.vue`
- Test: `src/maps/geocode-service.test.ts`
- Test: `src/views/MapView.test.ts`

- [ ] **Step 1: Escrever teste de cache e fallback**

```ts
// src/maps/geocode-service.test.ts
import { expect, it, vi } from 'vitest'
import { geocodeWithCache } from './geocode-service'
it('usa o cache antes de consultar Google', async () => {
  const provider = vi.fn()
  const cache = { get: vi.fn().mockResolvedValue({ lat: -16.68, lng: -49.25 }), put: vi.fn() }
  expect(await geocodeWithCache('Goiânia, GO', cache, provider)).toEqual({ lat: -16.68, lng: -49.25 })
  expect(provider).not.toHaveBeenCalled()
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/maps/geocode-service.test.ts`

Expected: FAIL com serviço ausente.

- [ ] **Step 3: Implementar serviço sem coordenadas inventadas**

```ts
// src/maps/geocode-service.ts
export interface Coordinate { lat: number; lng: number }
export interface GeocodeCache { get(address: string): Promise<Coordinate | undefined>; put(value: Coordinate & { address: string }): Promise<unknown> }
export async function geocodeWithCache(address: string, cache: GeocodeCache, provider: (address: string) => Promise<Coordinate>): Promise<Coordinate> {
  const cached = await cache.get(address)
  if (cached) return cached
  const coordinate = await provider(address)
  await cache.put({ address, ...coordinate })
  return coordinate
}
```

```ts
// src/maps/google-maps.ts
let loader: Promise<typeof google> | undefined
export function loadGoogleMaps(apiKey: string): Promise<typeof google> {
  if (!apiKey.trim()) return Promise.reject(new Error('Chave Google Maps ausente'))
  if (window.google?.maps) return Promise.resolve(window.google)
  if (loader) return loader
  loader = new Promise((resolve, reject) => {
    const callback = `initTecarMaps${Date.now()}`
    const callbacks = window as unknown as Record<string, unknown>
    callbacks[callback] = () => { delete callbacks[callback]; resolve(window.google) }
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&callback=${callback}&v=weekly`
    script.async = true; script.onerror = () => reject(new Error('Falha ao carregar Google Maps'))
    document.head.appendChild(script)
  })
  return loader
}
```

- [ ] **Step 4: Implementar view que degrada graciosamente**

```ts
// src/views/MapView.test.ts
import { mount } from '@vue/test-utils'
import { expect, it } from 'vitest'
import MapView from './MapView.vue'
it('mantém a aplicação utilizável sem chave', () => {
  const wrapper = mount(MapView, { props: { apiConfigured: false } })
  expect(wrapper.get('[role="status"]').text()).toContain('Configure uma chave Google Maps')
  expect(wrapper.find('#client-map').exists()).toBe(false)
})
```

```vue
<!-- src/views/MapView.vue -->
<script setup lang="ts">defineProps<{ apiConfigured: boolean }>()</script>
<template><section><h1>Mapa de clientes</h1>
  <div v-if="!apiConfigured" role="status" class="notice">Configure uma chave Google Maps restrita para ativar o mapa. Os demais recursos continuam disponíveis.</div>
  <div v-else id="client-map" aria-label="Mapa de clientes consolidados" />
</section></template>
```

- [ ] **Step 5: Rodar testes e commit**

Run: `npm test -- src/maps/geocode-service.test.ts src/views/MapView.test.ts`

Expected: PASS; MapView mostra fallback sem chave.

```powershell
git add src/maps src/views/MapView.vue src/views/MapView.test.ts
git commit -m "feat: add optional Google client map with geocode cache"
```

## Task 11: Carteira e Cliente 360

**Files:**
- Create: `src/views/PortfolioView.vue`
- Create: `src/views/Client360View.vue`
- Test: `src/views/PortfolioView.test.ts`
- Test: `src/views/Client360View.test.ts`

- [ ] **Step 1: Escrever testes de ranking e evidências**

```ts
// src/views/PortfolioView.test.ts
import { mount } from '@vue/test-utils'
import { expect, it } from 'vitest'
import PortfolioView from './PortfolioView.vue'
it('ordena a carteira por score e sinaliza revisão', () => {
  const wrapper = mount(PortfolioView, { props: { clients: [
    { id: '2', name: 'Paganini', score: 80, segment: 'CONQUISTAR' as const, matchStatus: 'MATCHED' as const },
    { id: '1', name: 'RG LOG', score: 40, segment: 'CONQUISTAR' as const, matchStatus: 'REVIEW' as const },
  ] } })
  expect(wrapper.findAll('tbody tr')[0].text()).toContain('Paganini')
  expect(wrapper.text()).toContain('Revisar correspondência')
})
```

```ts
// src/views/Client360View.test.ts
import { mount } from '@vue/test-utils'
import { expect, it } from 'vitest'
import Client360View from './Client360View.vue'
it('explica segmento, score e recomendação', () => {
  const wrapper = mount(Client360View, { props: { client: { name: 'TRANSMASUT', segment: 'CONQUISTAR' as const, score: 100, recommendation: { line: 'ACTROS' as const, reasons: ['Pesado rodoviário'] } } } })
  expect(wrapper.text()).toContain('Conquistar')
  expect(wrapper.text()).toContain('Actros')
  expect(wrapper.text()).toContain('Pesado rodoviário')
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/views/PortfolioView.test.ts src/views/Client360View.test.ts`

Expected: FAIL porque as views ainda não existem.

- [ ] **Step 3: Implementar as duas views**

```vue
<!-- src/views/PortfolioView.vue -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CommercialSegment } from '../domain/types'
const props = defineProps<{ clients: Array<{ id: string; name: string; score: number; segment: CommercialSegment; matchStatus: 'MATCHED' | 'REVIEW' }> }>()
const query = ref('')
const rows = computed(() => props.clients.filter((client) => client.name.toUpperCase().includes(query.value.toUpperCase())).sort((a, b) => b.score - a.score))
</script>
<template><section><h1>Carteira Matheus</h1><label>Buscar cliente<input v-model="query" type="search" /></label>
<table><thead><tr><th>Cliente</th><th>Segmento</th><th>Score</th><th>Correspondência</th></tr></thead><tbody>
<tr v-for="client in rows" :key="client.id"><td><RouterLink :to="`/clientes/${client.id}`">{{ client.name }}</RouterLink></td><td>{{ client.segment }}</td><td>{{ client.score }}</td><td>{{ client.matchStatus === 'REVIEW' ? 'Revisar correspondência' : 'Confirmada' }}</td></tr>
</tbody></table></section></template>
```

```vue
<!-- src/views/Client360View.vue -->
<script setup lang="ts">
import SegmentBadge from '../components/SegmentBadge.vue'
import type { CommercialSegment, MercedesLine } from '../domain/types'
defineProps<{ client: { name: string; segment: CommercialSegment; score: number; recommendation: { line: MercedesLine; reasons: string[] } } }>()
</script>
<template><section class="client-hero"><h1>{{ client.name }}</h1><SegmentBadge :segment="client.segment" /><strong>Score {{ client.score }}</strong></section>
<section><h2>Recomendação Mercedes-Benz</h2><h3>{{ client.recommendation.line }}</h3><ul><li v-for="reason in client.recommendation.reasons" :key="reason">{{ reason }}</li></ul></section>
<section><h2>Histórico de compras</h2><div data-testid="purchase-history" /></section><section><h2>CRM</h2><button type="button">Novo contato</button></section></template>
```

- [ ] **Step 4: Confirmar GREEN e commit**

Run: `npm test -- src/views/PortfolioView.test.ts src/views/Client360View.test.ts`

Expected: PASS, 2 tests.

```powershell
git add src/views/PortfolioView* src/views/Client360View*
git commit -m "feat: add portfolio and explainable client 360"
```

## Task 12: CRM local completo

**Files:**
- Create: `src/features/crm/ContactForm.vue`
- Create: `src/features/crm/InteractionForm.vue`
- Create: `src/features/crm/TaskForm.vue`
- Create: `src/features/crm/OpportunityForm.vue`
- Modify: `src/views/Client360View.vue`
- Test: `src/features/crm/ContactForm.test.ts`
- Test: `src/features/crm/TaskForm.test.ts`
- Test: `src/features/crm/CrmForms.test.ts`

- [ ] **Step 1: Escrever teste de contato e próxima ação**

```ts
// src/features/crm/ContactForm.test.ts
import { mount } from '@vue/test-utils'
import { expect, it } from 'vitest'
import ContactForm from './ContactForm.vue'
it('emite contato validado', async () => {
  const wrapper = mount(ContactForm, { props: { clientId: 'client-1' } })
  await wrapper.get('[name="name"]').setValue('Ana Compras')
  await wrapper.get('[name="phone"]').setValue('62999999999')
  await wrapper.get('form').trigger('submit')
  expect(wrapper.emitted('save')?.[0]?.[0]).toMatchObject({ clientId: 'client-1', name: 'Ana Compras' })
})
```

```ts
// src/features/crm/TaskForm.test.ts
import { mount } from '@vue/test-utils'
import { expect, it } from 'vitest'
import TaskForm from './TaskForm.vue'
it('emite tarefa aberta com data prevista', async () => {
  const wrapper = mount(TaskForm, { props: { clientId: 'client-1' } })
  await wrapper.get('[name="title"]').setValue('Agendar visita')
  await wrapper.get('[name="dueDate"]').setValue('2026-08-10')
  await wrapper.get('form').trigger('submit')
  expect(wrapper.emitted('save')?.[0]?.[0]).toMatchObject({ title: 'Agendar visita', status: 'OPEN' })
})
```

```ts
// src/features/crm/CrmForms.test.ts
import { mount } from '@vue/test-utils'
import { expect, it } from 'vitest'
import InteractionForm from './InteractionForm.vue'
import OpportunityForm from './OpportunityForm.vue'
it('registra interação com próxima ação', async () => {
  const wrapper = mount(InteractionForm, { props: { clientId: 'client-1' } })
  await wrapper.get('[name="summary"]').setValue('Visita realizada')
  await wrapper.get('[name="nextAction"]').setValue('Enviar proposta')
  await wrapper.get('form').trigger('submit')
  expect(wrapper.emitted('save')?.[0]?.[0]).toMatchObject({ nextAction: 'Enviar proposta' })
})
it('registra oportunidade com quantidade numérica', async () => {
  const wrapper = mount(OpportunityForm, { props: { clientId: 'client-1' } })
  await wrapper.get('[name="title"]').setValue('Renovação Actros')
  await wrapper.get('[name="quantity"]').setValue('10')
  await wrapper.get('form').trigger('submit')
  expect(wrapper.emitted('save')?.[0]?.[0]).toMatchObject({ quantity: 10, stage: 'PROSPECTING' })
})
```

- [ ] **Step 2: Confirmar RED**

Run: `npm test -- src/features/crm/ContactForm.test.ts`

Expected: FAIL com formulário ausente.

- [ ] **Step 3: Implementar formulários acessíveis e gravação via repositório**

```vue
<!-- src/features/crm/ContactForm.vue -->
<script setup lang="ts">
import { reactive } from 'vue'
const props = defineProps<{ clientId: string }>()
const emit = defineEmits<{ save: [contact: { id: string; clientId: string; name: string; phone: string; email: string }] }>()
const form = reactive({ name: '', phone: '', email: '' })
function submit() { if (form.name.trim()) emit('save', { id: crypto.randomUUID(), clientId: props.clientId, ...form }) }
</script>
<template><form @submit.prevent="submit"><label>Nome<input name="name" v-model="form.name" required /></label><label>Telefone<input name="phone" v-model="form.phone" /></label><label>Email<input name="email" v-model="form.email" type="email" /></label><button>Salvar contato</button></form></template>
```

```vue
<!-- src/features/crm/InteractionForm.vue -->
<script setup lang="ts">
import { reactive } from 'vue'
const props = defineProps<{ clientId: string }>(); const emit = defineEmits<{ save: [value: { id: string; clientId: string; occurredAt: string; summary: string; nextAction: string }] }>()
const form = reactive({ summary: '', nextAction: '' })
function submit() { if (form.summary.trim()) emit('save', { id: crypto.randomUUID(), clientId: props.clientId, occurredAt: new Date().toISOString(), ...form }) }
</script>
<template><form @submit.prevent="submit"><label>Resumo<textarea name="summary" v-model="form.summary" required /></label><label>Próxima ação<input name="nextAction" v-model="form.nextAction" /></label><button>Salvar interação</button></form></template>
```

```vue
<!-- src/features/crm/TaskForm.vue -->
<script setup lang="ts">
import { reactive } from 'vue'
const props = defineProps<{ clientId: string }>(); const emit = defineEmits<{ save: [value: { id: string; clientId: string; title: string; dueDate: string; status: 'OPEN' }] }>()
const form = reactive({ title: '', dueDate: '' })
function submit() { if (form.title.trim() && form.dueDate) emit('save', { id: crypto.randomUUID(), clientId: props.clientId, status: 'OPEN', ...form }) }
</script>
<template><form @submit.prevent="submit"><label>Título<input name="title" v-model="form.title" required /></label><label>Data prevista<input name="dueDate" v-model="form.dueDate" type="date" required /></label><button>Salvar tarefa</button></form></template>
```

```vue
<!-- src/features/crm/OpportunityForm.vue -->
<script setup lang="ts">
import { reactive } from 'vue'
const props = defineProps<{ clientId: string }>(); const emit = defineEmits<{ save: [value: { id: string; clientId: string; title: string; stage: string; quantity: number; estimatedValue: number }] }>()
const form = reactive({ title: '', quantity: 1, estimatedValue: 0 })
function submit() { if (form.title.trim()) emit('save', { id: crypto.randomUUID(), clientId: props.clientId, stage: 'PROSPECTING', title: form.title, quantity: Number(form.quantity), estimatedValue: Number(form.estimatedValue) }) }
</script>
<template><form @submit.prevent="submit"><label>Título<input name="title" v-model="form.title" required /></label><label>Quantidade<input name="quantity" v-model="form.quantity" type="number" min="1" /></label><label>Valor estimado<input name="estimatedValue" v-model="form.estimatedValue" type="number" min="0" /></label><button>Salvar oportunidade</button></form></template>
```

- [ ] **Step 4: Rodar todos os testes de CRM e commit**

Run: `npm test -- src/features/crm`

Expected: PASS para contatos, interações, tarefas e oportunidades.

```powershell
git add src/features/crm src/views/Client360View.vue
git commit -m "feat: persist local commercial CRM"
```

## Task 13: Configurações, tema e segurança da chave

**Files:**
- Create: `src/views/SettingsView.vue`
- Create: `.env.example`
- Test: `src/views/SettingsView.test.ts`

- [ ] **Step 1: Escrever teste que nunca exibe a chave completa**

```ts
// src/views/SettingsView.test.ts
import { mount } from '@vue/test-utils'
import { expect, it } from 'vitest'
import SettingsView from './SettingsView.vue'
it('mascara a chave configurada e explica restrições', () => {
  const wrapper = mount(SettingsView, { props: { currentKey: 'AIza-example-secret-key' } })
  expect(wrapper.text()).not.toContain('AIza-example-secret-key')
  expect(wrapper.text()).toContain('restrinja por domínio')
})
```

- [ ] **Step 2: Confirmar RED, implementar e confirmar GREEN**

```vue
<!-- src/views/SettingsView.vue -->
<script setup lang="ts">
const props = defineProps<{ currentKey?: string }>()
const masked = props.currentKey ? `••••${props.currentKey.slice(-4)}` : 'Não configurada'
</script>
<template><section><h1>Configurações</h1><p>Google Maps: {{ masked }}</p><p>Por segurança, restrinja por domínio e habilite apenas Maps JavaScript API e Geocoding API.</p><button type="button">Configurar chave neste dispositivo</button></section></template>
```

Run: `npm test -- src/views/SettingsView.test.ts`

Expected: PASS.

- [ ] **Step 3: Commit**

```powershell
git add .env.example src/views/SettingsView*
git commit -m "feat: add safe local settings and theme preferences"
```

## Task 14: Fluxo E2E, acessibilidade e responsividade

**Files:**
- Create: `playwright.config.ts`
- Create: `e2e/import-and-crm.spec.ts`
- Modify: `src/styles/base.css`

- [ ] **Step 1: Escrever o teste E2E antes dos ajustes finais**

```ts
// e2e/import-and-crm.spec.ts
import { test, expect } from '@playwright/test'
import path from 'node:path'
test('consulta dashboard e cadastra contato', async ({ page }) => {
  await page.goto('/importar')
  await page.locator('input[type="file"]').setInputFiles(path.resolve('EMPLACAMENTOS 01.08.2021 Á 30.07.xlsx'))
  await expect(page.getByText('22.504 registros válidos')).toBeVisible({ timeout: 120_000 })
  await page.getByRole('button', { name: 'Confirmar nova base local' }).click()
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Central de comando' })).toBeVisible()
  await page.getByRole('link', { name: 'Carteira' }).click()
  await page.getByRole('link', { name: /TRANSMASUT/i }).click()
  await page.getByRole('button', { name: 'Novo contato' }).click()
  await page.getByLabel('Nome').fill('Ana Compras')
  await page.getByRole('button', { name: 'Salvar contato' }).click()
  await expect(page.getByText('Ana Compras')).toBeVisible()
})
```

- [ ] **Step 2: Rodar e confirmar RED**

Run: `npm run build && npx playwright test e2e/import-and-crm.spec.ts`

Expected: FAIL no primeiro seletor/fluxo ainda não conectado.

- [ ] **Step 3: Conectar rotas, stores e repositórios; ajustar layout responsivo**

Substituir as rotas vazias de `src/router/index.ts` por:

```ts
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import ImportView from '../views/ImportView.vue'
import MapView from '../views/MapView.vue'
import PortfolioView from '../views/PortfolioView.vue'
import Client360View from '../views/Client360View.vue'
import SettingsView from '../views/SettingsView.vue'
export default createRouter({ history: createWebHistory(), routes: [
  { path: '/', component: DashboardView }, { path: '/mapa', component: MapView },
  { path: '/carteira', component: PortfolioView }, { path: '/clientes/:id', component: Client360View, props: true },
  { path: '/importar', component: ImportView }, { path: '/configuracoes', component: SettingsView },
] })
```

```css
/* acréscimo em src/styles/base.css */
@media (max-width: 800px) {
  .sidebar { position: fixed; inset: auto 0 0; display: flex; overflow-x: auto; z-index: 20; }
  .content { margin-left: 0; padding-bottom: 5rem; }
  .stats, .dashboard-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 520px) { .stats, .dashboard-grid { grid-template-columns: 1fr; } }
:focus-visible { outline: 3px solid #1b96ff; outline-offset: 2px; }
```

- [ ] **Step 4: Confirmar GREEN em desktop e viewport mobile**

Run: `npx playwright test e2e/import-and-crm.spec.ts`

Expected: PASS em Chromium desktop e projeto mobile configurado.

- [ ] **Step 5: Commit**

```powershell
git add playwright.config.ts e2e src
git commit -m "test: verify responsive import and CRM journey"
```

## Task 15: Verificação final e documentação operacional

**Files:**
- Create: `README.md`
- Create: `docs/data-dictionary.md`
- Create: `docs/google-maps-setup.md`

- [ ] **Step 1: Documentar instalação e operação sem backend**

`README.md` deve conter exatamente estes fluxos verificáveis:

```markdown
## Executar
npm install
npm run dev

## Validar
npm test
npm run build
npx playwright test

## Dados
O Excel é lido localmente pelo navegador. O arquivo original não é alterado.
O CRM permanece no IndexedDB deste dispositivo e não é sincronizado.
```

- [ ] **Step 2: Rodar a verificação completa**

Run: `npm test -- --run`

Expected: todos os testes unitários e de integração passam, zero falhas.

Run: `npm run build`

Expected: exit 0 e bundle em `dist/`.

Run: `npx playwright test`

Expected: todos os fluxos E2E passam.

- [ ] **Step 3: Fazer verificação manual com a base real**

Checklist:

```text
[ ] 22.504 registros válidos
[ ] 3.810 registros Mercedes-Benz
[ ] share geral 16,9%
[ ] temas claro e escuro
[ ] fluxo principal validado em Chrome e Edge
[ ] mapa mostra fallback sem chave
[ ] chave válida ativa mapa e geocodifica matriz
[ ] empate de marcas resulta em Explorar
[ ] CRM sobrevive a reimportação
[ ] arquivo Excel original permanece inalterado
```

- [ ] **Step 4: Commit final**

```powershell
git add README.md docs
git commit -m "docs: add Tecar MVP operating guide"
```

---

## Sequência de entrega

1. Tasks 1–4 produzem um domínio testável e a linguagem visual.
2. Tasks 5–8 produzem importação real e persistência segura.
3. Tasks 9–13 produzem a experiência comercial completa.
4. Tasks 14–15 conectam, verificam e documentam o MVP.

Nenhuma task deve promover dados inválidos, inventar coordenadas ou confirmar correspondência aproximada sem ação do usuário.
