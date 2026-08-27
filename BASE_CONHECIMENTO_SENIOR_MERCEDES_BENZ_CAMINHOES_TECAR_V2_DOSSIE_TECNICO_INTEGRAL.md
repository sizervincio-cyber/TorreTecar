# Base de Conhecimento Sênior - Mercedes-Benz Caminhões - Versão 2.0

**Auditoria técnica integral, engenharia de aplicação, vendas consultivas, treinamento, marketing de concessionária, inteligência de dados e governança comercial**

| Controle | Informação |
|---|---|
| Versão | 2.0 - Dossiê técnico integral |
| Data de consolidação | 03/08/2026 |
| Território prioritário | Goiânia, Aparecida de Goiânia e Anápolis - GO |
| Público interno | Gestão comercial, grandes contas, consultores, marketing, CRM, produto, pós-venda, peças, serviços, financiamento e treinamento |
| Fontes primárias | 33 fichas técnicas em PDF e 1 arquivo textual do pacote `prospectos.zip` |
| Fontes oficiais complementares | Mercedes-Benz Trucks Brasil, consultadas em 03/08/2026 |
| Classificação | Uso interno. Conteúdo técnico sujeito à ficha vigente, disponibilidade fabril, homologação, legislação e configuração final do veículo |

> **Regra de precedência:** em qualquer divergência, prevalecem a ficha técnica vigente do chassi exato, o Manual de Implementação, o pedido comercial aprovado, a legislação aplicável e a confirmação formal da Mercedes-Benz/concessionária. Esta base não substitui engenharia de aplicação, homologação de implemento, cotação, contrato, manual do veículo ou treinamento oficial da marca.


## Revisão Red Team da versão 2.0

A versão anterior era adequada como base estratégica, mas insuficiente para funcionar como repositório técnico de produto. Ela resumia famílias e configurações, porém não preservava integralmente todas as variações de entre-eixos, pesos por eixo, cabines, transmissões, relações de eixo, tanques, pneus, capacidades de subida e sistemas de segurança presentes em cada prospecto.

Esta versão corrige a lacuna com os seguintes controles:

- **31 dossiês técnicos únicos**, correspondentes às configurações não duplicadas do pacote;
- **66 páginas renderizadas e verificadas visualmente**;
- separação entre **dado literal do prospecto**, interpretação comercial e recomendação operacional;
- rastreabilidade por **arquivo de origem, versão, data e SHA-256**;
- preservação de variações por entre-eixos e de marcações de opcional (`*`) e indisponibilidade (`nd`);
- registro explícito de que desempenho é teórico e condicionado às premissas da própria ficha;
- ausência de preenchimento por inferência: dado não publicado permanece não declarado.

### Parecer crítico

O pacote é tecnicamente rico, mas não deve ser tratado como configurador comercial definitivo. Um prospecto descreve possibilidades e referências de produto; não confirma disponibilidade fabril, combinação válida de opcionais, compatibilidade com implemento, capacidade legal final, prazo, preço ou desempenho real na operação. Toda proposta deve passar por validação da configuração exata, engenharia de aplicação, legislação e pedido comercial.

---

## 1. Resumo executivo

Esta base transforma um conjunto disperso de prospectos em um sistema de conhecimento utilizável por vendas, gestão, treinamento e marketing. O material recebido contém boa profundidade técnica e datas recentes, mas não está pronto para uso corporativo sem governança: existem arquivos duplicados, nomes em UUID, erros de codificação, grafias inconsistentes e fichas de 2024 misturadas a fichas de 2026.

**Conclusões principais:**

1. **Cobertura técnica forte:** o pacote contempla 31 configurações únicas das famílias Accelo, Atego, Axor e Actros, com motor, potência, torque, transmissões, dimensões, pesos, pneus, freios, segurança e observações de configuração.
2. **Governança insuficiente:** há 33 PDFs, porém apenas 32 binários únicos e 31 conteúdos técnicos únicos. Um PDF é cópia binária exata e outro conteúdo aparece em dois PDFs diferentes.
3. **Risco comercial relevante:** preço, consumo real, prazo, disponibilidade de opcionais, capacidade legal final e compatibilidade com implemento não podem ser prometidos a partir de um prospecto genérico.
4. **Oportunidade de gestão:** a combinação de diagnóstico operacional, TCO, FleetBoard, Uptime, plano de manutenção, peças, financiamento e seminovos permite vender uma solução de disponibilidade e rentabilidade, não apenas o chassi.
5. **Treinamento deve ser orientado a aplicação:** conhecer potência e torque é necessário, mas insuficiente. O consultor deve dominar operação, carga, rota, implemento, legislação, ciclo financeiro, disponibilidade e custo por quilômetro.
6. **Marketing para grandes contas deve operar por ABM:** campanhas por segmento e conta-alvo, usando evidências operacionais, casos, dados de frota, janela de renovação e conteúdo técnico aprovado.

### Nota de maturidade da base recebida

A pontuação abaixo é uma avaliação interna desta auditoria, não um índice oficial da Mercedes-Benz.

| Dimensão | Nota /100 | Diagnóstico |
|---|---:|---|
| Proveniência técnica | 95 | Fichas de Marketing de Produto/Caminhões e conteúdo oficial; boa rastreabilidade interna |
| Completude técnica | 82 | Ampla cobertura de produto, porém sem preços, estoque, opcionais por chassi, custos e dados de mercado |
| Unicidade | 90 | Baixa duplicidade, mas há uma cópia binária e um conteúdo repetido em exportações distintas |
| Padronização de nomes | 55 | UUIDs, codificação `T#U00e9cnica`, grafias inconsistentes e ausência de taxonomia documental |
| Controle de versão | 65 | Datas e versões existem nas fichas, mas não há índice mestre, vigência, substituição ou histórico formal |
| Prontidão para CRM/BI | 60 | Conteúdo rico, porém predominantemente não estruturado em PDF/TXT |
| **Índice geral indicativo** | **76** | **Base tecnicamente valiosa, mas exige normalização, governança e atualização contínua** |

---

## 2. Escopo, método e níveis de confiança

### 2.1 Escopo da auditoria

Foram executadas as seguintes atividades:

- inventário de arquivos e formatos;
- extração textual das fichas técnicas;
- identificação de modelo, configuração, data e versão;
- cálculo de hash SHA-256 para detecção de cópias exatas;
- comparação de conteúdo para identificar duplicidade semântica;
- consolidação de motor, potência, torque e transmissão por configuração;
- análise de consistência, nomenclatura, vigência e risco de uso;
- complementação com páginas oficiais recentes da Mercedes-Benz Trucks Brasil;
- construção de playbooks de aplicação, venda, treinamento, marketing, CRM e KPIs.

### 2.2 Hierarquia de confiança

| Nível | Uso permitido | Exemplo |
|---|---|---|
| **A - Confirmado em ficha do chassi** | Proposta técnica preliminar, comparação e treinamento, sempre preservando notas e opcionais | Potência, torque, motor, transmissão, dimensões e pesos da ficha vigente |
| **B - Confirmado em página oficial** | Posicionamento de linha, serviços, aplicações recomendadas e benefícios institucionais | FleetBoard, Uptime, retorno do Axor, posicionamento de aplicação |
| **C - Inferência consultiva** | Diagnóstico e hipótese comercial; requer validação com cliente e engenharia | Melhor aderência de um modelo a uma rota ou perfil de carga |
| **D - Não disponível** | Não prometer nem estimar sem base específica | Preço final, consumo garantido, prazo fabril, valor de revenda futuro, aprovação de crédito |

### 2.3 Limitações

- Não foram fornecidos preços, custos de manutenção, tabela de opcionais, estoque, leads, histórico de vendas, emplacamentos, dados de concorrentes ou CRM.
- Não foi fornecido manual visual oficial da marca ou da Tecar; as orientações de marketing são operacionais e precisam de aprovação institucional.
- A matriz técnica abaixo é uma síntese. Pesos, dimensões, pneus, relações de eixo, CMT, PBTC e itens de segurança variam por entre-eixos, eixo, cabine, câmbio e opcionais.
- Fichas de 2024 podem representar linha anterior ainda presente no acervo. Antes de usar comercialmente, confirmar se o modelo está vigente, em estoque, sob encomenda ou descontinuado.

---

## 3. Auditoria dos dados e documentos

### 3.1 Inventário

- **34 arquivos úteis:** 33 PDFs e 1 TXT.
- **32 PDFs binariamente únicos.**
- **31 conteúdos técnicos/configurações únicos.**
- **1 duplicidade binária exata:** duas cópias do Accelo 1317.
- **1 duplicidade semântica:** duas exportações do Novo Atego 2433 com texto extraído idêntico, embora os arquivos tenham hashes diferentes.
- **15 PDFs com nomes UUID**, dificultando busca, versionamento e uso por humanos.
- **Datas das fichas:** de 09/06/2024 a 30/07/2026.

### 3.2 Achados críticos

| ID | Achado | Severidade | Impacto | Ação recomendada |
|---|---|---|---|---|
| DQ-01 | Mistura de fichas 2024 e 2026 sem status de vigência | Alta | Uso de produto antigo em proposta ou treinamento | Criar campo `status_vigencia` e revisão mensal com Produto |
| DQ-02 | Arquivos UUID sem identificação humana | Alta | Busca lenta, erro de anexação e baixa rastreabilidade | Renomear conforme padrão documental |
| DQ-03 | Duplicidades exata e semântica | Média | Contagem errada, versões paralelas e atualização divergente | Manter uma fonte mestre e arquivar cópias |
| DQ-04 | Grafias inconsistentes: BlueTec, PowerShift Advanced e nomes de arquivos | Média | Falha em pesquisa, filtros e comunicação externa | Normalizar metadados, sem alterar o PDF original |
| DQ-05 | Opcionais marcados por `*` podem não estar disponíveis | Alta | Promessa comercial incorreta | Validar configuração e disponibilidade antes da proposta |
| DQ-06 | Pesos legais e técnicos podem divergir | Crítica | Risco de não conformidade e dimensionamento incorreto | Usar sempre o menor limite aplicável e validar engenharia/legislação |
| DQ-07 | Ausência de índice mestre e substituição de versões | Alta | Ficha antiga continua circulando | Implantar catálogo com `vigente`, `substituída`, `sob revisão` e `arquivada` |
| DQ-08 | Conteúdo técnico em PDF não estruturado | Média | Dificulta CRM, BI, comparação e automação | Extrair atributos para tabela mestre com origem e data |

### 3.3 Padrão documental recomendado

**Nome do arquivo:**

```text
MB_<FAMILIA>_<MODELO>_<CONFIGURACAO>_<AAAA-MM-DD>_<VERSAO>_<STATUS>.pdf
```

Exemplo:

```text
MB_ACTROS_2653_S_6X4_2026-06-16_V2-26_VIGENTE.pdf
```

**Metadados mínimos:**

- família;
- modelo;
- configuração de tração/suspensão;
- cabine;
- norma de emissões;
- data da ficha;
- versão;
- status de vigência;
- substitui qual documento;
- responsável pela validação;
- data da última revisão;
- URL oficial ou origem;
- hash do arquivo.

### 3.4 Testes automáticos recomendados

1. unicidade do par `modelo + configuração + versão + data`;
2. hash duplicado;
3. campos obrigatórios não nulos;
4. data futura ou ficha com mais de 12 meses sem revisão;
5. enumeração controlada para família, tração, cabine e emissões;
6. potência e torque em faixas plausíveis;
7. opcionais preservados com marcação explícita;
8. bloqueio de publicação externa quando `status_vigencia != vigente`;
9. alerta de divergência entre ficha local e página oficial;
10. log de quem aprovou cada atualização.

---

## 4. Regras de uso seguro em vendas e marketing

### 4.1 O que pode ser afirmado

- atributos presentes na ficha exata e vigente;
- aplicações indicadas em página oficial;
- recursos de peças e serviços confirmados pela Mercedes-Benz;
- cálculos de TCO com premissas explícitas e dados do cliente;
- resultados de testes conduzidos e documentados com a operação real.

### 4.2 O que exige validação antes de comunicar

- disponibilidade imediata de veículo ou opcional;
- prazo de entrega;
- preço, taxa financeira, parcela e condição de crédito;
- consumo de combustível;
- produtividade, economia ou redução de manutenção;
- capacidade legal final após implemento;
- compatibilidade de tomada de força, tanque, entre-eixos, quinta roda e carroceria;
- homologação para aplicação especial;
- valor de revenda futuro;
- emissão de CO2 evitada.

### 4.3 Linguagem recomendada

Use:

- “A ficha técnica vigente informa...”
- “Na configuração analisada...”
- “O resultado depende da rota, carga, condução, implemento e manutenção.”
- “Vamos validar a aplicação com Engenharia/Produto antes do pedido.”
- “A simulação de TCO utiliza as premissas fornecidas pelo cliente.”

Evite:

- “É o mais econômico” sem estudo comparativo válido;
- “Faz X km/l” como garantia;
- “Carrega X toneladas” sem descontar tara, implemento e limites legais;
- “Tem todos os opcionais”;
- “Aprovação garantida”;
- “Entrega certa em determinada data” sem confirmação formal.

---

## 5. Fundamentos técnicos para o time comercial

### 5.1 Glossário essencial

| Termo | Definição operacional | Por que importa na venda |
|---|---|---|
| PBT | Peso Bruto Total do veículo | Limita o peso total do caminhão carregado |
| PBTC | Peso Bruto Total Combinado | Limita a composição com reboque/semirreboque |
| CMT | Capacidade Máxima de Tração | Capacidade técnica de tração; não substitui limite legal |
| Tara | Peso do veículo em ordem de marcha | Base para estimar carga útil após implemento e acessórios |
| Carga útil | PBT legal aplicável menos tara, implemento, ocupantes e acessórios | Indicador real de produtividade por viagem |
| Entre-eixos | Distância entre eixos de referência | Afeta implemento, distribuição de peso, raio de giro e manobrabilidade |
| 4x2 | Dois eixos, um eixo motriz | Aplicações urbanas/rodoviárias conforme peso e tração necessária |
| 6x2 | Três eixos, um conjunto motriz com eixo auxiliar | Maior capacidade legal, distribuição de carga e variedade de implementos |
| 6x4 | Três eixos, dois eixos motrizes | Maior tração para cargas pesadas, aclives e operações severas |
| 8x2 | Quatro eixos, configuração voltada a capacidade/distribuição | Aplicações de maior volume/peso com validação de implemento |
| Potência (cv) | Capacidade de realizar trabalho ao longo do tempo | Afeta desempenho em velocidade e produtividade |
| Torque (Nm) | Força de rotação disponível | Importante em arrancadas, aclives e carga elevada |
| Relação de eixo | Multiplicação final entre transmissão e rodas | Altera equilíbrio entre força, rotação e velocidade |
| PowerShift/AMT | Câmbio automatizado sem pedal de embreagem | Padroniza condução, reduz esforço e pode apoiar eficiência |
| BlueTec 6 / P-8 | Tecnologia de emissões associada ao PROCONVE P-8 | Exige diesel e ARLA 32 adequados e manutenção correta |
| ARLA 32 | Agente redutor usado no pós-tratamento | Operação sem ARLA adequado gera falhas e perda de desempenho |
| `*` | Item opcional | Não presumir disponibilidade nem inclusão no preço |
| `nd` | Não disponível | Não tratar como zero nem como ausência de dado genérica |
| S/LS do modelo | Designação de configuração do chassi/suspensão conforme família | Não confundir com siglas de cabine Space/TopSpace |
| C/E/LTB/LTA/S/TS | Abreviações de cabine nas fichas | Afetam conforto, altura, peso, aplicação e preço |

### 5.2 Regra de dimensionamento

A seleção correta segue esta sequência:

```text
Operação -> carga -> rota -> legislação -> implemento -> distribuição de peso
-> tração -> potência/torque -> transmissão/relação -> cabine -> autonomia
-> segurança -> serviços -> custo total -> configuração final
```

Começar pelo modelo preferido do cliente e tentar “encaixar” a operação depois é uma prática de alto risco.

---

## 6. Arquitetura do portfólio

### 6.1 Accelo

**Papel na carteira:** distribuição urbana e regional leve/média, com foco em manobrabilidade, capacidade de carga e facilidade de operação.

**Evidências do pacote:** motores OM 924 de 4,8 litros, 163 cv e 610 Nm nas fichas analisadas; versões 4x2 e 6x2; opções manuais e automatizadas conforme modelo; cabines curta/estendida conforme ficha.

**Principais aplicações a investigar:** carga seca urbana, alimentos e bebidas, e-commerce, varejo, atacado, serviços, distribuição farmacêutica, mudanças, gás e operações rurais leves. A aplicação final depende de peso, volume, legislação municipal e carroceria.

**Perguntas decisivas:**

- Quantas entregas por rota e quantas paradas?
- Há restrição de circulação, altura ou comprimento?
- A carga é limitada por peso ou por volume?
- Qual a tara real do implemento?
- Existe doca, rampa, plataforma elevatória ou necessidade de refrigeração?
- O veículo retorna vazio ou carregado?

### 6.2 Atego

**Papel na carteira:** plataforma versátil para operações urbanas, regionais, rodoviárias e configurações vocacionais, com ampla faixa de potência e tração.

**Evidências do pacote:** motores OM 924 e OM 926, de 185 a 321 cv e 700 a 1.250 Nm; configurações 4x2, 6x2, 6x4 e 8x2 nas fichas recebidas; transmissões manuais e PowerShift 3 Advanced conforme versão.

**Principais aplicações a investigar:** distribuição pesada, bebidas, carga seca, frigorificada, coleta de resíduos, baú, sider, tanque, basculante, betoneira, construção, agro e serviços especiais. Aplicações vocacionais exigem engenharia.

### 6.3 Axor

**Papel na carteira:** transporte rodoviário de média e longa distância com proposta de robustez, simplicidade operacional e baixo custo de operação.

**Evidências oficiais recentes:** a Mercedes-Benz relançou a linha no Brasil em 2025 e ampliou o portfólio em 2026 com suspensão traseira pneumática para 2038 e 2545, mantendo versões metálicas; as páginas oficiais posicionam 2038 4x2 e 2545 6x2 para cargas volumosas, fracionadas e densas. As fichas recebidas também incluem 2538 S 6x2.

**Ponto de venda:** separar claramente a proposta **S/metálica** da **LS/pneumática**, considerando preservação de carga, conforto, manutenção, tara, disponibilidade e aplicação.

### 6.4 Actros

**Papel na carteira:** extrapesados rodoviários e operações de alta produtividade, com maior conteúdo de conforto, conectividade e sistemas avançados de segurança conforme configuração.

**Evidências do pacote:** motores OM 460 e OM 471 de 449 a 530 cv, torques de 2.200 a 2.600 Nm, câmbios PowerShift 3 Advanced, configurações 4x2, 6x2 e 6x4 e variantes S/LS. A ficha do Actros 2653 S apresenta alternativas capazes de atender CMT técnico elevado sob condições específicas; nunca converter isso automaticamente em capacidade legal de operação.

**Ponto de venda:** produtividade deve ser demonstrada em custo por quilômetro, tempo de ciclo, disponibilidade, segurança, consumo medido e retenção de motorista.

---

## 7. Matriz técnica consolidada

> Esta matriz resume campos de alta confiança extraídos das fichas. A transmissão pode conter mais de uma alternativa e itens opcionais. Para pedido, use a ficha original e confirme o código de configuração.


### 7.1 Accelo

| Modelo | Configuração | Motor | Potência | Torque | Transmissão documentada | Data da ficha |
| --- | --- | --- | --- | --- | --- | --- |
| Accelo 1017 | 4x2 | OM924LA | 163 cv | 610 Nm | MB G 70-6 MB G 70-6 PowerShift 3 | 09/06/2024 |
| Accelo 1117 | 4x2 | OM924LA | 163 cv | 610 Nm | EATON ESO 6206 A MB G 90-6 AMT* | 27/07/2026 |
| Accelo 1317 | 6x2 | OM924LA | 163 cv | 610 Nm | MB G 70-6 MB G 70-6 PowerShift 3 | 08/07/2026 |
| Accelo 1417 | 6x2 | OM924LA | 163 cv | 610 Nm | EATON ESO 6206 MB G 90-6 AMT * | 28/07/2026 |
| Accelo 817 | 4x2 | OM924LA | 163 cv | 610 Nm | EATON ESO 6205 MB G 70-6 MB G 70-6 PowerShift 3 | 09/06/2024 |
| Accelo 917 | 4x2 | OM924LA | 163 cv | 610 Nm | EATON ESO 6205 | 30/04/2026 |


### 7.2 Atego

| Modelo | Configuração | Motor | Potência | Torque | Transmissão documentada | Data da ficha |
| --- | --- | --- | --- | --- | --- | --- |
| Atego 1419 | 4x2 | OM924LA | 185 cv | 700 Nm | EATON FOSA 5406A MB G 140-8* PowerShift 3 Advanced | 29/07/2026 |
| Atego 1719 | 4x2 | OM924LA | 185 cv | 700 Nm | MB G 90-6 MB G 140-8* PowerShift 3 Advanced | 19/07/2026 |
| Atego 1719 | 4x2 K | OM924LA | 185 cv | 700 Nm | MB G 90-6 MB G 140-8* PowerShift 3 Advanced | 30/07/2026 |
| Atego 1726 | 4x2 | OM926LA | 260 cv | 900 Nm | MB G 90-6 MB G 140-8* PowerShift 3 Advanced | 03/02/2026 |
| Atego 1726 | K 4x2 | OM926LA | 260 cv | 900 Nm | MB G 90-6 MB G 140-8* PowerShift 3 Advanced | 03/02/2026 |
| Atego 2429 | 6x2 | OM926LA | 286 cv | 1100 Nm | MB G 140-8 PowerShift 3 Advanced | 11/03/2026 |
| Atego 2429 | K 6x2 | OM926LA | 286 cv | 1100 Nm | MB G 140-8 PowerShift 3 Advanced | 11/03/2026 |
| Atego 2433 | 6x2 | OM926LA | 321 cv | 1250 Nm | MB G 211-12 PowerShift 3 Advanced | 25/02/2026 |
| Atego 3033 | 8x2 | OM926LA | 321 cv | 1250 Nm | MB G 211-12 PowerShift 3 Advanced | 27/04/2026 |
| Atego 3133 | 6x4 | OM926LA | 321 cv | 1250 Nm | MB G 211-12 PowerShift 3 Advanced | 06/07/2026 |


### 7.3 Axor

| Modelo | Configuração | Motor | Potência | Torque | Transmissão documentada | Data da ficha |
| --- | --- | --- | --- | --- | --- | --- |
| Axor 2038 | LS 4x2 | OM460LA | 381 cv | 1900 Nm | MB G 291-12 PowerShift 3 Advanced | 23/01/2026 |
| Axor 2038 | S 4x2 | OM460LA | 381 cv | 1900 Nm | MB G 291-12 PowerShift 3 Advanced MB G 340-12 PowerShift 3 Advanced* | 23/01/2026 |
| Axor 2538 | S 6x2 | OM460LA | 381 cv | 1900 Nm | MB G 291-12 PowerShift 3 Advanced MB G 340-12 PowerShift 3 Advanced * | 23/01/2026 |
| Axor 2545 | LS 6x2 | OM460LA | 449 cv | 2200 Nm | MB G 291-12 PowerShift 3 Advanced | 23/01/2026 |
| Axor 2545 | S 6x2 | OM460LA | 449 cv | 2200 Nm | MB G 291-12 PowerShift 3 Advanced MB G 340-12 PowerShift 3 Advanced* | 23/01/2026 |


### 7.4 Actros

| Modelo | Configuração | Motor | Potência | Torque | Transmissão documentada | Data da ficha |
| --- | --- | --- | --- | --- | --- | --- |
| Actros 2045 | LS 4x2 | OM460LA | 449 cv | 2200 Nm | MB G 291-12 Powershift 3 Advanced | 16/06/2026 |
| Actros 2045 | S 4x2 | OM460LA | 449 cv | 2200 Nm | MB G 291-12 Powershift 3 Advanced | 16/06/2026 |
| Actros 2548 | LS 6x2 | OM460LA | 476 cv | 2300 Nm | MB G 291-12 Powershift 3 Advanced | 16/06/2026 |
| Actros 2548 | S 6x2 | OM460LA | 476 cv | 2300 Nm | MB G 291-12 Powershift 3 Advanced MB G 340-12 Powershift 3 Advanced* | 16/06/2026 |
| Actros 2553 | LS 6x2 | OM471LA | 530 cv | 2600 Nm | MB G 291-12 Powershift 3 Advanced | 16/06/2026 |
| Actros 2553 | S 6x2 | OM471LA | 530 cv | 2600 Nm | MB G 291-12 Powershift 3 Advanced MB G 340-12 Powershift 3 Advanced | 16/06/2026 |
| Actros 2651 | LS 6x4 | OM460LA | 495 cv | 2400 Nm | MB G 291-12 Powershift 3 Advanced | 16/06/2026 |
| Actros 2651 | S 6x4 | OM460LA | 495 cv | 2400 Nm | MB G 291-12 Powershift 3 Advanced MB G 340-12 Powershift 3 Advanced | 16/06/2026 |
| Actros 2653 | LS 6x4 | OM471LA | 530 cv | 2600 Nm | MB G 291-12 Powershift 3 Advanced | 16/06/2026 |
| Actros 2653 | S 6x4 | OM471LA | 530 cv | 2600 Nm | MB G 291-12 Powershift 3 Advanced MB G 340-12 Powershift 3 Advanced* | 16/06/2026 |


### 7.5 Leitura gerencial da matriz

- **Accelo:** todos os modelos analisados usam OM 924, 163 cv e 610 Nm; a diferenciação comercial está principalmente em PBT/configuração, transmissão, entre-eixos, pneus, cabine e aplicação.
- **Atego:** há dois degraus claros de motorização: OM 924 nos 1419/1719 e OM 926 nos 1726/2429/2433/3033/3133. A escolha deve ser feita por severidade, peso, topografia e ciclo, não apenas por potência.
- **Axor:** OM 460 em 381 ou 449 cv; versões S e LS devem ser comparadas pela suspensão e pelo perfil da carga/operação.
- **Actros:** OM 460 nas versões 2045, 2548 e 2651; OM 471 nas 2553 e 2653. Câmbio, eixo, suspensão e pacote de segurança mudam substancialmente a aplicação e o preço.

---

## 8. Matriz operação x solução

As recomendações abaixo são ponto de partida de diagnóstico, não prescrição final.

| Operação | Variáveis críticas | Família inicial | Condições de avanço | Riscos de erro |
|---|---|---|---|---|
| Entrega urbana com muitas paradas | VUC, raio de giro, plataforma, volume, acesso, automatização | Accelo | Medir rota, docas, tara e restrições | Comprar por PBT nominal sem calcular carga útil |
| Distribuição regional | Km/dia, aclive, carga média, retorno, cabine | Accelo/Atego | Simular tempo de ciclo e consumo | Subdimensionar motor/transmissão |
| Bebidas | Centro de gravidade, suspensão, entre-eixos, distribuição lateral | Atego | Validar implemento e carga por eixo | Excesso em eixo mesmo com PBT dentro do limite |
| Refrigerado | Tara alta, energia do equipamento, isolamento, tempo de porta aberta | Accelo/Atego/Axor | Calcular carga útil líquida e autonomia | Ignorar peso do equipamento frigorífico |
| Carga seca/baú/sider | Volume, densidade, altura, docas, rota | Atego/Axor | Comparar custo por m³ e por tonelada | Escolher só pela potência |
| Grãos e commodities | PBTC, topografia, piso, fila, sazonalidade, tara | Axor/Actros | Avaliar composição, relação e tração | Usar CMT técnico como limite legal |
| Contêiner | Peso do contêiner, porto, fila, acessos, cavalo 4x2/6x2 | Axor/Actros | Medir composição e jornada | Não considerar distribuição na quinta roda |
| Carga sensível/alto valor | Vibração, segurança, rastreamento, risco, SLA | Axor LS/Actros LS | Avaliar suspensão, FleetBoard e segurança | Vender só o veículo, sem gestão de risco |
| Longa distância | Km/mês, relevo, descanso, retenção, consumo, disponibilidade | Axor/Actros | TCO com telemetria e plano de manutenção | Comparar apenas preço de aquisição |
| Operação severa/mista | Piso, rampa, atoleiro, poeira, temperatura, velocidade média | Atego/Actros configurado | Engenharia de aplicação e teste | Usar versão rodoviária sem pacote adequado |
| Vocacional/especial | PTO, implemento, centro de gravidade, duty cycle | Atego e configurações dedicadas | Projeto conjunto com implementador | Fechar chassi antes do projeto do implemento |

### 8.1 Critérios de desqualificação técnica

Não emitir recomendação final quando faltar qualquer item abaixo:

- peso e dimensões da carga;
- tara do implemento;
- composição legal pretendida;
- rota e topografia;
- distância e velocidade média;
- quantidade de paradas e horas de operação;
- tipo de piso;
- requisitos de tomada de força;
- limites de altura, comprimento ou circulação;
- combustível/ARLA e infraestrutura;
- estimativa de km mensal/anual;
- validação de distribuição de peso por eixo.

---

## 9. Método de venda consultiva para grandes contas

### 9.1 Etapas do processo

1. **Inteligência da conta:** tamanho da frota, marcas, modelos, idade, rotas, segmento, emplacamentos, unidades e decisores.
2. **Qualificação:** janela de renovação, dor econômica, aderência técnica, acesso e capacidade financeira.
3. **Diagnóstico operacional:** levantamento estruturado de carga, rota, ciclo, custos, manutenção, motoristas e riscos.
4. **Engenharia de solução:** chassi + implemento + serviços + financiamento + telemetria + plano de manutenção.
5. **Business case:** TCO, disponibilidade, produtividade, risco e fluxo de caixa.
6. **Demonstração/teste:** protocolo com rota, carga e indicadores definidos.
7. **Proposta executiva:** comparação transparente, premissas, configuração, escopo e próximos gates.
8. **Negociação multilateral:** operação, manutenção, finanças, compras, diretoria e motoristas.
9. **Entrega e adoção:** checklist, treinamento e ativação de serviços.
10. **Revisão pós-venda:** 30, 60, 90 e 180 dias com dados reais.

### 9.2 Questionário de diagnóstico

#### Conta e estratégia

- Qual o objetivo da renovação: expansão, substituição, redução de custo, imagem, segurança ou contrato novo?
- Quantos veículos existem por marca, modelo, ano e configuração?
- Qual a política de renovação e idade média?
- Há contrato de frete com prazo definido?
- Quem aprova tecnicamente, financeiramente e comercialmente?

#### Operação

- Qual carga, densidade, embalagem e risco?
- Peso médio, máximo e frequência de pico?
- Quilômetros por dia, mês e ano?
- Quantas viagens, entregas e paradas?
- Rotas fixas ou variáveis?
- Percentual de rodovia, urbano, terra e pátio?
- Aclives, altitude, temperatura e chuva?
- Velocidade média e tempo parado?
- Retorno vazio, parcial ou carregado?

#### Implemento e legislação

- Tipo, fabricante, tara e dimensões do implemento?
- Há equipamento frigorífico, plataforma, guindaste ou PTO?
- Qual composição e limite legal?
- Há restrições municipais ou de doca?
- Como está a distribuição por eixo na operação atual?

#### Custos e desempenho

- Consumo médio por rota e por veículo?
- Preço de combustível e ARLA 32?
- Custo de manutenção por km?
- Custo de pneu por km?
- Dias de parada não programada?
- Custo de veículo reserva, atraso e multa?
- Valor de revenda e prazo de permanência?
- Custo financeiro e prazo de recebimento do frete?

#### Pessoas e segurança

- Perfil e rotatividade de motoristas?
- Dificuldade de recrutamento?
- Política de treinamento e bonificação?
- Índice de acidentes e eventos de condução?
- Necessidade de telemetria, rastreamento e gestão de risco?

### 9.3 Score de oportunidade

| Critério | Peso |
|---|---:|
| Aderência técnica da operação ao portfólio | 20 |
| Janela de renovação até 12 meses | 15 |
| Dor econômica mensurável | 15 |
| Potencial de volume | 15 |
| Acesso ao decisor e comitê de compra | 10 |
| Capacidade financeira/crédito | 10 |
| Abertura para Mercedes-Benz | 10 |
| Urgência ou contrato mobilizador | 5 |
| **Total** | **100** |

**Classificação:** A = 75-100; B = 55-74; C = 35-54; D = abaixo de 35.

### 9.4 Próxima ação obrigatória por estágio

| Estágio | Evidência mínima | Próxima ação |
|---|---|---|
| Prospecto | Conta identificada e fonte | Confirmar frota e contato |
| Qualificado | Score e janela de compra | Reunião de diagnóstico |
| Diagnóstico | Formulário operacional preenchido | Engenharia/TCO |
| Solução | Configuração preliminar validada | Proposta e demonstração |
| Proposta | Escopo, preço, prazo e premissas | Reunião com comitê |
| Negociação | Mapa de objeções e concorrência | Plano de fechamento |
| Fechado | Pedido/contrato aprovado | Entrega e adoção |
| Pós-venda | Veículo ativado e baseline | Revisão 30/60/90 dias |

---

## 10. TCO, ROI e business case

### 10.1 Fórmulas fundamentais

```text
Carga útil estimada = menor PBT aplicável
                     - tara do chassi configurado
                     - tara do implemento
                     - ocupantes, acessórios e fluidos adicionais
```

```text
Custo mensal de combustível = (km mensal / km por litro) x preço do litro
```

```text
Custo de manutenção mensal = km mensal x custo de manutenção por km
```

```text
Custo de indisponibilidade = dias parados x margem de contribuição diária perdida
                           + veículo reserva
                           + multas/atrasos
                           + custos emergenciais
```

```text
TCO do ciclo = aquisição líquida
             + custo financeiro
             + combustível
             + ARLA 32
             + manutenção
             + pneus
             + seguros
             + tributos/licenças
             + motoristas/treinamento
             + indisponibilidade
             - valor de revenda líquido
```

```text
Economia anual = TCO anual da alternativa atual - TCO anual da solução proposta
ROI = ganho líquido acumulado / investimento incremental
Payback = investimento incremental / economia mensal média
```

### 10.2 Regras de modelagem

- Use o mesmo horizonte, quilometragem, carga e rota para todas as alternativas.
- Separe fatos, dados do cliente, estimativas e cenários.
- Trabalhe com cenário conservador, base e otimista.
- Não use somente consumo; disponibilidade e produtividade podem ter impacto maior.
- Inclua efeito do prazo de recebimento do frete no capital de giro.
- Faça análise de sensibilidade para diesel, km/mês, valor de revenda e dias parados.
- Não compare preço de chassi sem equalizar implemento, serviços e escopo.

### 10.3 KPIs do teste comparativo

- km/l e litros/100 km;
- consumo por tonelada-km;
- velocidade média;
- tempo de ciclo;
- marcha lenta;
- eventos de frenagem/segurança;
- nota de condução;
- carga transportada;
- disponibilidade;
- custo por km;
- custo por tonelada ou m³;
- satisfação do motorista;
- ocorrências de manutenção.

---

## 11. Portfólio de serviços como parte da solução

A oferta deve ser desenhada em camadas:

### 11.1 Veículo e aplicação

- chassi e configuração;
- cabine, suspensão e transmissão;
- implemento e integração;
- pacote de segurança;
- treinamento de condução e operação.

### 11.2 Conectividade e disponibilidade

A página oficial do FleetBoard informa recursos como geolocalização, viagens, movimentação da frota, mapas, tempos de parada, velocidade, consumo, emissão de CO2, produtividade, avaliação do motorista, alertas, manutenção e integração com o Mercedes-Benz Trucks Uptime. Os intervalos e funcionalidades dependem do plano contratado.

**Uso comercial correto:** transformar telemetria em um plano de gestão com metas, responsáveis e rituais. Instalar tecnologia sem processo não garante economia.

### 11.3 Peças e manutenção

Fontes oficiais recentes citam quatro linhas de peças: Genuínas, Remanufaturadas Renov, Alliance e Select Parts, além de planos de manutenção. A modalidade Complete Flex foi divulgada com pagamento relacionado aos quilômetros rodados. Confirmar sempre oferta vigente e elegibilidade.

### 11.4 Financiamento, consórcio e seminovos

- Banco Mercedes-Benz: simulação conforme política e aprovação de crédito;
- Consórcio Mercedes-Benz: solução de planejamento, não promessa de contemplação;
- SelecTrucks: alternativa de seminovos e apoio à renovação;
- seguros e garantia estendida: validar cobertura, exclusões e vigência.

### 11.5 Matriz de cross-sell

| Dor do cliente | Solução complementar | Evidência a acompanhar |
|---|---|---|
| Alto consumo | FleetBoard + treinamento | consumo, faixa verde, marcha lenta |
| Paradas inesperadas | Uptime + plano de manutenção | alertas, disponibilidade, falhas evitadas |
| Custo imprevisível | Plano de manutenção/garantia | R$/km e variação mensal |
| Segurança de carga | Gestão de risco/telemetria | eventos, rotas, ocorrências |
| Falta de capital | financiamento/consórcio/locação quando disponível | parcela, fluxo e custo efetivo |
| Renovação da frota | novo + avaliação de usado/SelecTrucks | valor líquido e idade média |
| Retenção de motorista | cabine, conforto, segurança e coaching | turnover, satisfação e incidentes |

---

## 12. Objeções e respostas consultivas

| Objeção | Resposta recomendada | Evidência necessária |
|---|---|---|
| “Está mais caro.” | “Vamos comparar o custo do ciclo e a produtividade na sua rota, não apenas o preço inicial.” | TCO equalizado |
| “Minha marca atual já funciona.” | “O objetivo não é trocar por opinião; é testar onde existe ganho mensurável ou redução de risco.” | piloto controlado |
| “Não acredito no consumo.” | “Não vou prometer um número genérico. Vamos medir com carga, rota e motorista definidos.” | protocolo de teste |
| “O motorista não gosta de automatizado.” | “Vamos avaliar treinamento, adaptação e resultado real antes da decisão.” | teste e feedback |
| “Manutenção da concessionária é cara.” | “Precisamos comparar custo por km, disponibilidade, garantia e risco de parada.” | histórico de manutenção |
| “Quero o modelo mais potente.” | “Potência é uma variável. Relação, torque, peso, rota e transmissão podem ser mais determinantes.” | estudo de aplicação |
| “Preciso carregar o máximo.” | “Primeiro calculamos carga útil legal após implemento e distribuição por eixo.” | pesagem e projeto |
| “O concorrente entrega antes.” | “Prazo é crítico; confirmaremos formalmente disponibilidade e impacto total da alternativa.” | compromisso de prazo documentado |

---

## 13. Academia de treinamento

### 13.1 Trilha inicial - 40 horas

| Módulo | Carga | Resultado esperado |
|---|---:|---|
| 1. Marca, rede e proposta de valor | 2h | Comunicação institucional correta |
| 2. Fundamentos de transporte e legislação | 4h | Entender PBT, PBTC, CMT, eixos e carga útil |
| 3. Accelo | 4h | Dimensionar operações urbanas e regionais |
| 4. Atego | 5h | Navegar gama e aplicações vocacionais |
| 5. Axor | 4h | Diferenciar S/LS, 2038/2538/2545 e aplicação rodoviária |
| 6. Actros | 5h | Construir proposta para alta produtividade e segurança |
| 7. Implementos e engenharia de aplicação | 4h | Evitar incompatibilidades e erros de distribuição |
| 8. TCO e finanças | 4h | Montar business case com sensibilidade |
| 9. FleetBoard, Uptime e serviços | 3h | Vender solução conectada e adoção |
| 10. CRM, pipeline e dados | 2h | Registrar dados completos e acionáveis |
| 11. Negociação de grandes contas | 2h | Gerir comitê e objeções |
| 12. Ética, LGPD e claims de marketing | 1h | Reduzir risco jurídico e reputacional |

### 13.2 Certificação interna

**Critérios mínimos:**

- 80% em prova técnica;
- estudo de caso com dimensionamento correto;
- apresentação de TCO com premissas rastreáveis;
- simulação de reunião com comprador, operação e manutenção;
- uso correto do CRM;
- aprovação em checklist de claims e compliance.

### 13.3 Recertificação

- trimestral: atualização de produto e disponibilidade;
- semestral: prova de portfólio e serviços;
- anual: caso prático completo e auditoria de CRM;
- imediata: sempre que houver lançamento, mudança regulatória ou ficha substituída.

### 13.4 Treinamento por função

| Função | Profundidade principal |
|---|---|
| Consultor | diagnóstico, aplicação, TCO, negociação e CRM |
| Gestor de grandes contas | estratégia de carteira, forecast, coaching e comitê executivo |
| Marketing | segmentação, conteúdo, dados, claims e atribuição |
| Pós-venda | disponibilidade, plano, manutenção e retorno de dados à venda |
| Técnico/engenharia | pesos, implementos, PTO, homologação e configuração |
| Financeiro | fluxo de caixa, crédito, custo efetivo e alternativas |
| Entrega técnica | checklist, condução, telemetria e adoção |

---

## 14. Marketing de concessionária e grandes contas

### 14.1 Princípio central

Marketing de caminhões deve reduzir risco percebido e provar aderência operacional. Conteúdo genérico de produto gera alcance; conteúdo por segmento, rota, dor e resultado gera oportunidade qualificada.

### 14.2 Personas do comitê de compra

| Persona | Pergunta principal | Conteúdo que converte |
|---|---|---|
| Proprietário/diretor | “Qual impacto no lucro, risco e crescimento?” | TCO, disponibilidade, case e fluxo de caixa |
| Operações | “Vai cumprir ciclo, carga e prazo?” | aplicação, rota, produtividade e teste |
| Manutenção | “Vai parar menos e ser fácil de manter?” | plano, rede, telemetria, peças e histórico |
| Financeiro | “Cabe no caixa e no risco?” | cenários, parcela, payback e residual |
| Compras | “A proposta é comparável e contratável?” | escopo equalizado, SLA e cronograma |
| Segurança/ESG | “Reduz risco e mede impacto?” | sistemas, telemetria, eventos e CO2 |
| Motorista | “É seguro, confortável e fácil de operar?” | cabine, ergonomia, teste e treinamento |

### 14.3 Pilares de conteúdo

1. **Aplicação:** qual caminhão para qual operação e por quê.
2. **Economia:** TCO, consumo medido, manutenção e disponibilidade.
3. **Segurança:** sistemas, condução, risco e prevenção.
4. **Produtividade:** carga, tempo de ciclo, velocidade média e autonomia.
5. **Pessoas:** conforto, motorista, treinamento e retenção.
6. **Pós-venda:** rede, peças, planos, Uptime e FleetBoard.
7. **Prova:** cases, depoimentos, testes e dados auditáveis.

### 14.4 ABM - Account Based Marketing

Para as grandes frotas do território:

- selecionar 20 a 50 contas-alvo por potencial, janela e aderência;
- mapear decisores e influenciadores;
- produzir uma página/dossiê por segmento;
- executar campanhas coordenadas de e-mail, WhatsApp autorizado, LinkedIn, visita e evento;
- registrar todas as interações no CRM;
- medir avanço da conta, não somente leads individuais.

### 14.5 Campanhas recomendadas

| Campanha | Público | Oferta | CTA |
|---|---|---|---|
| Diagnóstico de custo por km | Frotas com renovação | sessão de TCO | Agendar diagnóstico |
| Rota de produtividade | Operações rodoviárias | teste controlado | Inscrever veículo/rota |
| Clínica de aplicação | Implementadores e clientes | revisão chassi + implemento | Enviar projeto |
| FleetBoard na prática | Gestores de frota | demonstração com KPIs | Solicitar demo |
| Segurança e motorista | RH/operação | workshop | Inscrever equipe |
| Renovação 2027 | Clientes com frota envelhecida | plano de renovação | Receber simulação |

### 14.6 Regras de marca e compliance

- utilizar somente logos e arquivos oficiais;
- não alterar proporção, estrela ou identidade do veículo;
- obter autorização para uso de cliente, motorista, placa, carga e instalações;
- registrar origem de números e período medido;
- identificar simulações e condições;
- observar LGPD em leads, listas e campanhas;
- submeter claims técnicos e comparativos à aprovação;
- não publicar preço/taxa sem validade, condições e responsável.

### 14.7 Métricas de marketing

- contas engajadas;
- decisores alcançados por conta;
- MQL e SQL por segmento;
- oportunidade criada e receita influenciada;
- custo por oportunidade;
- taxa de comparecimento a eventos/testes;
- conteúdo que gerou reunião;
- tempo de avanço por conta;
- atribuição por campanha e UTM;
- consentimento e qualidade da base.

---

## 15. CRM e modelo de dados

### 15.1 Entidades mínimas

- Conta/empresa;
- unidade/filial;
- contato e papel no comitê;
- frota atual;
- veículo/modelo;
- operação/rota;
- implemento;
- oportunidade;
- solução/configuração;
- atividade;
- proposta;
- teste/demonstração;
- contrato/pedido;
- entrega;
- pós-venda;
- serviço conectado;
- fonte documental.

### 15.2 Dicionário de campos prioritários

| Campo | Tipo | Regra |
|---|---|---|
| `account_id` | UUID | chave única da conta |
| `cnpj_raiz` | texto validado | deduplicação por grupo econômico |
| `segmento` | enum | taxonomia controlada |
| `frota_total` | inteiro | data da última confirmação |
| `frota_mb` | inteiro | não deixar vazio; usar 0 quando confirmado |
| `marca_lider` | enum | origem registrada |
| `idade_media_frota` | decimal | em anos |
| `renovacao_12m` | inteiro | unidades prováveis |
| `km_mes` | decimal | por operação ou veículo |
| `carga_media_kg` | decimal | distinguir média e máximo |
| `tipo_carga` | enum/texto | classificação padronizada |
| `rota_origem_destino` | texto/geografia | permitir múltiplas rotas |
| `percentual_terra` | percentual | 0 a 100 |
| `implemento_tipo` | enum | com fabricante e tara |
| `consumo_atual_kml` | decimal | informar período e fonte |
| `custo_manutencao_km` | moeda/km | período mínimo recomendado de 12 meses |
| `dias_parada_ano` | decimal | programada e não programada separadas |
| `janela_compra` | data/faixa | obrigatório para forecast |
| `score_oportunidade` | 0-100 | cálculo transparente |
| `proximo_passo` | texto | obrigatório e datado |
| `modelo_recomendado` | relacionamento | não usar texto livre |
| `ficha_fonte_id` | relacionamento | versão técnica usada |
| `premissas_tco` | JSON/relacionamento | auditáveis |
| `consentimento_marketing` | boolean/data | LGPD |

### 15.3 Regras de qualidade do CRM

- nenhuma oportunidade sem próximo passo e data;
- nenhuma proposta sem diagnóstico mínimo;
- nenhum modelo recomendado sem fonte técnica;
- conta duplicada deve ser mesclada, não replicada;
- forecast exige decisor, valor, probabilidade baseada em estágio e data;
- números de frota devem ter fonte e data de confirmação;
- campos “0”, “desconhecido” e “não aplicável” devem ser distintos;
- histórico de alteração de estágio deve ser preservado.

---

## 16. KPIs de gestão

### 16.1 Comercial

| KPI | Fórmula |
|---|---|
| Cobertura de pipeline | valor ponderado do pipeline / meta do período |
| Taxa de qualificação | oportunidades qualificadas / prospectos trabalhados |
| Conversão diagnóstico-proposta | propostas / diagnósticos concluídos |
| Conversão proposta-pedido | pedidos / propostas válidas |
| Ciclo de venda | média de dias da criação ao fechamento |
| Acurácia do forecast | 1 - abs(previsto-realizado)/realizado |
| Share of wallet MB | veículos MB / frota elegível da conta |
| Renovação capturada | unidades vendidas / unidades renovadas pelo cliente |
| Receita por conta | receita total / contas ativas |
| Attach rate de serviços | veículos com serviço / veículos vendidos |

### 16.2 Produto e solução

- percentual de propostas com diagnóstico completo;
- percentual de configurações validadas por engenharia quando necessário;
- retrabalho de pedido por erro de configuração;
- aderência entre carga/rota e modelo vendido;
- desempenho pós-entrega versus business case;
- incidência de opcionais não disponíveis;
- divergência entre ficha usada e ficha vigente.

### 16.3 Treinamento

- taxa de conclusão;
- aprovação na primeira tentativa;
- nota prática;
- tempo até certificação;
- retenção em 90 dias;
- melhoria de conversão após treinamento;
- erros técnicos por consultor;
- qualidade do CRM por consultor.

### 16.4 Marketing

- contas-alvo engajadas;
- reuniões originadas;
- oportunidades e receita influenciadas;
- custo por oportunidade;
- conversão por segmento e campanha;
- aderência de consentimento;
- velocidade de resposta;
- eventos/testes convertidos em proposta.

### 16.5 Pós-venda e adoção

- ativação de FleetBoard/Uptime;
- veículos com plano de manutenção;
- disponibilidade física;
- paradas não programadas;
- consumo e marcha lenta;
- satisfação do cliente e motorista;
- retorno à concessionária;
- retenção na renovação seguinte.

---

## 17. Riscos e controles

| Risco | Probabilidade | Impacto | Controle |
|---|---|---|---|
| Ficha desatualizada em proposta | Média | Alto | catálogo mestre e bloqueio de versão |
| Promessa de consumo | Alta | Alto | protocolo de teste e disclaimer |
| Erro de carga útil | Média | Crítico | pesagem, tara do implemento e validação legal |
| Opcional indisponível | Média | Alto | consulta formal antes da proposta |
| Chassi incompatível com implemento | Baixa/Média | Crítico | engenharia de aplicação antes do pedido |
| CRM incompleto | Alta | Médio/Alto | campos obrigatórios e auditoria semanal |
| Campanha sem consentimento | Média | Alto | gestão de LGPD e opt-out |
| Material fora da identidade da marca | Média | Alto | aprovação de marketing |
| TCO enviesado | Média | Alto | premissas auditáveis e três cenários |
| Treinamento focado só em produto | Alta | Médio | casos de operação e avaliação prática |
| Falta de acompanhamento pós-venda | Alta | Alto | rotina 30/60/90/180 dias |

---

## 18. Plano de implantação 30-60-90 dias

### Dias 1-30 - Fundar a governança

- definir dono da base;
- renomear e catalogar documentos;
- remover duplicidades da pasta ativa;
- marcar vigência de cada ficha;
- criar matriz estruturada de produto;
- padronizar diagnóstico comercial;
- selecionar 20 contas-alvo de Goiânia, Aparecida e Anápolis;
- mapear frota, marcas, idade e janela de renovação;
- treinar equipe nos módulos 1, 2, 3 e 4.

### Dias 31-60 - Operar o método

- implantar score de oportunidade;
- criar calculadora de TCO;
- iniciar clínicas de aplicação;
- estruturar campanha de diagnóstico de custo por km;
- integrar vendas, pós-venda, FleetBoard e financiamento;
- auditar propostas e CRM semanalmente;
- executar os primeiros testes controlados;
- treinar Axor, Actros, serviços e negociação.

### Dias 61-90 - Escalar e provar

- revisar pipeline e forecast por conta;
- publicar cases aprovados;
- medir attach rate de serviços;
- comparar business case versus dados reais dos veículos entregues;
- criar ranking de contas por potencial e risco;
- certificar a equipe;
- definir rotina mensal de atualização técnica;
- apresentar dashboard executivo à diretoria.

---

## 19. Checklists operacionais

### 19.1 Antes de recomendar um veículo

- [ ] Operação e rota documentadas
- [ ] Peso médio e máximo confirmados
- [ ] Implemento e tara conhecidos
- [ ] Limites legais e por eixo validados
- [ ] Entre-eixos e manobrabilidade avaliados
- [ ] Tração, potência, torque e relação adequados
- [ ] Cabine e suspensão alinhadas à jornada e carga
- [ ] Autonomia de combustível/ARLA avaliada
- [ ] Opcionais e disponibilidade confirmados
- [ ] Ficha vigente vinculada no CRM
- [ ] Engenharia consultada quando aplicável

### 19.2 Antes de enviar proposta

- [ ] Código/configuração exatos
- [ ] Preço, impostos, validade e prazo
- [ ] Itens de série e opcionais separados
- [ ] Implemento e responsabilidades definidos
- [ ] Serviços, plano, conectividade e treinamento descritos
- [ ] Premissas de TCO anexadas
- [ ] Claims revisados
- [ ] Condições de crédito tratadas como sujeitas à aprovação
- [ ] Próximo gate agendado

### 19.3 Na entrega

- [ ] Conferência física e documental
- [ ] Treinamento de motorista
- [ ] Orientação de BlueTec 6 e ARLA 32
- [ ] Ativação de FleetBoard/Uptime contratados
- [ ] Plano de manutenção explicado
- [ ] Contatos de atendimento e emergência
- [ ] Baseline de consumo e operação registrado
- [ ] Revisões 30/60/90 dias agendadas

---

## 20. Lacunas para a versão 2.0

Para elevar a base de 76 para mais de 90 pontos de maturidade, incluir:

1. tabela oficial de opcionais e códigos;
2. status de produção, estoque e prazo por modelo;
3. preços e políticas comerciais com validade;
4. manuais de implementação e matrizes de implemento;
5. planos de manutenção e coberturas vigentes;
6. custos de peças e manutenção por aplicação;
7. dados de consumo de testes padronizados;
8. emplacamentos por município e segmento;
9. carteira de clientes, frota e janela de renovação;
10. benchmark concorrencial com fonte e data;
11. identidade visual oficial da Tecar e Mercedes-Benz;
12. casos aprovados com métricas antes/depois;
13. integração automática com CRM e BI;
14. processo formal de aprovação de conteúdo.

---

## 21. Fontes oficiais complementares

Consultadas em 03/08/2026. As páginas podem ser atualizadas após esta data.

1. [FleetBoard - Mercedes-Benz Trucks Brasil](https://www.mercedes-benz-trucks.com.br/pecas-e-servicos/servicos-para-o-seu-caminhao/fleetboard)
2. [Portfólio 2025 de caminhões, peças e serviços](https://www.mercedes-benz-trucks.com.br/imprensa/releases/mercedes-benz-anuncia-lancamentos-e-novidades-do-portfolio-2025-de-caminhoes-pecas-e-servicos-551)
3. [Ampliação do portfólio Axor em 2026](https://www.mercedes-benz-trucks.com.br/imprensa/releases/mercedes-benz-amplia-portfolio-do-axor-e-lanca-cavalos-mecanicos-com-suspensao-traseira-pneumatica-e-versao-plataforma-do-modelo-2038-704)
4. [Lançamento do Novo Axor no Brasil](https://www.mercedes-benz-trucks.com.br/imprensa/releases/mercedes-benz-revela-novo-axor-icone-de-sua-linha-de-extrapesados-que-retorna-ainda-mais-moderno-forte-e-robusto-629)
5. [Linha Axor - showroom oficial](https://www.mercedes-benz-trucks.com.br/caminhoes/axor)
6. [Actros 2653 LS 6x4 - showroom oficial](https://www.mercedes-benz-trucks.com.br/caminhoes/actros/2653-ls-6x4)
7. [Referência oficial recente a peças, serviços, FleetBoard e Uptime](https://www.mercedes-benz-trucks.com.br/imprensa/releases/dhl-supply-chain-adquire-75-caminhoes-mercedes-benz-para-o-transporte-de-cargas-691)
8. [Prêmio de revenda 2025: Actros 2653, Atego 1726 e Accelo 817](https://www.mercedes-benz-trucks.com.br/imprensa/releases/mercedes-benz-actros-2653-e-campeao-de-revenda-entre-caminhoes-extrapesados-637)

---

## 22. Registro das fichas técnicas recebidas

A coluna de hash apresenta os 12 primeiros caracteres do SHA-256, suficientes para controle operacional inicial. Para cadeia de custódia formal, guardar o hash completo.


| Modelo | Configuração | Data | Versão | Arquivo original | SHA-256 curto | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Accelo 1017 | 4x2 BlueTec 6 | 09/06/2024 | V1/25 | 2b343ef8-62a4-4a65-b8ef-b15509c03963.pdf | 9bffd99b4ac2 | Único |
| Accelo 1317 | 6x2 BlueTec 6 | 08/07/2026 | V1/26 | 80d7e839-71e0-4e6f-870a-466785c9d042 (1).pdf | 9e7d95eb622f | Duplicado/equivalente; não usar como fonte mestre |
| Accelo 1317 | 6x2 BlueTec 6 | 08/07/2026 | V1/26 | 80d7e839-71e0-4e6f-870a-466785c9d042.pdf | 9e7d95eb622f | Primário; há cópia equivalente |
| Accelo 817 | 4x2 BlueTec 6 | 09/06/2024 | V1/25 | b8fce583-c429-4f0d-9732-5402799ab313.pdf | c0b9ffed8b32 | Único |
| Actros 2045 | LS 4x2 BlueTec 6 | 16/06/2026 | V2/26 | Ficha T#U00e9cnica 2045 LS.pdf | 7fad0eec1d3e | Único |
| Actros 2045 | S 4x2 BlueTec 6 | 16/06/2026 | V2/26 | Ficha T#U00e9cnica 2045 S.pdf | 88e6fd362535 | Único |
| Actros 2548 | LS 6x2 BlueTec 6 | 16/06/2026 | V3/26 | Ficha T#U00e9cnica 2548 LS.pdf | 170f9432b39a | Único |
| Actros 2548 | S 6x2 BlueTec 6 | 16/06/2026 | V2/26 | Ficha T#U00e9cnica 2548 S.pdf | d9c5879bea1c | Único |
| Actros 2553 | LS 6x2 BlueTec 6 | 16/06/2026 | V4/26 | Ficha T#U00e9cnica 2553 LS.pdf | 5953fc2fedaf | Único |
| Actros 2553 | S 6x2 BlueTec 6 | 16/06/2026 | V3/26 | Ficha T#U00e9cnica 2553 S.pdf | 73c9eaf5715b | Único |
| Actros 2651 | LS 6x4 BlueTec 6 | 16/06/2026 | V2/26 | Ficha T#U00e9cnica 2651 LS.pdf | 4b8786a73995 | Único |
| Actros 2651 | S 6x4 BlueTec 6 | 16/06/2026 | V3/26 | Ficha T#U00e9cnica 2651 S.pdf | ea40e905f6cc | Único |
| Actros 2653 | LS 6x4 BlueTec 6 | 16/06/2026 | V2/26 | Ficha T#U00e9cnica 2653 LS.pdf | 5ea58d1a6aaf | Único |
| Actros 2653 | S 6x4 BlueTec 6 | 16/06/2026 | V2/26 | Ficha T#U00e9cnica 2653 S.pdf | f84ee7346933 | Único |
| Novo Accelo 1117 | 4x2 BlueTec 6 | 27/07/2026 | V6/26 | 698b148a-f8d0-424f-b6fb-5f60193513f0.pdf | e7214cc8d90d | Único |
| Novo Accelo 1417 | 6x2 BlueTec 6 | 28/07/2026 | V3/26 | bc3fe675-4b43-4d5e-84c9-ccdf7dde267e.pdf | 5eb17fe7f604 | Único |
| Novo Accelo 917 | 4x2 BlueTec 6 | 30/04/2026 | V3/26 | e1a56a82-8137-4617-a94f-f787c79cf0b0.pdf | 818c8503baf9 | Único |
| Novo Atego 1419 | 4x2 BlueTec 6 | 29/07/2026 | V7/26 | e56e1518-b7f8-4a10-825f-c54c539059a0.pdf | a23e34fefbe5 | Único |
| Novo Atego 1719 | 4x2 BlueTec 6 | 19/07/2026 | V5/26 | 611b7e05-dcee-4f54-a13a-e5d1e7ba7576.pdf | 7ca11fe12fbb | Único |
| Novo Atego 1719 | 4x2 K BlueTec 6 | 30/07/2026 | V7/26 | 0cb48595-0093-4592-b842-0c9c1cbd9a88.pdf | 2f90d1186130 | Único |
| Novo Atego 1726 | 4x2 BlueTec 6 | 03/02/2026 | V5/26 | 6c299880-5b6e-4d2f-8e95-360c55a62876.pdf | 89e9e98596bd | Único |
| Novo Atego 1726 | K 4x2 BlueTec 6 | 03/02/2026 | V3/26 | 6d1e9352-a88b-4950-a5ae-978cec870ba5.pdf | 541ed06a6ec3 | Único |
| Novo Atego 2429 | 6x2 BlueTec 6 | 11/03/2026 | V6/26 | 0fd54076-6bdd-4350-a9cc-4fa6c6022460.pdf | 59308c53f5c3 | Único |
| Novo Atego 2429 | K 6x2 BlueTec 6 | 11/03/2026 | V2/26 | 4dd85d31-fad2-4096-8feb-530f181a888b.pdf | 38f5103b30fe | Único |
| Novo Atego 2433 | 6x2 BlueTec 6 | 25/02/2026 | V1/26 | Ficha T#U00e9cnica 2433 6X2.pdf | 3ca516e895a2 | Primário; há cópia equivalente |
| Novo Atego 2433 | 6x2 BlueTec 6 | 25/02/2026 | V1/26 | b64d8ba2-425b-41f5-8a12-a5cf1a7444ac.pdf | 7bb101fee414 | Duplicado/equivalente; não usar como fonte mestre |
| Novo Atego 3033 | 8x2 BlueTec 6 | 27/04/2026 | V2/26 | Ficha T#U00e9cnica Novo ATEGO 3033.pdf | 9e55a0a8907f | Único |
| Novo Atego 3133 | 6x4 BlueTec 6 | 06/07/2026 | V6/26 | 33635741-eeb2-40ec-aeb8-deabd7b2d4db.pdf | 64f84cba8267 | Único |
| Novo Axor 2038 | LS 4x2 BlueTec 6 | 23/01/2026 | V2/26 | Ficha T#U00e9cnica Novo Axor 2038 LS.pdf | 2d8f1b9b7d25 | Único |
| Novo Axor 2038 | S 4x2 BlueTec 6 | 23/01/2026 | V2/26 | Ficha T#U00e9cnica Novo Axor 2038 S.pdf | fdfeef8730a5 | Único |
| Novo Axor 2538 | S 6x2 BlueTec 6 | 23/01/2026 | V1/26 | Ficha T#U00e9cnica 2538 S.pdf | e07ab3b6fa1f | Único |
| Novo Axor 2545 | LS 6x2 BlueTec 6 | 23/01/2026 | V2/26 | Ficha T#U00e9cnica 2545 LS.pdf | 3b05b876d63c | Único |
| Novo Axor 2545 | S 6x2 BlueTec 6 | 23/01/2026 | V2/26 | Ficha T#U00e9cnica 2545 S.pdf | 9daf7156b1c6 | Único |


---

## 23. Mapeamento de arquivos UUID para nomes legíveis


| Arquivo recebido | Conteúdo identificado | Configuração | Nome sugerido |
| --- | --- | --- | --- |
| 0cb48595-0093-4592-b842-0c9c1cbd9a88.pdf | Novo Atego 1719 | 4x2 K BlueTec 6 | MB_Atego_1719_4x2_K_BlueTec_6_30-07-2026.pdf |
| 0fd54076-6bdd-4350-a9cc-4fa6c6022460.pdf | Novo Atego 2429 | 6x2 BlueTec 6 | MB_Atego_2429_6x2_BlueTec_6_11-03-2026.pdf |
| 2b343ef8-62a4-4a65-b8ef-b15509c03963.pdf | Accelo 1017 | 4x2 BlueTec 6 | MB_Accelo_1017_4x2_BlueTec_6_09-06-2024.pdf |
| 33635741-eeb2-40ec-aeb8-deabd7b2d4db.pdf | Novo Atego 3133 | 6x4 BlueTec 6 | MB_Atego_3133_6x4_BlueTec_6_06-07-2026.pdf |
| 4dd85d31-fad2-4096-8feb-530f181a888b.pdf | Novo Atego 2429 | K 6x2 BlueTec 6 | MB_Atego_2429_K_6x2_BlueTec_6_11-03-2026.pdf |
| 611b7e05-dcee-4f54-a13a-e5d1e7ba7576.pdf | Novo Atego 1719 | 4x2 BlueTec 6 | MB_Atego_1719_4x2_BlueTec_6_19-07-2026.pdf |
| 698b148a-f8d0-424f-b6fb-5f60193513f0.pdf | Novo Accelo 1117 | 4x2 BlueTec 6 | MB_Accelo_1117_4x2_BlueTec_6_27-07-2026.pdf |
| 6c299880-5b6e-4d2f-8e95-360c55a62876.pdf | Novo Atego 1726 | 4x2 BlueTec 6 | MB_Atego_1726_4x2_BlueTec_6_03-02-2026.pdf |
| 6d1e9352-a88b-4950-a5ae-978cec870ba5.pdf | Novo Atego 1726 | K 4x2 BlueTec 6 | MB_Atego_1726_K_4x2_BlueTec_6_03-02-2026.pdf |
| 80d7e839-71e0-4e6f-870a-466785c9d042 (1).pdf | Accelo 1317 | 6x2 BlueTec 6 | MB_Accelo_1317_6x2_BlueTec_6_08-07-2026.pdf |
| 80d7e839-71e0-4e6f-870a-466785c9d042.pdf | Accelo 1317 | 6x2 BlueTec 6 | MB_Accelo_1317_6x2_BlueTec_6_08-07-2026.pdf |
| b64d8ba2-425b-41f5-8a12-a5cf1a7444ac.pdf | Novo Atego 2433 | 6x2 BlueTec 6 | MB_Atego_2433_6x2_BlueTec_6_25-02-2026.pdf |
| b8fce583-c429-4f0d-9732-5402799ab313.pdf | Accelo 817 | 4x2 BlueTec 6 | MB_Accelo_817_4x2_BlueTec_6_09-06-2024.pdf |
| bc3fe675-4b43-4d5e-84c9-ccdf7dde267e.pdf | Novo Accelo 1417 | 6x2 BlueTec 6 | MB_Accelo_1417_6x2_BlueTec_6_28-07-2026.pdf |
| e1a56a82-8137-4617-a94f-f787c79cf0b0.pdf | Novo Accelo 917 | 4x2 BlueTec 6 | MB_Accelo_917_4x2_BlueTec_6_30-04-2026.pdf |
| e56e1518-b7f8-4a10-825f-c54c539059a0.pdf | Novo Atego 1419 | 4x2 BlueTec 6 | MB_Atego_1419_4x2_BlueTec_6_29-07-2026.pdf |


---

## 24. Decisões de governança recomendadas

1. **Fonte única:** manter um repositório mestre somente leitura para documentos aprovados.
2. **Responsável:** Produto/Engenharia aprova técnica; Marketing aprova comunicação; Comercial usa; Dados controla versão.
3. **Cadência:** revisão mensal e revisão extraordinária em lançamentos ou mudanças.
4. **Distribuição:** CRM e propostas devem apontar para a fonte mestre, não para cópias locais.
5. **Histórico:** documentos substituídos permanecem arquivados, com data e motivo.
6. **Acesso:** separar conteúdo interno, material aprovado para cliente e conteúdo público.
7. **Auditoria:** amostra mensal de propostas, claims, versões e cálculos de TCO.
8. **Feedback:** pós-venda retorna dados reais para calibrar argumentos e treinamento.

---

## 25. Encerramento

O maior valor desta base não está em memorizar fichas, mas em criar disciplina de decisão. Um consultor sênior transforma especificação em aplicação, aplicação em resultado econômico e resultado em relacionamento de longo prazo. A concessionária ganha previsibilidade quando produto, marketing, vendas, engenharia, financiamento e pós-venda trabalham sobre a mesma fonte de dados, com premissas explícitas e acompanhamento após a entrega.

**Princípio final:** vender o caminhão certo, na configuração certa, para a operação certa, com serviços que sustentem disponibilidade e rentabilidade - e provar isso com dados.


---

## 26. Dossiê técnico integral por prospecto
Esta seção preserva os dados técnicos publicados em cada ficha única recebida. As transcrições mantêm as unidades, opcionais, indisponibilidades e notas específicas do documento. A diagramação foi convertida para blocos monoespaçados para reduzir o risco de associação incorreta entre colunas.

### 26.1 Cobertura e controles de completude
| Controle | Resultado |
|---|---:|
| PDFs recebidos | 33 |
| Páginas técnicas renderizadas | 66 |
| Dossiês técnicos únicos | 31 |
| Pares duplicados removidos da repetição | 2 |
| PDFs que exigiram OCR | 0 |
| Dossiês com dimensões | 31 |
| Dossiês com pesos | 31 |
| Dossiês com motor | 31 |
| Dossiês com transmissão | 31 |
| Dossiês com desempenho | 31 |
| Dossiês com freios e segurança | 31 |

### 26.2 Índice técnico normalizado
| # | Modelo | Configuração | Cabines publicadas | Motor | Potência | Torque | Transmissão(ões) | Versão/data |
|---:|---|---|---|---|---|---|---|---|
| 1 | Accelo 817 | 4x2 BlueTec 6 | [C] Curta* [E] Estendida | MB OM 924 LA • BlueTec 6• 4,8 lts. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 163 cv (120 kW) @ 2.200 rpm | 610 Nm (62 kgfm) @ 1.200 - 1.600 rpm | EATON ESO 6205 MB G 70-6 MB G 70-6 PowerShift 3 | V1/25 - 09/06/2024 |
| 2 | Novo Accelo 917 | 4x2 BlueTec 6 | [C] Curta [E] Estendida | MB OM 924 LA • BlueTec 6• 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 163 cv (120 kW) @ 2200 rpm | 610 Nm (62,2 kgfm) @ 1200 - 1600 rpm | EATON ESO 6205 | V3/26 - 30/04/2026 |
| 3 | Accelo 1017 | 4x2 BlueTec 6 | [C] Curta* [E] Estendida | MB OM 924 LA • BlueTec 6 • 4,8 lts. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 163 cv (120 kW) @ 2.200 rpm | 610 Nm (62 mkgf) @ 1.200 - 1.600 rpm | MB G 70-6 MB G 70-6 PowerShift 3 | V1/25 - 09/06/2024 |
| 4 | Novo Accelo 1117 | 4x2 BlueTec 6 | [C] Curta [E] Estendida | MB OM 924 LA • BlueTec 6• 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 163 cv (120 kW) @ 2200 rpm | 610 Nm (62,2 kgfm) @ 1200 - 1600 rpm | EATON ESO 6206 A MB G 90-6 AMT* | V6/26 - 27/07/2026 |
| 5 | Accelo 1317 | 6x2 BlueTec 6 | [C] Curta* [E] Estendida | MB OM 924 LA • BlueTec 6 • 4,8 lts. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 163 cv (120 kW) @ 2.200 rpm | 610 Nm (62,2 mkgf) @ 1.200 - 1.600 rpm | MB G 70-6 MB G 70-6 PowerShift 3 | V1/26 - 08/07/2026 |
| 6 | Novo Accelo 1417 | 6x2 BlueTec 6 | [C] Curta [E] Estendida | MB OM 924 LA • BlueTec 6• 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 163 cv (120 kW) @ 2200 rpm | 610 Nm (62,2 kgfm) @ 1200 - 1600 rpm | EATON ESO 6206 MB G 90-6 AMT * | V3/26 - 28/07/2026 |
| 7 | Novo Atego 1419 | 4x2 BlueTec 6 | [C] Curta [E] Estendida [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 924 LA • BlueTec 6 • 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 185 cv (136 kW) @ 2200 rpm | 700 Nm (71,4 mkgf) @ 1200 - 1600 rpm | EATON FOSA 5406A MB G 140-8* PowerShift 3 Advanced | V7/26 - 29/07/2026 |
| 8 | Novo Atego 1719 | 4x2 BlueTec 6 | [C] Curta [E] Estendida [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 924 LA • BlueTec 6 • 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 185 cv (136 kW) @ 2200 rpm | 700 Nm (71,4 mkgf) @ 1200 - 1600 rpm | MB G 90-6 MB G 140-8* PowerShift 3 Advanced | V5/26 - 19/07/2026 |
| 9 | Novo Atego 1719 | 4x2 K BlueTec 6 | [C] Curta [E] Estendida | MB OM 924 LA • BlueTec 6 • 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6) | 185 cv (136 kW) @ 2200 rpm | 700 Nm (71,4 mkgf) @ 1200 - 1600 rpm | MB G 90-6 MB G 140-8* PowerShift 3 Advanced | V7/26 - 30/07/2026 |
| 10 | Novo Atego 1726 | 4x2 BluetTec 6 | [C] Curta [E] Estendida [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 926 LA • BlueTec 6• 7,2 L. • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 260 cv (191 kW) @ 2200 rpm | 900 Nm (91,8 mkgf) @ 1200 - 1600 rpm | MB G 90-6 MB G 140-8* PowerShift 3 Advanced | V5/26 - 03/02/2026 |
| 11 | Novo Atego 1726 | K 4x2 BluetTec 6 | [C] Curta [E] Estendida | MB OM 926 LA • BlueTec 6 • 7,2 L • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 260 cv (191 kW) @ 2200 rpm | 900 Nm (91,8 mkgf) @ 1200 - 1600 rpm | MB G 90-6 MB G 140-8* PowerShift 3 Advanced | V3/26 - 03/02/2026 |
| 12 | Novo Atego 2429 | 6x2 BlueTec 6 | [C] Curta [E] Estendida [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 926 LA • BlueTec 6• 7,2 L. • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 286 cv (210 kW) @ 2200 rpm | 1100 Nm (112,2 kgfm) @ 1200 - 1600 rpm | MB G 140-8 PowerShift 3 Advanced | V6/26 - 11/03/2026 |
| 13 | Novo Atego 2429 | K 6x2 BlueTec 6 | [C] Curta [E] Estendida | MB OM 926 LA • BlueTec 6 • 7,2 L • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 286 cv (210 kW) @ 2200 rpm | 1100 Nm (112,2 mkgf) @ 1200 - 1600 rpm | MB G 140-8 PowerShift 3 Advanced | V2/26 - 11/03/2026 |
| 14 | Novo Atego 2433 | 6x2 BlueTec 6 | [C] Curta [E] Estendida [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 926 LA • BlueTec 6• 7,2 L. • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 321 cv (236 kW) @ 2200 rpm | 1250 Nm (127,5 mkgf) @ 1200 - 1600 rpm | MB G 211-12 PowerShift 3 Advanced | V1/26 - 25/02/2026 |
| 15 | Novo Atego 3033 | 8x2 BlueTec 6 | [C] Curta [E] Estendida [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 926 LA • BlueTec 6• 7,2 L. • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 321 cv (236 kW) @ 2200 rpm | 1250 Nm (127,5 mkgf) @ 1200 - 1600 rpm | MB G 211-12 PowerShift 3 Advanced | V2/26 - 27/04/2026 |
| 16 | Novo Atego 3133 | 6x4 BlueTec 6 | [E] Estendida | MB OM 926 LA • BlueTec 6 • 7,2 L • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 321 cv (236 kW) @ 2200 rpm | 1250 Nm (127,5 mkgf) @ 1200 - 1600 rpm | MB G 211-12 PowerShift 3 Advancedf | V6/26 - 06/07/2026 |
| 17 | Novo Axor 2038 | LS 4x2 BlueTec 6 | [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 381 cv (280 kW) @ 1600 rpm | 1900 Nm (193,7 kgfm) @ 1100 rpm | MB G 291-12 PowerShift 3 Advancd | V2/26 - 23/01/2026 |
| 18 | Novo Axor 2038 | S 4x2 BlueTec 6 | [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 381 cv (280 kW) @ 1600 rpm | 1900 Nm (193,7 kgfm) @ 1100 rpm | MB G 291-12 PowerShift 3 Advancd MB G 340-12 PowerShift 3 Advancd* | V2/26 - 23/01/2026 |
| 19 | Novo Axor 2538 | S 6x2 BlueTec 6 | [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 381 cv (280 kW) @ 1600 rpm | 1900 Nm (193,7 mkgf) @ 1100 rpm | MB G 291-12 PowerShift 3 Advancd MB G 340-12 PowerShift 3 Advancd * | V1/26 - 23/01/2026 |
| 20 | Novo Axor 2545 | LS 6x2 BluaTec 6 | [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 449 cv (330 kW) @ 1600 rpm | 2200 Nm (224,3 kgfm) @ 1100 rpm | MB G 291-12 PowerShift 3 Advancd | V2/26 - 23/01/2026 |
| 21 | Novo Axor 2545 | S 6x2 BlueTec 6 | [LTB] Leito Teto Baixo [LTA] Leito Teto Alto | MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6) | 449 cv (330 kW) @ 1600 rpm | 2200 Nm (224,3 kgfm) @ 1100 rpm | MB G 291-12 PowerShift 3 Advancd MB G 340-12 PowerShift 3 Advancd* | V2/26 - 23/01/2026 |
| 22 | Actros 2045 | LS 4x2 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6) | 449 cv (330 kW) @ 1600 rpm | 2200 Nm (224,3 kgfm) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced | V2/26 - 16/06/2026 |
| 23 | Actros 2045 | S 4x2 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6) | 449 cv (330 kW) @ 1600 rpm | 2.200 Nm (224,3 mkgf) @ 1.100 rpm | MB G 291-12 Powershift 3 Advanced | V2/26 - 16/06/2026 |
| 24 | Actros 2548 | LS 6x2 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 460 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6) | 476 cv (350 kW) @ 1600 rpm | 2300 Nm (234,5 mkgf) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced | V3/26 - 16/06/2026 |
| 25 | Actros 2548 | S 6x2 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 460 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6) | 476 cv (350 kW) @ 1600 rpm | 2300 Nm (234,5 mkgf) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced MB G 340-12 Powershift 3 Advanced* | V2/26 - 16/06/2026 |
| 26 | Actros 2553 | LS 6x2 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 471 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6) | 530 cv (390 kW) @ 1600 rpm | 2600 Nm (265,1 mkgf) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced | V4/26 - 16/06/2026 |
| 27 | Actros 2553 | S 6x2 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 471 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6) | 530 cv (390 kW) @ 1600 rpm | 2600 Nm (265,1 mkgf) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced MB G 340-12 Powershift 3 Advanced | V3/26 - 16/06/2026 |
| 28 | Actros 2651 | LS 6x4 BueTec 6 | [S] Space [TS] TopSpace | MB OM 460 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6) | 495 cv (364 kW) @ 1600 rpm | 2400 Nm (244,7 mkgf) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced | V2/26 - 16/06/2026 |
| 29 | Actros 2651 | S 6x4 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 460 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6) | 495 cv (364 kW) @ 1600 rpm | 2400 Nm (244,7 mkgf) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced MB G 340-12 Powershift 3 Advanced | V3/26 - 16/06/2026 |
| 30 | Actros 2653 | LS 6x4 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 471 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6) | 530 cv (390 kW) @ 1600 rpm | 2600 Nm (265,1 mkgf) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced | V2/26 - 16/06/2026 |
| 31 | Actros 2653 | S 6x4 BlueTec 6 | [S] Space [TS] TopSpace | MB OM 471 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6) | 530 cv (390 kW) @ 1600 rpm | 2600 Nm (265,1 mkgf) @ 1100 rpm | MB G 291-12 Powershift 3 Advanced MB G 340-12 Powershift 3 Advanced* | V2/26 - 16/06/2026 |

### 26.3 Como ler os dossiês

- Valores dimensionais estão em milímetros, salvo indicação diferente.
- Pesos e limites estão em quilogramas, salvo indicação diferente.
- `ee` representa a distância entre o primeiro eixo dianteiro e o primeiro eixo traseiro com tração.
- `*` identifica item opcional no prospecto; não confirma disponibilidade.
- `nd` significa item não disponível na configuração indicada.
- Nas colunas `legal/técnico`, deve-se observar o menor limite aplicável, além das restrições do implemento e da legislação.
- As capacidades de subida e velocidades são teóricas nas condições declaradas pelo fabricante e não constituem garantia de desempenho real.

---

### 26.4 Accelo 817 - 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `b8fce583-c429-4f0d-9732-5402799ab313.pdf` |
| Versão do prospecto | V1/25 |
| Data do prospecto | 09/06/2024 |
| SHA-256 | `c0b9ffed8b32c2bf0d33ed2498f01f5e4bfeb841365097aff73269723ef55a0c` |
| PBT - linha literal | Cab. Versão [C] 3.309 3.405 3.520 Peso Bruto Total (PBT) 16.000/8.300 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões (mm)1 | ee                                 31                       39                 46
[a] Distância entre eixos                               3.100                    3.900             4.600

[b] Comprimento total (c/ lanterna traseira)            6.134                    7.134             7.961

[c] Largura                                             2.176                    2.176             2.176

[d] Altura [C,E] (descarregado)                         2.480                    2.480             2.480

[e] Bitola (eixo dianteiro/eixo traseiro)               1.766/1.704              1.766/1.704       1.766/1.704

[f] Balanço (dianteiro/traseiro)                        1.300/1.700              1.300/1.900       1.700/2.030

[g] Ângulo de entrada (carregado)                       22°                      22°               22°

[h] Ângulo de saída (carregado com estepe)              12°                      12°               12°

[i] Altura: teto da cabine ao chassi [C] e [E]          1.632                    1.632             1.632

[j] Dist. mín. centro do eixo à carroceria [C]/[E]      420/600                  420/600           420/600

Círculo de viragem (parede a parede)                    12.600                   14.500            16.500
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          31            39              46       Pesos Admissíveis1 | ee                            legal/técnico 31 | 39 | 46
Eixo Dianteiro                                          2.129         2.254        2.344       Eixo Dianteiro                                                6.000/3.000

Eixo traseiro                                           1.180         1.151        1.176       Eixo Traseiro                                                10.000/5.300

Cab. Versão [C]                                         3.309         3.405        3.520       Peso Bruto Total (PBT)                                       16.000/8.300

Cab. Versão [E]                                         +11           +10          +9          Carga útil máx.+equip. [C]                     12.691/4.991 12.595/4.895 12.480/4.780

Câmbio EATON/G 70-6 aut.                                               -11/+10                 PBT +3º eixo | PBTC                                             11.000

Tanque Diesel 150 litros                                +63           +62          +62         Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                               considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
Tanque Diesel (2x15) litros                             nd            +257         +257

Tanque (Arla 32) 25 litros                              +11           +11          +13
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C]/Cabine Estendida[E], sem carroceria ou implemento, sem
motorista, com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor
de incêndio e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                 [C] Curta*                                            [E] Estendida

Suspensão da cabine                                     Metálica                                              Metálica
~~~

#### Motor

~~~text
Motor                                                MB OM 924 LA • BlueTec 6• 4,8 lts. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                          163 cv (120 kW) @ 2.200 rpm

Torque Máximo [NBR ISO 1585]                            610 Nm (62 kgfm) @ 1.200 - 1.600 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria                                24V | (2x12V)/100Ah

Alternador                                              28V / 80Ah
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                          EATON ESO 6205                      MB G 70-6                               MB G 70-6 PowerShift 3
Tipo                                                    Manual                              Manual                               Automatizada, sem pedal de embreagem

Nº marchas | Relações primeira/última                   5 | 5,76/0,77                       6 | 5,94/0,74                        6 | 5,76/0,77

Embreagem (auxílio pneumático)                          Monodisco, diâmetro 362mm           Monodisco, diâmetro 362mm            Monodisco, diâmetro 362mm
~~~

#### Eixos traseiros e relações

~~~text
Eixo traseiro                                        MB HL2 (R 325) estampado
Bloqueio                                                transversal (opcional)

Relações de eixo                                        i=3,91(43:11)                                               i=4,30(43:10)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                               escada, rebitado • material: LNE 50 (NBR 6656)
Suspensão dianteira                                     Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                      Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanque de combustível | Arla (litros)                   75 | 12                                                 150* | 12              150* | 25*            (2x150)*2

Rodas | Pneus                                           6.00x17.5 | 215/75R17.5

2
    Configuração (2x150) somente nos ee 39 e 46 e com Arla de 25 litros.
~~~

#### Desempenho teórico

~~~text
Desempenho                                           EATON ESO 6205                                     MB G 70-6                     MB G 70-6 AMT
Pneus                                                   215/75R17.5                                     215/75R17.5                     215/75R17.5

Relações de eixo                                        i=3,91/i=4,30*                                  i=3,91/i=4,30*                  i=3,91/i=4,30*

Velocidade máxima (km/h)                                97/97                                           98/97                           98/97

Capacidade de subida3 - 8.300 kg (%)                    41/45                                           42/47                           42/47

Capacidade de subida3 - 11.000 kg (%)                   31/34                                           32/35                           32/35

3
    Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | acionamento                                      Tambor/Disco* | Pneumático

Freio de estacionamento                                 Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                          Convencional / (Convencional + Top Brake - Freio de cabeçote)*

                                                        ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC® (Controle Eletrônico de
Eletrônica Auxiliar                                     Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                        (Assistência de Partida em Rampa)4* • Interface CAN - SAE J1939
4
    Somente com câmbio automatizado
~~~

---

### 26.5 Novo Accelo 917 - 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `e1a56a82-8137-4617-a94f-f787c79cf0b0.pdf` |
| Versão do prospecto | V3/26 |
| Data do prospecto | 30/04/2026 |
| SHA-256 | `818c8503baf9f844ce9b3c0a0e2792a1714bf257a00578834a5f2e7fff25c8d7` |
| PBT - linha literal | ferramentas Para PBT 9100 kg e eixo dianteiro 3600 kg, apenas com pneus 235/75R17.5 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                         31                     39                   46
[a] Distância entre eixos                                  3100                   3900                 4600

[b] Comprimento total (c/ lanterna)                        6136                   7135                 7965

[c] Largura                                                2175                   2175                 2175

[d] Altura [C,E] base da antena (descarregado)             2589                   2594                 2587

[e] Bitola eixo (dianteiro/traseiro)                       1838/1705              1838/1705            1838/1705

[f] Balanço (dianteiro/traseiro)                           1321/1700              1321/1900            1321/2030

[g] Ângulo de entrada (carregado)                          21°                    21°                  21°

[h] Angulo de saída (carregado)                            18°                    17°                  15°

[i] Altura: [C,E] base antena ao chassi                    1806                   1811                 1804

[j] Dist. min.:eixo dianteiro à carroceria [C/E] c/ eqp.   420/600                420/600              420/600

Círculo de viragem (parede a parede)                       12200                  14500                16500
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                             31          39              46          Pesos Admissíveis1 | ee                           legal/técnico 31 | 39 | 46
Eixo Dianteiro                                             2247        2390         2394        Eixo Dianteiro2                                                  6000/3400

Eixo Traseiro                                              1157        1048         1161        Eixo Traseiro                                                   10000/5500

Cab. [C/E]                                                 3404 /+10 3438 / +10 3555 / +10      PBT2                                                            16000/8900

Tanques (L):150 / (2x150)                                  +68 / nd    +68 / nd     +68 /+230   Carga útil máx.+ equip.                             12596/5496|12562/5462|12445/5345

Tanque (L): Arla 32: 25                                    +11         +11          +11         PBTC                                                           11000 / 11000
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de                      Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os             considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de       2
ferramentas                                                                                         Para PBT 9100 kg e eixo dianteiro 3600 kg, apenas com pneus 235/75R17.5
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                  [C] Curta                                         [E] Estendida

Suspensão da cabine                                      Metálica                                          Metálica
~~~

#### Motor

~~~text
Motor                                                 MB OM 924 LA • BlueTec 6• 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                           163 cv (120 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                             610 Nm (62,2 kgfm) @ 1200 - 1600 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                    24V | (2x12V)/100Ah | 28V/80Ah
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                           EATON ESO 6205
Tipo                                                     Manual

Nº marchas | Relações 1ª/última                          5 | 5,76/0,77

Embreagem (auxílio pneumático)                           Monodisco, 362 mm
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                         MB HL2 (R325) estampado
Bloqueio                                                 Transversal*

Relações de eixo                                         4,30(43:10)                                                  3,91(43:11)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                                escada, rebitado • material: LNE 50 (NBR 6656)
Suspensão dianteira                                      Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                       Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                       75 | 12                            75 | 25*                                 150* | 12   150* | 25*   (2x150)*3 | 25

Rodas | Pneus                                            6.00x17.5 | 215/75R17.5            6.75x17.5 | 235/75R17.5 *

3
    Configuração de tanques (2x150) litros, somente no ee 46 e com Arla de 25 litros.
~~~

#### Desempenho teórico

~~~text
Desempenho                                            EATON ESO 6205
Pneus                                                    215/75R17.5                                                    235/75R17.5

Relações de eixo                                         4,30 / 3,91*                                                   4,30 /| 3,91*

Velocidade máxima (km/h)                                 117 | 1204                                                     1204

Capacidade de subida5 - 8900 kg (%)                      42 / 38                                                        40 / 36

Capacidade de subida5 - 9100 kg (%)                      41 / 37                                                        39 / 36

Capacidade de subida5 - 11000 kg (%)                     34 / 31                                                        32 / 29

4
    Velocidade máxima limitada eletronicamente. 5 Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                       Tambor / Disco* | Pneumático

Freio de estacionamento                                  Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                           Convencional / Convencional + Top Brake® (Freio de cabeçote)

                                                         ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                      Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Interface
                                                         CAN - SAE J1939
~~~

---

### 26.6 Accelo 1017 - 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `2b343ef8-62a4-4a65-b8ef-b15509c03963.pdf` |
| Versão do prospecto | V1/25 |
| Data do prospecto | 09/06/2024 |
| SHA-256 | `9bffd99b4ac2d41dee008bf782506873fb6720f3b7b28381d6da59e7067b6a97` |
| PBT - linha literal | Cab. Versão [C]/[E] 3.426/3.436 3.565/3.575 3.642/3.652 Peso Bruto Total (PBT) 16.000/9.600 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                        31                    39                 46
[a] Distância entre eixos                               3.100                   3.900             4.600

[b] Comprimento total (c/ lanterna traseira)            6.033                   7.033             7.862

[c] Largura                                             2.284                   2.284             2.284

[d] Altura [C,E] (descarregado)                         2.600                   2.605             2.565

[e] Bitola (eixo dianteiro/eixo traseiro)               1790/1760               1790/1760         1790/1760

[f] Balanço (dianteiro/traseiro)                        1.233/1.700             1.233/1.700       1.233/1.700

[g] Ângulo de entrada (carregado)                       24°                     24°               23°

[h] Ângulo de saída (carregado com estepe)              19°                     17°               16°

[i] Altura: teto da cabine ao chassi [C]* e [E]         1.806                   1.811             1.771

[j] Dist. mín. centro do eixo à carroceria [C]*/[E]     411/591                 411/591           411/591

Círculo de viragem (parede a parede)                    12.600                  15.100            16.500
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                        31           39            46           Pesos Admissíveis1 | ee                            legal/técnico 31 | 39 | 46
Eixo Dianteiro                                        2.145        2.350         2.322        Eixo Dianteiro                                                6.000/3.200

Eixo Traseiro                                         1.281        1.215         1.320        Eixo Traseiro                                                10.000/6.400

Cab. Versão [C]/[E]                                   3.426/3.436 3.565/3.575 3.642/3.652     Peso Bruto Total (PBT)                                       16.000/9.600

Câmbio EATON/G 70-6 aut.                                              -11/+10                 Carga útil máx.+equip. [C]*                    12.574/6.174 12.435/6.035 12.358/5.958

Tanque Diesel 150 litros                              +63          +62           +62          PBT +3º eixo | PBTC                                             13.000

Tanque Diesel (2x150) litros                          nd           +150          +158         Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                              considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
Tanque (Arla 32) 25 litros                            +11          +11           +13
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C]/Cabine Estendida[E], sem carroceria ou implemento, sem
motorista, com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor
de incêndio e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                [C] Curta*                                           [E] Estendida

Suspensão da cabine                                    Metálica                                             Metálica
~~~

#### Motor

~~~text
Motor                                               MB OM 924 LA • BlueTec 6 • 4,8 lts. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                         163 cv (120 kW) @ 2.200 rpm

Torque Máximo [NBR ISO 1585]                           610 Nm (62 mkgf) @ 1.200 - 1.600 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria                               24V | (2x12V)/100Ah

Alternador                                             28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                         MB G 70-6                                        MB G 70-6 PowerShift 3
Tipo                                                   Manual                                           Automatizada, sem pedal de embreagem

Nº marchas | Relações primeira/última                  6 | 5,94/0,74                                    6 | 5,94/0,74

Embreagem (auxílio pneumático)                         Monodisco, diâmetro 362mm                        Monodisco, diâmetro 362mm
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                     MB HL2 (R 325) estampado
Bloqueio                                               transversal (opcional)

Relações de eixos                                      i=4,30(43:10)                                                               i=3,91(43:11)
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                              escada, rebitado • material: LNE 50 (NBR 6656)
Suspensão dianteira                                    Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                     Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanque de combustível | Arla (litros)                  75 | 12                                              150* | 12*             150* | 25*             (2x150)*2

Rodas | Pneus                                          6.75x17.5 | 235/75R17.5

2
    Configuração (2x150) somente com ee 46 e com Arla de 25 litros.
~~~

#### Desempenho teórico

~~~text
Desempenho                                          MB G 70-6                                          MB G 70-6 AMT
Pneus                                                  235/75R17.5                                        235/75R17.5

Relações de eixo                                       i=4,30 / 3,91                                      i=4,30 / 3,91

Velocidade máxima (km/h)                               nd                                                 nd

Capacidade de subida - 9.600 kg (%)4                   nd                                                 nd

Capacidade de subida - 13.000 kg (%)4                  nd                                                 nd

3
    Velocidade máxima limitada eletronicamente. 4 Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | acionamento                                     Tambor/Disco* | Pneumático

Freio de estacionamento                                Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                         Convencional + Top Brake (Freio de cabeçote)

                                                       ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC® (Controle Eletrônico de
Eletrônica Auxiliar                                    Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                       (Assistência de Partida em Rampa)5 • Interface CAN - SAE J1939
5
    Somente com câmbio automatizado
~~~

---

### 26.7 Novo Accelo 1117 - 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `698b148a-f8d0-424f-b6fb-5f60193513f0.pdf` |
| Versão do prospecto | V6/26 |
| Data do prospecto | 27/07/2026 |
| SHA-256 | `e7214cc8d90db16462407dc9d6e14ee6d038ab191f383a04a7b31bbdf0e5a596` |
| PBT - linha literal | Cab. [C/E] 3397 /+10 3397 /+10 3553 /+10 PBT 16000/10700 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                         31                      39                  46
[a] Distância entre eixos                                  3100                    3900                4600

[b] Comprimento total (c/ lanterna)                        6136                    7136                7966

[c] Largura                                                2176                    2176                2176

[d] Altura [C,E] base da antena (descarregado)             2600                    2605                2589

[e] Bitola eixo (dianteiro/traseiro)                       1810/1706               1810/1706           1810/1706

[f] Balanço (dianteiro/traseiro)                           1321/1700               1322/1900           1322/2030

[g] Ângulo de entrada (carregado)                          22°                     22°                 22°

[h] Angulo de saída (carregado)                            20°                     18°                 16°

[i] Altura: [C,E] base antena ao chassi                    1806                    1811                1804

[j] Dist. min.:eixo dianteiro à carroceria [C/E] c/ eqp.   420/600                 420/600             420/600

Círculo de viragem (parede a parede)                       12600                   15100               17200
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                             31          39               46       Pesos Admissíveis1 | ee                             legal/técnico 31 | 39 | 46
Eixo Dianteiro                                             2330        2256          2393        Eixo Dianteiro                                                  6000/3600

Eixo Traseiro                                              1067        1218          1160        Eixo Traseiro                                                   10000/7100

Cab. [C/E]                                                 3397 /+10 3397 /+10 3553 /+10         PBT                                                            16000/10700

Transm. G 90-6 AMT                                                           +90                 Carga útil máx.+ equip.                            12603/7303 12526/7226 12447/7147

Tanques (L):150 / (2x150)                                  +68 / nd    +68 / nd      +68 /+230   PBTC                                                          14000 / 14000

Tanque Arla 32: 25 l                                       +11         +11           +11         Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                                 considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                   [C] Curta                                         [E] Estendida

Suspensão da cabine                                       Metálica                                          Metálica
~~~

#### Motor

~~~text
Motor                                                  MB OM 924 LA • BlueTec 6• 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                            163 cv (120 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                              610 Nm (62,2 kgfm) @ 1200 - 1600 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                     24V | (2x12V)/100Ah | 28V/80Ah
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                            EATON ESO 6206 A                                     MB G 90-6 AMT*
Tipo                                                      Manual                                               Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                           6 | 6,20/0,78                                        6 | 6.70/0,73

Embreagem (auxílio pneumático)                            Monodisco, 362 mm                                    Monodisco, 362 mm
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                          MB HL2 (R325) estampado
Bloqueio                                                  Transversal*

Relações de eixos                                         4,30(43:10)                                                     3,91(43:11)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                                 escada, rebitado • material: LNE 50 (NBR 6656)
Suspensão dianteira                                       Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                        Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                        75 | 12                                            150* | 12*              150* | 25*        (2x150)*2 | 25

Rodas | Pneus                                             6.75x17.5 | 235/75R17.5

2
    Configuração de tanques (2x150) litros, somente no ee 46 e com Arla de 25 litros.
~~~

#### Desempenho teórico

~~~text
Desempenho                                             EATON ESO 6206                                                  MB G 90-6 AMT*
Pneus                                                     235/75R17.5                                                     235/75R17.5

Relações de eixo                                          4,30 / 3,91*                                                    4,30 / 3,91*

Velocidade máxima (km/h)                                  1203                                                            1203

Capacidade de subida4 - 10700 kg (%)                      36 / 33                                                         39 / 35

Capacidade de subida4 - 14000 kg (%)                      27 / 25                                                         29 / 27

3                                                 5
    Velocidade máxima limitada eletronicamente.       Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                        Tambor / Disco* | Pneumático

Freio de estacionamento                                   Câmara de mola acumuladora acionada pneumaticamente

Freio auxiliar                                            Convencional + Top Brake® (Freio de cabeçote)
                                                          ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                       Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                          (Assistência de Partida em Rampa)5 • Interface CAN - SAE J1939
5
    Somente com câmbio automatizado (AMT)
~~~

---

### 26.8 Accelo 1317 - 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `80d7e839-71e0-4e6f-870a-466785c9d042.pdf` |
| Versão do prospecto | V1/26 |
| Data do prospecto | 08/07/2026 |
| SHA-256 | `9e7d95eb622f197b25b2538cd6a1e546ab46106d37f1e8f1d3e6add89e0c8b0a` |
| PBT - linha literal | Cab. versão [C]* 4.287 4.331 Peso Bruto Total (PBT) 23.000/13.000 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                      39                                  46
[a] Distância entre eixos (1°-2°-3°)                    3.900+978                           4.600+978

[b] Comprimento total                                   8.031                               8.732

[c] Largura                                             2.232                               2.232

[d] Altura [C/E] (descarregado)                         2.423                               2.423

[e] Bitola (eixo dianteiro/eixo traseiro)               1.790/1.760                         1.790/1.760

[f] Balanço (dianteiro/traseiro)                        1.233/1.920                         1.233/1.920

[g] Ângulo de entrada (carregado)                       23°                                 23°

[h] Ângulo de saída (carregado com estepe)              nd                                  nd

[i] Altura: teto da cabine ao chassi [C]/[E]            1.646                               1.646

[j] Dist. mín. centro do eixo à carroceria [C]/[E]      411/591                             411/591

Círculo de viragem (parede a parede)                    15.900                              17.900
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          39                            46            Pesos Admissíveis1 | ee                                 legal/técnico 39 | 46
Eixo Dianteiro                                          2.332                         2.363         Eixo Dianteiro                                                   6.000/3.200

Eixo traseiro                                           1.955                         1.968         Eixo(s) Traseiro(s)                                            17.000/10.000

Cab. versão [C]*                                        4.287                         4.331         Peso Bruto Total (PBT)                                         23.000/13.000

Cab. Versão [E]                                         + 10                          .+ 10         Carga Útil Máx. + mais carroçaria                    18.713/8.713      18.669/8.669

Tanque Diesel 150 litros                                +62                           +62           PBTC                                                                13.000

                                                        +11 (somente tanque de                      Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
Tanque (Arla 32) 25 litros                                                            +11
                                                        150 litros)                                 considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
Tanque Diesel (2x15) litros                             nd                            +268

Câmbio G 70-6 aut.                                                      +10
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                [C] Curta*                                              [E] Estendida

Suspensão da cabine                                    Metálica                                                Metálica
~~~

#### Motor

~~~text
Motor                                               MB OM 924 LA • BlueTec 6 • 4,8 lts. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                         163 cv (120 kW) @ 2.200 rpm

Torque Máximo [NBR ISO 1585]                           610 Nm (62,2 mkgf) @ 1.200 - 1.600 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria                               24V 2x12V) | 100Ah

Alternador                                             28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                         MB G 70-6                                             MB G 70-6 PowerShift 3
Tipo                                                   Manual                                                Automatizada, sem pedal de embreagem

Nº marchas | Relações primeira/última                  6 | 6,94/0,74                                         6 | 6,94/0,74

Embreagem (auxílio pneumático)                         Monodisco, diâmetro 362mm                             Monodisco, diâmetro 362mm
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                     MB HL2-NR2 (R 325) estampado
Bloqueio                                               transversal (opcional)

Relações de eixos | Câmbio                             i=4,30(43:10)                         i=3,91(43:11)                         | MB G70-6

Relações de eixos | Câmbio                             i=4,30(43:10)                         i=3,91(43:11)                         | MB G 70-6 AMT
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                              escada, rebitado • material: LNE 50 (NBR 6656)
Suspensão dianteira                                    Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                     Tipo balancim com molas trapezoidais e suspensor pneumático do eixo auxiliar com acionamento pelo painel

Tanque de combustível | Arla (litros)                  75 | 12                                    150* | 12*                                    150* | 25*        (2x150)*2

Rodas | Pneus                                          6.00x17.5 | 215/75R17.5                    6.75x17.5 | 235/75R17.5*

2
    Configuração (2x150) somente com ee 46 e com Arla de 25 litros.
~~~

#### Desempenho teórico

~~~text
Desempenho                                          MB G 70-6                                             MB G 70-6 AMT
Pneus                                                  215/75R17.5                                           215/75R17.5

Relações de eixo                                       i=4,30 / i=3,91                                       i=4,30 / i=3,91

Velocidade máxima (km/h)                               nd                                                    nd

Capacidade de subida4 - 13.000 kg (%)                  nd                                                    nd

3
    Para MB G 70, ee 39 e i=4,30, velocidade máxima controlada eletronicamente de 90 km/h.

4
    Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | acionamento                                     Tambor | Pneumático

Freio de estacionamento                                Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                         Convencional + Top Brake (Freio de cabeçote)
                                                       ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC® (Controle Eletrônico de
Eletrônica Auxiliar                                    Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                       (Assistência de Partida em Rampa)* • Interface CAN - SAE J1939
*
    Somente com câmbio automatizado
~~~

---

### 26.9 Novo Accelo 1417 - 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `bc3fe675-4b43-4d5e-84c9-ccdf7dde267e.pdf` |
| Versão do prospecto | V3/26 |
| Data do prospecto | 28/07/2026 |
| SHA-256 | `5eb17fe7f604a2a3bcf757fb0fbfa0b53bc0aeeb57831446cd11c1bdae999386` |
| PBT - linha literal | Cab. [C/E] 4206 /+12 4251 /+12 PBT 23000/13800 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                         39                               46
[a] Distância entre eixos (1°-2°-3°)                       3900+978                         4600+978

[b] Comprimento total (c/ lanterna)                        8135                             8837

[c] Largura                                                2176                             2176

[d] Altura [C,E] base da antena (descarregado)             2423                             2423

[e] Bitola eixo (dianteiro/traseiro)                       1838/1760                        1838/1760

[f] Balanço (dianteiro/traseiro)                           1322/1921                        1322/1922

[g] Ângulo de entrada (carregado)                          21°                              22°

[h] Angulo de saída (carregado)                            nd                               nd

[i] Altura: [C,E] base antena ao chassi                    1646                             1646

[j] Dist. min.:eixo dianteiro à carroceria [C/E] c/ eqp.   420/600                          420/600

Círculo de viragem (parede a parede)                       nd                               nd
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                             39             46                          Pesos Admissíveis1 | ee                              legal/técnico 39 | 46
Eixo Dianteiro                                             2351           2399                     Eixo Dianteiro                                                   6000/3600

Eixo traseiro                                              1855           1852                     Eixo Traseiro                                                   17000/10400

Cab. [C/E]                                                 4206 /+12      4251 /+12                PBT                                                             23000/13800

Transm. G 90-6 AMT                                         +95            +95                      Carga útil máx.+ equip.                                   18794/9594 | 18749/9549

Tanques (L):150 / (2x150)                                  +68 / nd       +68 / +230                       2                                              (13800/13800) | (14000/14000)
                                                                                                   PBTC

Tanque Arla 32: 25 l                                       +11            +11                      Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                                   considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de                         2
                                                                                                       (PBTC) 13800 kg com pneus 215/75R17.5, (PBTC) 14000 kg com pneus 235/75R17.5,
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                  [C] Curta                                            [E] Estendida

Suspensão da cabine                                      Metálica                                             Metálica
~~~

#### Motor

~~~text
Motor                                                 MB OM 924 LA • BlueTec 6• 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                           163 cv (120 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                             610 Nm (62,2 kgfm) @ 1200 - 1600 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                    24V | (2x12V)/100Ah | 28V/80Ah
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                           EATON ESO 6206                                       MB G 90-6 AMT *
Tipo                                                     Manual                                               Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                          6 | 6,20/0,78                                        6 | 6.70/0,73

Embreagem (auxílio pneumático)                           Monodisco, 362 mm                                    Monodisco, 362 mm
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                       MB R325, estampado
Bloqueio                                                 Transversal*

Relações de eixos | Câmbio                               4,30(43:10)                            3,91(43:11)*                               | EATON

Relações de eixos | Câmbio                               4,30(43:10)                            3,91(43:11)*                               | MB G 90-6*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                                escada, rebitado • material: LNE 50 (NBR 6656)
Suspensão dianteira                                      Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                       Tipo balancim com molas trapezoidais e suspensor pneumático do eixo auxiliar com acionamento pelo painel

Tanques (L): combustível | Arla 32                       75 | 12                                 150* | 12*                                   150* | 25*     (2x150)*3 | 25

Rodas | Pneus                                            6.00x17.5 | 215/75R17.5                 6.75x17.5 | 235/75R17.5 *

3
    Configuração de tanques (2x150) litros, somente no ee 46 e com Arla de 25 litros.
~~~

#### Desempenho teórico

~~~text
Desempenho                                            EATON ESO 6206                                                      MB G 90-6 AMT
Pneus                                                    215/75R17.5 | 235/75R17.5 *                                      215/75R17.5 | 235/75R17.5 *

Relações de eixo                                         4,30 / 3,91*                                                     4,30 / 3,91*

                                                               4
Velocidade máxima (km/h)                                 120                                                              1204

Capacidade de subida5 - 14000 kg (%)                     27/26 | 27/25                                                    31/28 | 29/27

4
    Velocidade máxima limitada eletronicamente. 5 Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                       Tambor / Disco* | Pneumático

Freio de estacionamento                                  Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                           Convencional + Top Brake® (Freio de cabeçote)

                                                         ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                      Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                         (Assistência de Partida em Rampa)6 • Interface CAN - SAE J1939
6
    Somente com câmbio automatizado G 90-6 AMT
~~~

---

### 26.10 Novo Atego 1419 - 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `e56e1518-b7f8-4a10-825f-c54c539059a0.pdf` |
| Versão do prospecto | V7/26 |
| Data do prospecto | 29/07/2026 |
| SHA-256 | `a23e34fefbe527f20d3b6e338fcdc9122c133c4dafa5d74d2d5f6bbfb8e71558` |
| PBT - linha literal | Cab. [C] 4919 5035 5059 PBT 16000/14300 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                      36                       48                  54
[a] Distância entre eixos                               3540                   4740                  5.300

[b] Comprimento total (c/ lanterna)                     6.208                  8748                  8747

[c] Largura                                             2430                   2430                  2430

[d] Altura [C,E/LTB]/[LTA] c/ climatizador
                                                        2852 /3272             2852 /3272            2852 /3272
(descarregado)
[e] Bitola eixo (dianteiro/traseiro)                    1984 /1844             1984 /1844            1984 /1844

[f] Balanço (dianteiro/traseiro)                        1439 /1229             1439 /2569            1439 /2008

[g] Ângulo de entrada, (com /sem) spoiler, carregado    21° / 17°              21° / 17°             21° / 17°

[h] Angulo de saída (carregado)                         32°                    15°                   20°

[i] Altura: [C,E,LTB]/[LTA] ao chassi c/ climatizador   1.891/2.313            1.891/2.313           1.891/2.313

[j] Dist. eixo à Cab. [C/E/LTB,LTA] c/ eqp.             420 /490 /890          420 /490 /890         420 /490 /890

Círculo de viragem (parede a parede)                    15.000                 19.000                20.900
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          36            48            54         Pesos Admissíveis1 | ee                             legal/técnico 36 | 48 | 54

Eixo Dianteiro                                          3108          3199        3270         Eixo Dianteiro                                                   6000/4700

Eixo Traseiro                                           1811          1836        1789         Eixo Traseiro                                                   10000/9600

Cab. [C]                                                4919          5035        5059         PBT                                                            16000/14300

Cab. [E/LTB/LTA]                                                    +28 /+116 /+163            Carga útil máx.+ eqp.                               11081/9381|10875/9265|10941/9241

Banco central /3 lugares /Cama basculável                       +19/ +28/ (+26 só [E])         PBT + 3º eixo                                                  23000/21300

Eixo HL4 /Câmbio G 140                                                 -49/ +49                PBTC                                                               23000

Tanques (L): 300                                                         +95                   Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                               considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [C] Curta         [E] Estendida                 [LTB] Leito Teto Baixo                      [LTA] Leito Teto Alto

Suspensão da cabine                                  Metálica          Metálica                      Metálica                                    Metálica
~~~

#### Motor

~~~text
Motor                                             MB OM 924 LA • BlueTec 6 • 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       185 cv (136 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                         700 Nm (71,4 mkgf) @ 1200 - 1600 rpm

Tomada de força                                      No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)100Ah | 28V / 80A                                   24V | (2x12V)135Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       EATON FOSA 5406A                                                        MB G 140-8* PowerShift 3 Advanced
Tipo                                                 Manual                                                               Automatizado, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      6 | 7,05/0,78                                                        8, 9,30/0,79

Embreagem | Tomada de força                          Monodisco, 395 mm | Monodisco, 395 mm | MB NA 121-1b*                Monodisco, 395 mm | MB NA 121-1b*


                                                                                               MB HL4
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MERITOR MS 23.245                                                  MB HL4 (R390)*
                                                                                               (R390)*
Bloqueio                                             nd                                       Transversal*              Transversal*

                                                     4,88(39:8) / 5,57(39:7)* | EATON         4,78(43:9) | EATON        4,78(43:9) / 4,30(43:10)* / 3,91(43:11)* / 5,22(47:9) | | MB G
Relações de eixo | Câmbio
                                                     5406A                                    5406A                     140-8*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Suspensão Dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspesão Traeira                                     Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira Pneumática Opicional              4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   210 | 35                                                                 300* | 35

Rodas | Pneus                                        7.50x22.5 | 275/80R22.5                                                  7.50x20* | 10.00R20*


                                                      EATON 5406A |                                   EATON 5406A |
~~~

#### Desempenho teórico

~~~text
Desempenho                                                                                                                      MB G 140-8* | HL4 (R390)
                                                      MERITOR 23.245                                  HL4 (R390)*
Pneus                                                275/80R22.5                       275/80R22.5 275/80R22.5                    275/80R22.5 275/80R22.5 275/80R22.5 275/80R22.5

Relações de eixo                                     4,88                              5,77          4,78*                        4,78*        3,91*         4,30*         5,22*

Velocidade máxima (km/h)                             1202                              1202          1202                         1202         1202          1202          1202

Capacidade de subida3 - 21300 kg (%)                 21                                24            21                           28           23            25            30

Capacidade de subida3 - 23000 kg (%)                 19                                22            19                           25           21            23            28

2
    Velocidade máxima limitada eletronicamente. 3 Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa)4 • Interface CAN - SAE J1939
4
    Somento com câmbio automatizado MB G 140-8
~~~

---

### 26.11 Novo Atego 1719 - 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `611b7e05-dcee-4f54-a13a-e5d1e7ba7576.pdf` |
| Versão do prospecto | V5/26 |
| Data do prospecto | 19/07/2026 |
| SHA-256 | `7ca11fe12fbb6e827ecb5beff349caf97ec1dc8f06d6940fc4da6bdc84b9336d` |
| PBT - linha literal | Cab. [C] 5275 5299 5391 5415 PBT 16000/17100 |
| CMT - linha literal | Eixo HL4 /Câmbio G 140 -49/ +49 PBTC / CMT 27000 |

#### Dimensões

~~~text
Dimensões1 | ee                                      36                 42                 48               54
[a] Distância entre eixos                               3540               4100               4740             5300

[b] Comprimento total (c/ lanterna)                     6208               7086               8748             8747

[c] Largura                                             2430               2430               2430             2430

[d] Altura [C,E/LTB]/[LTA] c/ climatizador
                                                        2861/3281          2861/3281          2861/3281        2861/3281
(descarregado)
[e] Bitola eixo (dianteiro/traseiro)                    1984/1844          1984/1844          1984/1844        1984/1844

[f] Balanço (dianteiro/traseiro)                        1439/1229          1439/1547          1439/2569        1439/2008

[g] Ângulo de entrada, (com /sem) spoiler, carregado    21° | 17°          21° | 17°          21° | 17°        21° | 17°

[h] Angulo de saída (carregado)                         32º                26°                15°              20°

[i] Altura: [C,E,LTB]/[LTA] ao chassi c/ climatizador   1891/2313          1891/2313          1891/2313        1891/2313

[j] Dist. eixo à Cab. [C/E/LTB,LTA] c/ eqp.             420 /490 /890      420 /490 /890      420 /490 /890    420 /490 /890

Círculo de viragem (parede a parede)                    15000              17000              19000            20900
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          36         42        48       54             Pesos Admissíveis1 | ee           legal/técnico 36 |42 |48 |54

Eixo Dianteiro                                          3457        3523     3489      3611          Eixo Dianteiro                                          6000/6100

Eixo Traseiro                                           1818        1778     1902      1804          Eixo Traseiro                                          10000/11000

Cab. [C]                                                5275        5299     5391      5415          PBT                                                    16000/17100

Cab. [E/LTB/LTA]                                                    +28 /+116 /+163                  Carga útil máx.+ eqp.             10725/11825 10701/11801 10609/11709 10585/11685

Banco central /3 lugares /Cama basculável                       +19/ +28/ (+26 só [E])               PBT + 3º eixo                                          23000/24100

Eixo HL4 /Câmbio G 140                                                 -49/ +49                      PBTC / CMT                                                27000

Tanques (L): 300                                                           +95                       Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                                     considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [C] Curta         [E] Estendida                  [LTB] Leito Teto Baixo                          [LTA] Leito Teto Alto

Suspensão da cabine                                  Metálica          Metálica                       Metálica                                        Metálica
~~~

#### Motor

~~~text
Motor                                             MB OM 924 LA • BlueTec 6 • 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       185 cv (136 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                         700 Nm (71,4 mkgf) @ 1200 - 1600 rpm

Tomada de força                                      No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)100Ah | 28V / 80A                                    24V | (2x12V)135Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 90-6                                              MB G 140-8* PowerShift 3 Advanced
Tipo                                                 Manual                                                 Automatizado, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      6 | 6,70/0,73                                          8 | 9,30/0,79

Embreagem | Tomada de força                          Monodisco, 395 mm | MB NA 60-1b*                       Monodisco, 395 mm | MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MERITOR MS 23.245                                       MB HL4 (R390)*
Bloqueio                                             nd                                                      Transversal*

Relações de eixo | Câmbio                            4,88/6,84(39:8) / 5,57/7,60(39:7)* | MB G 90-6          4,78(43:9) / 4,30(43:10)* / 3,91(43:11)* / 5,22(49:7) | MB G 140-8*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Suspensão Dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspesão Traeira                                     Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira Pneumática Opicional              4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   210 | 35                                                                   300* | 35

Rodas | Pneus                                        7.50x22.5 | 275/80R22.5                                                    7.50x20* | 10.00R20*
~~~

#### Desempenho teórico

~~~text
Desempenho                                        MB G 90-6 | MERITOR MS 23.245                                    MB G 140-8* | HL4 (R390)
Pneus                                                275/80R22.5                    275/80R22.5                       275/80R22.5           275/80R22.5     275/80R22.5       275/80R22.5

Relações de eixo                                     4,88 /6,85                     5,77 /7,60*                       4,78                  4,30*           3,91*             5,22*

                                                           2                              2                                 2                     2               2
Velocidade máxima (km/h)                             120                            120                               120                   120             120               1202

Capacidade de subida3 - 23000 kg (%)                 18                             21                                25                    23              21                28

Capacidade de subida3 - 27000 kg (%)                 16                             18                                21                    19              17                24

2
    Velocidade máxima limitada eletronicamente. 3 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa)4 • Interface CAN - SAE J1939
4
    Somento com câmbio automatizado MB G 140-8
~~~

---

### 26.12 Novo Atego 1719 - 4x2 K BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `0cb48595-0093-4592-b842-0c9c1cbd9a88.pdf` |
| Versão do prospecto | V7/26 |
| Data do prospecto | 30/07/2026 |
| SHA-256 | `2f90d118613000245863de2a6505a03850fd43cb66025e1b3fa0796d31040652` |
| PBT - linha literal | Cab. [C/E] 5370 /+26 PBT 16000/17100 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                      36
[a] Distância entre eixos                               3540

[b] Comprimento total (c/ lanterna)                     6208

[c] Largura                                             2430

[d] Altura [C,E] c/ climatizador (descarregado)         2861

[e] Bitola (eixo dianteiro/eixo traseiro)               1984/1874

[f] Balanço (dianteiro/traseiro)                        1439/1229

[g] Ângulo entrada s/ spoiler (carregado)               21°

[h] Angulo de saída (carregado)                         32°

[i] Altura [C,E] ao chassi c/ climatizador              1891

[j] Dist. eixo à Cab [C/E] c/ eqp.                      420 /490

Círculo de viragem (parede a parede)                    15000
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                          36                  Pesos Admissíveis1 | ee                                    legal/técnico 36

Eixo Dianteiro                                                          3479                Eixo Dianteiro                                                   6000/6100

Eixo Traseiro                                                           1891                Eixo Traseiro                                                   10000/11000

Cab. [C/E]                                                           5370 /+26              PBT                                                             16000/17100

Banco central /3 lugares /Cama basculável                       +19/ +28/ (+26 só [E])      Carga útil máx.+ eqp.                                            1063/11730

Eixo HL4 /Câmbio G 140                                                -49 /+49              PBTC                                                               27000

Tanques (L): 300                                                         +95                Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                            considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas


    Cabine Avançada
Versões                                                 [C] Curta                                            [E] Estendida

Suspensão da cabine                                     Metálica                                             Metálica
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                 [C] Curta                                            [E] Estendida

Suspensão da cabine                                     Metálica                                             Metálica
~~~

#### Motor

~~~text
Motor                                             MB OM 924 LA • BlueTec 6 • 4,8 L. • 4 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       185 cv (136 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                         700 Nm (71,4 mkgf) @ 1200 - 1600 rpm

Tomada de força                                      No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)/100Ah | 28V / 80A                                24V | (2x12V)/135Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 90-6                                          MB G 140-8* PowerShift 3 Advanced
Tipo                                                 Manual                                             Automatizado, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      6 | 6,70/0,73                                      8 | 9,30/0,79

Tomada de força | Embreagem                          Monodisco, 395 mm | MB NA 60-1b*                   Monodisco, 395 mm | MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MERITOR MS 23.245                         MB HL4 (R390)*
Bloqueio                                             nd                                        Transversal*

Relações de eixo | Câmbio                            4,88(39:8) / 5,57/(39:7)*                                                                                  | MB G 90-6

Relações de eixo | Câmbio                                                                      4,78 (43:9) / 4,30(43:10)*          5,22(47:9)* / 3,91(43:11)*   | MB G 140-8*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Suspensão Dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspesão Traeira                                     Molas curtas trapezoidais

Suspensão Traseira Pneumática Opicional              4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   210 | 35                                                               300* | 35

Rodas | Pneus                                        7.50x22.5 | 275/80R22.5                                                7.50x20* | 10.00R20*
~~~

#### Desempenho teórico

~~~text
Desempenho                                        MB G 90-6 | MERITOR MS 23.245                                MB G 140-8* | HL4 (R390)*
Pneus                                                275/80R22.5                                                  275/80R22.5

Relações de eixo                                     4,88 / 5,57*                                                 4,78 / 3,91*                                     4,30* / 5,22*

Velocidade máxima (km/h)                             1202 / 117                                                   1202 / 1202                                      1202 / 116

Capacidade de subida3 - 23000 kg (%)                 18 / 21                                                      25 / 21                                          23 / 28

Capacidade de subida3 - 27000 kg (%)                 16 / 18                                                      21 / 17                                          19 / 24

2
    Velocidade máxima limitada eletronicamente. 3 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa)4 • Interface CAN - SAE J1939
4
    Somento com câmbio automatizado MB G 140-8
~~~

---

### 26.13 Novo Atego 1726 - 4x2 BluetTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `6c299880-5b6e-4d2f-8e95-360c55a62876.pdf` |
| Versão do prospecto | V5/26 |
| Data do prospecto | 03/02/2026 |
| SHA-256 | `89e9e98596bd46a05e91ce972255e1448d050cc572e9dda3abc6bb591f142eb3` |
| PBT - linha literal | Cab. [C] 5494 5524 5614 5638 PBT 16000/17100 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                 36                  42                48                 54
[a] Distância entre eixos                          3600               4160               4800               5360

[b] Comprimento total (c/ lanterna)                6259               7136               8798               8798

[c] Largura                                        2430               2430               2430               2430

[d] Altura [C,E/LTB]/[LTA] c/ climatizador
                                                   2784/2776/3252 2784/2776/3252 2784/2776/3252 2784/2776/3252
(descarregado)
[e] Bitola eixo (dianteiro/traseiro)               1985/1845          1985/1845          1985/1845          1985/1845

[f] Balanço (dianteiro/traseiro)                   1440/1219          1440/1536          1440/2558          1440/1998

[g] Ângulo de entrada, (com /sem) spoiler,
                                                   21° / 17°          21° / 17°          21° / 17°          21° / 17°
carregado

[h] Angulo de saída (carregado)                    32º                28º                15º                20°

[i] Altura: [C,E,LTB]/[LTA] ao chassi c/
                                                   1829/1821/2297 1829/1821/2297 1829/1821/2297 1829/1821/2297
climatizador

[j] Dist. eixo à Cab. [C/E/LTB,LTA] c/ eqp.        209/389/809        209/389/809        209/389/809        209/389/809

Círculo de viragem (parede a parede)               15000              17000              19000              20900
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                           36       42         48     54              Pesos Admissíveis1 | ee                legal/técnico 36 |42 |48 |54

Eixo Dianteiro                                           3561     3609       3645   3716         Eixo Dianteiro                                         6000/6100

Eixo Traseiro                                            1933     1915       1969   1922         Eixo Traseiro                                         10000/11000

Cab. [C]                                                 5494     5524       5614   5638         PBT                                                   16000/17100

Cab. [E/LTB/LTA]                                                  +28 /+116 /+163                Carga útil máx.+ eqp.             10506/11606 10476/11576 10386/11486 10362/11462

Banco central /3 lugares /Cama basculável                       +19/ +28/ (+26 só [E])                  2                                              33000 / 27000
                                                                                                 PBTC

Eixo HL4 /Câmbio G 140                                                -49/ +49                   Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                                 considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
Tanques (L): 300                                                         +95                     2
                                                                                                  PBTC de 33000 kg somente com câmbio MB G90-6, MB G 140-8 PBTC de 27000 kg pra
                                                                                                 o câmbio MB G 140-8
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [C] Curta         [E] Estendida                  [LTB] Leito Teto Baixo                         [LTA] Leito Teto Alto

Suspensão da cabine                                  Metálica          Metálica                       Metálica                                       Metálica
~~~

#### Motor

~~~text
Motor                                             MB OM 926 LA • BlueTec 6• 7,2 L. • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       260 cv (191 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                         900 Nm (91,8 mkgf) @ 1200 - 1600 rpm

Tomada de força                                      No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)100Ah | 28V / 80A                                    24V | (2x12V)135Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 90-6                                              MB G 140-8* PowerShift 3 Advanced
Tipo                                                 Manual                                                 Automatizado, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      6 | 6,70/0,73                                          8 | 9,30/0,79

Embreagem | Tomada de força                          Monodisco, 395 mm | MB NA 60-1b*                       Monodisco, 395 mm | MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MERITOR MS 23.245                                       MB HL4 (R390)*
Bloqueio                                             nd                                                      Transversal*

Relações de eixo | Câmbio                            4,88/6,84(39:8) / 5,57/7,60(39:7)* | MB G 90-6          4,78(43:9) / 4,30(43:10)* / 3,91(43:11)* / 5,22(49:7) | MB G 140-8*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Suspensão Dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspesão Traeira                                     Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira Pneumática Opicional              4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   210 | 35                                                                  300* | 35

Rodas | Pneus                                        7.50x22.5 | 275/80R22.5                                                   7.50x20* | 11.00R20*
~~~

#### Desempenho teórico

~~~text
Desempenho                                        MB G 90-6 | MERITOR MS 23.245                                                MB G 140-8* | HL4 (R390)
Pneus                                                275/80R22.5                                                                  275/80R22.5

Relações de eixo                                     4,88 / 5,57*                                                                 4,78 / 4,30* / 3,91* / 5,22*

                                                           3
Velocidade máxima (km/h)                             120                                                                          1203

Capacidade de subida4 - 27000 kg (%)                 20 /23                                                                       28 /23 /25 /30

Capacidade de subida4 - 33000 kg (%)                 16 /19                                                                       23 /18 /20 /25

3
    Velocidade máxima limitada eletronicamente. 4 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa)5 • Interface CAN - SAE J1939
5
    Somento com câmbio automatizado MB G 140-8
~~~

---

### 26.14 Novo Atego 1726 - K 4x2 BluetTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `6d1e9352-a88b-4950-a5ae-978cec870ba5.pdf` |
| Versão do prospecto | V3/26 |
| Data do prospecto | 03/02/2026 |
| SHA-256 | `541ed06a6ec3d23dfc18cde57a6e38c37d4110b3fbf30da3b7f1fa4fcfa36fce` |
| PBT - linha literal | Cab. [C/E] 5324 /+29 PBT 16000/1.100 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                      36
[a] Distância entre eixos                               3540

[b] Comprimento total (c/ lanterna)                     6198

[c] Largura                                             2430

[d] Altura [C,E] c/ climatizador (descarregado)         2861

[e] Bitola (eixo dianteiro/eixo traseiro)               1984 /1844

[f] Balanço (dianteiro/traseiro)                        1439 / 1219

[g] Ângulo entrada s/ spoiler (carregado)               21°

[h] Angulo de saída (carregado)                         33º

[i] Altura [C,E] ao chassi c/ climatizador              1891

[j] Dist. eixo à Cab. [C/E] c/ eqp.                     420 /490 /890

Círculo de viragem (parede a parede)                    15000
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                          36                  Pesos Admissíveis1 | ee                                    legal/técnico 36

Eixo Dianteiro                                                          2430                Eixo Dianteiro                                                   6000/6100

Eixo Traseiro                                                           1918                Eixo Traseiro                                                   10000/11000

Cab. [C/E]                                                            5324 /+29             PBT                                                             16000/1.100

Banco central /3 lugares /Cama basculável                       +19/ +28/ (+26 só [E])      Carga útil máx.+ eqp.                                           10.676/11776

Eixo HL4 /Câmbio G 140                                                +49/ +49              PBTC                                                               33000

Tanques (L): 300                                                         +95                Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                            considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas


    Cabine Avançada
Versões                                                 [C] Curta                                            [E] Estendida

Suspensão da cabine                                     Metálica                                             Metálica
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                 [C] Curta                                            [E] Estendida

Suspensão da cabine                                     Metálica                                             Metálica
~~~

#### Motor

~~~text
Motor                                             MB OM 926 LA • BlueTec 6 • 7,2 L • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       260 cv (191 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                         900 Nm (91,8 mkgf) @ 1200 - 1600 rpm

Tomada de força                                      No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal / Bateria | Alternador                24V (2x12V) / 100Ah | 28V / 80A                                24V (2x12V) / 135Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 90-6                                          MB G 140-8* PowerShift 3 Advanced
Tipo                                                 Manual                                             Automatizado

Nº marchas | Relações 1ª/última                      6 | 6,70/0,73                                      8 | 9,30/0,79

Tomada de força | Embreagem                          Monodisco, 395 mm | MB NA 60-1b*                   Monodisco, 395 mm | MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MERITOR MS 23.245                         MB HL4 (R390)*
Bloqueio                                             nd                                        Transversal*

Relações de eixo | Câmbio                            4,88(39:8) / 5,57/(39:7)*                                                                                      | MB G 90-6

Relações de eixo | Câmbio                                                                      4,78 (43:9) / 4,30(43:10)*          5,22(47:9)* / 3,91(43:11)*       | MB G 140-8*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Suspensão Dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira                                   Molas curtas trapezoidais

Suspensão Traseira Pneumática Opicional              4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   210 | 35                                                               300* | 35

Rodas | Pneus                                        7.50x22.5 | 275/80R22.5                                                7.50x20* | 11.00R20*
~~~

#### Desempenho teórico

~~~text
Desempenho                                        MB G 90-6 | MERITOR                                                   MB G 140-8* | HL4*
Pneus                                                275/80R22.5                                                        275/80R22.5                        275/80R22.5

Relações de eixo                                     4,88 / 5,57*                                                       4,78 / 3,91*                       4,30* / 5,22*

Velocidade máxima (km/h)                             1202/ 1202120                                                      1202/ 1202120                      1202/ 119

Capacidade de subida3 - 24100 kg (%)                 26 /31                                                             31 /25                             28 /34

Capacidade de subida3 - 33000 kg (%)                 16 /19                                                             23 /18                             20 /25

2
    Velocidade máxima limitada eletronicamente. 3 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa)4 • Interface CAN - SAE J1939
4
    Somento com câmbio automatizado MB G 140-8
~~~

---

### 26.15 Novo Atego 2429 - 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `0fd54076-6bdd-4350-a9cc-4fa6c6022460.pdf` |
| Versão do prospecto | V6/26 |
| Data do prospecto | 11/03/2026 |
| SHA-256 | `59308c53f5c3b424f6536f83a550b203daa4a9c45c69f5c80e53e83e36dc1b51` |
| PBT - linha literal | Cab. [C] 6288 6686 6711 PBT 23000/24100 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                       36                      48                    54
[a] Distância entre eixos                                3600+1250               4800+1250             5360+1250

[b] Comprimento total (c/ lanterna)                      7484                    9847                  9.847

[c] Largura                                              2460                    2460                  2460

[d] Altura [C,E/LTB]/[LTA] c/ climatizador
                                                         2849 /3369              2842 /3262            2849 /3369
(descarregado)
[e] Bitola eixo (dianteiro/traseiro)                     1984 /1874              1984 /1874            1984 /1874

[f] Balanço (dianteiro/traseiro)                         1439 /1195              1439 /2358            1439 /1798

[g] Ângulo entrada c/ spoiler / s spoiler] (carregado)   21° /17°                21° /17°              21° /17°

[h] Angulo de saída (carregado)                          nd°                     nd°                   nd°

[i] Altura: [C,E,LTB]/[LTA] ao chassi c/ climatizador    1893 /2313              1886 /2306            1893 /2313

[j] Dist. eixo à Cab. [C/E/LTB,LTA] c/ eqp.              420 /490 /890           420 /490 /890         420 /490 /890

Círculo de viragem (parede a parede)                     17200                   21200                 23100
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                           36              48           54         Pesos Admissíveis1 | ee                            legal/técnico 36 | 48 | 54

Eixo Dianteiro                                           3364            3672          3777      Eixo Dianteiro                                                 6000/6100

Eixos Traseiros                                          2924            3014          2934      Eixos Traseiros                                               17000/18000

Cab. [C]                                                 6288            6686          6711      PBT                                                           23000/24100

Cab [E/LTB/LTA]                                                      +29 /+62 /+108              Carga útil máx.+ eqp.                          16721/17812 16314/17414 16289/17389

Banco central /3 lugares /Cama basculável                  +19 /+28 /+26 (só [E,LTB,LTA])        PBTC                                                             27000

Tanques (L): 300 / (2x300)                               +95 /nd         +95 /+300               Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                                 considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas


    Cabine Avançada
Versões                                                  [C] Curta             [E] Estendida              [LTB] Leito Teto Baixo                   [LTA] Leito Teto Alto

Suspensão da cabine                                      Metálica              Metálica                   Metálica                                 Metálica
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                  [C] Curta             [E] Estendida              [LTB] Leito Teto Baixo                   [LTA] Leito Teto Alto

Suspensão da cabine                                      Metálica              Metálica                   Metálica                                 Metálica
~~~

#### Motor

~~~text
Motor                                               MB OM 926 LA • BlueTec 6• 7,2 L. • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                         286 cv (210 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                           1100 Nm (112,2 kgfm) @ 1200 - 1600 rpm

Tomada de força                                        No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                  24V | (2x12V)/100Ah | 28V / 80A                               24V | (2x12V)/135Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                         MB G 140-8 PowerShift 3 Advanced
Tipo                                                   Automatizado, sem pedal de embreagem

Nº marchas | Relações 1ª/última                        8, | 9,30/0,79

Embreagem | Tomada de força                            Monodisco, 395 mm | MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                     MB HL4 (R390)
Bloqueio                                               Transversal*

Relações de eixo                                       4,78 (43:9)                                               4,30 (43:10)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                              escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Suspensão dianteira                                    Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                     Tipo balancim, com molas trapezoidais e suspensor pneumático do eixo auxiliar

Suspensão Traseira Pneumática Opicional                4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                     210 | 35                                    300* | 35                                   (2x300 l)*2 | 35

Rodas | Pneus                                          7.50x22.5 | 275/80R22.5                     8.25x22.5 | 295/80R22.5                     7.50x20* | 10.00R20*

2
    Configuração de tanques (L) (2x300), apenas nos ee 48 e 54.
~~~

#### Desempenho teórico

~~~text
Desempenho                                          MB G 140-8
Pneus                                                  275/80R22.5                                                    275/80R22.5

Relações de eixo                                       4,78                                                           4,30*

Velocidade máxima (km/h)                               1203                                                           1203

Capacidade de subida3 - 24100 kg (%)                   38                                                             34

Capacidade de subida3 - 27000 kg (%)                   34                                                             31

3
    Velocidade máxima limitada eletronicamente. 4Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                     Tambor | Pneumático

Freio de estacionamento                                Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                         Convencional + Top Brake® (Freio de cabeçote)

                                                       ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                    Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                       (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.16 Novo Atego 2429 - K 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `4dd85d31-fad2-4096-8feb-530f181a888b.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 11/03/2026 |
| SHA-256 | `38f5103b30fe3b15e22eff840b322d59dd7b56c544c4926072a6ad69789c462c` |
| PBT - linha literal | Cab.[C/E] 6383 /+29 PBT 23000/24100 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                                                     36

[a] Distância entre eixos                                                         3540+1250

[b] Comprimento total (c/ lanterna)                                                    7424

[c] Largura                                                                            2460

[d] Altura [C,E] c/ climatizador (descarregado)                                        2849

[e] Bitola eixo (dianteiro/traseiro)                                              1984 /1874

[f] Balanço (dianteiro/traseiro)                                                  1439 /1195

[g] Ângulo entrada (carregado)                                                          21°

[h] Angulo de saída (carregado)                                                         nd

[i] Altura: [C,E] ao chassi c/ climatizador                                            1893

[j] Dist. eixo à Cab. [C/E] c/ eqp.                                                420 /490

Círculo de viragem (parede a parede)                                                   17200
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                         36                      Pesos Admissíveis1 | ee                                    legal/técnico 36
Eixo Dianteiro                                                         3457                    Eixo Dianteiro                                                   6000/6100

Eixos Traseiros                                                        2926                    Eixos Traseiros                                                 17000/18000

Cab.[C/E]                                                           6383 /+29                  PBT                                                             23000/24100

Banco central /3 lugares /Cama basculável                     +19 /+28 /+26 (só [E])           Carga útil máx.+ eqp.                                           16617/17717

Tanques (L): 300                                                       +95                     PBTC                                                               27000

1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,              Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
em ordem de marcha, Cabine Curta [C] sem carroceria ou implemento, sem motorista,              considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [C] Curta                                           [E] Estendida

Suspensão da cabine                                  Metálica                                            Metálica
~~~

#### Motor

~~~text
Motor                                             MB OM 926 LA • BlueTec 6 • 7,2 L • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       286 cv (210 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                         1100 Nm (112,2 mkgf) @ 1200 - 1600 rpm

Tomada de força                                      No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)/100Ah | 28V / 80A                                24V | (2x12V)/135Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 140-8 PowerShift 3 Advanced
Tipo                                                 Automatizado, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      8, | 9,30/0,79

Embreagem | Tomada de força                          Monodisco, 395 mm | MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MB HL4 (R390)
Bloqueio                                             Transversal*

Relações de eixo                                     4,78 (43:9)                                               4,30 (43:10)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Suspensão dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                   Tipo balancim, com molas trapezoidais e suspensor pneumático do eixo auxiliar

Suspensão Traseira Pneumática Opicional              4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   210 | 35                                   300* | 35

Rodas | Pneus                                        7.50x22.5 | 275/80R22.5                    7.50x20* | 10.00R20*                      7.50x22.5* | 11.00R22.5*
~~~

#### Desempenho teórico

~~~text
Desempenho                                        MB G 140-8
Pneus                                                275/80R22.5                                                    275/80R22.5

Relações de eixo                                     4,78                                                           4,30*

                                                           3
Velocidade máxima (km/h)                             120                                                            1203

Capacidade de subida4 - 23000 kg (%)                 40                                                             36

Capacidade de subida4 - 24100 kg (%)                 38                                                             34

Capacidade de subida4 - 27000 kg (%)                 34                                                             31

3
    Velocidade máxima limitada eletronicamente. 4Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)
                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.17 Novo Atego 2433 - 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2433 6X2.pdf` |
| Versão do prospecto | V1/26 |
| Data do prospecto | 25/02/2026 |
| SHA-256 | `3ca516e895a239a035d4349a6c6d6cf78af885f27d18903b4da4c29836483c64` |
| PBT - linha literal | Cab. [C] 6450 6760 6782 PBT 23000/24100 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                       36                     48                  54
[a] Distância entre eixos                                3600+1250              4800+1250           5360+1250

[b] Comprimento total (c/ lanterna)                      7484                   9847                9787

[c] Largura                                              2460                   2460                2460

[d] Altura [C,E/LTB]/[LTA] c/ climatizador
                                                         2849/3369              2842/3262           2849/3369
(descarregado)
[e] Bitola eixo (dianteiro/traseiro)                     1984/1874              1984/1874           1984/1874

[f] Balanço (dianteiro/traseiro)                         1439/1195              1.439/2.358         1.439/1.798

[g] Ângulo entrada c/ spoiler / s spoiler] (carregado)   21°/17°                21°/17°             21°/17°

[h] Angulo de saída (carregado)                          nd°                    nd°                 nd°

[i] Altura: [C,E,LTB]/[LTA] ao chassi c/ climatizador    1893/2313              1886/2306           1893/2313

[j] Dist. eixo à Cab. [C/E/LTB,LTA] c/ eqp.              420/490/890            420/490/890         420/490/890

Círculo de viragem (parede a parede)                     17200                  21200               23100
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                           36             48           54       Pesos Admissíveis1 | ee                            legal/técnico 36 | 48 | 54

Eixo Dianteiro                                           3504           3728          3844    Eixo Dianteiro                                                 6000/6100

Eixos Traseiros                                          2946           3032          2948    Eixos Traseiros                                               17000/18000

Cab. [C]                                                 6450           6760          6782    PBT                                                           23000/24100

Cab [E/LTB/LTA]                                                      +29 /+62 /+108           Carga útil máx.+ eqp.                          16550/17650 16240/17340 16208/17308

Banco central /3 lugares /Cama basculável                  +19 /+28 /+26 (só [E,LTB,LTA])     PBTC                                                             36000

Tanques (L): 300 / (2x300)                               +95/ nd        +95 /+300             Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                              considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas


    Cabine Avançada
Versões                                                  [C] Curta            [E] Estendida            [LTB] Leito Teto Baixo                   [LTA] Leito Teto Alto

Suspensão da cabine                                      Metálica             Metálica                 Metálica                                 Metálica
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                                  [C] Curta            [E] Estendida            [LTB] Leito Teto Baixo                   [LTA] Leito Teto Alto

Suspensão da cabine                                      Metálica             Metálica                 Metálica                                 Metálica
~~~

#### Motor

~~~text
Motor                                               MB OM 926 LA • BlueTec 6• 7,2 L. • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                         321 cv (236 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                           1250 Nm (127,5 mkgf) @ 1200 - 1600 rpm

Tomada de força                                        No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                  24V | (2x12V)/100Ah                                 24V | (2x12V)/135Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                         MB G 211-12 PowerShift 3 Advanced
Tipo                                                   Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                        12, sem anéis sincronizadores | 14,93/1,00

Embreagem | Tomada de força                            Monodisco, 430 mm | MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                     MB HL4 (R390)
Bloqueio                                               Transversal*

Relações de eixos                                      3,58 (43:12) / 3,31 (43:13)* / 3,91(43:9)* / 4,30(43:10)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                              escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Suspensão dianteira                                    Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                     Tipo balancim, com molas trapezoidais e suspensor pneumático do eixo auxiliar

Suspensão Traseira Pneumática Opicional                4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                     210 | 35                                       300* | 35                                2x300*2 | 35

Rodas | Pneus                                          7.50x22.5 | 275/80R22.5                        8.25x22.5 | 285/80R22.5                  7.50x20* | 10.00R20*

2
    Configuração de tanques (L) (2x300), apenas nos ee 48 e 54.
~~~

#### Desempenho teórico

~~~text
Desempenho                                          MB G 211-12
Pneus                                                  275/80R22.5

Relações de eixo                                       3,58 /3,31 /3,91* /4,30*

Velocidade máxima (km/h)                               116 /116 /111 /107

                       3                               55 /51 /61 /67
Capacidade de subida - 23000 kg (%)

Capacidade de subida3 - 24100 kg (%)                   53 /49 /68 /54

Capacidade de subida3 - 36000 kg (%)                   35 /32 /38 /42

3
    Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                     Tambor | Pneumático

Freio de estacionamento                                Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                         Convencional + Top Brake® (Freio de cabeçote)

                                                       ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                    Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                       (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.18 Novo Atego 3033 - 8x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica Novo ATEGO 3033.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 27/04/2026 |
| SHA-256 | `9e55a0a8907fd565e48c1c2eab12ce73b5794ff2bddbe65403c9604f50a91314` |
| PBT - linha literal | Cab.[C] 7.460 7.620 7.700 PBT 29000/30200 |
| CMT - linha literal | Não localizado como linha isolada; consultar quadro de pesos abaixo |

#### Dimensões

~~~text
Dimensões1 | ee                                      48                    54                    63

[a] Distância entre eixos (1°-2°-3°-4°)                 2350+3010+1250        2350+3010+1250        2350+3950+1250

[b] Comprimento total (c/ lanterna)                     9357                  9846                  9778

[c] Largura                                             2460                  2460                  2460

[d] Altura [C,E,LTB]/[LTA] c/ climatizador
                                                        2876 /3296            2869 /3289            2869 /3289
(descarregado)

[e] Bitola eixo (dianteiro/traseiro)                    1984 /1874            1984 /1874            1984 /1874

[f] Balanço (dianteiro/traseiro)                        1439 /1308            1439 /1797            1.439/789

[g] Ângulo de entrada, (com /sem) spoiler, carregado    21o/15o               21o/15o               21o/15o

[h] Angulo de saída (carregado)                         nd                    nd                    nd

[i] Altura: [C,E,LTB]/[LTA] ao chassi c/ climatizador   1893 /2313            1886 /2306            1.886/2.306

[j] Dist. eixo à Cab [C/E/LTB,LTA] c/ eqp.              420 /490 /890         420 /490 /890         420 /490 /890

Círculo de viragem (parede a parede)                    21700                 23700                 26800
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          48           54            63         Pesos Admissíveis1 | ee                            legal/técnico 48 | 54 | 63
Eixos Dianteiros (1º+2º)                                4774         4656          4858       Eixos Dianteiros (1º+2º)                                     12000/12200

Eixos Traseiros (3º+4º)                                 2638         2960          2702       Eixos Traseiros (3º+4º)                                      17000/18000

Cab.[C]                                                 7.460        7.620         7.700      PBT                                                          29000/30200

Cab.[E]/[LTB]/[LTA]                                               +28 /+116 /+163             Carga útil máx.+ eqp.                          21588/22788 21474/22674 21440/22640

Banco central /3 lugares /Cama basculável               +19 /+28 /+26                         PBTC                                                             36000

Tanques (L): 315 ou (2x315)                             +117 /+322                            Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                              considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos e pesos admissíveis em kg, em ordem de
marcha, Cabine Curta [C], sem carroceria ou implemento, sem motorista, com todos os
reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa de
ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [C] Curta              [E] Estendida          [LTB] Leito Teto Baixo                   [LTA] Leito Teto Alto

Suspensão da cabine                                  Metálica               Metálica               Metálica                                 Metálica
~~~

#### Motor

~~~text
Motor                                             MB OM 926 LA • BlueTec 6• 7,2 L. • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       321 cv (236 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                         1250 Nm (127,5 mkgf) @ 1200 - 1600 rpm

Tomada de força                                      No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)100Ah / (2x12V) | 135Ah | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 211-12 PowerShift 3 Advanced
Tipo                                                 Automatizado, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      12, sem anel sincronizador | 14,93/1,00

Embreagem | Tomada de força                          Monodisco, 430 mm | MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MB (R390)
Bloqueio                                             Transversal*

Relações de eixo                                     3,58(43:12) / 3,91(43:11)* / 4,30(43:10)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, parafusado e rebitado, sem emenda atrás da cabina • material: LNE 50 (NBR 6656)
Segundo eixo dianteiro                               Suspensor pneumático

Suspensão dianteira                                  Feixe de molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                   Tipo balancim, com molas trapezoidais e suspensor pneumático do eixo auxiliar

Suspensão Traseira Pneumática Opicional              PNEUMÁTICA* - 4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora* (Sob consulta)

Tanques (L): combustível | Arla 32                   210 | 35                                    315* | 35                           (2x315*) | 35 - somente nos ee 54 e 63.

Rodas | Pneus                                        7.50x22.5 | 275/80R22.5                     7.50x20* | 10.00R20*                8.25x22.5* | 295/80R22.5*
~~~

#### Desempenho teórico

~~~text
Desempenho                                        MB G 211-12
Pneus                                                275/80R22.5

Relações de eixo                                     3,58 / 3,91* / 4,30*

Velocidade máxima (km/h)                             1202/1202/113

Capacidade de subida3 - 29000 kg (%)                 44/48/53

Capacidade de subida3 - 30200 kg (%)                 42/46/51

Capacidade de subida3 - 36000 kg (%)                 35/38/42

2                                             3
    Velocidade máxima limitada eletronicamente. Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.19 Novo Atego 3133 - 6x4 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `33635741-eeb2-40ec-aeb8-deabd7b2d4db.pdf` |
| Versão do prospecto | V6/26 |
| Data do prospecto | 06/07/2026 |
| SHA-256 | `64f84cba8267dfa5e08ff845e3a890d07a977cb9588dab55722a6c8f64ba0f19` |
| PBT - linha literal | Cab. [E] 8477 PBT 23000/30500 |
| CMT - linha literal | Retarder +100 PBTC /CMT 56000 / 56000 |

#### Dimensões

~~~text
Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,
em ordem de marcha, Cabine Estendida [E] sem carroceria ou implemento, sem
motorista, com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor
de incêndio e caixa de ferramentas
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                         48                       Pesos Admissíveis1 | ee   legal/técnico 48

Eixo Dianteiro                                                         4104                     Eixo Dianteiro                 6000/6500

Eixos Traseiros                                                        4373                     Eixos Traseiros               17000/24000

Cab. [E]                                                               8477                     PBT                           23000/30500

Cama Basculável                                                         +26                     Carga útil máx.+ eqp.         14523/22023

Retarder                                                               +100                     PBTC /CMT                    56000 / 56000

Tanques (L): (2x300)                                                   +289
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,
em ordem de marcha, Cabine Estendida [E] sem carroceria ou implemento, sem
motorista, com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor
de incêndio e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                               [E] Estendida

Suspensão da Cabine                                   Metálica
~~~

#### Motor

~~~text
Motor                                              MB OM 926 LA • BlueTec 6 • 7,2 L • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        321 cv (236 kW) @ 2200 rpm

Torque Máximo [NBR ISO 1585]                          1250 Nm (127,5 mkgf) @ 1200 - 1600 rpm

Tomada de Força                                       No volante do motor*
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V)/135Ah | 28V/80A                                  24V | (2x12V)/170Ah* | 28V / 80A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 211-12 PowerShift 3 Advancedf
Tipo                                                  Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 14,93/1,00

Embreagem | Tomada de força                           Monodisco, 430 mm | MB NA 121-1b*

f
    Dois modos de operação: Power off-road, para condução em estradas de terra e ECO mode para condução em rodovias
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                    MB RT300P (HD7/HL7)
Bloqueio                                              Longitudinal e Transversal

Relações de eixo                                      5,33(28:21x4,00)                        4,83(29:24x4,00)*                           6,00(27:18x4,00)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, rebitado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                    Molas parabólicas tipo boogie com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    300 / (2x300)* | 60

Rodas | Pneus                                         9.00x22.5* | 295/80R22.5                     8.00X22.0 * | 11R22.0 *              8.25x22.5* | 295/80R22.5 *
~~~

#### Desempenho teórico

~~~text
Desempenho                                         MB G 211-12 | MB RT300P
Pneus                                                 295/80R22.5                                  295/80R22.5                             295/80R22.5

Relações de eixo                                      5,33                                         4,83*                                   6,00*

Velocidade máxima (km/h)                              98                                           108                                     87

Capacidade de subida2 - 30500 kg (%)                  60                                           55                                      68

                        2                             33                                           30                                      37
Capacidade de subida - 56000 kg (%)

Capacidade de subida2 - 63000 kg (%)                  29                                           26                                      33

2
    Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                    Tambor | Pneumático

Freio de estacionamento                               Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                        Convencional + Top Brake® (Freio de cabeçote)

Freio adicional                                       Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                   Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                      (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.20 Novo Axor 2038 - LS 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica Novo Axor 2038 LS.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 23/01/2026 |
| SHA-256 | `2d8f1b9b7d251bc6e3102c008feef08a20739b2271fa5c50a518284d3c97c33d` |
| PBT - linha literal | Cab. [LTB/LTA] 7173 /+45 PBT 16000/20100 |
| CMT - linha literal | Rodas de Alumínio / Freio a disco / Retarder -105 /-127 /+76 CMT 62000 |

#### Dimensões

~~~text
Dimensões1 | ee                                     36
[a] Distância entre eixos                              3551

[b] Comprimento total (c/ lanterna)                    5891

[c] Largura                                            2550

[d] Altura [LTB/LTA] c/ climatizador2, descarregado    3205 /3627

[e] Bitola (eixo dianteiro/eixo traseiro)              2077 /1803

[f] Balanço (dianteiro/traseiro)                       1440 /900

[g] Ângulo de entrada (carregado)                      13°

[h] Ângulo de saída (carregado)                        31°

[i] Altura: [LTB/LTA] ao chassi c/ climatizador2       2192 /2614

[j] Dist. eixo à Cab. [LTB/LTA] c/ eqp.                1185

[l] Posição 5ª roda                                    350

Círculo de viragem (parede a parede)                   14700
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                         36                                       Pesos Admissíveis1 | ee                                legal/técnico | 36
Eixo Dianteiro                                         4983                                  Eixo Dianteiro                                                   6000/7100

Eixo Traseiro                                          2190                                  Eixo Traseiro                                                   10000/13000

Cab. [LTB/LTA]                                         7173 /+45                             PBT                                                             16000/20100

Tanques (L): 410 / (410+320)                           +2 /+308                              Carga máx. na 5ª roda                                            8827/12927

Rodas de Alumínio / Freio a disco / Retarder           -105 /-127 /+76                       CMT                                                                62000
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,            Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
em ordem de marcha, Cabine Leito teto Baixo [LTB], sem carroceria ou implemento, sem         considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
motorista, com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor   2
de incêndio e caixa de ferramentas                                                               Altura do climatizador, 120 mm
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [LTB] Leito Teto Baixo                                           [LTA] Leito Teto Alto

Suspensão da cabine                                  Pneumática                                                       Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       381 cv (280 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                         1900 Nm (193,7 kgfm) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)/220Ah | 28V/150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 PowerShift 3 Advancd
Tipo                                                 Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      12, sem anéis sincronizadores | 16,46/1,00

Embreagem                                            Monodisco, 430 mm

Tomada de força                                      MB NA 131-2c* / MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                      MB R440 NFD
Bloqueio                                             Transversal*

Relações de eixo                                     2,85 (37:13 / 2,73 (41:15)* / 3,08 (40:13)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, rebitado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                   Pneumática, 4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   400 / 410* / (410+320)* | 90

Rodas | Pneus                                        8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                         G 291 | R440
Pneus                                                295/80R22.5

Relações de eixo                                     2,85 / 2,73* / 3,08*

Velocidade máxima (km/h)                             1203

Capacidade de subida4 - 46000 kg (%)                 35 / 34 / 39

Capacidade de subida4 - 62.000 kg (%)                25 / 24 / 27

3
    Velocidade máxima limitada eletronicamente. 4 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | acionamento                                   Tambor /Disco | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

Freio Adicional                                      Retarder Voith R 115 V* (opcional sob consulta)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa) • Interface CAN - SAE J1939


     [C]=Standard/Curta, [E]=Estendida, [L]=Leito, [LTB]=Leito Teto Baixo, [LTA]=Leito Teto Alto, [M]=MegaSpace, [S]=Space, [TS]=TopSpace.
     "ee"=distância entre 1º eixo dianteiro e 1º eixo traseiro com tração, nd=item não disponível, "*"=item opcional. Os itens opcionais citados neste folheto
     podem não estar imediatamente disponíveis para atendimento. Os dados apresentados podem variar de acordo com a configuração do veículo. Imagens
     meramente ilustrativas. O Manual de Implementação, para projetos de carrocerias e equipamentos e o Manual do Veículo encontram-se disponíveis em
     www.mercedes-benz-trucks.com.br. Procure um Concessionário Mercedes-Benz e consulte a disponibilidade das múltiplas configurações e opcionais
     oferecidos. O desempenho teórico é calculado considerando-se piso asfáltico seco e o limite de escorregamento. No interesse do desenvolvimento
     tecnológico, a Mercedes-Benz reserva-se o direito de alterar as especificações e os desenhos dos produtos sem prévio aviso. A qualidade do meio
     ambiente é respeitada pela tecnologia dos produtos Mercedes-Benz. Para mais informações, ligue 0800 970 90 90 ou acesse www.mercedes-benz-
     trucks.com.br. Mercedes-Benz, uma empresa Daimler Truck AG
~~~

---

### 26.21 Novo Axor 2038 - S 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica Novo Axor 2038 S.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 23/01/2026 |
| SHA-256 | `fdfeef8730a5a6ee06acbd12066817ac912f6882d0f2891a363f61a4bc1e6bcf` |
| PBT - linha literal | Cab. [LTB / LTA] 7506 / +45 PBT 16000/20100 |
| CMT - linha literal | CMT |

#### Dimensões

~~~text
Dimensões1 | ee                                     36

[a] Distância entre eixos                              3552

[b] Comprimento total (c/ lanterna)                    5992

[c] Largura                                            2550

[d] Altura [LTB/LTA] c/ climatizador2, descarregado    3240/3662

[e] Bitola (eixo dianteiro/eixo traseiro)              2077/1803

[f] Balanço (dianteiro/traseiro)                       1440/1000

[g] Ângulo de entrada (carregado)                      13°

[h] Ângulo de saída (carregado)                        30°

[i] Altura: [LTB/LTA] ao chassi c/ climatizador2       2192/2614

[j] Dist. eixo à Cab. [LTB/LTA] c/ eqp.                1185

[l] Posição 5ª roda                                    400

Círculo de viragem (parede a parede)                   17400
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                         36                                       Pesos Admissíveis1 | ee                                legal/técnico | 36
Eixo Dianteiro                                         4977                                  Eixo Dianteiro                                                   6000/7100

Eixo Traseiro                                          2529                                  Eixo Traseiro                                                   10000/13000

Cab. [LTB / LTA]                                       7506 / +45                            PBT                                                             16000/20100

Tanques (L): 410 / (410+320)                           +2 /+308                              Carga máx. na 5ª roda                                            8494/12594

Rodas de Alumínio / Retarder                           -105 /+76                                   3                                                         62000 /68000
                                                                                             CMT
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,            Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
em ordem de marcha, Cabine Leito teto Baixo [LTB], sem carroceria ou implemento, sem         considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
motorista, com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor   2
                                                                                              Altura do climatizador, 120 mm. 3CMT de 62000 kg com MB G 291, CMT de 68000 kg
de incêndio e caixa de ferramentas
                                                                                             apenas com MB G 340
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [LTB] Leito Teto Baixo                                              [LTA] Leito Teto Alto

Suspensão da cabine                                  Pneumática                                                          Pneumática
~~~

#### Motor

~~~text
Motor                                             MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       381 cv (280 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                         1900 Nm (193,7 kgfm) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)/230Ah | 28V/150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 291-12 PowerShift 3 Advancd                                 MB G 340-12 PowerShift 3 Advancd*
Tipo                                                 Automatizada, sem pedal de embreagem                          Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      12, sem anéis sincronizadores | 16,46/1,00                    12 sem anel sincronizador | 12,79/0,78

Embreagem                                            Monodisco, 430 mm                                             Monodisco, 430 mm

Tomada de força                                      MB NA 131-2c* / MB NA 121-1b*                                 MB NA 131-2c* / MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                     MB R440 NFD                                       MB R300P (c/ redução os cubos)*
Bloqueio                                             Transversal*                                      Transversal*

Relações de eixo                                     2,85 (37:13 / 2,73 (41:15)* / 3,08 (40:13)*       3,71 (26:24 x 3,42)* / 4,14 (29:24 x 3,43)* / 4,33 (26:24 x 4,00)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, rebitado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   400 / 410* / (410+320)* | 90

Rodas | Pneus                                        8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                        G 291 | R440                                                 G 340 | R300P
Pneus                                                295/80R22.5                                                  295/80R22.5

Relações de eixo                                     2,85 / 2,73* / 3,08*                                         3,71 / 4,14* / 4,33*

Velocidade máxima (km/h)                             1204                                                         1204

Capacidade de subida5 - 62000 kg (%)                 25 / 24 / 27                                                 nd

Capacidade de subida5 - 68000 kg (%)                 nd                                                           26 / 27 / 28

4
    Velocidade máxima limitada eletronicamente. 5 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

Freio Adicional                                      Retarder Voith R 115 V* (opcional sob consulta)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.22 Novo Axor 2538 - S 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2538 S.pdf` |
| Versão do prospecto | V1/26 |
| Data do prospecto | 23/01/2026 |
| SHA-256 | `e07ab3b6fa1f62c327a8bb10eb5b372e804c1b37d9dad45963edda92df2c080e` |
| PBT - linha literal | Cab. [LTB / LTA] 8991 /+45 PBT 23000/30100 |
| CMT - linha literal | Em ordem de marcha com Cabine Estendida [LTB], sem carroceria ou implemento, sem Altura do climatizador, 120 mm. 3CMT de 62000 kg com MB G 291, CMT de 68000 kg |

#### Dimensões

~~~text
Dimensões1 | ee                                    36
[a] Distância entre eixos                             3553+1350

[b] Comprimento total (c/ lanterna)                   7243

[c] Largura                                           2550

                                     2                3240/3662
[d] Altura [LTB/LTA] c/ climatizador (descarregado)

[e] Bitola (eixo dianteiro/eixo traseiro)             2077/1803

[f] Balanço (dianteiro/traseiro)                      1440/900

[g] Ângulo de entrada (carregado)                     13°

[h] Ângulo de saída (carregado)                       33°

[i] Altura: [LTB/LTA] ao chassi c/ climatizador2      2192/2614

[j] Dist. eixo à Cab. [LTB/LTA] c/ eqp.               1185

[l] Posição 5ª roda                                   400

Círculo de viragem (parede a parede)                  16900
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                      36                    Pesos Admissíveis1 | ee                                 legal/técnico 36
Eixo Dianteiro                                                      4970               Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                                     4021               Eixo Traseiro                                                   17000/23000

Cab. [LTB / LTA]                                                  8991 /+45            PBT                                                             23000/30100

Tanques (L): 410 / (410+320)                                      +2/ +308             Carga máx. na 5ª roda                                           14009/21109

Rodas de Alumínio / Retarder                                      -165 / +90           CMT3                                                           62000 /68.000

Câmbio G 340 + Eixo R300P                                           +125               Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                       considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1                                                                                      2
  Em ordem de marcha com Cabine Estendida [LTB], sem carroceria ou implemento, sem      Altura do climatizador, 120 mm. 3CMT de 62000 kg com MB G 291, CMT de 68000 kg
motorista, com tanques de combustível cheio, estepe, extintor de incêndio e caixa de   apenas com MB G 340
ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [LTB] Leito Teto Baixo                                            [LTA] Leito Teto Alto

Suspensão da cabine                                  Pneumática                                                        Pneumática
~~~

#### Motor

~~~text
Motor                                             MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       381 cv (280 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                         1900 Nm (193,7 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)/220Ah | 28V/150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 291-12 PowerShift 3 Advancd                            MB G 340-12 PowerShift 3 Advancd *
Tipo                                                 Automatizada, sem pedal de embreagem                        Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      12, sem anéis sincronizadores | 16,46/1,00                  12,sem anel sincronizador | 12,79/0,78

Embreagem                                            Monodisco, 430 mm                                           Monodisco, 430 mm

Tomada de força                                      MB NA 131-2c* / MB NA 121-1b*                               MB NA 131-2c* / MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MB R440 NFD                                                 MB R300P (cubos c/ redução)*
Bloqueio                                             Transversal*                                                Transversal*

Relações de eixo                                     2,85 (37:13) / 2,73 (41:15)* / 3,08 (40:13)*                4,33 (26:24 x 4,00)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, rebitado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   400 / 410* / (410+320)* | 90

Rodas | Pneus                                        8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                        G 291 | R440                                               G 340 | R300P
Pneus                                                295/80R22.5                                                295/80R22.5

Relações de eixo                                     2,85 / 2,73* / 3,08*                                       4,33

Velocidade máxima (km/h)                             1204                                                       1204

Capacidade de subida5 - 62000 kg (%)                 25 / 24 / 27                                               nd

Capacidade de subida5 - 68000 kg (%)                 nd                                                         28

4
    Velocidade máxima limitada eletronicamente. 5 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

Freio Adicional                                      Retarder Voith R 115 V* (opcional sob consulta)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.23 Novo Axor 2545 - LS 6x2 BluaTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2545 LS.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 23/01/2026 |
| SHA-256 | `3b05b876d63c5df30a3101299e110d41fd46d3b80a106b353f47d128b42c7e15` |
| PBT - linha literal | Cab. [LTB/LTA] 8803 /+45 PBT 23000/30100 |
| CMT - linha literal | Tanques (L): 410 / (410+320) +2 /+308 CMT 62000 |

#### Dimensões

~~~text
Dimensões1 | ee                                     36
[a] Distância entre eixos (1º-2º-3º)                   3550+1350

[b] Comprimento total (c/ lanterna)                    7240

[c] Largura                                            2550

[d] Altura [LTB/LTA] c/ climatizador2 (descarregado)   3205 /3627

[e] Bitola eixo (dianteiro/traseiro)                   2077 /1803

[f] Balanço (dianteiro/traseiro)                       1440 /900

[g] Ângulo de entrada (carregado)                      12°

[h] Ângulo de saída (carregado)                        31°

[i] Altura: [LTB/LTA] ao chassi c/ climatizador2       2192 /2614

[j] Dist. eixo à Cab. [LTB/LTA] c/ eqp.                1266

[l] Posição 5ª roda                                    400

Círculo de viragem (parede a parede)                   16900
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                        36                        Pesos Admissíveis1 | ee                              legal/técnico 33 | 36
Eixo Dianteiro                                                         5085                  Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                                        3718                  Eixos Traseiros                                                 17000/23000

Cab. [LTB/LTA]                                                      8803 /+45                PBT                                                             23000/30100

Rodas de Alumínio / Freio a disco / Retarder                        -165 /+76                Carga máx. na 5ª roda                                    14239/19339 | 14197/19297

Tanques (L): 410 / (410+320)                                         +2 /+308                CMT                                                                62000

1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,            Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
em ordem de marcha, Cabine Leito teto Baixo [LTB], sem carroceria ou implemento, sem         considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
motorista, com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor   2
de incêndio e caixa de ferramentas                                                               Altura do climatizador, 120 mm
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [LTB] Leito Teto Baixo                                           [LTA] Leito Teto Alto

Suspensão da cabine                                  Pneumática                                                       Pneumática
~~~

#### Motor

~~~text
Motor                                             MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       449 cv (330 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                         2200 Nm (224,3 kgfm) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)/230Ah | 28V/150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 291-12 PowerShift 3 Advancd
Tipo                                                 Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      12, sem anéis sincronizadores | 16,46/1,00

Embreagem                                            Monodisco, 430mm

Tomada de força                                      MB NA 131-2c* / MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                     MB R440 NFD
Bloqueio                                             Transversal*

Relações de eixo                                     2,85 (37:13 / 2,73 (41:15)* / 3,08 (40:13)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, rebitado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                   Pneumática, 4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   400 / 410* / (410+320)* | 90

Rodas | Pneus                                        8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                        G 291 | R440
Pneus                                                295/80R22.5

Relações de eixo                                     2,85 / 2,73* / 3,08*

Velocidade máxima (km/h)                             1203

Capacidade de subida4 - 58500 kg (%)                 32 / 30 / 35

Capacidade de subida4 - 62000 kg (%)                 30 / 28 / 32

3
    Velocidade máxima limitada eletronicamente. 4 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

Freio Adicional                                      Retarder Voith R 115 V* (opcional sob cnsulta)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.24 Novo Axor 2545 - S 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2545 S.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 23/01/2026 |
| SHA-256 | `9daf7156b1c6550157011987d57db0d84f83b70c9fc1f18ce94b11ab143fd757` |
| PBT - linha literal | Cab. [LTB/LTA] 8991 /+45 PBT 23000/30100 |
| CMT - linha literal | CMT |

#### Dimensões

~~~text
Dimensões1 | ee                                    36

[a] Distância entre eixos (1º-2º-3º)                  3553+1350

[b] Comprimento total (c/ lanterna)                   7243

[c] Largura                                           2550

[d] Altura [LTB/LTA] c/ climatizador2(descarregado)   3240/3662

[e] Bitola eixo (dianteiro/traseiro)                  2077/1803

[f] Balanço (dianteiro/traseiro)                      1440/900

[g] Ângulo de entrada (carregado)                     13°

[h] Ângulo de saída (carregado)                       33°

[i] Altura: [LTB/LTA] ao chassi c/ climatizador2      2192/2614

] Dist. eixo dianteiro à Cab. [LTB/LTA] c/ eqp.       1185

[l] Posição 5ª roda                                   400

Círculo de viragem (parede a parede)                  16900
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                      36                    Pesos Admissíveis1 | ee                                 legal/técnico 36

Eixo Dianteiro                                                      4970               Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                                     4021               Eixos Traseiros                                                 17000/23000

Cab. [LTB/LTA]                                                    8991 /+45            PBT                                                             23000/30100

Rodas de Alumínio / Retarder                                      -165 /+76            Carga máx. na 5ª roda                                           14009/21109

Câmbio G 340 + Eixo R300P                                           +125                     3                                                        62000 /68.000
                                                                                       CMT

Tanques (L): 410 / (410+320)                                      +2 /+308             Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                       considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1                                                                                      2
  Em ordem de marcha com Cabine Estendida [LTB], sem carroceria ou implemento, sem      Altura do climatizador, 120 mm. 3CMT de 62000 kg apenas com MB G 291, CMT de
motorista, com tanques de combustível cheio, estepe, extintor de incêndio e caixa de   68000 kg apenas com MB G 340
ferramentas.
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada
Versões                                              [LTB] Leito Teto Baixo                                             [LTA] Leito Teto Alto

Suspensão da cabine                                  Pneumática                                                         Pneumática
~~~

#### Motor

~~~text
Motor                                             MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. em linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                       449 cv (330 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                         2200 Nm (224,3 kgfm) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                24V | (2x12V)/230Ah | 28V/150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                       MB G 291-12 PowerShift 3 Advancd                               MB G 340-12 PowerShift 3 Advancd*
Tipo                                                 Automatizada, sem pedal de embreagem                        Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                      12, sem anéis sincronizadores | 16,46/1,00                  12, sem anel sincronizador | 12,79/0,78

Embreagem                                            Monodisco, 430 mm                                           Monodisco, 430mm

Tomada de força                                      MB NA 131-2c* / MB NA 121-1b*                               MB NA 131-2c* / MB NA 121-1b*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                   MB R440 NFD                                                MB R300P (cubos c/ redução)*
Bloqueio                                             Transversal*                                               Ttransversal*'

Relações de eixo                                     2,85 (37:13 / 2,73 (41:15)* / 3,08 (40:13)*                4,33 (26:24 x 4,00)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                            escada, rebitado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                  Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                   400 / 410* / (410+320)* | 90

Rodas | Pneus                                        8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                        G 291 | R440                                               G 340 | R300P
Pneus                                                295/80R22.5                                                295/80R22.5

Relações de eixo                                     2,85 / 2,73* / 3,08*                                       4,33*

Velocidade máxima (km/h)                             1204                                                       1204

Capacidade de subida5 - 62000 kg (%)                 30 / 28 / 32                                               nd

Capacidade de subida5 - 68000 kg (%)                 nd                                                         33

4
    Velocidade máxima limitada eletronicamente. 5 Em movimetno
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança
Tipo | Acionamento                                   Tambor | Pneumático

Freio de estacionamento                              Câmara de mola acumuladora acionada pneumaticamente

Freio Auxiliar                                       Convencional + Top Brake® (Freio de cabeçote)

Freio Adicional                                      Retarder Voith R 115 V* (opcional sob cnsulta)

                                                     ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
Eletrônica Auxiliar                                  Estabilidade) • EBD (Distribuição Eletrônica de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) • Hill Holder
                                                     (Assistência de Partida em Rampa) • Interface CAN - SAE J1939
~~~

---

### 26.25 Actros 2045 - LS 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2045 LS.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `7fad0eec1d3ee36962c249c5d2e2f3d6b374e62e9451d3f7b7de00d631855366` |
| PBT - linha literal | Cab. [S/TS] 7959 /+52 PBT 16000/20100 |
| CMT - linha literal | Defletores: teto+lateral curta +64 CMT 62000 |

#### Dimensões

~~~text
Dimensões1 | ee                                      36

[a] Distância entre eixos                              3550

[b] Comprimento total (c/ lanterna)                    5860

[c] Largura                                            2500

[d] Altura [S/TS] base antena (descarregado)           3373/3672

[e] Bitola eixo (dianteiro/traseiro)                   2080/1802

[f] Balanço (dianteiro/traseiro)                       1396/914

[g] Ângulo de entrada (carregado)                      13°

[h] Ângulo de saída (carregado)                        nd

[i] Altura: [S/TS] base antena ao chassi               2287/2637

[k] Posição da 5ª roda                                 250

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         1108/1102

Círculo de viragem (parede a parede)                   14400
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          36                                    Pesos Admissíveis1 | ee                                    legal/técnico 36
Eixo Dianteiro                                         5246                                   Eixo Dianteiro                                                   6000/7100

Eixo Traseiro                                          2713                                   Eixo Traseiro                                                   10000/13000

Cab. [S/TS]                                            7959 /+52                              PBT                                                             16000/20100

Retarder / Rodas de alumínio / Beliche                 -76 /-77 /+24                          Carga máx. na 5ª roda                                            8041/12141

Defletores: teto+lateral curta                         +64                                    CMT                                                                62000

Tanques (L): (535+320) / 535                           -63 /-393                              Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                              considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                             [TS] TopSpace

Suspensão da Cabine                                   Metálica - Conforto                                                   Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        449 cv (330 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2200 Nm (224,3 kgfm) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V)/230Ah | 28V/150A                                24V | (2x12V)/220Ah* | 28V/150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 Powershift 3 Advanced
Tipo                                                  Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 16,46/1,00

Embreagem                                             Monodisco, 430 mm

Tomada de força                                       MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                      MB R440 NFD                                                            MB R440
Bloqueio                                              Transversal (série)                                                    Transversal (série)

Relações de eixo                                      2,84(37:13)                          2,84(37:13)*                      3,08(40:13)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão Dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira                                    Pneumática, 4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    (535+410) / (535+320)* / 535* | 90

Rodas | Pneus                                         8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                         RD 440 NFD
Pneus                                                 295/80R22.5                                  295/80R22.5                              295/80R22.5

Relações de eixo                                      2,84                                         2,73*                                    3,08*

Velocidade máxima (km/h)                              1202                                         1202                                     1202

Capacidade de subida3 - 58500 kg (%)                  32                                           31                                       35

Capacidade de subida3 - 62000 kg (%)                  30                                           29                                       33

2
    Velocidade máxima limitada eletronicamente 3Em movimento.
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                     EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor, Disco* | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Convencional + Top Brake | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.26 Actros 2045 - S 4x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2045 S.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `88e6fd3625357cb6f7b88507bfa066ca6981102c833fdaffb6e93eece8cd1035` |
| PBT - linha literal | Cab. [S/TS] 8334 /+52 PBT 16000/20100 |
| CMT - linha literal | Defletores: teto+lateral curta +64 CMT 62000 |

#### Dimensões

~~~text
Dimensões1 | ee                                      36
[a] Distância entre eixos                              3550

[b] Comprimento total (c/ lanterna)                    5946

[c] Largura                                            2520

[d] Altura [S/TS] base antena (descarregado)           3371/3670

[e] Bitola eixo (dianteiro/traseiro)                   2080/1802

[f] Balanço (dianteiro/traseiro)                       1396/1000

[g] Ângulo de entrada (carregado)                      13°

[h] Ângulo de saída (carregado)                        nd

[i] Altura: [S/TS] base antena ao chassi               2336/2635

[k] Posição da 5ª roda                                 250

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         1108/1102

Círculo de viragem (parede a parede)                   14400
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          36                                    Pesos Admissíveis1 | ee                                    legal/técnico 36
Eixo Dianteiro                                         5106                                   Eixo Dianteiro                                                   6000/7100

Eixo Traseiro                                          3228                                   Eixo Traseiro                                                   10000/13100

Cab. [S/TS]                                            8334 /+52                              PBT                                                             16000/20100

Retarder / Rodas de alumínio / Beliche                 -76 /-77 /+24                          Carga máx. na 5ª roda                                            7666/11766

Defletores: teto+lateral curta                         +64                                    CMT                                                                62000
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,             Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,            considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                             [TS] TopSpace

Suspensão da Cabine                                   Metálica - Conforto                                                   Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 460 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        449 cv (330 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2.200 Nm (224,3 mkgf) @ 1.100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V)/230Ah | 28V / 150A                             24V | (2x12V)/220Ah* | 28V / 150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 Powershift 3 Advanced
Tipo                                                  Automatizada, sem pedal de embreagem

Nº marchas | Relações primeira/última                 12, sem anéis sincronizadores | 16,46/1,00

Embreagem                                             Monodisco, 430 mm

Tomada de força                                       MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                      MB 440 NFD                                                             MB 440
Bloqueio                                              Transversal (série)                                                    Transversal (série)

Relações de eixo                                      2,84(37:13)                        2,73(41:15)*                        3,08(40:13)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão Dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira                                    Molas trapezoidais com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    (410 + 320) | 90

Rodas | Pneus                                         8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                         MB 440 NFD                                                                           MB 440
Pneus                                                 295/80R22.5                              295/80R22.5                               295/80R22.5

Relações de eixo                                      2,84                                     2,73*                                     3,08*

Velocidade máxima (km/h)                              1202                                     1202                                      1202

Capacidade de subida3 - 58500 kg (%)                  31                                       32                                        35

Capacidade de subida3 - 62000 kg (%)                  29                                       30                                        33

2
    Velocidade máxima limitada eletronicamente 3Em movimento.
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                     EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor, Disco* | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Convencional + Top Brake | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.27 Actros 2548 - LS 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2548 LS.pdf` |
| Versão do prospecto | V3/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `170f9432b39a2257a6b14041214141ec977cbd30e41d178dbe71c9b2e03305e7` |
| PBT - linha literal | Cab. [S/TS] 9047 / +92 9210 / +52 PBT 23000/28100 |
| CMT - linha literal | Defletores: teto+lateral curta / laterais longos +64/ (+75 somente Cab. [TS]) CMT 62000 |

#### Dimensões

~~~text
Dimensões1 | ee                                       33                                36

[a] Distância entre eixos (1º-2º-3º)                    3250+1350                          3550+1350

[b] Comprimento total (c/ lanterna)                     6903                               7203

[c] Largura                                             2500                               2500

[d] Altura [S/TS] base antena (descarregado)            3373/3672                          3373/3672

[e] Bitola eixo (dianteiro/traseiro)                    2080/1802                          2080/1802

[f] Balanço (dianteiro/traseiro)                        1396/907                           1396/907

[g] Ângulo de entrada (carregado)                       13°                                13°

[h] Ângulo de saída (carregado)                         nd                                 nd

[i] Altura: [S/TS] base antena ao chassi                2287/2637                          2287/2637

[k] Posição da 5ª roda                                  400                                400

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.          1108 /1102                         1108 /1102

Círculo de viragem (parede a parede)                    17800                              18000
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                 33               36                Pesos Admissíveis1 | ee                                 legal/técnico 33 | 36
Eixo Dianteiro                                                  5103             5274             Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                            2219 + 1725       2215 + 1721          Eixos Traseiros                                                 17000/23000

Cab. [S/TS]                                                  9047 / +92       9210 / +52          PBT                                                             23000/28100

Retarder / Rodas de alumínio / Beliche                   .76/ -121/ (+24 somente Cab. [TS]        Carga máx. na 5ª roda                                  13953/19053       13790/18890

Defletores: teto+lateral curta / laterais longos             +64/ (+75 somente Cab. [TS])         CMT                                                                62000

Tanques (L): +535 (ee 36)                               nd                       +34              Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                                  considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis
legal/técnico em kg, em ordem de marcha, Cabine Space [S], sem
carroceria ou implemento, sem motorista, com todos os reservatórios
de fluidos cheios, freios a tambor, estepe, extintor de incêndio e caixa
de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                              [TS] TopSpace

Suspensão da Cabine                                   Metálica - Conforto                                                    Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 460 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        476 cv (350 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2300 Nm (234,5 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V) / 230Ah | 28V / 150Ah
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 Powershift 3 Advanced
Tipo                                                  Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 16,46/1,00

Embreagem                                             Monodisco, 430 mm

Tomada de força                                       MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixos Traseiros                                    MB R440 NFD                                                                         MB R440
Bloqueio                                              Transversal                                                                       Transversal

Relações de eixo                                      i=2,85(37:13)                          i=2,73(41:15)*                             i=3,08 (40:13)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão Dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                    Pneumática, 4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    ee 33 (410+320) | 90                             ee 36 (480+410) / (535+410)* | 90

Rodas | Pneus                                         8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                         RD 440 NFD                                                                  RD 440
Pneus                                                 295/80R22.5                                                                 295/80R22.5

Relações de eixo                                      2,85 | 2,73*                                                                3,08*

Velocidade máxima (km/h)                              1202                                                                        115

                        3                             36 / 40                                                                     44
Capacidade de subida - 53000 kg (%)

Capacidade de subida3 - 55500 kg (%)                  32 / 37                                                                     40

Capacidade de subida3 - 62000 kg (%)                  30 / 34                                                                     38

2
    Velocidade máxima limitada eletronicamente. 3Em movimento.
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                     EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor, Disco* | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Convencional + Top Brake | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.28 Actros 2548 - S 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2548 S.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `d9c5879bea1c2cee132dc91afb71e5db7951ca390ac5bc05b7ddab2b072003d2` |
| PBT - linha literal | Cab. [S/TS] 9772 / +92 PBT 23000/30100 |
| CMT - linha literal | Defletores: teto+lateral curta / laterais longos (+64/ +75) somente Cab. [TS] CMT 62000 / 68000 2 |

#### Dimensões

~~~text
Dimensões1 | ee                                      36
[a] Distância entre eixos (1º-2º-3º)                   3550+1350

[b] Comprimento total (c/ lanterna)                    6903

[c] Largura                                            2500

[d] Altura [S/TS] base antena (descarregado)           3373/3672

[e] Bitola eixo (dianteiro/traseiro)                   2080/1802

[f] Balanço (dianteiro/traseiro)                       1396/907

[g] Ângulo de entrada (carregado)                      13°

[h] Ângulo de saída (carregado)                        nd

[i] Altura: [S/TS] base antena ao chassi               2335/2637

[k] Posição da 5ª roda                                 450

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         1108 /1102

Círculo de viragem (parede a parede)                   18500
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          36                                       Pesos Admissíveis1 | ee                                 legal/técnico 36

Eixo Dianteiro                                                         5331                   Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                                        4441                   Eixos Traseiros                                                 17000/23000

Cab. [S/TS]                                                          9772 / +92               PBT                                                             23000/30100

                                                            +76/-121 / (+24 somente Cab.      Carga máx. na 5ª roda                                           13228/20328
Retarder / Rodas de alumínio / Beliche
                                                                         [TS)]

Defletores: teto+lateral curta / laterais longos            (+64/ +75) somente Cab. [TS]      CMT                                                            62000 / 68000 2

                                                                                              2
Tanques (L): +410 / 535 / (535+410)                    +393 / +34 / +427                          CMT 68000 somente com câmbio G 340 e eixo HL7
1                                                                                             Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,
                                                                                              considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                                [TS] TopSpace

Suspensão da Cabine                                   Metálica - Conforto                                                      Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 460 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        476 cv (350 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2300 Nm (234,5 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V) / 230Ah | 28V / 150Ah
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 Powershift 3 Advanced                                MB G 340-12 Powershift 3 Advanced*
Tipo                                                  Automatizada, sem pedal de embreagem                             Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12 sem anéis sincronizadores | 16,46/1,00                        12, sem anéis sincronizadores | 12,79/0,78

Embreagem                                             Monodisco, diâmetro 430 mm                                       Bidisco, 400 mm / Monodisco, 430 mm*

Tomada de força                                       MB 131-2c*                                                       MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                      MB R440 NFD                                MB R440                      MB (RT 300 P)* - cubos com redução
Bloqueio                                              Transversal (série)                        Transversal (série)          Transversal (série)

Relações de eixo | Câmbio                             2,85(37:13) / 2,73(41:15)* | MB G 291      i=3,08(40:13)* | MB G 291    i=4,33(26:24x4,00) | MB G 340
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão Dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira                                    Molas trapezoidais com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    480 / (480+410)* / 535* / (535+410) | 90

Rodas | Pneus                                         8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                         MB G 291-12 | RD 440 NFD                        MB G 291-12 | RD 440                    MB G 340-12 | RT 300 P*
Pneus                                                 295/80R22.5                                     295/80R22.5                            295/80R22.5

Relações de eixo                                      2,85 / 2,73*                                    3,08*                                  4,33

Velocidade máxima (km/h)                              1202                                            1202                                   115

                        3                             36 / 37                                         40                                     44
Capacidade de subida - 53000 kg (%)

Capacidade de subida3 - 58500 kg (%)                  32 / 34                                         34                                     40

Capacidade de subida3 - 62000 kg (%)                  30 / 32                                         34                                     38

Capacidade de subida3 - 68000 kg (%)                  nd / nd                                         nd                                     34

2
    Velocidade máxima limitada eletronicamente. 3Em movimento.
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                     EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor, Disco* | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Convencional + Top Brake | Retarder Voith R 115 HV*
                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.29 Actros 2553 - LS 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2553 LS.pdf` |
| Versão do prospecto | V4/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `5953fc2fedafd70e5c0399b848359088e4d09514ec02e077b93026838c15ff6b` |
| PBT - linha literal | Cab. [S]/[TS] 9300 / +74 9561 / +74 PBT 23000/28100 |
| CMT - linha literal | Defletores, teto+lateral curta / laterais longas +64/ (+75 somente Cab. [TS]) CMT 62000 |

#### Dimensões

~~~text
Dimensões1 | ee                                      33                                36

[a] Distância entre eixos (1º-2º-3º)                   3250-1350                        3550-1350

[b] Comprimento total (c/ lanterna)                    6905                             7205

[c] Largura                                            2520                             2520

[d] Altura [S/TS] base antena (descarregado)           3373/3672                        3373/3672

[e] Bitola eixo (dianteiro/traseiro)                   2080/1802                        2080/1802

[f] Balanço (dianteiro/traseiro)                       1397/900                         1397/900

[g]/[h] Ângulos: entrada / saída (carregado)           13° / nd                         13° / nd

[i] Altura: [S/TS] base antena ao chassi               2338/2637                        2338/2637

[k] Posição da 5ª roda                                 400                              400

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         1108/1103                        1108/1103

Círculo de viragem (parede a parede)                   17300                            18000
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          33                36                    Pesos Admissíveis1 | ee                              legal/técnico 33 | 36
Eixo Dianteiro                                         5352               5444                  Eixo Dianterio                                          6000/7100           6000/7100

Eixos Traseiros                                        3948               4117                  Eixos Traseiros                                        17000/21000       17000/21000

Cab. [S]/[TS]                                          9300 / +74         9561 / +74            PBT                                                             23000/28100

Retarder / Rodas de alumínio / Beliche                  .76/ -121/ (+24 somente Cab. [TS]       Carga máx. na 5ª roda                                  13700/18800       13439/18539

Defletores, teto+lateral curta / laterais longas            +64/ (+75 somente Cab. [TS])        CMT                                                                 62000

Tanques (L): (+535-480)                                nd                 +34                   Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
                                                                                                considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                                [TS] TopSpace

Suspensão da Cabine                                   Metálica - Conforto                                                      Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 471 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        530 cv (390 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2600 Nm (265,1 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V)/230Ah | 28V/150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 Powershift 3 Advanced
Tipo                                                  Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 16,46/1,00

Embreagem                                             Bidisco, 400 mm

Tomada de força                                       MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                      MB R440 NFD
Bloqueio                                              Transversal (série)

Relações de eixo                                      i=2,85(37:13)                                                i=2,73(41:15)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão Dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira                                    Pneumática, 4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    ee 33 (410+320) | 90                             ee 36 (480+410) / (535+410)* | 90

Rodas | Pneus                                         8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                         MB G 291-12 | MB 440 NFD
Pneus                                                 295/80R22.5                                                    295/80R22.5

Relações de eixo                                      i=2,85                                                         i=2,73*

Velocidade máxima (km/h)                              1202                                                           1202

Capacidade de subida3 - 58500 kg (%)                  26                                                             25

Capacidade de subida3 - 62000 kg (%)                  24                                                             23

2
    Velocidade máxima limitada eletronicamente 3Em movimento.
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                     EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Freio motor de alta performance Jake Brake ® - 580 cv | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.30 Actros 2553 - S 6x2 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2553 S.pdf` |
| Versão do prospecto | V3/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `73c9eaf5715ba96b75eb07b47934dc3bb027d9fb17c20e3b91af71a0bf4521ba` |
| PBT - linha literal | Cab. [S] / [TS] 9964 / + 74 PBT 23000/30100 |
| CMT - linha literal | Defletores: teto+lateral curta / laterais longos (+64/ +75) somente Cab. [TS] CMT |

#### Dimensões

~~~text
Dimensões1 | ee                                      36

[a] Distância entre eixos (1º-2º-3º)                   3550-1350

[b] Comprimento total (c/ lanterna)                    7205

[c] Largura                                            2520

[d] Altura [S/TS] base antena (descarregado)           3371/3670

[e] Bitola eixo (dianteiro/traseiro)                   2080/1872

[f] Balanço (dianteiro/traseiro)                       1397/900

[g] Ângulo de entrada (carregado)                      13°

[h] Angulo de saída (carregado s/ estepe)              nd

[i] Altura: [S/TS] base antena ao chassi               2336/2635

[k] Posição da 5ª roda                                 400

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         1108/1113

Círculo de viragem (parede a parede)                   nd
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                          36                                       Pesos Admissíveis1 | ee                           legal/técnico 36
Eixo Dianteiro                                         5447                                   Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                        4517                                   Eixos Traseiros                                                 17000/23000

Cab. [S] / [TS]                                        9964 / + 74                            PBT                                                             23000/30100

                                                            +76/-121 / (+24 somente Cab.      Carga máx. sobre a 5ª roda                                      13036/20136
Retarder / Rodas de alumínio / Beliche
                                                                         [TS)]
                                                                                                    2                                              62000 / 68000
Defletores: teto+lateral curta / laterais longos            (+64/ +75) somente Cab. [TS]      CMT

1                                                                                             2
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,                 CMT - 68.000, somente com câmbio G 340 e eixo traseiro HL7 (RT 300 P)
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio   Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
e caixa de ferramentas                                                                        considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                               [TS] TopSpace

Suspensão da Cabine                                   Metálica - Conforto                                                     Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 471 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        530 cv (390 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2600 Nm (265,1 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V (2x12V)/230Ah | 28V/150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 Powershift 3 Advanced                                         MB G 340-12 Powershift 3 Advanced
Tipo | Embreagem                                      Automatizada, sem pedal de embreagem | Monodisco, diâmetro 430 mm Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 16,46/1,00                                12, sem anéis sincronizadores | 12,79/0,78

Embreagem                                             Monodisco, 430 mm / Bidisco 400 mm*                                       Bidisco 400 mm*

Tomada de força                                       MB 131-2c*                                                                MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                      MB R440 NFD                                         MB HL7 (RT 300 P) cubos com redução*
Bloqueio                                              Transversal (série)                                 Transversal (série)

Relações de eixo | Câmbio                             i=2,73(41:15) / i=2,85(37:13) * | MB G 291          i=4,33(26:24x4,00) | MB G 340
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão Dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão Traseira                                    Molas trapezoidais com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (l): combustível | Arla 32                    (480 + 410) | 90

Rodas | Pneus                                         8.25x22.5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                         MB G 291-12 | RD 440 NFD                                         MB G 340-12 | RT 300 P *
Pneus                                                 295/80R22.5                                                      295/80R22.5

Relações de eixo                                      i=2,73 / i=2,85*                                                 i=4,33

Velocidade máxima (km/h)                              1203                                                             1203

Capacidade de subida4 - 62000 kg (%)                  23 / 24                                                          28

Capacidade de subida4 - 68000 kg (%)                  nd / nd                                                          26

3
    Velocidade máxima limitada eletronicamente 4Em movimento.
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                     EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | acionamento                                    Tambor | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Freio motor de alta performance Jake Brake ® - 580 cv | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.31 Actros 2651 - LS 6x4 BueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2651 LS.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `4b8786a73995053a838e69a209377d987d566d6c868bc5c0343c0f2137c56a40` |
| PBT - linha literal | Cab.[S/TS] 9821 10038 PBT 23000/27100 |
| CMT - linha literal | Defletores: teto+lateral curta / laterais longos +64/ (+75 somente Cab [TS] CMT 80000 |

#### Dimensões

~~~text
Dimensões1 | ee                                      33                                36

[a] Distância entre eixos (1º-2º-3º)                   3250-1350                          3550-1350

[b] Comprimento total (c/ lanterna)                    6900                               7200

[c] Largura                                            2525                               2525

[d] Altura [S/TS] base antena (descarregado)           3420/3635                          3420/3635

[e] Bitola eixo (dianteiro/traseiro)                   2080/1802                          2080/1802

[f] Balanço (dianteiro/traseiro)                       1400/900                           1400/900

[g] Ângulo de entrada (carregado)                      12°                                12°

[h] Ângulo de saída (carregado)                        >20°                               >20°

[i] Altura: [S/TS] base antena ao chassi               2375/2690                          2375/2690

[k] Posição da 5ª roda                                 500                                500

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         900                                900

Círculo de viragem (parede a parede)                   17800                              18500
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                33                36               Pesos Admissíveis1 | ee                                 legal/Técnico 33 | 36
Eixo Dianteiro                                                 5578             5721             Eixo Dianteiro                                                    6000/7100

Eixos Traseiros                                                2243             4317             Eixos Traseiros                                                  17000/20000

Cab.[S/TS]                                                     9821            10038             PBT                                                              23000/27100
                                                          +76/-121 / (+24 somente Cab.           Carga máx. na 5ª roda                                   13179/17279      12962/17062
Retarder / Rodas de alumínio / Beliche
                                                                       [TS)]

Defletores: teto+lateral curta / laterais longos             +64/ (+75 somente Cab [TS]          CMT                                                                 80000

                                                                                                 Para cumprimento da legislação (lei da balança), o valores admissíveis
Tanques (L): -320 (ee 33) /-410 (ee 36)                        -335             -420             a serem considerados serão sempre o menor valor entre, o LEGAL e
1
                                                                                                 o TÉCNICO
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                             [TS] TopSpace

Suspensão da Cabina                                   Metálica - Conforto                                                   Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 460 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        495 cv (364 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2400 Nm (244,7 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V)/230Ah | 28V / 150A                              24V | (2x12V)/220Ah* | 28V / 150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 Powershift 3 Advanced
Tipo                                                  Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 16,46/1,00

Embreagem                                             Monodisco, 430 mm / Bidisco 400 mm*

Tomada de força                                       MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                      MB R440
Bloqueio                                              Longitudinal e Transversal (série)

Relações de eixo                                      3,08(40:13)                              2,84(37:13)                              3,31(43:13)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                    Pneumática, 4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    ee 33 (410+320)                                                           ee 36 (535+410)

Rodas | Pneus                                         8.25x22,5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                         MB R440
Pneus                                                 295/80R22.5                                  295/80R22.5                           295/80R22.5

Relações de eixo                                      3,08                                         2,84*                                 3,31*

Velocidade máxima (km/h)                              1202                                         1202                                  1202

Capacidade de subida3 - 27100 kg (%)                  67                                           60                                    75

Capacidade de subida3 - 74000 kg (%)                  20                                           19                                    22

Capacidade de subida3 - 80000 kg (%)                  19                                           17                                    20

2
    Velocidade máxima limitada eletronicamente. 3Em movimento.
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                     EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor, Disco* | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Convencional + Top Brake | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.32 Actros 2651 - S 6x4 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2651 S.pdf` |
| Versão do prospecto | V3/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `ea40e905f6ccb6b39126460c26a60dc2a3b2767bb05e7d63b461d32306d9fe10` |
| PBT - linha literal | 10168 PBT 23000/27100 |
| CMT - linha literal | Defletores: teto+lateral curta / laterais longos +64/ (+75 somente Cab [TS] CMT 80000 / 120.0002 |

#### Dimensões

~~~text
Dimensões1 | ee                                      33                                36
[a] Distância entre eixos (1º-2º-3º)                   3250-1350                          3550-1350

[b] Comprimento total (c/ lanterna)                    6900                               7203

[c] Largura                                            2525                               2525

[d] Altura [S/TS] base antena (descarregado)           3455/3670                          3455/3670

[e] Bitola eixo (dianteiro/traseiro)                   2080/1802                          2080/1802

[f] Balanço (dianteiro/traseiro)                       1400/875                           1400/875

[g] Ângulo de entrada (carregado)                      14°                                14°

[h] Ângulo de saída (carregado)                        >20°                               >20°

[i] Altura: [S/TS] base antena ao chassi               2375/2690                          2375/2690

[k] Posição da 5ª roda                                 550                                550

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         900                                900

Círculo de viragem (parede a parede)                   17800                              18500
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                    33               36               Pesos Admissíveis1 | ee                              legal/Técnico 33 | 36

Eixo Dianteiro                                                    5595             5712          Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                                   2354             4456          Eixos Traseiros                                                 17000/20000

                                                                                   10168         PBT                                                             23000/27100
Cab.[S/TS]                                                      9949 /+52
                                                                                    /+52
                                                        +76/-121 /.26 /(+24 somente Cab.         Carga máx. na 5ª roda                                  13051/17151       12832/16932
Retarder / Rodas de alumínio / HL7 / Beliche
                                                                       [TS)]

Defletores: teto+lateral curta / laterais longos             +64/ (+75 somente Cab [TS]          CMT                                                           80000 / 120.0002

                                                                                                 2
Tanques (L): -320 (ee33) /-410 (ee36)                             -420              -335             CMT 120000 kg somente com câmbio G 340 e eixo HL7

1                                                                                                Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,                considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                             [TS] TopSpace

Suspensão da Cabina                                   Metálica - Conforto                                                   Pneumática
~~~

#### Motor

~~~text
Motor                                                 MB OM 460 LA • BlueTec 6 • 12,8 L. • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        495 cv (364 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2400 Nm (244,7 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V)/220Ah | 28V / 150A                               24V | (2x12V)/230Ah | 28V / 150A
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                           MB G 291-12 Powershift 3 Advanced                           MB G 340-12 Powershift 3 Advanced
Tipo                                                  Automatizada, sem pedal de embreagem                           Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 16,46/1,00                     12, sem anéis sincronizadores | 12,79/0,78

Embreagem                                             Monodisco, 430 mm / Bidisco 400 mm*                            Bidisco 400 mm*

Tomada de força                                       MB 131-2c*                                                     MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                         MB R440                                             MB RT 300 P* - cubos com redução
Bloqueio                                              Transversal e longitudinal (série)                     Longitudinal e Transversal (série)

Relações de eixo                                      3,08(40:13) / 2,85(37:13)* / 3,31(43:13)*              4,33(26:24 x 4,00)
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                                escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                    Molas trapezoidais com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    ee 33 (410+320) | 90                                           ee 36 (535+410) | 90

Rodas | Pneus                                         8.25x22,5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                            MB G 291 | MB R 440                                  MB G 340* | MB RT 300 P*
Pneus                                                 295/80R22.5                                             295/80R22.5

Relações de eixo                                      3,08 / 2,85* / 3,31*                                    4,33

Velocidade máxima (km)                                115/ 115/ 115                                           112

                        3                             22/ 20/ 24                                              33
Capacidade de subida - 74000 kg (%)

Capacidade de subida3 - 80000 kg (%)                  20/ 19/ 22                                              30

Capacidade de subida3 - 120000 kg (%)                 -                                                       20

2
    Velocidade máxima limitada eletronicamente; 3 Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                        EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor, Disco* | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Convencional + Top Brake | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.33 Actros 2653 - LS 6x4 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2653 LS.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `5ea58d1a6aaf59283ef251b1a1dc0cb44a9aa2bf4d09051f407d7a963e3e054e` |
| PBT - linha literal | Cab. [S/TS] 9371 /+92 9747 /+92 PBT 23000/27100 |
| CMT - linha literal | Defletores: teto+lateral curta / laterais longos (+64/ +75) somente Cab. [TS] CMT 80000 |

#### Dimensões

~~~text
Dimensões1 | ee                                      33                                36
[a] Distância entre eixos (1º-2º-3º)                   3250+1350                          3550+1350

[b] Comprimento total (c/ lanterna)                    6896                               7196

[c] Largura                                            2500                               2500

[d] Altura [S/TS] base antena (descarregado)           3371/3670                          3371/3670

[e] Bitola eixo (dianteiro/traseiro)                   2080/1802                          2080/1802

[f] Balanço (dianteiro/traseiro)                       1396/900                           1396/900

[g] Ângulo de entrada (carregado)                      13°                                13°

[h] Ângulo de saída (carregado)                        nd                                 nd

[i] Altura: [S/TS] base antena ao chassi               2336/2635                          2336/2635

[k] Posição da 5ª roda                                 450                                450

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         1143/1147                          1143/1147

Círculo de viragem (parede a parede)                   17200                              18000
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                 33               36               Pesos Admissíveis1 | ee                                 legal/técnico 33 | 36

Eixo Dianteiro                                                 5121             5317             Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                             2125+2125        2215+2215           Eixos Traseiros                                                 17000/20000

Cab. [S/TS]                                                  9371 /+92        9747 /+92          PBT                                                             23000/27100

                                                            +76/-121 / (+24 somente Cab.         Carga máx. na 5ª roda                                  13629/17729       13253/17353
Retarder / Rodas de alumínio / Beliche
                                                                         [TS)]

Defletores: teto+lateral curta / laterais longos            (+64/ +75) somente Cab. [TS]         CMT                                                                80000
                                                                                                 Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
Tanques (L): 320 (ee 33) / 410 (ee 36)                 -307 / nd          nd / -98               considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                             [TS] TopSpace

Suspensão da Cabine                                   Metálica - Conforto                                                   Pneumática
~~~

#### Motor

~~~text
Motor                                              MB OM 471 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        530 cv (390 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2600 Nm (265,1 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V) / 230Ah | 28V / 150Ah
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                        MB G 291-12 Powershift 3 Advanced
Tipo                                                  Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 16,46/1,00

Embreagem                                             Bidicso, 400 mm

Tomada de força                                       MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                      MB R440 NFD
Bloqueio                                              Transversal e longitudinal (série)

Relações de eixo                                      i=3,08(40:13)                          i=2,85(37:13) *                                i=3,31(43:13)*
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                             escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                    Pneumática, 4 bolsas por eixo, amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    ee 33 (410) / (410+ 320)* | 90                             ee 36 (480+410) / (535+410)* | 90

Rodas | Pneus                                         8.25x22,5 | 295/80R22.5                                    8.25x22,5 | 315/80R22.5*
~~~

#### Desempenho teórico

~~~text
Desempenho                                         MB R440
Pneus                                                 295/80R22.5                                  295/80R22.5                              295/80R22.5

Relações de eixo                                      3,08                                         2,85*                                    3,31*

Velocidade máxima (km/h)                              1202                                         1202                                     1202

Capacidade de subida3 - 74000 kg (%)                  80                                           80                                       80

Capacidade de subida3 - 80000 kg (%)                  33                                           30                                       35

2
    Velocidade máxima limitada eletronicamente. 3Em movimento.
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                     EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor, Disco* | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Freio motor de alta performance Jake Brake® - 580 cv | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • ESS (Luzes Traseiras de Frenagem de Emergência) • Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill
                                                      Holder (Assistência de Partida em Rampa) • Hold (Assistente de Parada) • Senores de Chuva e Iluminação • Chave Inteligente
Eletrônica Auxiliar                                   com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo de Frenagem) com reconhecimento de pedestres* • (SGA)
                                                      Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto
                                                      Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag motorista* • MirrorCam* (Espelho retrovisor com câmera
                                                      digital)
~~~

---

### 26.34 Actros 2653 - S 6x4 BlueTec 6

| Campo | Valor |
|---|---|
| Arquivo-fonte | `Ficha Técnica 2653 S.pdf` |
| Versão do prospecto | V2/26 |
| Data do prospecto | 16/06/2026 |
| SHA-256 | `f84ee73469332cd72292f63bbed07d8517a1c1fc06cf5bfd1b52c03ddac0f174` |
| PBT - linha literal | 10003 PBT 23000/27100 |
| CMT - linha literal | Eixo HL7 \| Arla 32 (75 L) -26 \| -24 CMT 80000 / 1200002 |

#### Dimensões

~~~text
Dimensões1 | ee                                      33                                36

[a] Distância entre eixos (1º-2º-3º)                   3250-1350                          3550-1350

[b] Comprimento total (c/ lanterna)                    6903                               7203

[c] Largura                                            2520                               2520

[d] Altura [S/TS] base antena (descarregado)           3406/3705                          3406/3705

[e] Bitola eixo (dianteiro/traseiro)                   2080/1802                          2080/1802

[f] Balanço (dianteiro/traseiro)                       1396/907                           1396/907

[g] Ângulo de entrada (carregado)                      15°                                15°

[h] Ângulo de saída (carregado)                        nd                                 nd

[i] Altura: [S/TS] base antena ao chassi '             2336/2635                          2336/2635

[k] Posição da 5ª roda                                 450                                450

[l] Dist. eixo dianteiro à Cab. [S/TS] c/ eqp.         1143/1147                          1143/1147

Círculo de viragem (parede a parede)                   17200                              18000
~~~

#### Pesos, pesos admissíveis, carga útil, PBT/PBTC/CMT e notas da página 1

~~~text
Pesos1 | ee                                                    33                36              Pesos Admissíveis1 | ee                              legal/técnico | 33 | 36
Eixo Dianteiro                                                    5126              5373         Eixo Dianteiro                                                   6000/7100

Eixos Traseiros                                                   4412              4630         Eixos Traseiros                                                 17000/20000
                                                                                   10003         PBT                                                             23000/27100
Cab. [S/TS]                                                    9538 / +74
                                                                                    /+74
                                                            +76/-121 / (+24 somente Cab.         Carga máx. na 5ª roda                                  13462/17100       12997/17097
Retarder / Rodas de alumínio / Beliche
                                                                         [TS)]

Eixo HL7 | Arla 32 (75 L)                                             -26 | -24                  CMT                                                           80000 / 1200002

                                                                                                 2
Defletores: teto+lateral curta / laterais longos            (+64/ +75) somente Cab. [TS]             CMT 120000 somente com câmbio G 340 e eixo HL7
                                                                                                 Para cumprimento da legislação (lei da balança), o valores admissíveis a serem
Tanques (L): +320 / +410                                        +330/ nd          nd /+393       considerados serão sempre o menor valor entre, o LEGAL e o TÉCNICO
1
 Veículo com dimensões em mm, pesos em kg, pesos admissíveis legal/técnico em kg,
em ordem de marcha, Cabine Space [S], sem carroceria ou implemento, sem motorista,
com todos os reservatórios de fluidos cheios, freios a tambor, estepe, extintor de incêndio
e caixa de ferramentas
~~~

#### Cabines e suspensão da cabine

~~~text
Cabine Avançada - MP5
Versões                                               [S] Space                                                              [TS] TopSpace

Suspensão da Cabine                                   Metálica - Conforto                                                    Pneumática
~~~

#### Motor

~~~text
Motor                                                 MB OM 471 LA • BlueTec 6 • 12,8 L • 6 cil. linha • PROCONVE P-8 (Euro 6)
Potência Máxima [NBR ISO 1585]                        530 cv (390 kW) @ 1600 rpm

Torque Máximo [NBR ISO 1585]                          2600 Nm (265,1 mkgf) @ 1100 rpm
~~~

#### Sistema elétrico

~~~text
Sistema Elétrico
Tensão Nominal | Bateria | Alternador                 24V | (2x12V) / 230Ah | 28V / 150Ah
~~~

#### Transmissão e embreagem

~~~text
Transmissão                                           MB G 291-12 Powershift 3 Advanced                            MB G 340-12 Powershift 3 Advanced*
Tipo                                                  Automatizada, sem pedal de embreagem                          Automatizada, sem pedal de embreagem

Nº marchas | Relações 1ª/última                       12, sem anéis sincronizadores | 16,46/1,00                    12, sem anéis sincronizadores | 12,79/0,78

Embreagem                                             Bidisco, 400 mm                                               Bidisco, 400 mm

Tomada de força                                       MB 131-2c*                                                    MB 131-2c*
~~~

#### Eixos traseiros e relações

~~~text
Eixo Traseiro                                         MB R440                                             MB RT 300 P* - cubos com redução
Bloqueio                                              Transversal e longitudinal (série)                     Transversal e longitudinal (série)

Relações de eixo                                      3,08(40:13) / 2,85(37:13)* / 3,31(43:13)*              4,33(26:24 x 4,00)
~~~

#### Chassi, suspensões, tanques, rodas e pneus

~~~text
Chassi                                                escada, parafusado • material: LNE 60 (NBR 6656)
Suspensão dianteira                                   Molas parabólicas com amortecedores telescópicos de dupla ação e barra estabilizadora

Suspensão traseira                                    Molas trapezoidais com amortecedores telescópicos de dupla ação e barra estabilizadora

Tanques (L): combustível | Arla 32                    ee 33 (410) / (410+320)* | 90 | 75*                                    ee 36 (480+410) | 90 | 75*

Rodas | Pneus                                         8.25x22,5 | 295/80R22.5
~~~

#### Desempenho teórico

~~~text
Desempenho                                            MB G 291-12 | MB 440                                  MB G 340* | MB RT 300 P*
Pneus                                                 295/80R22.5                                              295/80R22.5

Relações de eixo                                      3,08 / 2,85* / 3,31*                                     4,33*

Velocidade máxima (km/h)                              1202                                                     1202

Capacidade de subida3 - 74000 kg (%)                  22/20/24                                                 36

Capacidade de subida3 - 80000 kg (%)                  20/19/22                                                 33

Capacidade de subida3 - 120000 kg (%)                 -                                                        22

2
    Velocidade máxima limitada eletronicamente; 3 Em movimento
~~~

#### Freios e sistemas de segurança

~~~text
Freios e Sistemas de Segurança                        EBS (Sistema de Freio com Gerenciamento Eletrônico)
Tipo | Acionamento                                    Tambor | Pneumático

Freio de estacionamento                               Eletrônico com acionamento por tecla no painel

Freio Auxiliar | Freio Adicional                      Freio motor de alta performance Jake Brake® - 580 cv | Retarder Voith R 115 HV*

                                                      ABS (Sistema Anti Travamento das Rodas) • ASR (Controle de Aderência em Aceleração) • ESC/ESP® (Controle Eletrônico de
                                                      Estabilidade) • EBD (Distribuição Eletrônica de Força de Frenagem) • ESS (Luzes Traseiras de Frenagem de Emergência) •
                                                      Alarme Marcha Ré com Luzes Iintermitentes • HSA/Hill Holder (Assistência de Partida em Rampa) • Hold (Assistente de
Eletrônica Auxiliar                                   Parada) • Senores de Chuva e Iluminação • Chave Inteligente com Controle Remoto • Faróis em LED • ABA 5 (Assistente Ativo
                                                      de Frenagem) com reconhecimento de pedestres* • (SGA) Assistente de Ponto Cego* • Assistente de Fadiga* • Farol para
                                                      Auxílio em Manobra* • Farol Alto Inteligente* • (ACC) Piloto Automático Adaptativo* • Sensor de Faixa de Rolagem* • Air Bag
                                                      motorista* • MirrorCam* (Espelho retrovisor com câmera digital)
~~~


---

## 27. Registro de duplicidades e fonte mestre

| Conteúdo | Arquivo mestre usado | Arquivo duplicado/equivalente | Tratamento |
|---|---|---|---|
| Accelo 1317 6x2 BlueTec 6 | `80d7e839-71e0-4e6f-870a-466785c9d042.pdf` | `80d7e839-71e0-4e6f-870a-466785c9d042 (1).pdf` | Cópia binária idêntica; dados não repetidos |
| Novo Atego 2433 6x2 BlueTec 6 | `Ficha Técnica 2433 6X2.pdf` | `b64d8ba2-425b-41f5-8a12-a5cf1a7444ac.pdf` | Texto técnico equivalente; arquivo legível mantido como mestre |

## 28. Protocolo de validação antes da recomendação comercial

1. Confirmar o código exato do modelo, tração, suspensão, cabine e entre-eixos.
2. Confirmar se cada item marcado com `*` está disponível e homologado na combinação pretendida.
3. Recalcular tara e carga útil com implemento, acessórios, motorista, combustível e equipamentos.
4. Aplicar o menor limite entre legislação, chassi, pneus, eixos, quinta roda, implemento e composição.
5. Validar relação de eixo, pneus e transmissão para velocidade operacional, aclives e massa combinada.
6. Validar tomada de força, posicionamento de tanques, balanços e interferências de carroceria.
7. Não converter capacidade de subida teórica em promessa de produtividade ou consumo.
8. Anexar ao CRM a ficha usada, data, versão, premissas e aprovação técnica.
9. Na proposta, separar item de série, opcional solicitado, opcional confirmado e item indisponível.
10. Antes do pedido, emitir checklist assinado por Comercial, Produto/Engenharia e cliente.

## 29. Conclusão Red Team

A base passa a ser adequada para treinamento técnico, consulta comercial e pré-dimensionamento, porque preserva a ficha completa por configuração. Ainda assim, não é um configurador fabril nem substitui validação formal. O principal risco residual é o uso de dados corretos em uma combinação incorreta de opcionais, entre-eixos, pneus, eixo, cabine ou implemento. A governança deve impedir que a simples presença de um item no prospecto seja interpretada como disponibilidade automática ou compatibilidade universal.
