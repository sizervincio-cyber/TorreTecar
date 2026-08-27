# Plano Completo — Software Tecar de Estoque e Rentabilidade

Versão: 1.0  
Data de consolidação: 09/08/2026  
Produto: Estoque e Calculadora de Rentabilidade Mercedes-Benz Caminhões  
Empresa: Tecar  
Status: especificação funcional, financeira, técnica e de segurança consolidada

---

## 1. Visão do produto

O software será uma aplicação web responsiva para consulta de caminhões em estoque e simulação de rentabilidade comercial. O vendedor deverá conseguir localizar um veículo, conferir sua disponibilidade, selecionar o destino da venda e receber imediatamente a margem, o preço mínimo e a comissão conforme a regra da casa de origem.

A aplicação será construída para uso prioritário em smartphones, mas também deverá operar em tablets e computadores. A fonte operacional do estoque será uma planilha Google Sheets publicada em modo somente leitura.

### Objetivos

- Centralizar a consulta de estoque Mercedes-Benz da Tecar.
- Reduzir erros de transcrição entre estoque e planilha de rentabilidade.
- Aplicar automaticamente a regra correta por casa de origem e destino.
- Permitir simulações comerciais sem modificar a planilha oficial.
- Exibir memória de cálculo auditável para créditos, débitos e comissões.
- Continuar funcionando com o último estoque válido quando a internet falhar.

### Fora do escopo da primeira versão

- Edição do Google Sheets.
- Carteira de clientes e prospecção.
- Autenticação ou gestão de usuários.
- Aprovação formal de descontos.
- Assinatura eletrônica.
- Integração com ERP ou DMS.
- Gravação de propostas em servidor.

---

## 2. Fontes auditadas

### Arquivos locais

- `carteira_gestor_grandes_frotas_mercedes_estoque_rentabilidade_v4_auto_import (1).html`
- `Planilhas de rentabilidade.xls`

### Fonte remota

- Google Sheets: `https://docs.google.com/spreadsheets/d/1Tu9nmFAd1bliC9xpb3M6ZCFYCj0YvVJz76OWAUFOjKs/edit?gid=0#gid=0`
- Aba de estoque: `gid=0`
- Permissão planejada: somente leitura.
- Publicação necessária: `Arquivo → Compartilhar → Publicar na Web`.
- Formato recomendado: CSV da aba de estoque.
- Republicação automática: habilitada.

### Hierarquia das fontes

1. Google Sheets publicado e validado.
2. Última carga remota válida armazenada no aparelho.
3. Estoque de contingência incorporado ao HTML.

Uma carga remota inválida nunca deverá substituir o último conjunto válido.

---

## 3. Arquitetura definida

```text
Google Sheets publicado — somente leitura
                    │
                    ▼
       consulta automática por HTTP GET
                    │
                    ▼
        validação de esquema e conteúdo
                    │
          ┌─────────┴─────────┐
          │ carga válida      │ carga inválida/falha
          ▼                   ▼
   atualiza o estoque    mantém o último cache
   e o cache local       e sinaliza contingência
          │
          ▼
  pesquisa e seleção do caminhão
          │
          ▼
  origem + destino da operação
          │
          ▼
  motor auditado de rentabilidade
          │
          ▼
  margem, preço mínimo e comissão
```

### Restrições técnicas

- Nenhum método remoto `POST`, `PUT`, `PATCH` ou `DELETE`.
- Nenhuma chave de API ou senha no HTML.
- Nenhuma biblioteca externa necessária para o cálculo.
- Interface executável por hospedagem estática HTTPS.
- Fallback incorporado para abertura imediata e contingência.

---

## 4. Fluxo de uso aprovado

Foi aprovado o fluxo **Estoque primeiro**.

### Etapa 1 — Estoque

1. O sistema abre exibindo o último estoque disponível.
2. A sincronização remota acontece em segundo plano.
3. O vendedor pesquisa por modelo, variante, chassi, nota fiscal, cor ou cliente.
4. Pode filtrar por casa, situação, modelo e idade do estoque.
5. Seleciona um caminhão.
6. Confere custo, preços de referência, dias em estoque e situação.
7. Aciona `Simular rentabilidade`.

### Etapa 2 — Simulação

1. O sistema preenche automaticamente os dados disponíveis do caminhão.
2. A origem é definida pela casa do estoque.
3. O vendedor informa ou confirma o destino da venda.
4. O motor escolhe o cenário tributário.
5. O vendedor pode alterar preço de venda e despesas simuláveis.
6. Margem e comissão são recalculadas instantaneamente.
7. A memória de cálculo pode ser expandida para auditoria.
8. O resumo pode ser copiado ou impresso.

### Navegação móvel

- Barra inferior fixa com `Estoque` e `Simulação`.
- Botões com área mínima de toque de 44 px.
- Nenhuma rolagem horizontal obrigatória.
- Resultado principal visível durante a edição.

---

## 5. Casas e rotas comerciais

### Casas identificadas no estoque

| Casa | Estado operacional | Cenário local padrão |
| --- | --- | --- |
| Aparecida | Goiás | `aparecida_go` |
| Anápolis | Goiás | `anapolis_go` |
| Palmas | Tocantins | `tocantins_local` |
| Barra | Mato Grosso | `mato_grosso_local` |

### Seleção automática de cenário

| Origem | Destino | Cenário |
| --- | --- | --- |
| Aparecida | Goiás | Aparecida → Goiás |
| Anápolis | Goiás | Anápolis → Goiás |
| Barra/MT | Mato Grosso | Mato Grosso local |
| Palmas | Tocantins | Tocantins local |
| Aparecida | Tocantins | Aparecida → Tocantins |
| Aparecida, Anápolis ou Goiás | Mato Grosso | Goiás → Mato Grosso |

### Regra de segurança

Origem e destino são comparados por nomes normalizados e exatos. O sistema não deverá usar correspondência parcial. Entradas como `XANAPOLISY`, `BARRA FUNDA` ou `NOVA GOIAS` não poderão selecionar uma regra fiscal automaticamente.

Combinações não mapeadas deverão bloquear o cálculo automático e exigir seleção explícita de um cenário conhecido.

---

## 6. Regras financeiras por cenário

As fórmulas efetivas do arquivo `.xls` prevalecem sobre textos ou rótulos divergentes encontrados nas abas.

| Cenário | Crédito ICMS | Débito ICMS | Fundo | Gerais | Financeiro | Encargo venda | Redução | Créd. outorgado | Protege | Meta | Comissão NF | Comissão fundo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Aparecida → Goiás | 7% | 9% | 3% | 0% | 0% | 2,2% | 3,94% | 0% | 0% | 3% | 0,2% | 2,5% |
| Anápolis → Goiás | 7% | 9% | 3% | 0% | 0,5% | 1% | 3,94% | 0% | 0% | 3% | 0,2% | 2,5% |
| Mato Grosso local | 7% | 12% | 3% | 2,59% | 0% | 2,2% | 0% | 0% | 0% | 3% | 0,3% | 2,5% |
| Tocantins local | 7% | 8% | 3% | 2,6% | 1% | 1,2% | 0% | 0% | 0% | 3% | 0,3% | 2,5% |
| Aparecida → Tocantins | 7% | 12% | 3% | 0% | 0% | 2,2% | 0% | 4% | 15% | 6% | 0,2% | 2,5% |
| Goiás → Mato Grosso | 7% | 12% | 3% | 2,6% | 0% | 3,5% | 0% | 4% | 15% | 6% | 0,2% | 2,5% |

### Custo padrão de entrega/inspeção

- Aparecida → Goiás: R$ 385,90.
- Anápolis → Goiás: R$ 385,90.
- Mato Grosso local: R$ 385,90.
- Demais cenários: zero como padrão, ajustável na simulação.

### Limites definidos

- Valores monetários aceitos: de R$ 0,00 a R$ 1.000.000.000.000,00.
- Percentuais aceitos: de 0% a 100%.
- Valores ausentes são tratados como zero apenas quando o campo não for obrigatório.
- Fundo fixo ausente usa a regra do cenário.
- Fundo fixo explicitamente igual a zero permanece zero.
- Despesa negativa em texto é rejeitada com mensagem clara.
- Comissão negativa é bloqueada por padrão.
- Reprodução da comissão negativa legada somente por opção avançada explícita.

---

## 7. Fórmulas do motor

### Entradas

- `Custo do veículo`
- `IPI`
- `Valor da venda`
- `Frete`
- `Entrega/inspeção`
- `Emplacamento`
- `Acessórios`
- `Outras despesas`
- `Bônus de fábrica`
- `Bônus/fundo variável`
- Percentuais do cenário

### Custo com IPI

```text
Custo com IPI = Custo do veículo + IPI
```

### Créditos

```text
Crédito ICMS = Custo com IPI × alíquota de crédito ICMS
Fundo fixo = Custo com IPI × percentual do fundo
Crédito outorgado = Valor da venda × percentual de crédito outorgado

Total de créditos =
  Valor da venda
  + Crédito ICMS
  + Fundo fixo
  + Crédito outorgado
  + Bônus de fábrica
  + Bônus variável
```

### Débitos

```text
Débito ICMS = Valor da venda × alíquota de débito ICMS

Redução =
  máximo(0, Custo com IPI - Crédito ICMS)
  × percentual de redução

Despesas gerais = Valor da venda × percentual geral
Encargos financeiros = Valor da venda × percentual financeiro
Encargos sobre venda = Valor da venda × percentual de venda
Protege = Crédito outorgado × percentual Protege

Despesas operacionais =
  Frete
  + Entrega/inspeção
  + Emplacamento
  + Acessórios
  + Outras despesas

Total de débitos =
  Custo com IPI
  + Débito ICMS
  + Redução
  + Despesas gerais
  + Encargos financeiros
  + Encargos sobre venda
  + Protege
  + Despesas operacionais
```

### Rentabilidade

```text
Margem em R$ = Total de créditos - Total de débitos
Margem % = Margem em R$ ÷ Valor da venda × 100

Rentabilidade sem Fundo Estrela = Margem em R$ - Fundo fixo
Diferença para a meta = Margem % - Meta do cenário
```

### Comissão

```text
Comissão do fundo = Fundo fixo × percentual de comissão do fundo

Base fora do fundo =
  máximo(0, Rentabilidade sem Fundo Estrela)

Comissão fora do fundo = Base fora do fundo × 5%
Comissão sobre NF = Valor da venda × percentual de comissão da NF

Comissão total =
  Comissão do fundo
  + Comissão fora do fundo
  + Comissão sobre NF
```

### Preço mínimo

O preço mínimo deverá resolver algebricamente o valor de venda necessário para atingir a meta do cenário. Se o coeficiente for inviável, não finito ou produzir valor superior ao limite monetário suportado, o sistema exibirá `Preço mínimo indisponível`.

### Política de arredondamento

- Cálculo interno em precisão integral do JavaScript.
- Arredondamento para duas casas apenas na exibição de valores monetários.
- Percentuais exibidos com duas casas.
- Testes de referência aceitam diferença máxima de R$ 0,02 e 0,01 ponto percentual.

---

## 8. Campos importados do estoque

O importador deverá reconhecer 31 colunas, preferencialmente por cabeçalho normalizado e não somente pela posição.

| Nº | Campo | Uso |
| ---: | --- | --- |
| 1 | Nº | Identificador da linha |
| 2 | Casa | Origem e filtro |
| 3 | Modelo | Pesquisa e identificação |
| 4 | Variante | Identificação técnica |
| 5 | UP | Unidade/processo |
| 6 | Cor | Pesquisa e detalhe |
| 7 | Ano | Ano/modelo |
| 8 | NF | Nota fiscal |
| 9 | Pagamento | Referência operacional |
| 10 | Faturamento fábrica | Data operacional |
| 11 | Chassi | Identificador único e deduplicação |
| 12 | Campanha | Preço alternativo de venda |
| 13 | Margem 5% | Preço padrão da simulação |
| 14 | Margem 10% | Preço público de referência |
| 15 | Permanência | Localização física |
| 16 | Valor NF | Custo padrão do veículo |
| 17 | ICMS | Referência fiscal do estoque |
| 18 | Frete | Despesa automática |
| 19 | Fundo fixo | Percentual ou referência do fundo |
| 20 | Fundo variável | Percentual ou valor monetário |
| 21 | Bônus | Bônus de fábrica |
| 22 | Despesa | Observações e custo identificado |
| 23 | Pneus | Detalhe técnico |
| 24 | Cliente | Reserva/cliente |
| 25 | Status | Liberado, reservado ou vendido |
| 26 | Casa venda | Unidade comercial |
| 27 | Data reserva | Controle da reserva |
| 28 | Dias reserva | Idade da reserva |
| 29 | Vencimento fábrica | Referência de vencimento |
| 30 | Dias | Dias em estoque |
| 31 | Vencido | Dias vencidos |

### Campos críticos

A carga será rejeitada se não localizar:

- Casa
- Modelo
- Chassi
- Valor NF
- Pelo menos um preço de referência
- Status

### Normalização

- Acentos, caixa e espaços dos cabeçalhos são normalizados.
- Moedas brasileiras são convertidas para números.
- Percentuais podem chegar como `3%`, `0,03` ou valor equivalente.
- Datas seriais do Excel são convertidas para datas reais.
- Linhas vazias ou sem modelo/chassi são descartadas.
- Chassis duplicados são consolidados, preservando a última linha válida.

---

## 9. Caminhões definidos no estoque de contingência

O inventário incorporado possui **27 veículos**, usado apenas quando a fonte remota e o cache não estiverem disponíveis.

### Resumo por casa

| Casa | Quantidade |
| --- | ---: |
| Aparecida | 14 |
| Anápolis | 6 |
| Palmas | 5 |
| Barra | 2 |

### Resumo por situação

| Situação | Quantidade |
| --- | ---: |
| Liberado | 17 |
| Reservado | 7 |
| Vendido | 3 |

### Catálogo por modelo

| Modelo | Qtd. | Casas | Faixa Valor NF | Faixa preço 5% |
| --- | ---: | --- | ---: | ---: |
| Accelo 1117/39 | 3 | Palmas, Anápolis, Aparecida | R$ 342.180,45–365.439,47 | R$ 388.700,00–409.000,00 |
| Accelo 1117/46 | 8 | Aparecida, Palmas | R$ 347.115,81–374.554,69 | R$ 389.000,00–415.000,00 |
| Accelo 1417/46 | 1 | Anápolis | R$ 401.586,67 | R$ 456.500,00 |
| Accelo 817/39 | 1 | Anápolis | R$ 305.705,72 | R$ 346.000,00 |
| Accelo 817/46 | 1 | Barra | R$ 308.635,50 | R$ 346.000,00 |
| Accelo 917/39 | 1 | Palmas | R$ 332.134,87 | R$ 380.000,00 |
| Accelo 917/46 | 2 | Palmas, Anápolis | R$ 336.836,60–358.745,74 | R$ 385.500,00–402.000,00 |
| Actros 2653 S/36 | 6 | Aparecida, Palmas, Barra, Anápolis | R$ 859.972,34–868.544,02 | R$ 888.500,00–932.500,00 |
| Atego 1719/48 | 1 | Aparecida | R$ 464.347,00 | R$ 518.500,00 |
| Atego 2429/36 | 1 | Aparecida | R$ 473.815,64 | R$ 540.000,00 |
| Atego 2429/48 | 1 | Aparecida | R$ 499.542,53 | R$ 556.000,00 |
| Atego 3033/63 | 1 | Anápolis | R$ 622.573,49 | R$ 694.000,00 |

### Relação unitária do fallback

| Nº | Casa | Modelo | Variante | Ano | Chassi | Status | Valor NF | Preço 5% | Preço 10% | Dias |
| ---: | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Palmas | Accelo 1117/39 | 0071T | 25/26 | 9BM951104TB411758 | Liberado | R$ 342.180,45 | R$ 388.700,00 | R$ 412.500,00 | 511 |
| 2 | Anápolis | Accelo 1117/39 | 0403T | 26/26 | 9BM951104TB461732 | Reservado | R$ 365.439,47 | R$ 409.000,00 | R$ 432.000,00 | 69 |
| 3 | Aparecida | Accelo 1117/39 | 0510T | 26/26 | 9BM951104TB480167 | Liberado | R$ 356.807,29 | R$ 399.500,00 | R$ 422.500,00 | 8 |
| 5 | Aparecida | Accelo 1117/46 | 0110T | 25/26 | 9BM951104TB435012 | Liberado | R$ 347.213,34 | R$ 389.000,00 | R$ 413.000,00 | 342 |
| 6 | Aparecida | Accelo 1117/46 | 0224T | 25/26 | 9BM951104TB450554 | Liberado | R$ 347.115,81 | R$ 389.000,00 | R$ 413.000,00 | 251 |
| 7 | Aparecida | Accelo 1117/46 | 0224T | 25/26 | 9BM951104TB450590 | Liberado | R$ 347.115,81 | R$ 389.000,00 | R$ 413.000,00 | 251 |
| 8 | Aparecida | Accelo 1117/46 | 0224T | 25/26 | 9BM951104TB450525 | Vendido | R$ 347.115,81 | R$ 389.000,00 | R$ 413.000,00 | 251 |
| 9 | Aparecida | Accelo 1117/46 | 0208T | 25/26 | 9BM951104TB448297 | Liberado | R$ 347.115,81 | R$ 389.000,00 | R$ 413.000,00 | 251 |
| 10 | Aparecida | Accelo 1117/46 | 0388T | 26/26 | 9BM951104TB460629 | Liberado | R$ 370.833,31 | R$ 415.000,00 | R$ 438.500,00 | 8 |
| 17 | Aparecida | Accelo 1117/46 | 0583T | 26/27 | 9BM951104VB476944 | Liberado | R$ 374.554,69 | R$ 415.000,00 | R$ 438.500,00 | 8 |
| 19 | Palmas | Accelo 1117/46 | 0388T | 26/26 | 9BM951104TB460436 | Liberado | R$ 370.833,31 | R$ 415.000,00 | R$ 438.500,00 | 6 |
| 24 | Anápolis | Accelo 1417/46 | 0050T | 25/26 | 9BM951111TB406107 | Reservado | R$ 401.586,67 | R$ 456.500,00 | R$ 484.000,00 | 552 |
| 26 | Anápolis | Accelo 817/39 | 2171T | 26/26 | 9BM951102TB454540 | Reservado | R$ 305.705,72 | R$ 346.000,00 | R$ 363.500,00 | 190 |
| 33 | Barra | Accelo 817/46 | 2170T | 26/26 | 9BM951102TB454840 | Reservado | R$ 308.635,50 | R$ 346.000,00 | R$ 367.000,00 | 190 |
| 42 | Palmas | Accelo 917/39 | 00026T | 25/26 | 9BM951102TB413977 | Reservado | R$ 332.134,87 | R$ 380.000,00 | R$ 403.000,00 | 500 |
| 43 | Palmas | Accelo 917/46 | 00028T | 25/26 | 9BM951102TB406071 | Liberado | R$ 336.836,60 | R$ 385.500,00 | R$ 409.000,00 | 552 |
| 45 | Anápolis | Accelo 917/46 | 0204T | 26/26 | 9BM951102TB462440 | Reservado | R$ 358.745,74 | R$ 402.000,00 | R$ 425.000,00 | 69 |
| 46 | Aparecida | Actros 2653 S/36 | 8765T | 26/27 | 1677541857 | Vendido | R$ 868.544,02 | R$ 888.500,00 | R$ 945.000,00 | 0 |
| 48 | Aparecida | Actros 2653 S/36 | 9042T | 26/27 | 1677545263 | Liberado | R$ 859.972,34 | R$ 932.500,00 | R$ 980.000,00 | 0 |
| 49 | Aparecida | Actros 2653 S/36 | 9042T | 26/27 | 1677545265 | Liberado | R$ 859.972,34 | R$ 932.500,00 | R$ 980.000,00 | 0 |
| 50 | Palmas | Actros 2653 S/36 | 9042T | 26/27 | 1677545310 | Liberado | R$ 859.972,34 | R$ 932.500,00 | R$ 980.000,00 | 0 |
| 51 | Barra | Actros 2653 S/36 | 9040T | 26/27 | 1677545273 | Liberado | R$ 859.972,34 | R$ 932.500,00 | R$ 980.000,00 | 0 |
| 52 | Anápolis | Actros 2653 S/36 | 9042T | 26/27 | 1677545282 | Liberado | R$ 859.972,34 | R$ 932.500,00 | R$ 980.000,00 | 0 |
| 55 | Aparecida | Atego 1719/48 | 9430T | 26/27 | 9BM951501VB477378 | Liberado | R$ 464.347,00 | R$ 518.500,00 | R$ 548.000,00 | 8 |
| 62 | Aparecida | Atego 2429/36 | 4353T | 26/26 | 9BM951511TB471850 | Liberado | R$ 473.815,64 | R$ 540.000,00 | R$ 571.000,00 | 24 |
| 69 | Aparecida | Atego 2429/48 | 3857T | 25/26 | 9BM951511TB431250 | Vendido | R$ 499.542,53 | R$ 556.000,00 | R$ 590.000,00 | 371 |
| 72 | Anápolis | Atego 3033/63 | 1832T | 26/26 | 9BM951544TB462813 | Reservado | R$ 622.573,49 | R$ 694.000,00 | R$ 733.500,00 | 6 |

---

## 10. Regras do estoque

### Situações

- `LIBERADO`: disponível para simulação e venda.
- `RESERVADO`: permanece consultável; exibe cliente/casa da reserva; exige atenção antes de simular.
- `VENDIDO`: permanece consultável para histórico/referência, com aviso visual.
- Situação desconhecida: tratada como `SEM STATUS`, sem assumir disponibilidade.

### Idade do estoque

- Até 180 dias: estado normal.
- Acima de 180 dias: atenção.
- Acima de 360 dias: crítico.
- Dias negativos ou inválidos: normalizados e sinalizados para revisão.

### Preço inicial da simulação

Prioridade:

1. Margem 5%.
2. Campanha.
3. Margem 10%.
4. Zero, exigindo entrada manual.

O vendedor poderá alternar entre Campanha, Margem 5% e Margem 10% sem perder os demais dados importados.

### Conversão de fundos

- Fundo fixo entre `0` e `1`: interpretado como percentual decimal.
- Fundo fixo maior que `1`: interpretado como percentual já convertido.
- Fundo variável entre `0` e `1`: convertido em valor usando o Valor NF.
- Fundo variável maior que `1`: tratado como valor monetário.

---

## 11. Interface definida

### Direção visual

- Estética industrial refinada Mercedes-Benz.
- Fundo grafite/preto fosco.
- Superfícies de alto contraste.
- Azul técnico como cor de ação.
- Verde para resultado saudável/liberado.
- Âmbar para atenção/reserva/margem abaixo da meta.
- Vermelho para prejuízo, falha ou estoque crítico.
- Tipografia clara, compacta e apropriada para leitura em campo.

### Tela de estoque — celular

- Cabeçalho com nome do produto e estado da sincronização.
- Campo de busca em destaque.
- Chips roláveis de casa e situação.
- KPIs compactos.
- Cartões verticais contendo:
  - situação;
  - casa;
  - modelo e variante;
  - ano;
  - chassi;
  - Valor NF;
  - preço Margem 5%;
  - dias em estoque.
- Detalhe em folha inferior/modal acessível.
- Botão `Simular rentabilidade`.

### Tela de estoque — desktop

- Tabela com cabeçalho fixo.
- Filtros completos.
- Painel lateral de detalhes.
- Destaque da linha selecionada.

### Tela de simulação

- Identificação do caminhão sempre visível.
- Casa de origem somente leitura.
- Destino obrigatório.
- Campos comerciais em primeiro nível.
- Regras tributárias dentro de seção avançada.
- Cartão de resultado com margem em R$ e %.
- Semáforo comparando resultado e meta.
- Preço mínimo.
- Comissão total.
- Memória de cálculo expansível.
- Botões para restaurar valores do estoque, salvar, copiar e imprimir.

---

## 12. Estados de sincronização

| Estado | Significado | Comportamento |
| --- | --- | --- |
| Atualizando | Requisição em andamento | Mantém estoque atual visível |
| Atualizado | Carga remota válida | Exibe quantidade e horário |
| Cache | Remoto indisponível | Usa última carga válida |
| Base incorporada | Sem cache no primeiro uso | Usa os 27 veículos do fallback |
| Estrutura incompatível | CSV alterado/incompleto | Rejeita carga e preserva cache |

### Requisitos de rede

- Timeout padrão: 12 segundos.
- Cache HTTP desabilitado na requisição de atualização.
- Nova tentativa manual por botão.
- Sincronização automática na abertura.
- Interface nunca deverá ficar bloqueada aguardando a rede.

---

## 13. Segurança e red team

### Ameaças consideradas

- Alteração acidental da estrutura da planilha.
- Conteúdo malicioso em células.
- Fórmula injetada em exportação CSV.
- Dados parciais substituindo estoque válido.
- Regra fiscal aplicada por correspondência imprecisa.
- Valores infinitos, negativos ou absurdos.
- Comissão negativa não intencional.
- Cache corrompido.
- Falha de rede durante a atualização.

### Controles

- Whitelist de host Google configurado.
- Somente HTTP GET.
- Limite de CSV: 5 MB.
- Limite de linhas: 10.000.
- Validação de campos críticos.
- Textos externos inseridos por `textContent` ou escapados.
- Nenhuma execução de HTML vindo da planilha.
- Proteção de exportação contra valores iniciados em `=`, `+`, `-` ou `@`.
- Dados remotos validados completamente antes de gravar cache.
- Cache versionado.
- Origem/destino com correspondência exata.
- Valores monetários e taxas dentro de limites explícitos.
- Resultado financeiro imutável após cada cálculo.
- Mensagens de erro sem dados internos sensíveis.

---

## 14. Persistência e exportação

### Dados locais

- Último estoque remoto válido.
- Data e origem da atualização.
- Última simulação.
- URL pública configurada para o estoque.
- Preferências de visualização.

### Não armazenar

- Senhas.
- Tokens.
- Chaves de API.
- Dados de cartão ou pagamento.
- Credenciais Google.

### Resumo copiável/imprimível

Deverá conter:

- modelo;
- variante;
- ano;
- chassi;
- casa de origem;
- destino;
- cenário;
- custo;
- preço de venda;
- margem em R$;
- margem em %;
- meta;
- preço mínimo;
- comissão;
- data e hora;
- aviso: `Simulação comercial — confirmar regras fiscais vigentes`.

---

## 15. Acessibilidade e responsividade

- Idioma da página: `pt-BR`.
- Largura mínima: 320 px.
- Foco visível.
- Navegação por teclado.
- Rótulos permanentes em campos.
- `inputmode="decimal"` para valores.
- Regiões de atualização com `aria-live`.
- Cores sempre acompanhadas por texto ou ícone.
- Respeito a `prefers-reduced-motion`.
- Impressão limpa em A4.
- Breakpoints de validação: 320, 360, 390, 768, 1024 e 1440 px.

---

## 16. Plano de implementação

### Fase 1 — Motor financeiro

- Estruturar os seis cenários.
- Implementar seleção exata de rota.
- Implementar créditos, débitos, margem, preço mínimo e comissão.
- Implementar limites e validações.
- Criar casos de ouro do XLS.

### Fase 2 — Motor de estoque

- Implementar parser CSV completo.
- Mapear cabeçalhos por alias.
- Converter moedas, percentuais e datas.
- Validar carga.
- Deduplicar por chassi.
- Implementar cache seguro.

### Fase 3 — Interface móvel de estoque

- Construir cabeçalho e estado de sincronização.
- Construir busca e filtros.
- Construir KPIs.
- Construir cartões móveis e tabela desktop.
- Construir detalhe do veículo.

### Fase 4 — Integração da calculadora

- Preencher simulação pelo veículo.
- Selecionar destino e cenário.
- Atualizar resultados instantaneamente.
- Exibir memória de cálculo.
- Implementar semáforo de margem.

### Fase 5 — Contingência e saída

- Persistir estoque e simulação.
- Implementar estados de falha.
- Implementar cópia do resumo.
- Implementar impressão A4.
- Documentar publicação e uso.

### Fase 6 — Verificação final

- Testes financeiros.
- Testes de importação.
- Testes de segurança.
- Testes de acessibilidade.
- Testes responsivos.
- Teste completo com e sem rede.

---

## 17. Matriz de testes financeiros

### Casos obrigatórios

- Um caso preenchido para cada um dos seis cenários.
- Caso de Anápolis reproduzindo:
  - custo: R$ 291.970,47;
  - venda: R$ 330.000,00;
  - frete: R$ 3.992,45;
  - margem esperada: aproximadamente R$ 17.885,74;
  - margem esperada: aproximadamente 5,42%;
  - comissão esperada: aproximadamente R$ 1.335,31.
- Venda zero.
- Custo zero.
- Fundo fixo ausente.
- Fundo fixo explicitamente zero.
- Crédito outorgado e Protege.
- Comissão negativa bloqueada.
- Despesa negativa rejeitada.
- Valor acima do limite.
- Taxa negativa ou acima de 100%.
- Preço mínimo recalculado atingindo a meta.
- Rota inválida rejeitada.

### Tolerância

- Valores monetários: R$ 0,02.
- Percentuais: 0,01 ponto percentual.

---

## 18. Critérios de aceite

O software será considerado aprovado quando:

- abrir sem depender da internet;
- exibir imediatamente o cache ou fallback;
- atualizar automaticamente o estoque publicado;
- nunca escrever no Google Sheets;
- rejeitar CSV incompatível sem perder o estoque anterior;
- permitir busca e filtros no celular;
- selecionar um caminhão e preencher a simulação;
- aplicar a regra correta por origem e destino;
- calcular margem, meta, preço mínimo e comissão;
- exibir memória de cálculo auditável;
- impedir correspondência fiscal parcial;
- funcionar sem rolagem horizontal em 320 px;
- copiar e imprimir o resumo;
- manter todos os testes automatizados aprovados;
- exibir claramente a data/hora da fonte de estoque.

---

## 19. Dependências operacionais

Para a sincronização automática funcionar em produção:

1. A planilha deve ser compartilhada como leitura.
2. A aba de estoque deve ser publicada na Web em CSV.
3. A republicação automática deve permanecer habilitada.
4. A URL CSV publicada deve ser configurada no software.
5. A planilha não deve expor informações confidenciais que não possam ser públicas.
6. Alterações de cabeçalho devem ser coordenadas com a aplicação.

---

## 20. Decisões fechadas

- Escopo atual: somente Estoque + Calculadora.
- Interface: estoque primeiro.
- Plataforma: web responsiva e mobile-first.
- Fonte de dados: Google Sheets somente leitura.
- Contingência: cache local + 27 veículos incorporados.
- Regra fiscal: casa de origem + destino.
- Fórmulas: fórmulas efetivas do XLS, não apenas rótulos.
- Comissão negativa: bloqueada por padrão.
- Rota desconhecida: não inferir.
- Dados remotos inválidos: não substituir cache.
- Entrega: aplicação estática sem backend obrigatório.

---

## 21. Estado técnico registrado

O motor financeiro já foi iniciado em branch isolada e possui 31 testes automatizados aprovados, incluindo correções de correspondência exata de rotas, fundo fixo zero, limites financeiros, preço mínimo e despesas negativas. As etapas de sincronização completa, interface de estoque e integração visual permanecem descritas neste plano para execução posterior.

