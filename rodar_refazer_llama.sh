#!/usr/bin/env bash
# Retoma os juízes do llama3.1 interrompidos por timeout na rodada principal (23/11/2026).
# Espera a rodada principal terminar para não dividir a GPU. O juizes.py retoma de onde parou.
cd "$(dirname "$0")"
until grep -q "^=== fim " resultados/principal.log; do sleep 60; done
for J in holistico holistico_normas; do
  echo "=== refazer llama3.1:8b $J $(date '+%d/%m %H:%M:%S')"
  python3 juizes.py --juiz "$J" --modelo llama3.1:8b --dialogos dialogos.jsonl --recuperacao hibrida || echo "FALHOU $J"
done
echo "=== fim refazer $(date '+%d/%m %H:%M:%S')"
