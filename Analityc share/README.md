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

## Telas

**Decisão** — Control Tower · Mercado · Território · Geointeligência
**Cliente** — Clientes · Customer 360 · Recorrência · Sazonalidade · Oportunidades
**Diagnóstico** — Concorrência · Licitações · Graph Explorer · Sensibilidade · Data Quality
**Governança** — Importações · Regras

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

Razão social, chassi, placa e o comportamento de compra por cliente **permanecem como no
original**. Como o nome da empresa identifica o cliente de forma mais direta que o CNPJ, a
pseudonimização do documento reduz pouco a exposição: em repositório público, este conteúdo
é informação comercial identificável e indexável.
