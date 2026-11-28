---
tipo: protocolo
area: Academico
criado: 2026-11-23
status: CONGELADO em 23/11/2026, 02h40, antes da rodada principal (commit deste arquivo)
relacionado: "[[submissao-applied-intelligence]] · [[resultados-preliminares]] · [[taxonomia-erros]]"
---

# Pré-registro leve: rodada principal

Este documento fixa hipóteses, métricas e análise **antes** da rodada principal. Ele vira versão final com um commit datado, depois do piloto. Mudanças posteriores entram como emenda, com data e motivo, e o artigo as declara.

## Dados (congelados)

| Arquivo | SHA-256 (16) | Conteúdo |
|---|---|---|
| `fatos_norma.jsonl` | 53918fb57945c1b3 | 61 fatos-norma, 84 versões erradas |
| `dialogos.jsonl` | 1199c65790d4766f | 300 diálogos, sementes 101–103, **estratificados** (emenda 1): 108 limpos, 96 com um erro, 96 mistos; 2.113 afirmações, 13,5% erradas, 187 erros críticos; 120 respostas sem erro e 135 com erro crítico |
| `piloto.jsonl` | e1e2937f981af61a | 30 diálogos, semente 1, sem estratos (`--sem-estratos` o reproduz). **Fora da análise principal:** serviu para ajustar o prompt e o desenho |

Sobreposição de respostas entre o piloto e o conjunto principal: 0.

## Juízes e prompts (congelados após o piloto)

Os juízes são: holístico, holístico com normas, por afirmação, por afirmação + regras (método proposto) e por afirmação sem RAG. Recuperação: híbrida BM25 + bge-m3 em trechos (RRF, k = 3).

Hash dos prompts em `juizes.py` (SHA-256/16): SISTEMA 5049d6e21e4be10d · P_HOLISTICO 73a9b52ef7e3c094 · P_EXTRAIR 44077df7a44901a7 · P_VERIFICAR f08def070b48ffcd.

**Ajuste feito antes do piloto:** a regra de equivalência de quantidades ("seis meses = 180 dias") entrou depois de um falso alarme no teste com um único diálogo do piloto.

Modelos: temperatura 0, semente 42, `think: false`, contexto de 8.192 tokens. **Exceção:** o gpt-oss:20b não desliga o raciocínio (com `think: false` devolve texto quebrado no teste de 23/11) e roda com `think: "low"`, o nível mínimo.

**Modelos da rodada principal (4 famílias):** qwen3.5:9b, gemma4:12b, llama3.1:8b, gpt-oss:20b.

**Cache por prompt:** chamadas idênticas (mesmo modelo, sistema, prompt e opções) reaproveitam a primeira saída. O custo reportado é o da chamada original, como num sistema sem cache. `juizes.py` congelado: SHA-256/16 = 312021da3883b73f.

## Hipóteses

- **H1 (principal, reformulada na emenda 1).** No nível da resposta, o juiz por afirmação + regras tem **FAR-crítico menor** que o juiz holístico **com o mesmo falso alarme**, para o mesmo modelo.
  - Operacionalização: o corte da nota do holístico ("reprova se nota ≤ t") é escolhido no conjunto principal como o de falso alarme mais próximo (sem passar) do falso alarme do juiz por afirmação.
  - Teste: McNemar exato pareado sobre as respostas com ≥ 1 erro crítico, com o holístico nesse corte.
  - Complementos: a AUC das duas suspeições (holístico = 6 − nota; por afirmação = nº de afirmações contestadas), com IC bootstrap, e a decisão binária "aprovada" de cada juiz, reportada como veio.
- **H2.** O ganho da H1 não custa falso alarme: a diferença de falso alarme por resposta entre os dois juízes fica abaixo de 10 p.p.
  Teste: IC 95% bootstrap da diferença.
  *Com a emenda 1, o conjunto tem 120 respostas sem erro, contra 24 antes.*
- **H3 (ablações).** Retirar a recuperação (sem RAG) aumenta o FAR-crítico por afirmação. Retirar as regras não reduz a precisão da contestação. Dar as normas ao juiz holístico (holístico com normas) não alcança o juiz por afirmação.
- **H5 (localização, emenda 1).** Os problemas listados pelo juiz holístico apontam a afirmação errada em menos da metade dos casos, e uma fração relevante deles acusa afirmações corretas.
  - Medida automática: o texto do problema contém ≥ 40% das palavras da afirmação.
  - Validade: o autor confere a medida numa amostra de 50 problemas, reportada.
- **H4 (custo).** O juiz por afirmação custa mais tokens e mais latência que o holístico. Reportamos a razão e a fronteira de Pareto. Não é um teste de significância.

## Métricas

- **Primária:** FAR-crítico no nível da resposta, ou seja, a fração das respostas com erro crítico que o juiz aprovou.
- **Secundárias:**
  - falso alarme por resposta e por afirmação;
  - FAR-crítico por afirmação;
  - precisão, recall e F1 da contestação;
  - recall por categoria de erro e nos itens difíceis;
  - latência p50/p95 e tokens.

## Análise

- **IC 95%:** bootstrap com reamostragem por diálogo, 10.000 réplicas, semente 7.
- **Correção para comparações múltiplas:** Holm em cada família. Família 1 = H1 nos modelos testados. Família 2 = as ablações da H3.
- **α = 0,05.**
- **Modelos:** pelo menos 3 famílias abertas locais (Qwen, Gemma, Mistral ou IBM, gpt-oss se couber). A H1 é testada em cada modelo, e o resultado vale se for consistente na maioria.
- **"Insuficiente" conta como não contestado** (análise principal). Na análise de sensibilidade, "insuficiente" conta como contestado.
- **JSON inválido** conta como aprovado/não contestado, que é o pior caso para o juiz. A taxa de JSON inválido é reportada.
- **Segmentação:** pelo gabarito na análise principal. A extração por LLM (fim a fim) entra como análise secundária, com a taxa de alinhamento reportada.

## Emenda 1 (23/11/2026, após o piloto e antes da rodada principal)

**Motivo.** No piloto, o juiz holístico (qwen3.5:9b) reprovou as 30 respostas, com nota de 2 a 4. Isso deu FAR-crítico de 0% e falso alarme de 100%. Com a métrica binária, um juiz que reprova tudo vence sem localizar erro nenhum. Além disso, só 8% das respostas não tinham erro.

**Mudanças:**
1. O conjunto principal foi estratificado em limpo / um erro / misto, cerca de 1/3 cada.
2. A H1 passou a comparar os juízes com o mesmo falso alarme, com a AUC como complemento.
3. Entrou a H5 (localização).
4. Os resultados são reportados por estrato.

Nenhum dado do conjunto principal tinha sido visto por um juiz LLM quando a emenda foi feita.

## Resultado do piloto (qwen3.5:9b, 30 diálogos, só 3 sem erro; não entra na análise)

| Juiz | FAR-crít. resp. | Falso alarme resp. | FAR-crít. afirm. | Precisão | Recall | F1 | s/diálogo |
|---|---|---|---|---|---|---|---|
| Holístico | 0,00 | 1,00 | — | — | — | — | 12 |
| Holístico + normas | 0,04 | 1,00 | — | — | — | — | 14 |
| Por afirmação | 0,00 | 0,33 | 0,22 | 0,74 | 0,73 | 0,73 | 50 |
| Por afirmação + regras | 0,00 | 0,33 | 0,20 | 0,71 | 0,76 | 0,73 | 43 |
| Por afirmação sem RAG | 0,08 | 0,33 | 0,39 | 0,48 | 0,55 | 0,51 | 33 |

- Os holísticos reprovam tudo, o que motivou a emenda 1.
- Tirar a recuperação dobra o FAR-crítico por afirmação: o RAG é o componente que mais pesa.
- As regras dão um ganho pequeno de recall e de latência.

## Exclusões

Nenhum diálogo do conjunto principal é excluído depois de visto. Se houver falha de execução (timeout), o diálogo é refeito com a mesma configuração, e a falha é reportada.

## Após a rodada principal (23/11/2026, 19h14): desvios e análises exploratórias

Nada abaixo altera as hipóteses nem as análises pré-registradas, que estão reportadas como saíram (`experimento/analise.py`, `resultados/analise.md`).

- **Timeout que persistiu.** Depois de refeito com a mesma configuração, 1 diálogo do llama3.1 holístico seguiu em timeout e foi contado como aprovado com nota 5 (pior caso). O gpt-oss holístico devolveu 1 JSON vazio, tratado da mesma forma.
- **O pareamento da H1 não ficou pareado de fato.** A nota do holístico tem 5 níveis, e o corte admissível deixou o holístico com 20 a 26 p.p. **menos** falso alarme que o proposto. Isso favorece o proposto.
- **Exploratória 1 (varredura dos dois lados).** O proposto também ganha um corte ("reprova se ≥ k afirmações contestadas"), e a comparação é feita nos pontos de falso alarme mais próximos. Entra no artigo marcada como exploratória.
- **Exploratória 2 (contestações falsas das regras).** As 43 contestações falsas das regras vêm de um único fato-norma em que a recuperação erra o dispositivo.
- **Título.** Foi revisto depois dos resultados: *… Holistic Judges Can Rank but Cannot Point to the Error*. O título antigo ("Miss Critical Errors") não era sustentado pelos dados.
- **Conferência manual da H5 (23/11/2026).** O autor rotulou 50 problemas sem ver o rótulo automático (`experimento/concordancia_h5.py`).
  - Concordância de 76%, κ = 0,44.
  - A medida automática subconta: nunca marcou "erro" indevidamente (3/3), mas perdeu as paráfrases.
  - À mão: 12% dos problemas apontam o erro, 22% acusam afirmação correta e 66% não apontam nenhuma.
  - A H5 é confirmada nas duas partes.

## Emenda 2 (24/11/2026, antes de rodar os juízes novos)

**Motivo.** Revisão do orientador (Prof. Carlo): o holístico pode ir mal por causa da **saída em texto livre** ou do **critério amplo** do prompt ("correção e adequação"), e não por ser holístico. A emenda testa as duas explicações. Nenhum dos juízes abaixo tinha sido rodado no conjunto principal quando ela foi escrita; os prompts foram testados só em 3 diálogos para conferir o formato.

**Juízes novos (4 modelos × 300 diálogos; mesmas opções de decodificação):**
- **holistico_sentencas:** critério igual ao do holístico; a resposta vem em sentenças numeradas (S1…Sn = afirmações do gabarito), e a saída é {decisao, nota, sentencas_nao_conformes: [{id, dispositivo, motivo}]}.
- **holistico_sentencas_normas:** o mesmo, com o top-3 por afirmação da recuperação híbrida, igual ao do verificador (trechos de até 700 caracteres; prompts de até ~3.400 tokens no teste, abaixo de 8.192).
- **holistico_conformidade:** formato igual ao do holístico; critério restrito: "Aprove se nenhuma afirmação contradiz a norma. Estilo, completude e tom não contam. Liste problemas só se houver contradição normativa."

Hashes (SHA-256/16): P_SENTENCAS f251e43fd9cd00c1 · P_CONFORMIDADE 029599b361a2c328 · juizes.py 07a94f35e97e398c.

**Hipóteses e análise (fixadas aqui):**
- **H6 (formato).** Com saída por sentença, o holístico localiza pior que o verificador. Medida única de localização para todos os juízes, só nas respostas com erro:
  - precisão = sentenças apontadas que são erros reais;
  - recall = erros apontados.
  O resultado sai com IC bootstrap pareado por modelo. **Se o holístico por sentença com normas alcançar o verificador** (IC da diferença de F1 contendo 0, ou a favor do holístico), o artigo é reenquadrado: o problema era a saída em texto livre.
- **H7 (critério).** O prompt restrito à conformidade reduz o falso alarme do holístico. Teste: McNemar exato pareado nas 120 respostas sem erro, holístico contra holístico_conformidade, por modelo, com Holm na família 3 (4 modelos).
- Para todos os juízes também saem FAR-crítico, falso alarme e AUC, como na análise principal. JSON inválido conta como aprovado e sem sentença apontada (pior caso).

### Registro posterior à emenda 2 (24/11/2026, antes de analisar os juízes locais da emenda)
- **Claude Haiku 5.5 (exploratório).** Todos os juízes, menos o "sem recuperação", rodaram também no Claude Haiku 5.5 pela Batch API, com raciocínio desligado e amostragem padrão (a API não aceita temperatura): 1.639 pedidos únicos, US$ 0,39. 22 respostas (1,3%) atingiram o limite de 1.024 tokens e contam como JSON inválido (pior caso). O Haiku **não entra** nas famílias de testes (H1–H7, Holm); é relatado à parte como checagem de escala.
- **Erro ambíguo (item 1d).** O erro plantado "O limite do consignado CLT é 35% da sua remuneração" (F26) é ambíguo: há um sublimite de 35% para empréstimos no art. 1º, § 1º da Lei 10.820. Os 6 diálogos que o contêm não são reescritos. Toda métrica sai também **sem esses 6 diálogos** (sensibilidade). Detalhes em [[revisao-normativa-1d]].
- **Bloco 2 do orientador (análises adicionais, rotuladas como tal):**
  - bootstrap em dois níveis (diálogo × fato) nas métricas por afirmação;
  - FAR-crítico a falso alarme exatamente pareado, por limiar aleatorizado no envelope convexo da ROC;
  - localização única para todos os juízes (precisão, recall e F1 nas respostas com erro) e acurácia de citação.
  Script: `experimento/analise_emenda2.py`.

### Segundo anotador (24/11/2026, depois da emenda 2)
Validação independente do gabarito por uma anotadora com formação jurídica. Ela confirmou 58 dos 61 fatos (3 "parcialmente": F13, F24, F38) e 79 dos 84 erros (5 "ambíguos": F06, F13, F26, F58, F59). Nas rejeitadas, 40 de 42 frases contestadas pelos juízes estão corretas e 2 são ambíguas. A gravidade teve κ = 0,40 [0,17; 0,62]: a anotadora marcou como crítica 13 fatos que classificamos como não críticos (o contrário aconteceu em 4). A análise de sensibilidade da revisão 1d foi ampliada para excluir os 15 diálogos com os 5 erros ambíguos. Esta é uma decisão posterior aos dados e é reportada como exploratória.

### Resultado da emenda 2 e reenquadramento (24/11/2026, noite)
Com os 4 modelos completos, a H6 foi confirmada só no qwen3.5 e no llama3.1. No gemma4 (ΔF1 +0,10 [−0,04; 0,24]) e no gpt-oss (−0,12 [−0,27; 0,02]), o IC contém zero, que é a condição pré-registrada de reenquadramento. O artigo foi reenquadrado: o holístico falha como barreira pelo **critério** (H7 em 4 de 4), ao localizar pelo **formato** e ao citar pela falta de **recuperação**. Novo título: "LLM Judges as Compliance Gates in Brazilian Banking: Criterion, Output Format and Retrieval Matter More than Claim Decomposition".

## Emenda 3 (25/11/2026, antes de rodar os juízes novos no conjunto principal)

**Motivo.** Parecer simulado no perfil da Applied Intelligence (`Parecer Applied Intelligence — LLM Judges as Compliance Gates in Brazilian Banki.md`, 24/11/2026). Os pontos M1, M3, M4, M8 e M9 pedem juízes e ablações que ainda não rodaram. Nenhum dos juízes abaixo foi rodado no conjunto principal quando esta emenda foi escrita. O RAGAs e o MiniCheck foram testados **só no piloto** (2 diálogos, seed 1), para conferir o formato.

**Juízes e variantes novos (300 diálogos; temperatura 0, semente 42, contexto 8.192, mesmas opções de raciocínio):**
- **holistico_conformidade_sentencas_normas** (M3; 4 modelos): critério do holístico só conformidade, formato por sentença e o mesmo top-3 por afirmação do verificador. É a célula do desenho que faltava: critério estreito + saída por sentença + normas, sem decomposição.
- **holistico_normas_k3** (M4; 4 modelos): o holístico + normas recebendo o **top-3** por afirmação (deduplicado, até 700 caracteres), igual ao verificador, em vez do top-1.
- **afirmacao_regras com recuperação oráculo** (M9; 4 modelos): o verificador recebe só o artigo do gabarito de cada afirmação.
- **afirmacao_regras fim a fim** (M8; gemma4, llama3.1 e gpt-oss): segmentação pelo LLM, como já foi feito no qwen3.5.
- **RAGAs faithfulness** (M1; 4 modelos; ragas 0.4.4 com os prompts originais, `ragas_juiz.py`): contexto = o mesmo top-3 por afirmação do holístico por sentença + normas. Aprova se todas as afirmações extraídas forem sustentadas; escore de suspeita = 1 − faithfulness. Localização: afirmação do gabarito apontada quando a afirmação extraída alinhada (Jaccard ≥ 0,5) não é sustentada.
- **MiniCheck** (M1; Bespoke-MiniCheck-7B, Q4_K_M, no Ollama): cada afirmação do gabarito contra o mesmo top-3 do verificador; "No" = contestada; escore de suspeita = número de "No".

Hashes (SHA-256/16): P_CONF_SENTENCAS a4b0eb085fae704e · P_MINICHECK c972842e14683075 · juizes.py 7449c92a5be97a77 · ragas_juiz.py b85ab2fc07eecba0.

**Hipóteses e análise (fixadas aqui; família 4 = H8, família 5 = H9, família 6 = H10, Holm dentro de cada uma):**
- **H8 (célula que faltava).** O holístico só conformidade + por sentença + normas localiza pior que o verificador (ΔF1 com IC bootstrap em dois níveis). **Regra de decisão:** se o IC contiver 0 ou favorecer o holístico em pelo menos 3 de 4 modelos, a recomendação prática passa a ser esse juiz (mais barato), e o título e a Discussão mudam. Também saem FAR-crítico no falso alarme exatamente pareado e o falso alarme da decisão binária.
- **H3b (normas com top-3).** Com o top-3, o holístico + normas continua sem igualar o verificador: FAR-crítico no falso alarme exatamente pareado e ΔF1 de localização. Substitui a parte "normas" da H3 se o resultado mudar; o top-1 continua reportado.
- **H9 (recuperação oráculo).** Com o artigo do gabarito, o FAR-crítico por afirmação do verificador cai em relação à recuperação híbrida (diferença pareada, bootstrap em dois níveis, por modelo). Também sai a acurácia do veredito condicionada a acerto ou erro da recuperação híbrida (artigo do gabarito no top-3 ou não).
- **H10 (baselines externos).** O verificador localiza melhor (F1) que o RAGAs faithfulness e que o MiniCheck com o mesmo contexto. Também saem FAR-crítico no falso alarme exatamente pareado, falso alarme da decisão binária e AUC.
- **Fim a fim (M8):** descritivo, como na Seç. 5.6 (alinhamento, FAR-crítico, falso alarme, AUC).
- Saída inválida conta como aprovada e sem afirmação apontada (pior caso), como antes; o tratamento *fail-closed* sai em paralelo (ver abaixo).

**Análises adicionais sem rodada nova de juiz.** Foram decididas depois de ver os resultados das emendas 1 e 2 e por isso saem rotuladas como exploratórias:
1. motivos de rejeição nas respostas sem erro e número de respostas limpas com afirmações fora do foco da pergunta (M2);
2. bootstrap em dois níveis (diálogo × fato) também no nível de resposta, permutação por cluster para os testes pareados e número de erros críticos distintos (M5);
3. FAR-crítico em falso alarme fixo (0,05; 0,10; 0,20), VPP e carga de revisão em prevalências de 1%, 2% e 5%, e barreira de três saídas (aprovar / escalar / bloquear) com "insuficiente" = escalar (M6);
4. FAR-crítico com a gravidade da anotadora e com a união das duas (M7);
5. tratamento *fail-closed* das saídas inválidas (menor);
6. sensibilidade do limiar de 40% (30% e 50%) da localização em texto livre e do Jaccard 0,5 (0,4 e 0,6) no alinhamento (menor);
7. precisão da localização sobre as 300 respostas, contando contestações em respostas limpas (menor).

**Resultado da H8 (25/11/2026, 12h40; análise em `experimento/resultados/analise_emenda3.md`).** ΔF1 (holístico só conformidade + por sentença + normas − verificador), p bootstrap com Holm na família de 4 modelos: qwen3.5 −0,13 [−0,26; −0,01], p Holm 0,10; gemma4 +0,15 [−0,00; 0,28], p Holm 0,11; llama3.1 −0,51 [−0,67; −0,35], p Holm < 0,001; gpt-oss −0,02 [−0,19; 0,13], p Holm 0,76. Sem diferença após Holm em 3 de 4 modelos → **regra de decisão disparada** (sem Holm seriam 2 de 4; o texto declara isso). O juiz usa 36–40% dos tokens do verificador. Novo título: "Configuring LLM Judges as Compliance Gates in Brazilian Banking: Criterion and Output Format Close the Gap to Claim-Level Verification". H3b (top-3): o verificador continua localizando melhor em 3 de 4 (gemma empata).

**Desvio (27/11/2026, 00:45): limite de tempo no RAGAs.** No llama3.1, um diálogo entrou em geração descontrolada no Ollama: o contexto desliza e a geração não termina, e ficou mais de 40 min sem resposta, contra no máximo 100 s nos outros diálogos desse modelo. O `ragas_juiz.py` passou a ter um limite de 1.800 s por diálogo; o estouro vira exceção e conta como pior caso, pela regra já fixada (aprovada, nada apontado). O limite fica acima do máximo observado antes (878 s, no qwen3.5), então nada do que já tinha rodado muda. O processo do llama foi interrompido e retomado do ponto onde parou depois do gemma4 e do gpt-oss (o script pula os diálogos já feitos). Hash novo do `ragas_juiz.py`: 7f55ed1d001ec57f (era b85ab2fc07eecba0).

**Análise exploratória pós-parecer (28/11/2026, NÃO pré-registrada): TOST da H8** (`experimento/tost_h8.py`). Equivalência se o IC 90% bootstrap da diferença ficar dentro de [−δ, +δ]. ΔF1 (configurado − verificador): qwen3.5 [−0,24; −0,03], gemma4 [+0,02; +0,26], llama3.1 [−0,65; −0,38], gpt-oss [−0,16; +0,11] → equivalência em ±0,10 em nenhum modelo. ΔFAR-crítico no falso alarme pareado: [−0,02; +0,12], [−0,03; +0,01], [+0,24; +0,42], [−0,05; +0,04] → equivalência em ±0,05 no gemma4 e no gpt-oss. A regra de decisão continua disparada como pré-registrada, mas o texto passa a dizer "não claramente pior, a menor custo" em vez de "empata". Título ajustado: "Configuring LLM Judges as Compliance Gates in Brazilian Banking: Criterion, Output Format and Norms Narrow the Gap to Claim-Level Verification".
