#!/usr/bin/env bash
# Emenda 4 (28/11/2026; parecer do Prof. Carlo): frases compostas. Registrada antes de rodar.
# Ordem por prioridade: C1 e C2 (juiz configurado, recomendação atual) nos 4 modelos; depois V (verificador fim a fim).
set -u
cd "$(dirname "$0")"
MODELOS="${MODELOS:-qwen3.5:9b gemma4:12b llama3.1:8b gpt-oss:20b}"
log() { echo "=== $* $(date '+%d/%m %H:%M:%S')"; }
python3 compor_frases.py
for M in $MODELOS; do
  log "$M C1 (frases compostas, recuperação pela afirmação)"
  python3 juizes.py --juiz holistico_conformidade_sentencas_normas --modelo "$M" --dialogos dialogos_compostos.jsonl --segmentacao pontuacao || echo "FALHOU $M C1"
  log "$M C2 (frases compostas, recuperação pela frase)"
  python3 juizes.py --juiz holistico_conformidade_sentencas_normas --modelo "$M" --dialogos dialogos_compostos.jsonl --segmentacao pontuacao --consulta frase || echo "FALHOU $M C2"
done
for M in $MODELOS; do
  log "$M V (verificador fim a fim nas frases compostas)"
  python3 juizes.py --juiz afirmacao_regras --modelo "$M" --dialogos dialogos_compostos.jsonl --segmentacao llm || echo "FALHOU $M V"
done
log "fim"
