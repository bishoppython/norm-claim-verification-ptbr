#!/usr/bin/env bash
# Rodada principal (autorizada pelo Bispo em 23/11/2026: "execute o que for necessário").
# 4 famílias de modelos já instaladas; 5 juízes com segmentação do gabarito; extração por LLM
# (fim a fim) só no qwen, como análise secundária. Cache por prompt em resultados/cache__*.jsonl.
set -u
cd "$(dirname "$0")"
MODELOS="${MODELOS:-qwen3.5:9b gemma4:12b llama3.1:8b gpt-oss:20b}"
for M in $MODELOS; do
  for J in afirmacao_regras holistico afirmacao holistico_normas afirmacao_sem_rag; do
    echo "=== $M $J $(date '+%d/%m %H:%M:%S')"
    python3 juizes.py --juiz "$J" --modelo "$M" --dialogos dialogos.jsonl --recuperacao hibrida || echo "FALHOU $M $J"
  done
done
echo "=== fim-a-fim qwen3.5:9b $(date '+%d/%m %H:%M:%S')"
python3 juizes.py --juiz afirmacao_regras --modelo qwen3.5:9b --dialogos dialogos.jsonl --recuperacao hibrida --segmentacao llm || echo "FALHOU fim-a-fim"
echo "=== fim $(date '+%d/%m %H:%M:%S')"
