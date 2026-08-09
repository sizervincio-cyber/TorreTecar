# Estoque e Calculadora de Rentabilidade Tecar

Data: 2026-08-09  
Status: design aprovado  
Entrega: aplicação web estática e responsiva, utilizável em desktop e smartphone

## 1. Objetivo

Criar uma aplicação focada exclusivamente em consulta de estoque e simulação de rentabilidade de caminhões Mercedes-Benz. A solução deve consultar automaticamente uma planilha Google Sheets em modo somente leitura, continuar utilizável quando a rede falhar e reproduzir as fórmulas efetivas da planilha `Planilhas de rentabilidade.xls`.

O HTML atual é referência funcional e fonte do estoque inicial. A nova entrega será separada e não alterará o arquivo original.

## 2. Escopo

Incluído:

- sincronização automática e manual do estoque publicado no Google Sheets;
- cache local do último estoque válido e fallback embutido;
- pesquisa por modelo, variante, chassi, NF, cor e cliente;
- filtros por casa, modelo, situação e idade do estoque;
- seleção de veículo e preenchimento automático da simulação;
- seleção de destino da venda e regra automática por origem/destino;
- simulação de preço, frete, bônus, despesas e acessórios;
- resultados auditáveis em reais e percentuais;
- memória de cálculo de créditos, débitos e comissões;
- persistência local da última simulação;
- exportação/impressão do resumo da simulação;
- interface responsiva, acessível e otimizada para toque.

Fora do escopo nesta versão:

- carteira de clientes;
- autenticação de usuários;
- edição ou gravação na planilha Google;
- backend próprio;
- aprovação comercial ou assinatura eletrônica.

## 3. Arquitetura escolhida

A planilha de estoque será publicada na Web como CSV, com atualização automática habilitada. A aplicação fará apenas requisições HTTP GET ao endereço publicado.

Fluxo de dados:

1. Ao abrir, a aplicação apresenta imediatamente o último cache válido ou o estoque embutido.
2. Em segundo plano, tenta consultar o CSV publicado com timeout.
3. O CSV é analisado e validado em memória.
4. Somente um conjunto válido substitui o cache e a tela atual.
5. A interface informa fonte, quantidade de veículos e horário da atualização.
6. Se a consulta falhar, a aplicação conserva os dados anteriores e sinaliza que estão desatualizados.

Não haverá chave de API, credencial ou segredo no front-end.

## 4. Fluxo de interface

Foi escolhida a opção A: estoque como tela inicial e calculadora como segunda etapa.

### 4.1 Estoque

- Cabeçalho compacto com marca Tecar/Mercedes-Benz e estado da sincronização.
- Busca em destaque e filtros rápidos por casa e situação.
- KPIs compactos: total, liberados, reservados e veículos com mais de 180/360 dias.
- Celular: cartões verticais com estado, casa, modelo, chassi, ano, preço de referência e dias de estoque.
- Desktop: tabela densa com painel lateral de detalhes.
- A ação `Simular rentabilidade` abre a calculadora já preenchida.
- Navegação inferior fixa no celular entre `Estoque` e `Simulação`.

### 4.2 Calculadora

- Identificação do veículo selecionado sempre visível.
- Origem inferida pela casa do estoque; destino obrigatório e ajustável.
- Campos principais primeiro: custo, preço de venda, frete, bônus e despesas.
- Regras tributárias em seção avançada, identificadas como parâmetros auditados.
- Resultado principal fixo e legível durante a edição.
- Memória de cálculo expansível para créditos, débitos, fundo e comissão.
- Ações: restaurar dados do estoque, limpar, salvar localmente, copiar resumo e imprimir/exportar.

## 5. Mapeamento do estoque

O importador reconhece 31 colunas na ordem da planilha atual:

`Nº`, `Casa`, `Modelo`, `Variante`, `UP`, `Cor`, `Ano`, `NF`, `Pagamento`, `Faturamento fábrica`, `Chassi`, `Campanha`, `Margem 5%`, `Margem 10%`, `Permanência`, `Valor NF`, `ICMS`, `Frete`, `Fundo fixo`, `Fundo variável`, `Bônus`, `Despesa`, `Pneus`, `Cliente`, `Status`, `Casa venda`, `Data reserva`, `Dias reserva`, `Vencimento fábrica`, `Dias`, `Vencido`.

O mapeamento será tolerante a variações de acento, capitalização e espaços nos cabeçalhos, mas rejeitará a carga se campos críticos não forem localizados: casa, modelo, chassi, valor NF, preço de referência e status.

Valores monetários brasileiros, percentuais e datas seriais do Excel serão normalizados antes do uso.

## 6. Cenários de rentabilidade

As fórmulas efetivas do `.xls` prevalecem sobre rótulos divergentes.

| Cenário | Regra principal |
| --- | --- |
| Aparecida → Goiás | crédito ICMS 7%; débito efetivo 9%; fundo 3%; encargos venda 2,2%; redução 3,94%; meta 3% |
| Anápolis → Goiás | crédito ICMS 7%; débito efetivo 9%; fundo 3%; financeiro 0,5%; encargos venda 1%; redução 3,94%; meta 3% |
| Mato Grosso local | crédito ICMS 7%; débito 12%; fundo 3%; encargos venda 2,2%; meta 3% |
| Tocantins local | crédito ICMS 7%; débito efetivo 8%; fundo 3%; financeiro 1%; encargos venda 1,2%; meta 3% |
| Aparecida → Tocantins | crédito ICMS 7%; débito 12%; fundo 3%; crédito outorgado 4%; Protege 15% do crédito outorgado; encargos venda 2,2%; meta 6% |
| Goiás → Mato Grosso | crédito ICMS 7%; débito 12%; fundo 3%; crédito outorgado 4%; Protege 15%; despesas gerais 2,6%; encargos venda 3,5%; meta 6% |

Para combinações não mapeadas, o sistema não inventará regra: exigirá seleção manual de um cenário conhecido e exibirá alerta.

## 7. Cálculos

Entradas principais:

- custo do veículo e IPI;
- valor da venda;
- frete, entrega/inspeção, emplacamento, acessórios e outras despesas;
- bônus de fábrica e bônus/fundo variável;
- alíquotas do cenário selecionado.

Créditos:

- venda;
- crédito de ICMS sobre custo com IPI;
- fundo fixo;
- crédito outorgado quando aplicável;
- bônus de fábrica e variável.

Débitos:

- custo com IPI;
- débito de ICMS sobre venda;
- redução de crédito quando aplicável;
- despesas gerais, financeiras e encargos sobre venda;
- Protege sobre crédito outorgado;
- despesas operacionais informadas.

Saídas:

- margem em reais e percentual sobre venda;
- margem sem Fundo Estrela;
- diferença para a meta;
- preço mínimo para atingir a meta;
- comissão do fundo, comissão fora do fundo, comissão sobre NF e total;
- total de créditos e débitos.

Comissões negativas serão bloqueadas por padrão. Uma opção avançada permitirá reproduzir o comportamento legado somente quando explicitamente ativada.

## 8. Validação e segurança

- Apenas requisições GET para a URL configurada.
- Nenhuma rotina de escrita no Google Sheets.
- Timeout e tratamento explícito de falha de rede.
- Limite de tamanho do CSV e de quantidade de linhas.
- Validação de cabeçalhos e campos críticos antes de atualizar o cache.
- Rejeição de linhas vazias ou sem identificação mínima.
- Textos externos inseridos somente como texto escapado; nenhum HTML da planilha será executado.
- Fórmulas iniciadas por `=`, `+`, `-` ou `@` serão tratadas como texto ao exportar CSV para evitar formula injection.
- Cache versionado e separado da simulação.
- Mensagens de erro não expõem dados internos nem substituem o último conjunto válido.

## 9. Estados de sincronização

- `Atualizando`: consulta em andamento.
- `Atualizado`: carga remota válida, com data/hora.
- `Cache`: rede indisponível, usando última carga válida.
- `Base incorporada`: primeiro uso sem acesso remoto.
- `Estrutura incompatível`: CSV recebido, mas rejeitado por alteração de esquema.

## 10. Responsividade e acessibilidade

- Largura mínima de projeto: 320 px.
- Alvos de toque com pelo menos 44 px.
- Sem rolagem horizontal obrigatória no celular.
- Campos numéricos com teclado decimal apropriado.
- Rótulos persistentes; placeholders não substituem labels.
- Foco visível, navegação por teclado e regiões de status anunciadas.
- Cores de situação sempre acompanhadas por texto/ícone.
- Respeito a `prefers-reduced-motion`.
- Impressão limpa em A4 do resumo da simulação.

## 11. Testes e critérios de aceite

### Financeiro

- Casos de referência preenchidos no `.xls` devem reproduzir margem, percentual e comissão dentro de tolerância de R$ 0,02 e 0,01 ponto percentual.
- Testes para venda zero, custo zero, valores negativos, percentuais inválidos e cenário não mapeado.
- Testes separados para os seis cenários.

### Dados

- Importação de valores brasileiros e datas seriais.
- Reordenação de colunas sem quebra quando cabeçalhos forem reconhecidos.
- Rejeição de esquema incompleto sem perda do cache anterior.
- Deduplicação por chassi, preservando a linha mais recente/válida.

### Interface

- Testes em 320, 360, 390, 768, 1024 e 1440 px.
- Busca, filtros, seleção, retorno ao estoque e restauração dos dados do veículo.
- Uso por teclado e foco visível.
- Impressão do resumo sem controles interativos.

### Aceite final

- Aplicação abre diretamente por arquivo ou hospedagem estática.
- Estoque aparece imediatamente, mesmo sem rede.
- Sincronização automática é somente leitura e não bloqueia a interface.
- Seleção de veículo preenche a calculadora.
- Origem e destino aplicam a regra correta.
- Resultados exibem memória de cálculo auditável.
- A interface funciona sem rolagem horizontal em smartphone.

## 12. Dependência operacional

Antes da sincronização remota funcionar em produção, o proprietário da planilha deve usar `Arquivo → Compartilhar → Publicar na Web`, publicar apenas a aba de estoque em CSV e manter a republicação automática habilitada. A URL publicada será configurada como constante no HTML final. Até isso ocorrer, a aplicação usará o estoque embutido e o cache local.
