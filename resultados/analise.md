# Análise pré-registrada: rodada principal

300 diálogos (108 limpos, 96 com um erro, 96 mistos); 135 respostas com erro crítico, 120 sem erro;
2.113 afirmações. IC 95% por bootstrap por diálogo (10.000 réplicas, semente 7).

## Tabela 1. Nível da resposta (decisão binária como veio)

| Modelo | Juiz | FAR-crítico | Falso alarme | AUC |
|---|---|---|---|---|
| qwen3.5-9b | holistico | 0.02 [0.00; 0.05] | 0.93 [0.88; 0.97] | 0.76 [0.70; 0.81] |
| qwen3.5-9b | holistico_normas | 0.02 [0.00; 0.05] | 0.88 [0.81; 0.93] | 0.80 [0.75; 0.85] |
| qwen3.5-9b | afirmacao | 0.12 [0.07; 0.18] | 0.47 [0.38; 0.56] | 0.79 [0.74; 0.84] |
| qwen3.5-9b | afirmacao_regras | 0.09 [0.04; 0.14] | 0.66 [0.57; 0.74] | 0.78 [0.72; 0.83] |
| qwen3.5-9b | afirmacao_sem_rag | 0.07 [0.03; 0.11] | 0.62 [0.54; 0.71] | 0.66 [0.59; 0.72] |
| gemma4-12b | holistico | 0.00 [0.00; 0.00] | 0.97 [0.94; 1.00] | 0.82 [0.77; 0.87] |
| gemma4-12b | holistico_normas | 0.00 [0.00; 0.00] | 0.88 [0.82; 0.94] | 0.88 [0.84; 0.92] |
| gemma4-12b | afirmacao | 0.02 [0.00; 0.05] | 0.87 [0.80; 0.92] | 0.71 [0.65; 0.77] |
| gemma4-12b | afirmacao_regras | 0.02 [0.00; 0.05] | 0.89 [0.83; 0.94] | 0.69 [0.63; 0.75] |
| gemma4-12b | afirmacao_sem_rag | 0.80 [0.73; 0.87] | 0.00 [0.00; 0.00] | 0.60 [0.57; 0.63] |
| llama3.1-8b | holistico | 0.02 [0.00; 0.05] | 0.93 [0.88; 0.97] | 0.64 [0.59; 0.69] |
| llama3.1-8b | holistico_normas | 0.04 [0.01; 0.08] | 0.92 [0.87; 0.96] | 0.63 [0.59; 0.67] |
| llama3.1-8b | afirmacao | 0.21 [0.15; 0.28] | 0.19 [0.12; 0.26] | 0.79 [0.73; 0.84] |
| llama3.1-8b | afirmacao_regras | 0.18 [0.12; 0.24] | 0.39 [0.30; 0.48] | 0.75 [0.69; 0.80] |
| llama3.1-8b | afirmacao_sem_rag | 0.81 [0.75; 0.88] | 0.17 [0.10; 0.24] | 0.51 [0.46; 0.56] |
| gpt-oss-20b | holistico | 0.01 [0.00; 0.02] | 0.97 [0.94; 1.00] | 0.60 [0.55; 0.66] |
| gpt-oss-20b | holistico_normas | 0.02 [0.00; 0.05] | 0.91 [0.85; 0.96] | 0.68 [0.62; 0.74] |
| gpt-oss-20b | afirmacao | 0.11 [0.06; 0.17] | 0.68 [0.60; 0.77] | 0.72 [0.65; 0.78] |
| gpt-oss-20b | afirmacao_regras | 0.08 [0.04; 0.13] | 0.79 [0.72; 0.86] | 0.70 [0.64; 0.76] |
| gpt-oss-20b | afirmacao_sem_rag | 0.31 [0.23; 0.39] | 0.62 [0.53; 0.71] | 0.56 [0.49; 0.63] |

## Tabela 2. Nível da afirmação (juízes por afirmação)

| Modelo | Juiz | FAR-crítico | Falso alarme | Precisão | Recall | F1 | Recall difíceis |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | afirmacao | 0.26 [0.19; 0.32] | 0.10 [0.09; 0.12] | 0.54 [0.48; 0.59] | 0.76 [0.71; 0.81] | 0.63 | 0.64 |
| qwen3.5-9b | afirmacao_regras | 0.24 [0.18; 0.30] | 0.13 [0.11; 0.14] | 0.49 [0.44; 0.54] | 0.78 [0.73; 0.82] | 0.60 | 0.64 |
| qwen3.5-9b | afirmacao_sem_rag | 0.35 [0.28; 0.42] | 0.23 [0.20; 0.25] | 0.30 [0.26; 0.34] | 0.63 [0.57; 0.69] | 0.41 | 0.82 |
| gemma4-12b | afirmacao | 0.25 [0.18; 0.32] | 0.23 [0.21; 0.25] | 0.33 [0.29; 0.36] | 0.71 [0.65; 0.76] | 0.45 | 1.00 |
| gemma4-12b | afirmacao_regras | 0.24 [0.17; 0.30] | 0.24 [0.22; 0.26] | 0.32 [0.28; 0.36] | 0.73 [0.68; 0.78] | 0.45 | 1.00 |
| gemma4-12b | afirmacao_sem_rag | 0.87 [0.82; 0.92] | 0.00 [0.00; 0.00] | 1.00 [1.00; 1.00] | 0.12 [0.09; 0.16] | 0.22 | 0.00 |
| llama3.1-8b | afirmacao | 0.29 [0.23; 0.35] | 0.06 [0.04; 0.07] | 0.64 [0.58; 0.71] | 0.69 [0.63; 0.73] | 0.66 | 0.45 |
| llama3.1-8b | afirmacao_regras | 0.28 [0.22; 0.34] | 0.08 [0.07; 0.10] | 0.57 [0.51; 0.63] | 0.70 [0.64; 0.75] | 0.63 | 0.45 |
| llama3.1-8b | afirmacao_sem_rag | 1.00 [1.00; 1.00] | 0.03 [0.02; 0.04] | 0.10 [0.03; 0.18] | 0.02 [0.01; 0.04] | 0.03 | 0.00 |
| gpt-oss-20b | afirmacao | 0.36 [0.28; 0.43] | 0.14 [0.13; 0.16] | 0.42 [0.37; 0.46] | 0.64 [0.59; 0.70] | 0.50 | 0.45 |
| gpt-oss-20b | afirmacao_regras | 0.34 [0.27; 0.41] | 0.17 [0.15; 0.18] | 0.39 [0.34; 0.43] | 0.67 [0.61; 0.72] | 0.49 | 0.45 |
| gpt-oss-20b | afirmacao_sem_rag | 0.75 [0.68; 0.81] | 0.13 [0.11; 0.14] | 0.24 [0.19; 0.29] | 0.26 [0.21; 0.31] | 0.25 | 0.64 |

### Recall por categoria de erro (proposto)

| Modelo | conceito | dado | direito | prazo | promessa | valor |
|---|---|---|---|---|---|---|
| qwen3.5-9b | 0.77 | 0.67 | 0.84 | 0.85 | 0.58 | 0.76 |
| gemma4-12b | 1.00 | 0.67 | 0.71 | 0.80 | 0.51 | 0.85 |
| llama3.1-8b | 0.77 | 0.67 | 0.59 | 0.73 | 0.89 | 0.73 |
| gpt-oss-20b | 1.00 | 0.42 | 0.66 | 0.46 | 0.51 | 0.92 |

## H1. Proposto x holístico com o mesmo falso alarme

Corte do holístico: reprova se nota ≤ t, com o falso alarme mais próximo do proposto sem passar.

| Modelo | t | FA proposto | FA holístico | FAR-crít. proposto | FAR-crít. holístico | Δ FAR (prop − hol) | só prop. pega | só hol. pega | p | p Holm |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen3.5-9b | 3 | 0.66 | 0.46 | 0.09 [0.04; 0.14] | 0.15 [0.09; 0.21] | -0.06 [-0.13; 0.01] | 15 | 7 | 0.1338 | 0.2676 |
| gemma4-12b | 3 | 0.89 | 0.63 | 0.02 [0.00; 0.05] | 0.06 [0.02; 0.10] | -0.04 [-0.09; 0.01] | 8 | 3 | 0.2266 | 0.2676 |
| llama3.1-8b | 3 | 0.39 | 0.17 | 0.18 [0.12; 0.24] | 0.57 [0.49; 0.65] | -0.39 [-0.49; -0.30] | 58 | 5 | 0.0000 | 0.0000 |
| gpt-oss-20b | 2 | 0.79 | 0.57 | 0.08 [0.04; 0.13] | 0.23 [0.16; 0.30] | -0.15 [-0.22; -0.07] | 25 | 5 | 0.0003 | 0.0010 |

### AUC: proposto − holístico (IC pareado)

| Modelo | Δ AUC |
|---|---|
| qwen3.5-9b | 0.02 [-0.03; 0.08] |
| gemma4-12b | -0.13 [-0.20; -0.06] |
| llama3.1-8b | 0.11 [0.04; 0.18] |
| gpt-oss-20b | 0.10 [0.03; 0.17] |

## H2. Diferença de falso alarme (proposto − holístico), limite 10 p.p.

| Modelo | Decisão binária como veio | No corte pareado da H1 |
|---|---|---|
| qwen3.5-9b | -0.27 [-0.36; -0.18] | 0.20 [0.10; 0.30] |
| gemma4-12b | -0.08 [-0.15; -0.02] | 0.26 [0.15; 0.37] |
| llama3.1-8b | -0.54 [-0.64; -0.45] | 0.23 [0.11; 0.34] |
| gpt-oss-20b | -0.18 [-0.26; -0.11] | 0.22 [0.12; 0.33] |

## H3. Ablações (família 2, Holm sobre os 12 testes)

| Modelo | Comparação | Δ [IC 95%] | discordantes | p | p Holm |
|---|---|---|---|---|---|
| qwen3.5-9b | sem RAG: FAR-crít. por afirmação (sem RAG − proposto) | 0.11 [0.03; 0.19] | 42/21 | 0.0111 | 0.0111 |
| qwen3.5-9b | sem regras: precisão (sem regras − proposto) | 0.05 [0.03; 0.06] | FP só s/ regras 0 / só proposto 43 | 0.0000 | 0.0000 |
| qwen3.5-9b | holístico+normas no FA pareado: FAR-crít. (proposto − hol.+normas) | -0.18 [-0.25; -0.11] | 27/3 (t=3, FA 0.17) | 0.0000 | 0.0000 |
| gemma4-12b | sem RAG: FAR-crít. por afirmação (sem RAG − proposto) | 0.64 [0.56; 0.71] | 119/0 | 0.0000 | 0.0000 |
| gemma4-12b | sem regras: precisão (sem regras − proposto) | 0.00 [-0.01; 0.02] | FP só s/ regras 19 / só proposto 43 | 0.0032 | 0.0063 |
| gemma4-12b | holístico+normas no FA pareado: FAR-crít. (proposto − hol.+normas) | -0.12 [-0.18; -0.07] | 16/0 (t=3, FA 0.20) | 0.0000 | 0.0001 |
| llama3.1-8b | sem RAG: FAR-crít. por afirmação (sem RAG − proposto) | 0.72 [0.66; 0.78] | 135/0 | 0.0000 | 0.0000 |
| llama3.1-8b | sem regras: precisão (sem regras − proposto) | 0.07 [0.05; 0.10] | FP só s/ regras 0 / só proposto 43 | 0.0000 | 0.0000 |
| llama3.1-8b | holístico+normas no FA pareado: FAR-crít. (proposto − hol.+normas) | -0.53 [-0.62; -0.44] | 74/2 (t=3, FA 0.03) | 0.0000 | 0.0000 |
| gpt-oss-20b | sem RAG: FAR-crít. por afirmação (sem RAG − proposto) | 0.41 [0.31; 0.50] | 87/11 | 0.0000 | 0.0000 |
| gpt-oss-20b | sem regras: precisão (sem regras − proposto) | 0.03 [0.01; 0.04] | FP só s/ regras 0 / só proposto 43 | 0.0000 | 0.0000 |
| gpt-oss-20b | holístico+normas no FA pareado: FAR-crít. (proposto − hol.+normas) | -0.21 [-0.30; -0.13] | 33/4 (t=2, FA 0.38) | 0.0000 | 0.0000 |

## Por estrato (FAR-crítico / falso alarme por resposta, decisão como veio)

| Modelo | Juiz | limpo: FA | um_erro: FAR | um_erro: FA | misto: FAR |
|---|---|---|---|---|---|
| qwen3.5-9b | holistico | 0.92 | 0.03 | — | 0.01 |
| qwen3.5-9b | holistico_normas | 0.88 | 0.03 | — | 0.01 |
| qwen3.5-9b | afirmacao | 0.47 | 0.21 | — | 0.04 |
| qwen3.5-9b | afirmacao_regras | 0.67 | 0.14 | — | 0.04 |
| qwen3.5-9b | afirmacao_sem_rag | 0.64 | 0.06 | — | 0.07 |
| gemma4-12b | holistico | 0.97 | 0.00 | — | 0.00 |
| gemma4-12b | holistico_normas | 0.88 | 0.00 | — | 0.00 |
| gemma4-12b | afirmacao | 0.87 | 0.03 | — | 0.01 |
| gemma4-12b | afirmacao_regras | 0.90 | 0.03 | — | 0.01 |
| gemma4-12b | afirmacao_sem_rag | 0.00 | 0.89 | — | 0.72 |
| llama3.1-8b | holistico | 0.94 | 0.03 | — | 0.01 |
| llama3.1-8b | holistico_normas | 0.93 | 0.08 | — | 0.01 |
| llama3.1-8b | afirmacao | 0.19 | 0.30 | — | 0.14 |
| llama3.1-8b | afirmacao_regras | 0.40 | 0.25 | — | 0.11 |
| llama3.1-8b | afirmacao_sem_rag | 0.17 | 0.83 | — | 0.81 |
| gpt-oss-20b | holistico | 0.97 | 0.00 | — | 0.01 |
| gpt-oss-20b | holistico_normas | 0.91 | 0.05 | — | 0.00 |
| gpt-oss-20b | afirmacao | 0.69 | 0.21 | — | 0.03 |
| gpt-oss-20b | afirmacao_regras | 0.80 | 0.14 | — | 0.03 |
| gpt-oss-20b | afirmacao_sem_rag | 0.63 | 0.35 | — | 0.28 |

## Sensibilidade: "insuficiente" conta como contestado

| Modelo | Juiz | % insuficiente | FAR-crít. resp. | FA resp. | FAR-crít. afirm. | FA afirm. |
|---|---|---|---|---|---|---|
| qwen3.5-9b | afirmacao | 9.0% | 0.07 | 0.81 | 0.16 | 0.19 |
| qwen3.5-9b | afirmacao_regras | 6.9% | 0.07 | 0.81 | 0.14 | 0.19 |
| qwen3.5-9b | afirmacao_sem_rag | 54.1% | 0.00 | 1.00 | 0.09 | 0.80 |
| gemma4-12b | afirmacao | 13.0% | 0.00 | 0.94 | 0.02 | 0.34 |
| gemma4-12b | afirmacao_regras | 10.4% | 0.00 | 0.93 | 0.04 | 0.33 |
| gemma4-12b | afirmacao_sem_rag | 98.3% | 0.00 | 1.00 | 0.00 | 1.00 |
| llama3.1-8b | afirmacao | 6.6% | 0.13 | 0.61 | 0.26 | 0.13 |
| llama3.1-8b | afirmacao_regras | 6.5% | 0.11 | 0.63 | 0.25 | 0.15 |
| llama3.1-8b | afirmacao_sem_rag | 10.6% | 0.45 | 0.58 | 0.96 | 0.13 |
| gpt-oss-20b | afirmacao | 16.1% | 0.01 | 0.91 | 0.04 | 0.28 |
| gpt-oss-20b | afirmacao_regras | 12.6% | 0.01 | 0.89 | 0.06 | 0.27 |
| gpt-oss-20b | afirmacao_sem_rag | 74.4% | 0.00 | 1.00 | 0.09 | 0.88 |

## H5. Localização pelos juízes holísticos

| Modelo | Juiz | erros localizados | problemas que apontam erro | problemas que acusam afirmação correta | problemas/resposta |
|---|---|---|---|---|---|
| qwen3.5-9b | holistico | 0.59 | 0.15 | 0.36 | 3.9 |
| qwen3.5-9b | holistico_normas | 0.76 | 0.23 | 0.38 | 3.4 |
| gemma4-12b | holistico | 0.24 | 0.04 | 0.03 | 5.3 |
| gemma4-12b | holistico_normas | 0.45 | 0.10 | 0.04 | 4.4 |
| llama3.1-8b | holistico | 0.28 | 0.06 | 0.22 | 4.7 |
| llama3.1-8b | holistico_normas | 0.18 | 0.04 | 0.19 | 4.6 |
| gpt-oss-20b | holistico | 0.29 | 0.06 | 0.11 | 5.2 |
| gpt-oss-20b | holistico_normas | 0.34 | 0.07 | 0.10 | 4.8 |

## H4. Custo por diálogo (chamada original; cache não reduz o custo reportado)

| Modelo | Juiz | tokens | chamadas LLM | latência p50 (s) | p95 (s) | regras decidiram |
|---|---|---|---|---|---|---|
| qwen3.5-9b | holistico | 511 | 1.0 | 12.3 | 19.3 | — |
| qwen3.5-9b | holistico_normas | 1856 | 1.0 | 13.9 | 21.3 | — |
| qwen3.5-9b | afirmacao | 9677 | 7.0 | 50.0 | 62.6 | — |
| qwen3.5-9b | afirmacao_regras | 8996 | 6.5 | 46.5 | 60.0 | 7.2% |
| qwen3.5-9b | afirmacao_sem_rag | 2092 | 7.0 | 31.4 | 38.2 | — |
| gemma4-12b | holistico | 468 | 1.0 | 11.9 | 15.6 | — |
| gemma4-12b | holistico_normas | 1904 | 1.0 | 16.5 | 24.8 | — |
| gemma4-12b | afirmacao | 10119 | 7.0 | 118.3 | 138.3 | — |
| gemma4-12b | afirmacao_regras | 9417 | 6.5 | 110.6 | 136.7 | 7.2% |
| gemma4-12b | afirmacao_sem_rag | 1998 | 7.0 | 24.6 | 28.7 | — |
| llama3.1-8b | holistico | 516 | 1.0 | 7.6 | 12.3 | — |
| llama3.1-8b | holistico_normas | 1985 | 1.0 | 10.6 | 19.4 | — |
| llama3.1-8b | afirmacao | 10455 | 7.0 | 65.9 | 77.4 | — |
| llama3.1-8b | afirmacao_regras | 9726 | 6.5 | 61.6 | 75.5 | 7.2% |
| llama3.1-8b | afirmacao_sem_rag | 2185 | 7.0 | 20.0 | 24.2 | — |
| gpt-oss-20b | holistico | 618 | 1.0 | 8.5 | 25.1 | — |
| gpt-oss-20b | holistico_normas | 1841 | 1.0 | 13.1 | 30.8 | — |
| gpt-oss-20b | afirmacao | 9823 | 7.0 | 124.4 | 146.8 | — |
| gpt-oss-20b | afirmacao_regras | 9136 | 6.5 | 115.1 | 144.2 | 7.2% |
| gpt-oss-20b | afirmacao_sem_rag | 2519 | 7.0 | 32.3 | 39.5 | — |

## JSON inválido e timeout

| Modelo | Juiz | chamadas com JSON inválido | timeouts |
|---|---|---|---|
| qwen3.5-9b | holistico | 0 / 300 | 0 |
| qwen3.5-9b | holistico_normas | 0 / 300 | 0 |
| qwen3.5-9b | afirmacao | 0 / 2113 | 0 |
| qwen3.5-9b | afirmacao_regras | 0 / 2113 | 0 |
| qwen3.5-9b | afirmacao_sem_rag | 0 / 2113 | 0 |
| gemma4-12b | holistico | 0 / 300 | 0 |
| gemma4-12b | holistico_normas | 0 / 300 | 0 |
| gemma4-12b | afirmacao | 0 / 2113 | 0 |
| gemma4-12b | afirmacao_regras | 0 / 2113 | 0 |
| gemma4-12b | afirmacao_sem_rag | 0 / 2113 | 0 |
| llama3.1-8b | holistico | 1 / 300 | 1 |
| llama3.1-8b | holistico_normas | 0 / 300 | 0 |
| llama3.1-8b | afirmacao | 0 / 2113 | 0 |
| llama3.1-8b | afirmacao_regras | 0 / 2113 | 0 |
| llama3.1-8b | afirmacao_sem_rag | 0 / 2113 | 0 |
| gpt-oss-20b | holistico | 1 / 300 | 0 |
| gpt-oss-20b | holistico_normas | 0 / 300 | 0 |
| gpt-oss-20b | afirmacao | 0 / 2113 | 0 |
| gpt-oss-20b | afirmacao_regras | 0 / 2113 | 0 |
| gpt-oss-20b | afirmacao_sem_rag | 0 / 2113 | 0 |

## Fim a fim (qwen3.5:9b, afirmações extraídas pelo LLM)

- Taxa de alinhamento (afirmação do gabarito com extraída de Jaccard ≥ 0,5): 83.5%
- Afirmações extraídas por resposta: 9.0 (gabarito: 7.0)

| Segmentação | FAR-crítico resp. | Falso alarme resp. | AUC | FAR-crít. afirm. |
|---|---|---|---|---|
| gabarito (oráculo) | 0.09 [0.04; 0.14] | 0.66 [0.57; 0.74] | 0.78 [0.72; 0.83] | 0.24 [0.18; 0.30] |
| LLM (fim a fim) | 0.06 [0.02; 0.10] | 0.70 [0.62; 0.78] | 0.74 [0.68; 0.80] | 0.33 [0.25; 0.40] |
