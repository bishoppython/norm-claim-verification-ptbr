# Análise da emenda 2 e do bloco 2 (gerado por analise_emenda2.py)

Juízes/modelos com arquivo completo: 39. IC 95% por bootstrap (10.000 réplicas, semente 7): dois níveis (diálogo × fato) nas métricas por afirmação; por diálogo nas métricas por resposta.

## 1b. Localização (respostas com erro)

| Modelo | Juiz | precisão | recall | F1 | citação estrita | citação branda | erros apontados com dispositivo |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | holístico | 0,40 [0,31; 0,51] | 0,59 [0,48; 0,70] | 0,48 [0,38; 0,57] | — | — | 0/170 |
| qwen3.5-9b | holístico + normas | 0,46 [0,37; 0,55] | 0,76 [0,65; 0,85] | 0,57 [0,49; 0,66] | — | — | 0/218 |
| qwen3.5-9b | holístico (só conformidade) | 0,38 [0,31; 0,46] | 0,76 [0,64; 0,85] | 0,51 [0,43; 0,59] | — | — | 0/216 |
| qwen3.5-9b | holístico por sentença | 0,32 [0,26; 0,39] | 0,88 [0,77; 0,95] | 0,47 [0,40; 0,54] | 0,00 | 0,10 | 251/251 |
| qwen3.5-9b | holístico por sentença + normas | 0,36 [0,30; 0,44] | 0,90 [0,81; 0,96] | 0,52 [0,44; 0,59] | 0,37 | 0,46 | 257/257 |
| qwen3.5-9b | por afirmação, sem regras | 0,67 [0,49; 0,89] | 0,76 [0,62; 0,88] | 0,71 [0,58; 0,84] | 0,50 | 0,58 | 216/217 |
| qwen3.5-9b | por afirmação + regras (proposto) | 0,64 [0,48; 0,85] | 0,78 [0,64; 0,89] | 0,70 [0,57; 0,83] | 0,49 | 0,58 | 191/222 |
| qwen3.5-9b | por afirmação, sem recuperação | 0,45 [0,31; 0,62] | 0,63 [0,47; 0,77] | 0,52 [0,39; 0,65] | 0,03 | 0,19 | 154/179 |
| gemma4-12b | holístico | 0,67 [0,46; 0,87] | 0,24 [0,14; 0,36] | 0,35 [0,22; 0,49] | — | — | 0/69 |
| gemma4-12b | holístico + normas | 0,82 [0,68; 0,93] | 0,45 [0,31; 0,59] | 0,58 [0,44; 0,70] | — | — | 0/129 |
| gemma4-12b | holístico (só conformidade) | 0,52 [0,39; 0,65] | 0,52 [0,38; 0,65] | 0,52 [0,40; 0,63] | — | — | 0/148 |
| gemma4-12b | holístico por sentença | 0,40 [0,32; 0,49] | 0,90 [0,81; 0,96] | 0,55 [0,46; 0,64] | 0,00 | 0,05 | 256/256 |
| gemma4-12b | holístico por sentença + normas | 0,55 [0,43; 0,67] | 0,89 [0,80; 0,96] | 0,68 [0,57; 0,77] | 0,58 | 0,58 | 245/254 |
| gemma4-12b | por afirmação, sem regras | 0,47 [0,33; 0,65] | 0,71 [0,55; 0,85] | 0,57 [0,43; 0,71] | 0,70 | 0,72 | 202/202 |
| gemma4-12b | por afirmação + regras (proposto) | 0,47 [0,35; 0,64] | 0,73 [0,58; 0,86] | 0,57 [0,45; 0,71] | 0,68 | 0,71 | 179/209 |
| gemma4-12b | por afirmação, sem recuperação | 1,00 [1,00; 1,00] | 0,12 [0,03; 0,24] | 0,22 [0,06; 0,39] | — | — | 0/35 |
| llama3.1-8b | holístico | 0,31 [0,22; 0,43] | 0,28 [0,19; 0,38] | 0,30 [0,21; 0,39] | — | — | 0/80 |
| llama3.1-8b | holístico + normas | 0,24 [0,15; 0,36] | 0,18 [0,11; 0,27] | 0,21 [0,13; 0,29] | — | — | 0/52 |
| llama3.1-8b | holístico (só conformidade) | 0,31 [0,23; 0,39] | 0,43 [0,33; 0,54] | 0,36 [0,28; 0,44] | — | — | 0/124 |
| llama3.1-8b | holístico por sentença | 0,28 [0,23; 0,33] | 0,93 [0,87; 0,97] | 0,43 [0,36; 0,49] | 0,00 | 0,04 | 223/265 |
| llama3.1-8b | holístico por sentença + normas | 0,28 [0,23; 0,34] | 0,87 [0,80; 0,94] | 0,42 [0,36; 0,49] | 0,37 | 0,38 | 219/250 |
| llama3.1-8b | por afirmação, sem regras | 0,75 [0,58; 0,92] | 0,69 [0,54; 0,82] | 0,72 [0,59; 0,83] | 0,36 | 0,44 | 193/196 |
| llama3.1-8b | por afirmação + regras (proposto) | 0,71 [0,55; 0,89] | 0,70 [0,55; 0,83] | 0,70 [0,58; 0,81] | 0,34 | 0,44 | 167/200 |
| llama3.1-8b | por afirmação, sem recuperação | 0,14 [0,00; 1,00] | 0,02 [0,00; 0,08] | 0,04 [0,01; 0,16] | — | — | 0/6 |
| gpt-oss-20b | holístico | 0,46 [0,32; 0,61] | 0,29 [0,18; 0,40] | 0,36 [0,24; 0,47] | — | — | 0/83 |
| gpt-oss-20b | holístico + normas | 0,52 [0,37; 0,68] | 0,34 [0,22; 0,46] | 0,41 [0,28; 0,53] | — | — | 0/96 |
| gpt-oss-20b | holístico (só conformidade) | 0,58 [0,42; 0,75] | 0,29 [0,18; 0,42] | 0,39 [0,26; 0,51] | — | — | 0/84 |
| gpt-oss-20b | holístico por sentença | 0,31 [0,25; 0,37] | 0,84 [0,74; 0,92] | 0,45 [0,39; 0,51] | 0,00 | 0,15 | 239/240 |
| gpt-oss-20b | holístico por sentença + normas | 0,34 [0,28; 0,41] | 0,83 [0,72; 0,91] | 0,48 [0,41; 0,56] | 0,21 | 0,48 | 237/237 |
| gpt-oss-20b | por afirmação, sem regras | 0,57 [0,39; 0,81] | 0,64 [0,48; 0,79] | 0,61 [0,45; 0,76] | 0,44 | 0,73 | 184/184 |
| gpt-oss-20b | por afirmação + regras (proposto) | 0,55 [0,39; 0,77] | 0,67 [0,51; 0,81] | 0,60 [0,46; 0,75] | 0,43 | 0,72 | 161/191 |
| gpt-oss-20b | por afirmação, sem recuperação | 0,36 [0,20; 0,61] | 0,26 [0,13; 0,40] | 0,30 [0,16; 0,44] | 0,00 | 0,34 | 53/73 |
| claude-haiku-5-5 | holístico | 0,32 [0,26; 0,38] | 0,86 [0,77; 0,93] | 0,47 [0,39; 0,54] | — | — | 0/245 |
| claude-haiku-5-5 | holístico + normas | 0,34 [0,28; 0,40] | 0,92 [0,85; 0,97] | 0,49 [0,43; 0,56] | — | — | 0/264 |
| claude-haiku-5-5 | holístico (só conformidade) | 0,46 [0,37; 0,56] | 0,73 [0,63; 0,82] | 0,57 [0,48; 0,65] | — | — | 0/209 |
| claude-haiku-5-5 | holístico por sentença | 0,30 [0,25; 0,35] | 0,94 [0,87; 0,98] | 0,45 [0,39; 0,51] | 0,13 | 0,43 | 263/268 |
| claude-haiku-5-5 | holístico por sentença + normas | 0,26 [0,22; 0,31] | 0,97 [0,92; 1,00] | 0,42 [0,36; 0,47] | 0,53 | 0,54 | 270/278 |
| claude-haiku-5-5 | por afirmação, sem regras | 0,57 [0,43; 0,74] | 0,85 [0,71; 0,95] | 0,68 [0,55; 0,81] | 0,49 | 0,58 | 242/242 |
| claude-haiku-5-5 | por afirmação + regras (proposto) | 0,56 [0,43; 0,72] | 0,85 [0,71; 0,95] | 0,68 [0,55; 0,80] | 0,48 | 0,57 | 213/243 |

## Tabela 4. Por afirmação, todas as respostas (IC de dois níveis)

| Modelo | Juiz | FAR-crítico | falso alarme | precisão | recall |
|---|---|---|---|---|---|
| qwen3.5-9b | por afirmação, sem regras | 0,26 [0,10; 0,44] | 0,10 [0,03; 0,20] | 0,54 [0,36; 0,82] | 0,76 [0,62; 0,88] |
| qwen3.5-9b | por afirmação + regras (proposto) | 0,24 [0,09; 0,42] | 0,13 [0,04; 0,23] | 0,49 [0,33; 0,75] | 0,78 [0,64; 0,89] |
| qwen3.5-9b | por afirmação, sem recuperação | 0,35 [0,18; 0,55] | 0,23 [0,12; 0,35] | 0,30 [0,20; 0,46] | 0,63 [0,47; 0,77] |
| gemma4-12b | por afirmação, sem regras | 0,25 [0,08; 0,46] | 0,23 [0,12; 0,35] | 0,33 [0,21; 0,50] | 0,71 [0,55; 0,85] |
| gemma4-12b | por afirmação + regras (proposto) | 0,24 [0,08; 0,43] | 0,24 [0,13; 0,37] | 0,32 [0,22; 0,48] | 0,73 [0,58; 0,86] |
| gemma4-12b | por afirmação, sem recuperação | 0,87 [0,71; 0,98] | 0,00 [0,00; 0,00] | 1,00 [1,00; 1,00] | 0,12 [0,03; 0,24] |
| llama3.1-8b | por afirmação, sem regras | 0,29 [0,13; 0,47] | 0,06 [0,02; 0,12] | 0,64 [0,46; 0,87] | 0,69 [0,54; 0,82] |
| llama3.1-8b | por afirmação + regras (proposto) | 0,28 [0,13; 0,45] | 0,08 [0,03; 0,16] | 0,57 [0,40; 0,81] | 0,70 [0,55; 0,83] |
| llama3.1-8b | por afirmação, sem recuperação | 1,00 [1,00; 1,00] | 0,03 [0,00; 0,10] | 0,10 [0,00; 1,00] | 0,02 [0,00; 0,08] |
| gpt-oss-20b | por afirmação, sem regras | 0,36 [0,17; 0,58] | 0,14 [0,05; 0,25] | 0,42 [0,26; 0,68] | 0,64 [0,48; 0,79] |
| gpt-oss-20b | por afirmação + regras (proposto) | 0,34 [0,16; 0,55] | 0,17 [0,07; 0,28] | 0,39 [0,25; 0,63] | 0,67 [0,51; 0,81] |
| gpt-oss-20b | por afirmação, sem recuperação | 0,75 [0,57; 0,90] | 0,13 [0,05; 0,23] | 0,24 [0,12; 0,45] | 0,26 [0,13; 0,40] |
| claude-haiku-5-5 | por afirmação, sem regras | 0,08 [0,00; 0,25] | 0,19 [0,10; 0,30] | 0,41 [0,28; 0,59] | 0,85 [0,71; 0,95] |
| claude-haiku-5-5 | por afirmação + regras (proposto) | 0,10 [0,00; 0,26] | 0,21 [0,11; 0,32] | 0,39 [0,27; 0,57] | 0,85 [0,71; 0,95] |

## H6. F1 de localização: holístico por sentença com normas − verificador proposto

| Modelo | ΔF1 (holístico sent.+normas − proposto) | IC 95% | ΔF1 (holístico sent. − proposto) | IC 95% |
|---|---|---|---|---|
| qwen3.5-9b | -0,18 | [-0,31; -0,06] | -0,23 | [-0,36; -0,11] |
| gemma4-12b | 0,10 | [-0,04; 0,24] | -0,02 | [-0,17; 0,12] |
| llama3.1-8b | -0,28 | [-0,41; -0,15] | -0,28 | [-0,41; -0,15] |
| gpt-oss-20b | -0,12 | [-0,27; 0,02] | -0,15 | [-0,31; -0,00] |
| claude-haiku-5-5 | -0,26 | [-0,39; -0,13] | -0,23 | [-0,36; -0,09] |

## Por resposta (com e sem os 15 diálogos dos 5 erros ambíguos)

| Modelo | Juiz | falso alarme | FAR-crítico | falso alarme (sem amb.) | FAR-crítico (sem amb.) |
|---|---|---|---|---|---|
| qwen3.5-9b | holístico | 0,93 [0,88; 0,97] | 0,02 [0,00; 0,05] | 0,93 [0,88; 0,97] | 0,02 [0,00; 0,04] |
| qwen3.5-9b | holístico + normas | 0,88 [0,81; 0,93] | 0,02 [0,00; 0,05] | 0,88 [0,81; 0,93] | 0,02 [0,00; 0,06] |
| qwen3.5-9b | holístico (só conformidade) | 0,60 [0,51; 0,69] | 0,10 [0,05; 0,15] | 0,60 [0,51; 0,69] | 0,11 [0,06; 0,17] |
| qwen3.5-9b | holístico por sentença | 1,00 [1,00; 1,00] | 0,00 [0,00; 0,00] | 1,00 [1,00; 1,00] | 0,00 [0,00; 0,00] |
| qwen3.5-9b | holístico por sentença + normas | 0,99 [0,97; 1,00] | 0,00 [0,00; 0,00] | 0,99 [0,97; 1,00] | 0,00 [0,00; 0,00] |
| qwen3.5-9b | por afirmação, sem regras | 0,47 [0,38; 0,56] | 0,12 [0,07; 0,18] | 0,47 [0,38; 0,56] | 0,09 [0,04; 0,15] |
| qwen3.5-9b | por afirmação + regras (proposto) | 0,66 [0,57; 0,74] | 0,09 [0,04; 0,14] | 0,66 [0,57; 0,74] | 0,06 [0,02; 0,10] |
| qwen3.5-9b | por afirmação, sem recuperação | 0,62 [0,54; 0,71] | 0,07 [0,03; 0,11] | 0,62 [0,54; 0,71] | 0,06 [0,02; 0,10] |
| gemma4-12b | holístico | 0,97 [0,94; 1,00] | 0,00 [0,00; 0,00] | 0,97 [0,94; 1,00] | 0,00 [0,00; 0,00] |
| gemma4-12b | holístico + normas | 0,88 [0,82; 0,94] | 0,00 [0,00; 0,00] | 0,88 [0,82; 0,94] | 0,00 [0,00; 0,00] |
| gemma4-12b | holístico (só conformidade) | 0,20 [0,13; 0,27] | 0,19 [0,13; 0,26] | 0,20 [0,13; 0,27] | 0,17 [0,11; 0,24] |
| gemma4-12b | holístico por sentença | 0,95 [0,91; 0,98] | 0,00 [0,00; 0,00] | 0,95 [0,91; 0,98] | 0,00 [0,00; 0,00] |
| gemma4-12b | holístico por sentença + normas | 0,57 [0,49; 0,66] | 0,03 [0,01; 0,06] | 0,57 [0,49; 0,66] | 0,02 [0,00; 0,04] |
| gemma4-12b | por afirmação, sem regras | 0,87 [0,80; 0,92] | 0,02 [0,00; 0,05] | 0,87 [0,80; 0,92] | 0,01 [0,00; 0,03] |
| gemma4-12b | por afirmação + regras (proposto) | 0,89 [0,83; 0,94] | 0,02 [0,00; 0,05] | 0,89 [0,83; 0,94] | 0,01 [0,00; 0,03] |
| gemma4-12b | por afirmação, sem recuperação | 0,00 [0,00; 0,00] | 0,80 [0,73; 0,87] | 0,00 [0,00; 0,00] | 0,79 [0,71; 0,86] |
| llama3.1-8b | holístico | 0,93 [0,88; 0,97] | 0,02 [0,00; 0,05] | 0,93 [0,88; 0,97] | 0,02 [0,00; 0,06] |
| llama3.1-8b | holístico + normas | 0,92 [0,87; 0,96] | 0,04 [0,01; 0,08] | 0,92 [0,87; 0,96] | 0,04 [0,01; 0,08] |
| llama3.1-8b | holístico (só conformidade) | 0,43 [0,34; 0,53] | 0,28 [0,21; 0,36] | 0,43 [0,34; 0,53] | 0,26 [0,18; 0,34] |
| llama3.1-8b | holístico por sentença | 0,96 [0,92; 0,99] | 0,00 [0,00; 0,00] | 0,96 [0,92; 0,99] | 0,00 [0,00; 0,00] |
| llama3.1-8b | holístico por sentença + normas | 0,38 [0,29; 0,46] | 0,29 [0,21; 0,37] | 0,38 [0,29; 0,46] | 0,28 [0,20; 0,36] |
| llama3.1-8b | por afirmação, sem regras | 0,19 [0,12; 0,26] | 0,21 [0,15; 0,28] | 0,19 [0,12; 0,26] | 0,20 [0,13; 0,27] |
| llama3.1-8b | por afirmação + regras (proposto) | 0,39 [0,30; 0,48] | 0,18 [0,12; 0,24] | 0,39 [0,30; 0,48] | 0,16 [0,10; 0,22] |
| llama3.1-8b | por afirmação, sem recuperação | 0,17 [0,10; 0,24] | 0,81 [0,75; 0,88] | 0,17 [0,10; 0,24] | 0,80 [0,73; 0,87] |
| gpt-oss-20b | holístico | 0,97 [0,94; 1,00] | 0,01 [0,00; 0,02] | 0,97 [0,94; 1,00] | 0,01 [0,00; 0,03] |
| gpt-oss-20b | holístico + normas | 0,91 [0,85; 0,96] | 0,02 [0,00; 0,05] | 0,91 [0,85; 0,96] | 0,02 [0,00; 0,04] |
| gpt-oss-20b | holístico (só conformidade) | 0,22 [0,15; 0,29] | 0,41 [0,33; 0,50] | 0,22 [0,15; 0,29] | 0,39 [0,30; 0,47] |
| gpt-oss-20b | holístico por sentença | 0,88 [0,82; 0,94] | 0,03 [0,01; 0,06] | 0,88 [0,82; 0,94] | 0,02 [0,00; 0,06] |
| gpt-oss-20b | holístico por sentença + normas | 0,82 [0,74; 0,88] | 0,04 [0,01; 0,08] | 0,82 [0,74; 0,88] | 0,02 [0,00; 0,04] |
| gpt-oss-20b | por afirmação, sem regras | 0,68 [0,60; 0,77] | 0,11 [0,06; 0,17] | 0,68 [0,60; 0,77] | 0,11 [0,06; 0,18] |
| gpt-oss-20b | por afirmação + regras (proposto) | 0,79 [0,72; 0,86] | 0,08 [0,04; 0,13] | 0,79 [0,72; 0,86] | 0,08 [0,04; 0,13] |
| gpt-oss-20b | por afirmação, sem recuperação | 0,62 [0,53; 0,71] | 0,31 [0,23; 0,39] | 0,62 [0,53; 0,71] | 0,30 [0,22; 0,39] |
| claude-haiku-5-5 | holístico | 0,84 [0,77; 0,90] | 0,00 [0,00; 0,00] | 0,84 [0,77; 0,90] | 0,00 [0,00; 0,00] |
| claude-haiku-5-5 | holístico + normas | 0,99 [0,97; 1,00] | 0,00 [0,00; 0,00] | 0,99 [0,97; 1,00] | 0,00 [0,00; 0,00] |
| claude-haiku-5-5 | holístico (só conformidade) | 0,39 [0,30; 0,48] | 0,14 [0,08; 0,20] | 0,39 [0,30; 0,48] | 0,12 [0,07; 0,18] |
| claude-haiku-5-5 | holístico por sentença | 0,93 [0,89; 0,97] | 0,00 [0,00; 0,00] | 0,93 [0,89; 0,97] | 0,00 [0,00; 0,00] |
| claude-haiku-5-5 | holístico por sentença + normas | 1,00 [1,00; 1,00] | 0,00 [0,00; 0,00] | 1,00 [1,00; 1,00] | 0,00 [0,00; 0,00] |
| claude-haiku-5-5 | por afirmação, sem regras | 0,79 [0,72; 0,86] | 0,02 [0,00; 0,05] | 0,79 [0,72; 0,86] | 0,02 [0,00; 0,06] |
| claude-haiku-5-5 | por afirmação + regras (proposto) | 0,85 [0,78; 0,91] | 0,01 [0,00; 0,04] | 0,85 [0,78; 0,91] | 0,02 [0,00; 0,04] |

## H7. Rejeição de respostas sem erro: holístico x holístico só conformidade (McNemar exato, Holm na família de 4)

| Modelo | falso alarme holístico | falso alarme só conformidade | discordantes (só hol. / só conf.) | p | p Holm |
|---|---|---|---|---|---|
| qwen3.5-9b | 0,93 | 0,60 | 39 / 0 | 0,0000 | 0,0000 |
| gemma4-12b | 0,97 | 0,20 | 93 / 0 | 0,0000 | 0,0000 |
| llama3.1-8b | 0,93 | 0,43 | 61 / 1 | 0,0000 | 0,0000 |
| gpt-oss-20b | 0,97 | 0,22 | 91 / 0 | 0,0000 | 0,0000 |
| claude-haiku-5-5 | 0,84 | 0,39 | 55 / 1 | 0,0000 | exploratório |

## Comparação pareada pelo envelope convexo da ROC (H1 refeita)

FAR-crítico do holístico no **mesmo falso alarme** do verificador proposto, com limiar aleatorizado entre dois vértices do envelope convexo da curva ROC da nota 1-5.

| Modelo | Juiz holístico | falso alarme do proposto | FAR-crítico do proposto | FAR-crítico do holístico pareado | diferença (hol. − prop.) [IC 95%] |
|---|---|---|---|---|---|
| qwen3.5-9b | holístico | 0,66 | 0,09 | 0,09 | 0,00 [-0,05; 0,06] |
| qwen3.5-9b | holístico + normas | 0,66 | 0,09 | 0,11 | 0,02 [-0,03; 0,08] |
| qwen3.5-9b | holístico (só conformidade) | 0,66 | 0,09 | 0,11 | 0,02 [-0,05; 0,09] |
| qwen3.5-9b | holístico por sentença | 0,66 | 0,09 | 0,21 | 0,12 [0,04; 0,20] |
| qwen3.5-9b | holístico por sentença + normas | 0,66 | 0,09 | 0,20 | 0,11 [0,04; 0,19] |
| gemma4-12b | holístico | 0,89 | 0,02 | 0,02 | -0,00 [-0,04; 0,02] |
| gemma4-12b | holístico + normas | 0,89 | 0,02 | 0,00 | -0,02 [-0,05; 0,00] |
| gemma4-12b | holístico (só conformidade) | 0,89 | 0,02 | 0,03 | 0,00 [-0,03; 0,03] |
| gemma4-12b | holístico por sentença | 0,89 | 0,02 | 0,02 | -0,01 [-0,04; 0,03] |
| gemma4-12b | holístico por sentença + normas | 0,89 | 0,02 | 0,01 | -0,01 [-0,04; 0,01] |
| llama3.1-8b | holístico | 0,39 | 0,18 | 0,42 | 0,24 [0,14; 0,35] |
| llama3.1-8b | holístico + normas | 0,39 | 0,18 | 0,44 | 0,27 [0,17; 0,36] |
| llama3.1-8b | holístico (só conformidade) | 0,39 | 0,18 | 0,45 | 0,27 [0,10; 0,41] |
| llama3.1-8b | holístico por sentença | 0,39 | 0,18 | 0,59 | 0,41 [0,30; 0,53] |
| llama3.1-8b | holístico por sentença + normas | 0,39 | 0,18 | 0,28 | 0,10 [0,00; 0,31] |
| gpt-oss-20b | holístico | 0,79 | 0,08 | 0,11 | 0,02 [-0,05; 0,09] |
| gpt-oss-20b | holístico + normas | 0,79 | 0,08 | 0,05 | -0,03 [-0,09; 0,05] |
| gpt-oss-20b | holístico (só conformidade) | 0,79 | 0,08 | 0,10 | 0,01 [-0,04; 0,07] |
| gpt-oss-20b | holístico por sentença | 0,79 | 0,08 | 0,08 | 0,00 [-0,06; 0,08] |
| gpt-oss-20b | holístico por sentença + normas | 0,79 | 0,08 | 0,06 | -0,02 [-0,09; 0,07] |
| claude-haiku-5-5 | holístico | 0,85 | 0,01 | 0,01 | -0,01 [-0,03; 0,02] |
| claude-haiku-5-5 | holístico + normas | 0,85 | 0,01 | 0,04 | 0,03 [-0,01; 0,07] |
| claude-haiku-5-5 | holístico (só conformidade) | 0,85 | 0,01 | 0,03 | 0,02 [-0,01; 0,05] |
| claude-haiku-5-5 | holístico por sentença | 0,85 | 0,01 | 0,03 | 0,02 [-0,02; 0,06] |
| claude-haiku-5-5 | holístico por sentença + normas | 0,85 | 0,01 | 0,04 | 0,03 [-0,02; 0,09] |

## Ablação: sem recuperação x por afirmação sem regras (por afirmação, todas as respostas)

| Modelo | juiz | falso alarme por afirmação | recall de erros |
|---|---|---|---|
| qwen3.5-9b | por afirmação, sem regras | 0,10 | 0,76 |
| qwen3.5-9b | por afirmação, sem recuperação | 0,23 | 0,63 |
| gemma4-12b | por afirmação, sem regras | 0,23 | 0,71 |
| gemma4-12b | por afirmação, sem recuperação | 0,00 | 0,12 |
| llama3.1-8b | por afirmação, sem regras | 0,06 | 0,69 |
| llama3.1-8b | por afirmação, sem recuperação | 0,03 | 0,02 |
| gpt-oss-20b | por afirmação, sem regras | 0,14 | 0,64 |
| gpt-oss-20b | por afirmação, sem recuperação | 0,13 | 0,26 |
| claude-haiku-5-5 | por afirmação, sem regras | 0,19 | 0,85 |
