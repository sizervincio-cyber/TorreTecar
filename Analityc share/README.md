# Market Intelligence Command Center

Painel de inteligência de mercado para caminhões pesados (rede Mercedes-Benz / Tecar),
construído como um único arquivo HTML autocontido.

## Arquivos

| Arquivo | Papel |
|---|---|
| `Market_Intelligence_Command_Center.html` | Aplicação completa (Vue 3 + Chart.js + amCharts 5 + Leaflet + Cytoscape) |
| `EMPLACAMENTO - ANÁLISE PERFIL CLIENTES.xlsx` | Matriz fonte — 2.357 emplacamentos, jan–ago/2026 |

## Como rodar

O arquivo abre direto no navegador, mas para que a planilha seja lida como **fonte viva**
é preciso servi-lo por HTTP (o `fetch` do XLSX não funciona sob `file://`):

```bash
python -m http.server 8741
```

Depois abra <http://localhost:8741/Market_Intelligence_Command_Center.html>.

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

O HTML embute registros comerciais reais: razão social, CNPJ, chassi, placa e comportamento
de compra por cliente. **Mantenha este repositório privado.** Publicar o painel em GitHub
Pages ou em qualquer host público torna esses dados acessíveis e indexáveis.

Para uma versão publicável, gere antes um snapshot anonimizado (mascarar CNPJ, razão social,
chassi e placa) — os cálculos do painel continuam funcionando sobre dados mascarados.
