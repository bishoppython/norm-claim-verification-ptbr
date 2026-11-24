#!/usr/bin/env bash
# Piloto autorizado pelo Bispo em 23/11/2026: qwen3.5:9b, 5 juízes, 30 diálogos, recuperação híbrida.
set -u
cd "$(dirname "$0")"
M=qwen3.5:9b
for J in holistico holistico_normas afirmacao_regras afirmacao afirmacao_sem_rag; do
  echo "=== $J $(date +%H:%M:%S)"
  python3 juizes.py --juiz "$J" --modelo "$M" --dialogos piloto.jsonl --recuperacao hibrida || echo "FALHOU $J"
done
echo "=== fim $(date +%H:%M:%S)"
