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
