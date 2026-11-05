# Padrão visual dos relatórios da Torre Tecar

Extraído dos relatórios recentes ("Carteira Matheus – Análise 360", "Extrapesados 6x4 – Mercado × Preço × Potência", "Carteira por Vendedor – Nov 2026"). O CSS completo está em `assets/modelo.html`.

## Página
- 1280×720 px, fundo branco, `@page{size:1280px 720px;margin:0}`; na tela as páginas ficam sobre cinza `#8a8f96`.
- Fonte: `'Inter','Segoe UI',system-ui,sans-serif`, números tabulares (`font-variant-numeric: tabular-nums`).
- Margens laterais 46 px. Cabeçalho com linha inferior preta de 2 px; rodapé com linha cinza de 1 px.

## Cores
| Token | Uso | Valor |
|---|---|---|
| `--ink` / `--ink2` / `--ink3` | texto principal / secundário / rótulos | `#0d0f12` / `#3c4450` / `#79828f` |
| `--line` / `--soft` | bordas / fundos suaves | `#dfe3e8` / `#f2f4f6` |
| `--mb` | Mercedes-Benz, títulos, etiquetas | `#111318` |
| `--vo` Volvo · `--sc` Scania · `--daf` DAF · `--iv` Iveco · `--vw` VW · `--out` outras | marcas | `#3B6EA5` · `#B8432F` · `#C9A227` · `#7E5BA6` · `#4E8F5B` · `#9AA3AD` |
| `--good` / `--bad` / `--warn` / `--acc` | positivo / negativo / atenção / destaque | `#1e7b4f` / `#b3261e` / `#b7791f` / `#00A19B` |

## Componentes
- **Cabeçalho `.hd`**: `.n` (número grande cinza-claro) · `.t` com `h2` (20 px, 750) e `.s` (11,5 px cinza) · `.tag` (etiqueta preta, 9 px, caixa alta, espaçada).
- **KPI `.kp`**: borda esquerda de 3 px colorida (`.kp.b` vermelho, `.g` verde, `.w` âmbar, `.a` turquesa, `.n` cinza; padrão preto). `.l` rótulo em caixa alta 8 px · `.v` valor 25 px 800 (com `<small>` para unidade) · `.d` nota 9,5 px.
- **Painel `.pn`**: borda 1 px, raio 7 px; `h3` 9,5 px caixa alta com `<em>` à direita para nota/recorte.
- **Tabela**: cabeçalho 8 px caixa alta com linha preta 1,5 px; linhas finas `--soft`; números à direita; `th.l/td.l` à esquerda; `tr.tot` linha de total; `tr.hi` destaque suave; `.pos`/`.neg` verde/vermelho; `.dim` cinza.
- **Chip `.chip`**: etiqueta pequena com borda (`.chip.mb` preto cheio; `.b`, `.g`, `.w`).
- **Leitura `.co`**: fundo `--soft`, borda esquerda 3 px (`.co.b`, `.g`, `.w`), `.t` rótulo em caixa alta ("LEITURA", "O QUE MUDA EM 2026", "RECORTE", "FONTE DOS PREÇOS").
- **Barras inline `.bar`**: 7 px de altura para mini-barras em tabela (Tecar preto × outras cinza).
- **Legenda `.lg`**: quadrados 9 px com a cor da marca.
- **Capa `.pg.cv`**: fundo preto, olho (`.eye`), título 52 px, subtítulo, faixa de 4 números (`.strip`) e rodapé.

## Escrita
- Título = conclusão com número. Bom: "Vendedor médio: 282 clientes, 48 compram por ano, mercado de 169 caminhões — Tecar vende 28". Ruim: "Análise da carteira".
- Subtítulo diz o que a página mostra e o recorte.
- KPIs: 3 a 5 por página, cada um com rótulo curto, valor e uma linha de contexto.
- Rodapé esquerdo = fontes e regras; direito = "TECAR CAMINHÕES · EMPLACAMENTOS ATÉ dd/mm/aaaa · dd/mm/aaaa".
- Bullets finais (3) com o que fazer: verbo no começo, um número em cada.

## Variante editorial (one-pager para cliente, ex.: Estudo de TCO)
- Retrato 810×1440, fundo creme `#f3f3ee`, título enorme em duas cores (texto `#13261f` e verde `#1f6b54`), rótulos em `IBM Plex Mono` caixa alta, barras cinza `#a9b3ad` com o vencedor em verde.
- Use só quando o pedido for material para cliente final; relatórios internos seguem o padrão 1280×720.
