#!/usr/bin/env bash
# Emenda 2 (24/11/2026; GPU autorizada pelo Bispo em 24/11: "Sim autorizo"). Sugestões do orientador:
# 1a holístico com saída por sentença (sem normas e com o mesmo top-3 por afirmação do verificador);
# 1c holístico com prompt restrito à conformidade. 4 modelos x 300 diálogos. Cache por prompt.
set -u
cd "$(dirname "$0")"
MODELOS="${MODELOS:-qwen3.5:9b llama3.1:8b gemma4:12b gpt-oss:20b}"
for M in $MODELOS; do
  for J in holistico_conformidade holistico_sentencas holistico_sentencas_normas; do
    echo "=== $M $J $(date '+%d/%m %H:%M:%S')"
    python3 juizes.py --juiz "$J" --modelo "$M" --dialogos dialogos.jsonl --recuperacao hibrida || echo "FALHOU $M $J"
  done
done
echo "=== fim $(date '+%d/%m %H:%M:%S')"
