# Análise da emenda 3 (gerado por analise_emenda3.py)

IC 95% por bootstrap (10.000 réplicas, semente 7): por diálogo nas métricas por resposta, salvo indicação; dois níveis (diálogo × fato) nas métricas por afirmação e de localização.

## Por resposta (decisão como devolvida) e localização

| Modelo | Juiz | falso alarme | FAR-crítico | AUC | precisão loc. | recall loc. | F1 loc. | precisão (300 resp.) |
|---|---|---|---|---|---|---|---|---|
| qwen3.5-9b | holístico | 0,93 [0,88; 0,97] | 0,02 [0,00; 0,05] | 0,76 | 0,40 [0,31; 0,51] | 0,59 [0,48; 0,70] | 0,48 [0,38; 0,57] | — |
| qwen3.5-9b | holístico + normas | 0,88 [0,81; 0,93] | 0,02 [0,00; 0,05] | 0,80 | 0,46 [0,37; 0,55] | 0,76 [0,65; 0,85] | 0,57 [0,49; 0,66] | — |
| qwen3.5-9b | holístico (só conformidade) | 0,60 [0,51; 0,69] | 0,10 [0,05; 0,15] | 0,77 | 0,38 [0,31; 0,46] | 0,76 [0,64; 0,85] | 0,51 [0,43; 0,59] | — |
| qwen3.5-9b | holístico por sentença | 1,00 [1,00; 1,00] | 0,00 [0,00; 0,00] | 0,66 | 0,32 [0,26; 0,39] | 0,88 [0,77; 0,95] | 0,47 [0,40; 0,54] | 0,19 |
| qwen3.5-9b | holístico por sentença + normas | 0,99 [0,97; 1,00] | 0,00 [0,00; 0,00] | 0,67 | 0,36 [0,30; 0,44] | 0,90 [0,81; 0,96] | 0,52 [0,44; 0,59] | 0,21 |
| qwen3.5-9b | por afirmação, sem regras | 0,47 [0,38; 0,56] | 0,12 [0,07; 0,18] | 0,79 | 0,67 [0,49; 0,89] | 0,76 [0,62; 0,88] | 0,71 [0,58; 0,84] | 0,54 |
| qwen3.5-9b | por afirmação + regras (proposto) | 0,66 [0,57; 0,74] | 0,09 [0,04; 0,14] | 0,78 | 0,64 [0,48; 0,85] | 0,78 [0,64; 0,89] | 0,70 [0,57; 0,83] | 0,49 |
| qwen3.5-9b | por afirmação, sem recuperação | 0,62 [0,54; 0,71] | 0,07 [0,03; 0,11] | 0,66 | 0,45 [0,31; 0,62] | 0,63 [0,47; 0,77] | 0,52 [0,39; 0,65] | 0,30 |
| qwen3.5-9b | holístico só conformidade + por sentença + normas | 0,86 [0,79; 0,92] | 0,02 [0,00; 0,05] | 0,72 | 0,43 [0,35; 0,52] | 0,85 [0,75; 0,93] | 0,57 [0,49; 0,66] | 0,28 |
| qwen3.5-9b | holístico + normas (top-3) | 0,96 [0,92; 0,99] | 0,01 [0,00; 0,02] | 0,80 | 0,38 [0,30; 0,46] | 0,73 [0,62; 0,83] | 0,50 [0,42; 0,58] | — |
| qwen3.5-9b | RAGAs faithfulness | 0,91 [0,85; 0,96] | 0,04 [0,01; 0,08] | 0,71 | 0,39 [0,30; 0,50] | 0,55 [0,44; 0,67] | 0,46 [0,37; 0,55] | 0,25 |
| qwen3.5-9b | MiniCheck | 0,93 [0,88; 0,97] | 0,01 [0,00; 0,04] | 0,70 | 0,45 [0,35; 0,58] | 0,95 [0,87; 1,00] | 0,61 [0,50; 0,72] | 0,30 |
| qwen3.5-9b | verificador, recuperação oráculo | 0,45 [0,36; 0,54] | 0,04 [0,01; 0,08] | 0,86 | 0,74 [0,59; 0,92] | 0,93 [0,84; 0,98] | 0,83 [0,71; 0,93] | 0,62 |
| qwen3.5-9b | verificador, fim a fim | 0,70 [0,62; 0,78] | 0,06 [0,02; 0,10] | 0,74 | 0,64 [0,48; 0,83] | 0,70 [0,59; 0,80] | 0,67 [0,55; 0,78] | 0,50 |
| gemma4-12b | holístico | 0,97 [0,94; 1,00] | 0,00 [0,00; 0,00] | 0,82 | 0,67 [0,46; 0,87] | 0,24 [0,14; 0,36] | 0,35 [0,22; 0,49] | — |
| gemma4-12b | holístico + normas | 0,88 [0,82; 0,94] | 0,00 [0,00; 0,00] | 0,88 | 0,82 [0,68; 0,93] | 0,45 [0,31; 0,59] | 0,58 [0,44; 0,70] | — |
| gemma4-12b | holístico (só conformidade) | 0,20 [0,13; 0,27] | 0,19 [0,13; 0,26] | 0,80 | 0,52 [0,39; 0,65] | 0,52 [0,38; 0,65] | 0,52 [0,40; 0,63] | — |
| gemma4-12b | holístico por sentença | 0,95 [0,91; 0,98] | 0,00 [0,00; 0,00] | 0,79 | 0,40 [0,32; 0,49] | 0,90 [0,81; 0,96] | 0,55 [0,46; 0,64] | 0,26 |
| gemma4-12b | holístico por sentença + normas | 0,57 [0,49; 0,66] | 0,03 [0,01; 0,06] | 0,82 | 0,55 [0,43; 0,67] | 0,89 [0,80; 0,96] | 0,68 [0,57; 0,77] | 0,40 |
| gemma4-12b | por afirmação, sem regras | 0,87 [0,80; 0,92] | 0,02 [0,00; 0,05] | 0,71 | 0,47 [0,33; 0,65] | 0,71 [0,55; 0,85] | 0,57 [0,43; 0,71] | 0,33 |
| gemma4-12b | por afirmação + regras (proposto) | 0,89 [0,83; 0,94] | 0,02 [0,00; 0,05] | 0,69 | 0,47 [0,35; 0,64] | 0,73 [0,58; 0,86] | 0,57 [0,45; 0,71] | 0,32 |
| gemma4-12b | por afirmação, sem recuperação | 0,00 [0,00; 0,00] | 0,80 [0,73; 0,87] | 0,60 | 1,00 [1,00; 1,00] | 0,12 [0,03; 0,24] | 0,22 [0,06; 0,39] | 1,00 |
| gemma4-12b | holístico só conformidade + por sentença + normas | 0,47 [0,39; 0,57] | 0,06 [0,02; 0,10] | 0,78 | 0,65 [0,52; 0,79] | 0,81 [0,70; 0,90] | 0,72 [0,61; 0,82] | 0,50 |
| gemma4-12b | holístico + normas (top-3) | 0,96 [0,92; 0,99] | 0,00 [0,00; 0,00] | 0,85 | 0,76 [0,63; 0,86] | 0,51 [0,38; 0,63] | 0,61 [0,48; 0,71] | — |
| gemma4-12b | RAGAs faithfulness | 0,98 [0,96; 1,00] | 0,00 [0,00; 0,00] | 0,71 | 0,41 [0,18; 0,67] | 0,06 [0,02; 0,12] | 0,11 [0,03; 0,20] | 0,31 |
| gemma4-12b | MiniCheck | 0,93 [0,88; 0,97] | 0,01 [0,00; 0,04] | 0,70 | 0,45 [0,35; 0,58] | 0,95 [0,87; 1,00] | 0,61 [0,50; 0,72] | 0,30 |
| gemma4-12b | verificador, recuperação oráculo | 0,66 [0,57; 0,74] | 0,01 [0,00; 0,02] | 0,82 | 0,70 [0,55; 0,86] | 0,96 [0,90; 1,00] | 0,81 [0,70; 0,91] | 0,55 |
| gemma4-12b | verificador, fim a fim | 0,96 [0,92; 0,99] | 0,02 [0,00; 0,05] | 0,64 | 0,49 [0,34; 0,68] | 0,54 [0,40; 0,67] | 0,52 [0,39; 0,64] | 0,34 |
| llama3.1-8b | holístico | 0,93 [0,88; 0,97] | 0,02 [0,00; 0,05] | 0,64 | 0,31 [0,22; 0,43] | 0,28 [0,19; 0,38] | 0,30 [0,21; 0,39] | — |
| llama3.1-8b | holístico + normas | 0,92 [0,87; 0,96] | 0,04 [0,01; 0,08] | 0,63 | 0,24 [0,15; 0,36] | 0,18 [0,11; 0,27] | 0,21 [0,13; 0,29] | — |
| llama3.1-8b | holístico (só conformidade) | 0,43 [0,34; 0,53] | 0,28 [0,21; 0,36] | 0,63 | 0,31 [0,23; 0,39] | 0,43 [0,33; 0,54] | 0,36 [0,28; 0,44] | — |
| llama3.1-8b | holístico por sentença | 0,96 [0,92; 0,99] | 0,00 [0,00; 0,00] | 0,52 | 0,28 [0,23; 0,33] | 0,93 [0,87; 0,97] | 0,43 [0,36; 0,49] | 0,17 |
| llama3.1-8b | holístico por sentença + normas | 0,38 [0,29; 0,46] | 0,29 [0,21; 0,37] | 0,67 | 0,28 [0,23; 0,34] | 0,87 [0,80; 0,94] | 0,42 [0,36; 0,49] | 0,17 |
| llama3.1-8b | por afirmação, sem regras | 0,19 [0,12; 0,26] | 0,21 [0,15; 0,28] | 0,79 | 0,75 [0,58; 0,92] | 0,69 [0,54; 0,82] | 0,72 [0,59; 0,83] | 0,64 |
| llama3.1-8b | por afirmação + regras (proposto) | 0,39 [0,30; 0,48] | 0,18 [0,12; 0,24] | 0,75 | 0,71 [0,55; 0,89] | 0,70 [0,55; 0,83] | 0,70 [0,58; 0,81] | 0,57 |
| llama3.1-8b | por afirmação, sem recuperação | 0,17 [0,10; 0,24] | 0,81 [0,75; 0,88] | 0,51 | 0,14 [0,00; 1,00] | 0,02 [0,00; 0,08] | 0,04 [0,01; 0,16] | 0,10 |
| llama3.1-8b | holístico só conformidade + por sentença + normas | 0,01 [0,00; 0,03] | 0,82 [0,75; 0,89] | 0,58 | 0,36 [0,20; 0,54] | 0,13 [0,06; 0,21] | 0,19 [0,10; 0,29] | 0,35 |
| llama3.1-8b | holístico + normas (top-3) | 0,93 [0,89; 0,97] | 0,02 [0,00; 0,05] | 0,61 | 0,26 [0,15; 0,39] | 0,19 [0,11; 0,28] | 0,22 [0,13; 0,31] | — |
| llama3.1-8b | RAGAs faithfulness | 0,93 [0,88; 0,97] | 0,00 [0,00; 0,00] | 0,61 | 0,41 [0,09; 0,80] | 0,03 [0,00; 0,08] | 0,06 [0,01; 0,13] | 0,20 |
| llama3.1-8b | MiniCheck | 0,93 [0,88; 0,97] | 0,01 [0,00; 0,04] | 0,70 | 0,45 [0,35; 0,58] | 0,95 [0,87; 1,00] | 0,61 [0,50; 0,72] | 0,30 |
| llama3.1-8b | verificador, recuperação oráculo | 0,13 [0,08; 0,20] | 0,41 [0,33; 0,50] | 0,73 | 0,84 [0,63; 1,00] | 0,43 [0,28; 0,60] | 0,57 [0,41; 0,72] | 0,75 |
| llama3.1-8b | verificador, fim a fim | 0,62 [0,53; 0,70] | 0,13 [0,07; 0,18] | 0,69 | 0,59 [0,44; 0,76] | 0,56 [0,43; 0,69] | 0,57 [0,45; 0,69] | 0,46 |
| gpt-oss-20b | holístico | 0,97 [0,94; 1,00] | 0,01 [0,00; 0,02] | 0,60 | 0,46 [0,32; 0,61] | 0,29 [0,18; 0,40] | 0,36 [0,24; 0,47] | — |
| gpt-oss-20b | holístico + normas | 0,91 [0,85; 0,96] | 0,02 [0,00; 0,05] | 0,68 | 0,52 [0,37; 0,68] | 0,34 [0,22; 0,46] | 0,41 [0,28; 0,53] | — |
| gpt-oss-20b | holístico (só conformidade) | 0,22 [0,15; 0,29] | 0,41 [0,33; 0,50] | 0,71 | 0,58 [0,42; 0,75] | 0,29 [0,18; 0,42] | 0,39 [0,26; 0,51] | — |
| gpt-oss-20b | holístico por sentença | 0,88 [0,82; 0,94] | 0,03 [0,01; 0,06] | 0,59 | 0,31 [0,25; 0,37] | 0,84 [0,74; 0,92] | 0,45 [0,39; 0,51] | 0,20 |
| gpt-oss-20b | holístico por sentença + normas | 0,82 [0,74; 0,88] | 0,04 [0,01; 0,08] | 0,60 | 0,34 [0,28; 0,41] | 0,83 [0,72; 0,91] | 0,48 [0,41; 0,56] | 0,23 |
| gpt-oss-20b | por afirmação, sem regras | 0,68 [0,60; 0,77] | 0,11 [0,06; 0,17] | 0,72 | 0,57 [0,39; 0,81] | 0,64 [0,48; 0,79] | 0,61 [0,45; 0,76] | 0,42 |
| gpt-oss-20b | por afirmação + regras (proposto) | 0,79 [0,72; 0,86] | 0,08 [0,04; 0,13] | 0,70 | 0,55 [0,39; 0,77] | 0,67 [0,51; 0,81] | 0,60 [0,46; 0,75] | 0,39 |
| gpt-oss-20b | por afirmação, sem recuperação | 0,62 [0,53; 0,71] | 0,31 [0,23; 0,39] | 0,56 | 0,36 [0,20; 0,61] | 0,26 [0,13; 0,40] | 0,30 [0,16; 0,44] | 0,24 |
| gpt-oss-20b | holístico só conformidade + por sentença + normas | 0,28 [0,20; 0,36] | 0,27 [0,19; 0,34] | 0,75 | 0,67 [0,51; 0,83] | 0,51 [0,38; 0,64] | 0,58 [0,45; 0,70] | 0,55 |
| gpt-oss-20b | holístico + normas (top-3) | 0,97 [0,93; 0,99] | 0,00 [0,00; 0,00] | 0,62 | 0,51 [0,35; 0,67] | 0,28 [0,18; 0,39] | 0,36 [0,24; 0,47] | — |
| gpt-oss-20b | RAGAs faithfulness | 0,97 [0,94; 1,00] | 0,01 [0,00; 0,02] | 0,73 | 0,35 [0,26; 0,47] | 0,37 [0,26; 0,48] | 0,36 [0,27; 0,45] | 0,22 |
| gpt-oss-20b | MiniCheck | 0,93 [0,88; 0,97] | 0,01 [0,00; 0,04] | 0,70 | 0,45 [0,35; 0,58] | 0,95 [0,87; 1,00] | 0,61 [0,50; 0,72] | 0,30 |
| gpt-oss-20b | verificador, recuperação oráculo | 0,29 [0,21; 0,38] | 0,04 [0,01; 0,07] | 0,92 | 0,85 [0,67; 1,00] | 0,94 [0,86; 0,99] | 0,89 [0,78; 0,98] | 0,76 |
| gpt-oss-20b | verificador, fim a fim | 0,70 [0,61; 0,78] | 0,07 [0,03; 0,11] | 0,71 | 0,60 [0,44; 0,77] | 0,59 [0,46; 0,72] | 0,59 [0,47; 0,71] | 0,44 |
| claude-haiku-5-5 | holístico | 0,84 [0,77; 0,90] | 0,00 [0,00; 0,00] | 0,79 | 0,32 [0,26; 0,38] | 0,86 [0,77; 0,93] | 0,47 [0,39; 0,54] | — |
| claude-haiku-5-5 | holístico + normas | 0,99 [0,97; 1,00] | 0,00 [0,00; 0,00] | 0,70 | 0,34 [0,28; 0,40] | 0,92 [0,85; 0,97] | 0,49 [0,43; 0,56] | — |
| claude-haiku-5-5 | holístico (só conformidade) | 0,39 [0,30; 0,48] | 0,14 [0,08; 0,20] | 0,80 | 0,46 [0,37; 0,56] | 0,73 [0,63; 0,82] | 0,57 [0,48; 0,65] | — |
| claude-haiku-5-5 | holístico por sentença | 0,93 [0,89; 0,97] | 0,00 [0,00; 0,00] | 0,69 | 0,30 [0,25; 0,35] | 0,94 [0,87; 0,98] | 0,45 [0,39; 0,51] | 0,19 |
| claude-haiku-5-5 | holístico por sentença + normas | 1,00 [1,00; 1,00] | 0,00 [0,00; 0,00] | 0,66 | 0,26 [0,22; 0,31] | 0,97 [0,92; 1,00] | 0,42 [0,36; 0,47] | 0,16 |
| claude-haiku-5-5 | por afirmação, sem regras | 0,79 [0,72; 0,86] | 0,02 [0,00; 0,05] | 0,74 | 0,57 [0,43; 0,74] | 0,85 [0,71; 0,95] | 0,68 [0,55; 0,81] | 0,41 |
| claude-haiku-5-5 | por afirmação + regras (proposto) | 0,85 [0,78; 0,91] | 0,01 [0,00; 0,04] | 0,72 | 0,56 [0,43; 0,72] | 0,85 [0,71; 0,95] | 0,68 [0,55; 0,80] | 0,39 |

## H8. Contra o verificador proposto (afirmacao_regras)

| Modelo | Juiz | ΔF1 (juiz − proposto) [IC] | p ΔF1 | p Holm | FAR-crítico do proposto | FAR-crítico do juiz no mesmo falso alarme | diferença (juiz − proposto) [IC] |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | holístico só conformidade + por sentença + normas | -0,13 [-0,26; -0,01] | 0,034 | 0,102 | 0,09 | 0,14 | 0,05 [-0,04; 0,13] |
| gemma4-12b | holístico só conformidade + por sentença + normas | 0,15 [-0,00; 0,28] | 0,054 | 0,107 | 0,02 | 0,01 | -0,01 [-0,04; 0,01] |
| llama3.1-8b | holístico só conformidade + por sentença + normas | -0,51 [-0,67; -0,35] | 0,000 | 0,000 | 0,18 | 0,50 | 0,33 [0,22; 0,43] |
| gpt-oss-20b | holístico só conformidade + por sentença + normas | -0,02 [-0,19; 0,13] | 0,760 | 0,760 | 0,08 | 0,08 | -0,00 [-0,06; 0,05] |

## H3b. Contra o verificador proposto (afirmacao_regras)

| Modelo | Juiz | ΔF1 (juiz − proposto) [IC] | p ΔF1 | p Holm | FAR-crítico do proposto | FAR-crítico do juiz no mesmo falso alarme | diferença (juiz − proposto) [IC] |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | holístico + normas (top-3) | -0,20 [-0,33; -0,07] | 0,003 | 0,009 | 0,09 | 0,11 | 0,02 [-0,03; 0,08] |
| gemma4-12b | holístico + normas (top-3) | 0,03 [-0,13; 0,17] | 0,720 | 0,720 | 0,02 | 0,02 | -0,00 [-0,04; 0,02] |
| llama3.1-8b | holístico + normas (top-3) | -0,49 [-0,62; -0,34] | 0,000 | 0,000 | 0,18 | 0,45 | 0,27 [0,17; 0,37] |
| gpt-oss-20b | holístico + normas (top-3) | -0,24 [-0,43; -0,07] | 0,008 | 0,017 | 0,08 | 0,09 | 0,01 [-0,06; 0,08] |

## H10. Contra o verificador proposto (afirmacao_regras)

| Modelo | Juiz | ΔF1 (juiz − proposto) [IC] | p ΔF1 | p Holm | FAR-crítico do proposto | FAR-crítico do juiz no mesmo falso alarme | diferença (juiz − proposto) [IC] |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | RAGAs faithfulness | -0,24 [-0,39; -0,10] | 0,001 | 0,001 | 0,09 | 0,12 | 0,03 [-0,05; 0,11] |
| qwen3.5-9b | MiniCheck | -0,09 [-0,23; 0,04] | 0,168 | 0,671 | 0,09 | 0,13 | 0,04 [-0,02; 0,11] |
| gemma4-12b | RAGAs faithfulness | -0,47 [-0,61; -0,32] | 0,000 | 0,000 | 0,02 | 0,02 | 0,00 [-0,04; 0,03] |
| gemma4-12b | MiniCheck | 0,03 [-0,11; 0,17] | 0,636 | 1,000 | 0,02 | 0,03 | 0,01 [-0,02; 0,04] |
| llama3.1-8b | RAGAs faithfulness | -0,64 [-0,77; -0,50] | 0,000 | 0,000 | 0,18 | 0,44 | 0,26 [0,09; 0,39] |
| llama3.1-8b | MiniCheck | -0,09 [-0,24; 0,06] | 0,221 | 0,671 | 0,18 | 0,25 | 0,08 [-0,02; 0,21] |
| gpt-oss-20b | RAGAs faithfulness | -0,24 [-0,40; -0,10] | 0,000 | 0,001 | 0,08 | 0,04 | -0,04 [-0,10; 0,01] |
| gpt-oss-20b | MiniCheck | 0,00 [-0,15; 0,15] | 0,936 | 1,000 | 0,08 | 0,07 | -0,01 [-0,07; 0,05] |

## H9. Recuperação oráculo x híbrida (verificador, por afirmação; dois níveis)

| Modelo | FAR-crít. afirm. híbrida | FAR-crít. afirm. oráculo | diferença (oráculo − híbrida) [IC] | falso alarme afirm. híbrida | oráculo | acurácia do veredito: recuperação acertou | errou |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | 0,24 [0,09; 0,42] | 0,07 [0,01; 0,18] | -0,17 [-0,35; -0,03] | 0,13 | 0,09 | 0,94 | 0,65 |
| gemma4-12b | 0,24 [0,08; 0,43] | 0,06 [0,00; 0,15] | -0,18 [-0,38; -0,01] | 0,24 | 0,12 | 0,85 | 0,49 |
| llama3.1-8b | 0,28 [0,13; 0,45] | 0,58 [0,37; 0,77] | 0,30 [0,07; 0,53] | 0,08 | 0,02 | 0,90 | 0,86 |
| gpt-oss-20b | 0,34 [0,16; 0,55] | 0,06 [0,00; 0,15] | -0,28 [-0,49; -0,10] | 0,17 | 0,05 | 0,94 | 0,48 |

p bootstrap da diferença (bicaudal) e Holm nos 4 modelos locais: qwen3.5-9b p = 0,006, Holm 0,017; gemma4-12b p = 0,043, Holm 0,043; llama3.1-8b p = 0,012, Holm 0,023; gpt-oss-20b p = 0,002, Holm 0,009.

Recall@3 da recuperação híbrida nas 2.113 afirmações: 0,72.

## M8. Fim a fim (segmentação pelo LLM)

| Modelo | afirmações do gabarito alinhadas | extraídas por resposta | falso alarme | FAR-crítico | AUC | FAR-crít. afirm. |
|---|---|---|---|---|---|---|
| qwen3.5-9b | 0,83 | 9,0 | 0,70 [0,62; 0,78] | 0,06 [0,02; 0,10] | 0,74 | 0,33 [0,20; 0,46] |
| gemma4-12b | 0,69 | 11,8 | 0,96 [0,92; 0,99] | 0,02 [0,00; 0,05] | 0,64 | 0,42 [0,26; 0,59] |
| llama3.1-8b | 0,87 | 8,6 | 0,62 [0,53; 0,70] | 0,13 [0,07; 0,18] | 0,69 | 0,45 [0,30; 0,61] |
| gpt-oss-20b | 0,82 | 8,6 | 0,70 [0,61; 0,78] | 0,07 [0,03; 0,11] | 0,71 | 0,40 [0,24; 0,58] |

## M5. Dependência por fato no nível de resposta

As 135 respostas com erro crítico contêm 49 erros críticos distintos, de 35 fatos-norma.

| Modelo | Juiz | FAR-crítico [IC diálogo] | [IC dois níveis] | falso alarme [IC diálogo] | [IC dois níveis] |
|---|---|---|---|---|---|
| qwen3.5-9b | holístico | 0,02 [0,00; 0,05] | [0,00; 0,06] | 0,93 [0,88; 0,97] | [0,87; 0,97] |
| qwen3.5-9b | holístico (só conformidade) | 0,10 [0,05; 0,15] | [0,04; 0,16] | 0,60 [0,51; 0,69] | [0,48; 0,72] |
| qwen3.5-9b | holístico por sentença + normas | 0,00 [0,00; 0,00] | [0,00; 0,00] | 0,99 [0,97; 1,00] | [0,97; 1,00] |
| qwen3.5-9b | por afirmação + regras (proposto) | 0,09 [0,04; 0,14] | [0,04; 0,16] | 0,66 [0,57; 0,74] | [0,54; 0,77] |
| gemma4-12b | holístico | 0,00 [0,00; 0,00] | [0,00; 0,00] | 0,97 [0,94; 1,00] | [0,94; 1,00] |
| gemma4-12b | holístico (só conformidade) | 0,19 [0,13; 0,26] | [0,12; 0,27] | 0,20 [0,13; 0,27] | [0,12; 0,29] |
| gemma4-12b | holístico por sentença + normas | 0,03 [0,01; 0,06] | [0,00; 0,07] | 0,57 [0,49; 0,66] | [0,47; 0,68] |
| gemma4-12b | por afirmação + regras (proposto) | 0,02 [0,00; 0,05] | [0,00; 0,06] | 0,89 [0,83; 0,94] | [0,81; 0,95] |
| llama3.1-8b | holístico | 0,02 [0,00; 0,05] | [0,00; 0,06] | 0,93 [0,88; 0,97] | [0,87; 0,98] |
| llama3.1-8b | holístico (só conformidade) | 0,28 [0,21; 0,36] | [0,20; 0,37] | 0,43 [0,34; 0,53] | [0,33; 0,54] |
| llama3.1-8b | holístico por sentença + normas | 0,29 [0,21; 0,37] | [0,21; 0,38] | 0,38 [0,29; 0,46] | [0,27; 0,48] |
| llama3.1-8b | por afirmação + regras (proposto) | 0,18 [0,12; 0,24] | [0,10; 0,27] | 0,39 [0,30; 0,48] | [0,27; 0,52] |
| gpt-oss-20b | holístico | 0,01 [0,00; 0,02] | [0,00; 0,03] | 0,97 [0,94; 1,00] | [0,94; 1,00] |
| gpt-oss-20b | holístico (só conformidade) | 0,41 [0,33; 0,50] | [0,31; 0,52] | 0,22 [0,15; 0,29] | [0,14; 0,31] |
| gpt-oss-20b | holístico por sentença + normas | 0,04 [0,01; 0,08] | [0,01; 0,09] | 0,82 [0,74; 0,88] | [0,73; 0,90] |
| gpt-oss-20b | por afirmação + regras (proposto) | 0,08 [0,04; 0,13] | [0,03; 0,14] | 0,79 [0,72; 0,86] | [0,69; 0,88] |

Diferenças pareadas com IC de dois níveis por resposta (H1 exato e H7):

| Modelo | comparação | diferença | IC diálogo | IC dois níveis |
|---|---|---|---|---|
| qwen3.5-9b | H1 exato: FAR-crít. holístico − proposto | 0,00 | [-0,05; 0,06] | [-0,07; 0,08] |
| qwen3.5-9b | H7: falso alarme só conformidade − holístico | -0,33 | [-0,41; -0,24] | [-0,44; -0,22] |
| gemma4-12b | H1 exato: FAR-crít. holístico − proposto | -0,00 | [-0,04; 0,02] | [-0,04; 0,03] |
| gemma4-12b | H7: falso alarme só conformidade − holístico | -0,77 | [-0,85; -0,70] | [-0,86; -0,68] |
| llama3.1-8b | H1 exato: FAR-crít. holístico − proposto | 0,24 | [0,14; 0,35] | [0,11; 0,38] |
| llama3.1-8b | H7: falso alarme só conformidade − holístico | -0,50 | [-0,59; -0,40] | [-0,61; -0,38] |
| gpt-oss-20b | H1 exato: FAR-crít. holístico − proposto | 0,02 | [-0,05; 0,09] | [-0,06; 0,11] |
| gpt-oss-20b | H7: falso alarme só conformidade − holístico | -0,76 | [-0,83; -0,68] | [-0,84; -0,66] |

## M6. Pontos de operação realistas

FAR-crítico de cada juiz no falso alarme fixo (envelope convexo da própria curva; IC por diálogo, 2.000 réplicas).

| Modelo | Juiz | FA 0,05 | FA 0,10 | FA 0,20 |
|---|---|---|---|---|
| qwen3.5-9b | holístico | 0,82 [0,70; 0,89] | 0,64 [0,44; 0,77] | 0,42 [0,32; 0,54] |
| qwen3.5-9b | holístico + normas | 0,55 [0,43; 0,76] | 0,44 [0,29; 0,55] | 0,26 [0,19; 0,36] |
| qwen3.5-9b | holístico (só conformidade) | 0,71 [0,51; 0,83] | 0,51 [0,35; 0,66] | 0,34 [0,26; 0,44] |
| qwen3.5-9b | holístico por sentença + normas | 0,85 [0,76; 0,90] | 0,71 [0,53; 0,80] | 0,49 [0,41; 0,61] |
| qwen3.5-9b | holístico só conformidade + por sentença + normas | 0,78 [0,57; 0,86] | 0,56 [0,44; 0,72] | 0,46 [0,37; 0,53] |
| qwen3.5-9b | por afirmação + regras (proposto) | 0,60 [0,52; 0,69] | 0,52 [0,41; 0,61] | 0,35 [0,26; 0,47] |
| qwen3.5-9b | RAGAs faithfulness | 0,84 [0,68; 0,89] | 0,69 [0,50; 0,78] | 0,47 [0,33; 0,58] |
| qwen3.5-9b | MiniCheck | 0,84 [0,72; 0,89] | 0,69 [0,50; 0,79] | 0,48 [0,38; 0,59] |
| gemma4-12b | holístico | 0,60 [0,48; 0,68] | 0,45 [0,28; 0,57] | 0,28 [0,20; 0,36] |
| gemma4-12b | holístico + normas | 0,38 [0,29; 0,60] | 0,30 [0,20; 0,39] | 0,14 [0,09; 0,25] |
| gemma4-12b | holístico (só conformidade) | 0,77 [0,63; 0,84] | 0,55 [0,26; 0,68] | 0,19 [0,13; 0,35] |
| gemma4-12b | holístico por sentença + normas | 0,56 [0,48; 0,63] | 0,50 [0,43; 0,57] | 0,39 [0,32; 0,45] |
| gemma4-12b | holístico só conformidade + por sentença + normas | 0,79 [0,74; 0,84] | 0,69 [0,63; 0,75] | 0,50 [0,39; 0,58] |
| gemma4-12b | por afirmação + regras (proposto) | 0,76 [0,68; 0,85] | 0,69 [0,60; 0,77] | 0,55 [0,43; 0,64] |
| gemma4-12b | RAGAs faithfulness | 0,84 [0,67; 0,89] | 0,68 [0,51; 0,78] | 0,49 [0,36; 0,59] |
| gemma4-12b | MiniCheck | 0,84 [0,72; 0,89] | 0,69 [0,50; 0,79] | 0,48 [0,38; 0,59] |
| llama3.1-8b | holístico | 0,75 [0,67; 0,82] | 0,67 [0,56; 0,75] | 0,55 [0,46; 0,65] |
| llama3.1-8b | holístico + normas | 0,69 [0,61; 0,77] | 0,66 [0,58; 0,73] | 0,58 [0,52; 0,65] |
| llama3.1-8b | holístico (só conformidade) | 0,88 [0,85; 0,92] | 0,82 [0,78; 0,86] | 0,69 [0,64; 0,74] |
| llama3.1-8b | holístico por sentença + normas | 0,91 [0,87; 0,93] | 0,81 [0,75; 0,85] | 0,62 [0,50; 0,70] |
| llama3.1-8b | holístico só conformidade + por sentença + normas | 0,79 [0,72; 0,85] | 0,75 [0,68; 0,80] | 0,66 [0,61; 0,71] |
| llama3.1-8b | por afirmação + regras (proposto) | 0,74 [0,65; 0,83] | 0,66 [0,53; 0,73] | 0,49 [0,36; 0,57] |
| llama3.1-8b | RAGAs faithfulness | 0,92 [0,83; 0,94] | 0,84 [0,75; 0,87] | 0,70 [0,59; 0,75] |
| llama3.1-8b | MiniCheck | 0,84 [0,72; 0,89] | 0,69 [0,50; 0,79] | 0,48 [0,38; 0,59] |
| gpt-oss-20b | holístico | 0,93 [0,92; 0,94] | 0,86 [0,84; 0,88] | 0,73 [0,67; 0,77] |
| gpt-oss-20b | holístico + normas | 0,91 [0,88; 0,93] | 0,81 [0,75; 0,85] | 0,62 [0,50; 0,70] |
| gpt-oss-20b | holístico (só conformidade) | 0,79 [0,66; 0,88] | 0,66 [0,53; 0,76] | 0,44 [0,30; 0,57] |
| gpt-oss-20b | holístico por sentença + normas | 0,94 [0,92; 0,94] | 0,87 [0,85; 0,89] | 0,74 [0,70; 0,77] |
| gpt-oss-20b | holístico só conformidade + por sentença + normas | 0,82 [0,71; 0,88] | 0,65 [0,42; 0,76] | 0,37 [0,25; 0,52] |
| gpt-oss-20b | por afirmação + regras (proposto) | 0,78 [0,64; 0,85] | 0,65 [0,54; 0,76] | 0,52 [0,40; 0,61] |
| gpt-oss-20b | RAGAs faithfulness | 0,85 [0,70; 0,90] | 0,72 [0,55; 0,80] | 0,47 [0,33; 0,60] |
| gpt-oss-20b | MiniCheck | 0,84 [0,72; 0,89] | 0,69 [0,50; 0,79] | 0,48 [0,38; 0,59] |
| claude-haiku-5-5 | holístico | 0,64 [0,56; 0,72] | 0,57 [0,49; 0,64] | 0,44 [0,35; 0,52] |
| claude-haiku-5-5 | holístico + normas | 0,83 [0,67; 0,89] | 0,66 [0,51; 0,78] | 0,51 [0,42; 0,60] |
| claude-haiku-5-5 | holístico (só conformidade) | 0,72 [0,62; 0,79] | 0,59 [0,43; 0,68] | 0,32 [0,21; 0,47] |
| claude-haiku-5-5 | holístico por sentença + normas | 0,81 [0,64; 0,89] | 0,65 [0,56; 0,78] | 0,57 [0,49; 0,65] |
| claude-haiku-5-5 | por afirmação + regras (proposto) | 0,74 [0,66; 0,81] | 0,67 [0,57; 0,74] | 0,54 [0,43; 0,61] |

VPP (fração dos bloqueios que têm erro crítico) e carga de revisão (fração das respostas bloqueadas), pela sensibilidade e pelo falso alarme medidos, em prevalências de erro crítico de 1%, 2% e 5%.

| Modelo | Juiz e ponto | sensibilidade | falso alarme | VPP 1% | VPP 2% | VPP 5% | carga 2% |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | proposto, m = 1 | 0,91 | 0,66 | 0,014 | 0,027 | 0,068 | 0,66 |
| qwen3.5-9b | proposto, FA 0,10 | 0,48 | 0,10 | 0,046 | 0,089 | 0,201 | 0,11 |
| qwen3.5-9b | proposto, FA 0,20 | 0,65 | 0,20 | 0,032 | 0,062 | 0,145 | 0,21 |
| qwen3.5-9b | holístico só conformidade | 0,90 | 0,60 | 0,015 | 0,030 | 0,073 | 0,61 |
| gemma4-12b | proposto, m = 1 | 0,98 | 0,89 | 0,011 | 0,022 | 0,055 | 0,89 |
| gemma4-12b | proposto, FA 0,10 | 0,31 | 0,10 | 0,030 | 0,059 | 0,139 | 0,10 |
| gemma4-12b | proposto, FA 0,20 | 0,45 | 0,20 | 0,022 | 0,044 | 0,106 | 0,20 |
| gemma4-12b | holístico só conformidade | 0,81 | 0,20 | 0,039 | 0,076 | 0,175 | 0,21 |
| llama3.1-8b | proposto, m = 1 | 0,82 | 0,39 | 0,021 | 0,041 | 0,099 | 0,40 |
| llama3.1-8b | proposto, FA 0,10 | 0,34 | 0,10 | 0,034 | 0,065 | 0,153 | 0,10 |
| llama3.1-8b | proposto, FA 0,20 | 0,51 | 0,20 | 0,025 | 0,049 | 0,118 | 0,21 |
| llama3.1-8b | holístico só conformidade | 0,72 | 0,43 | 0,016 | 0,033 | 0,080 | 0,44 |
| gpt-oss-20b | proposto, m = 1 | 0,92 | 0,79 | 0,012 | 0,023 | 0,058 | 0,79 |
| gpt-oss-20b | proposto, FA 0,10 | 0,35 | 0,10 | 0,034 | 0,066 | 0,155 | 0,10 |
| gpt-oss-20b | proposto, FA 0,20 | 0,48 | 0,20 | 0,024 | 0,047 | 0,113 | 0,21 |
| gpt-oss-20b | holístico só conformidade | 0,59 | 0,22 | 0,027 | 0,052 | 0,124 | 0,22 |

Barreira de três saídas do verificador: bloqueia se alguma afirmação é contestada; escala se nenhuma é contestada mas alguma é "insuficiente"; aprova o resto.

| Modelo | sem erro: aprova / escala / bloqueia | erro crítico: aprova / escala / bloqueia | automação (aprova+bloqueia) | FAR-crítico só nos aprovados |
|---|---|---|---|---|
| qwen3.5-9b | 0,19 / 0,15 / 0,66 | 0,07 / 0,02 / 0,91 | 0,92 | 0,07 |
| gemma4-12b | 0,07 / 0,04 / 0,89 | 0,00 / 0,02 / 0,98 | 0,97 | 0,00 |
| llama3.1-8b | 0,37 / 0,24 / 0,39 | 0,11 / 0,07 / 0,82 | 0,86 | 0,11 |
| gpt-oss-20b | 0,11 / 0,10 / 0,79 | 0,01 / 0,07 / 0,92 | 0,91 | 0,01 |
| claude-haiku-5-5 | 0,05 / 0,10 / 0,85 | 0,00 / 0,01 / 0,99 | 0,95 | 0,00 |

## M7. FAR-crítico com a gravidade da anotadora

Fatos críticos: nossos 35, da anotadora 44, união 48.

| Modelo | Juiz | nossa gravidade | anotadora | união | H1 exato (hol. − prop.), anotadora [IC] |
|---|---|---|---|---|---|
| qwen3.5-9b | holístico | 0,02 | 0,02 | 0,02 | 0,03 [-0,03; 0,09] |
| qwen3.5-9b | holístico (só conformidade) | 0,10 | 0,10 | 0,10 |  |
| qwen3.5-9b | holístico por sentença + normas | 0,00 | 0,00 | 0,00 |  |
| qwen3.5-9b | por afirmação + regras (proposto) | 0,09 | 0,08 | 0,08 |  |
| gemma4-12b | holístico | 0,00 | 0,00 | 0,00 | -0,00 [-0,03; 0,02] |
| gemma4-12b | holístico (só conformidade) | 0,19 | 0,20 | 0,21 |  |
| gemma4-12b | holístico por sentença + normas | 0,03 | 0,03 | 0,03 |  |
| gemma4-12b | por afirmação + regras (proposto) | 0,02 | 0,02 | 0,02 |  |
| llama3.1-8b | holístico | 0,02 | 0,03 | 0,03 | 0,25 [0,15; 0,35] |
| llama3.1-8b | holístico (só conformidade) | 0,28 | 0,28 | 0,30 |  |
| llama3.1-8b | holístico por sentença + normas | 0,29 | 0,31 | 0,32 |  |
| llama3.1-8b | por afirmação + regras (proposto) | 0,18 | 0,17 | 0,17 |  |
| gpt-oss-20b | holístico | 0,01 | 0,01 | 0,01 | 0,02 [-0,05; 0,09] |
| gpt-oss-20b | holístico (só conformidade) | 0,41 | 0,42 | 0,44 |  |
| gpt-oss-20b | holístico por sentença + normas | 0,04 | 0,04 | 0,04 |  |
| gpt-oss-20b | por afirmação + regras (proposto) | 0,08 | 0,09 | 0,09 |  |

Respostas com erro crítico: nossa gravidade 135; anotadora 151; união 159.

## Saídas inválidas: como implementado x fail-open (aprova) x fail-closed (bloqueia)

Como implementado: na decisão binária, o holístico com saída inválida fica com aprovada = False (bloqueia); na nota, vale 5 (aprova); no verificador, veredito inválido não contesta (aprova).

| Modelo | Juiz | inválidas | inválidas bloqueadas como implementado | falso alarme (impl. / open / closed) | FAR-crítico (impl. / open / closed) |
|---|---|---|---|---|---|
| claude-haiku-5-5 | holístico | 1 | 1 | 0,84 / 0,84 / 0,84 | 0,00 / 0,00 / 0,00 |
| claude-haiku-5-5 | holístico (só conformidade) | 3 | 3 | 0,39 / 0,39 / 0,39 | 0,14 / 0,16 / 0,14 |
| claude-haiku-5-5 | holístico por sentença | 15 | 15 | 0,93 / 0,86 / 0,93 | 0,00 / 0,03 / 0,00 |
| claude-haiku-5-5 | holístico por sentença + normas | 3 | 3 | 1,00 / 0,98 / 1,00 | 0,00 / 0,00 / 0,00 |
| gemma4-12b | RAGAs faithfulness | 1 | 0 | 0,98 / 0,98 / 0,99 | 0,00 / 0,00 / 0,00 |
| gpt-oss-20b | holístico | 1 | 1 | 0,97 / 0,97 / 0,97 | 0,01 / 0,01 / 0,01 |
| gpt-oss-20b | RAGAs faithfulness | 4 | 0 | 0,97 / 0,97 / 0,98 | 0,01 / 0,01 / 0,00 |
| llama3.1-8b | holístico | 1 | 1 | 0,93 / 0,93 / 0,93 | 0,02 / 0,03 / 0,02 |
| llama3.1-8b | holístico (só conformidade) | 3 | 3 | 0,43 / 0,42 / 0,43 | 0,28 / 0,30 / 0,28 |
| llama3.1-8b | holístico + normas (top-3) | 5 | 5 | 0,93 / 0,93 / 0,93 | 0,02 / 0,05 / 0,02 |
| llama3.1-8b | holístico por sentença | 1 | 1 | 0,96 / 0,96 / 0,96 | 0,00 / 0,00 / 0,00 |
| llama3.1-8b | RAGAs faithfulness | 1 | 0 | 0,93 / 0,93 / 0,93 | 0,00 / 0,00 / 0,00 |
| qwen3.5-9b | holístico (só conformidade) | 1 | 1 | 0,60 / 0,60 / 0,60 | 0,10 / 0,10 / 0,10 |
| qwen3.5-9b | holístico só conformidade + por sentença + normas | 1 | 1 | 0,86 / 0,85 / 0,86 | 0,02 / 0,02 / 0,02 |
| qwen3.5-9b | RAGAs faithfulness | 20 | 0 | 0,91 / 0,91 / 0,99 | 0,04 / 0,04 / 0,00 |

## Sensibilidade do limiar de localização em texto livre (F1 nas respostas com erro)

| Modelo | Juiz | 30% | 40% | 50% |
|---|---|---|---|---|
| qwen3.5-9b | holístico | 0,46 | 0,48 | 0,46 |
| qwen3.5-9b | holístico + normas | 0,53 | 0,57 | 0,60 |
| qwen3.5-9b | holístico (só conformidade) | 0,49 | 0,51 | 0,53 |
| gemma4-12b | holístico | 0,40 | 0,35 | 0,24 |
| gemma4-12b | holístico + normas | 0,58 | 0,58 | 0,43 |
| gemma4-12b | holístico (só conformidade) | 0,48 | 0,52 | 0,45 |
| llama3.1-8b | holístico | 0,33 | 0,30 | 0,27 |
| llama3.1-8b | holístico + normas | 0,22 | 0,21 | 0,18 |
| llama3.1-8b | holístico (só conformidade) | 0,36 | 0,36 | 0,37 |
| gpt-oss-20b | holístico | 0,37 | 0,36 | 0,24 |
| gpt-oss-20b | holístico + normas | 0,44 | 0,41 | 0,25 |
| gpt-oss-20b | holístico (só conformidade) | 0,39 | 0,39 | 0,33 |

## Sensibilidade do Jaccard do alinhamento fim a fim

| Modelo | Jaccard | alinhadas | FAR-crítico resp. | falso alarme resp. | FAR-crít. afirm. |
|---|---|---|---|---|---|
| qwen3.5-9b | 0,4 | 0,90 | 0,06 | 0,70 | 0,29 |
| qwen3.5-9b | 0,5 | 0,83 | 0,06 | 0,70 | 0,33 |
| qwen3.5-9b | 0,6 | 0,75 | 0,06 | 0,70 | 0,39 |
| gemma4-12b | 0,4 | 0,87 | 0,02 | 0,96 | 0,37 |
| gemma4-12b | 0,5 | 0,69 | 0,02 | 0,96 | 0,42 |
| gemma4-12b | 0,6 | 0,54 | 0,02 | 0,96 | 0,50 |
| llama3.1-8b | 0,4 | 0,92 | 0,13 | 0,62 | 0,43 |
| llama3.1-8b | 0,5 | 0,87 | 0,13 | 0,62 | 0,45 |
| llama3.1-8b | 0,6 | 0,77 | 0,13 | 0,62 | 0,50 |
| gpt-oss-20b | 0,4 | 0,90 | 0,07 | 0,70 | 0,37 |
| gpt-oss-20b | 0,5 | 0,82 | 0,07 | 0,70 | 0,40 |
| gpt-oss-20b | 0,6 | 0,70 | 0,07 | 0,70 | 0,43 |
