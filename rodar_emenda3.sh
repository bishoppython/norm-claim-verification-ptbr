#!/usr/bin/env bash
# Emenda 3 (25/11/2026; GPU autorizada pelo Bispo em 25/11: "Tudo, inclusive RAGAs").
# Registrada antes de rodar: commit 7dfaed7c (vault) e 41cb0dc (GitHub, push 25/11/2026 00:09 -03).
# Ordem por prioridade do parecer: M3, M9, MiniCheck, M4, fim a fim (M8), RAGAs (M1).
set -u
cd "$(dirname "$0")"
MODELOS="${MODELOS:-qwen3.5:9b llama3.1:8b gemma4:12b gpt-oss:20b}"
log() { echo "=== $* $(date '+%d/%m %H:%M:%S')"; }
for M in $MODELOS; do
  log "$M holistico_conformidade_sentencas_normas (M3)"
  python3 juizes.py --juiz holistico_conformidade_sentencas_normas --modelo "$M" || echo "FALHOU $M M3"
done
for M in $MODELOS; do
  log "$M afirmacao_regras oraculo (M9)"
  python3 juizes.py --juiz afirmacao_regras --modelo "$M" --recuperacao oraculo || echo "FALHOU $M M9"
done
log "bespoke-minicheck (M1)"
python3 juizes.py --juiz minicheck --modelo bespoke-minicheck || echo "FALHOU minicheck"
for M in $MODELOS; do
  log "$M holistico_normas_k3 (M4)"
  python3 juizes.py --juiz holistico_normas_k3 --modelo "$M" || echo "FALHOU $M M4"
done
for M in llama3.1:8b gemma4:12b gpt-oss:20b; do
  log "$M afirmacao_regras fim a fim (M8)"
  python3 juizes.py --juiz afirmacao_regras --modelo "$M" --segmentacao llm || echo "FALHOU $M M8"
done
for M in $MODELOS; do
  log "$M ragas (M1)"
  ~/.venvs/ragas/bin/python ragas_juiz.py --modelo "$M" 2>&1 | grep -v -i "warn\|deprecat\|from ragas\|metric = " || true
done
log "fim"
