# Norm-grounded claim-level verification of LLM answers in Brazilian banking

Reproduction package for *Norm-Grounded Claim-Level Verification of LLM Answers in Brazilian Banking:
Holistic Judges Can Rank but Cannot Point to the Error* (submitted to Applied Intelligence).

Code comments and data are in Brazilian Portuguese; the dialogues are synthetic and contain no personal data.

## Contents
| Path | What it is |
|---|---|
| `fontes/` | The 12 norms as collected (with `inventario.csv`: URL, access date, SHA-256), the 409 articles and the bge-m3 embeddings |
| `fatos_norma.jsonl` | 61 norm facts, each with provision, verbatim excerpt, severity and planted errors (84) |
| `dialogos.jsonl` | Main set: 300 stratified synthetic dialogues (seeds 101–103) with claim-level ground truth |
| `piloto.jsonl` | 30-dialogue pilot (seed 1), not used in the analysis |
| `resultados/` | Every judge output (4 models × 5 judges + end-to-end), logs, prompt caches, `analise.md`/`analise.json` |
| `PREREGISTRATION.md` | Preregistration as frozen before the main run, with amendment 1 and the post-run notes |

## Reproducing
Python ≥ 3.10 with `numpy` (and `matplotlib` for the figure). Judges run on a local [Ollama](https://ollama.com) server
(models `qwen3.5:9b`, `gemma4:12b`, `llama3.1:8b`, `gpt-oss:20b`; embeddings `bge-m3`).

```bash
python fatos_norma.py                      # rebuild the facts and check every excerpt against the norm text
python gerar_dialogos.py                   # regenerate dialogos.jsonl (deterministic)
python densa.py --avaliar dialogos.jsonl   # retrieval recall@k
python regras.py --avaliar dialogos.jsonl --oraculo
./rodar_principal.sh                       # all judges (local Ollama; cached prompts are not re-sent)
python analise.py                          # preregistered analysis -> resultados/analise.md
python figura_curvas.py                    # Fig. 1
```

The prompt caches (`resultados/cache__*.jsonl`) return the original LLM outputs, so rerunning `rodar_principal.sh`
reproduces the published judge outputs exactly. Ollama is still needed for the query embeddings (`bge-m3`) used by
retrieval. `analise.py` and `metricas.py` need only the files in `resultados/`.

## Licences
Code: MIT (`LICENSE`). Data, norm facts, dialogues and outputs: CC BY 4.0 (`LICENSE-DATA`). The norm texts are
Brazilian official acts, which are not subject to copyright (Law 9,610/1998, art. 8, IV).
