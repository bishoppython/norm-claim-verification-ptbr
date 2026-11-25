# LLM judges as compliance gates in Brazilian banking (norm-grounded claim-level verification)

Reproduction package for *LLM Judges as Compliance Gates in Brazilian Banking:
Criterion, Output Format and Retrieval Matter More than Claim Decomposition* (submitted to Applied Intelligence).

Code comments and data are in Brazilian Portuguese; the dialogues are synthetic and contain no personal data.

## Contents
| Path | What it is |
|---|---|
| `fontes/` | The 12 norms as collected (with `inventario.csv`: URL, access date, SHA-256), the 409 articles and the bge-m3 embeddings |
| `fatos_norma.jsonl` | 61 norm facts, each with provision, verbatim excerpt, severity and planted errors (84) |
| `dialogos.jsonl` | Main set: 300 stratified synthetic dialogues (seeds 101–103) with claim-level ground truth |
| `piloto.jsonl` | 30-dialogue pilot (seed 1), not used in the analysis |
| `resultados/` | Every judge output (4 models × 8 judges + end-to-end; Claude Haiku 5.5 × 7 judges), logs, prompt caches, `analise.md`/`analise.json` (main analysis), `analise_emenda2.md`/`.json` (amendment 2, localisation, two-level CIs, convex-hull comparison, sensitivity), `concordancia_anotador.md` |
| `anotador/` | Ground-truth validation spreadsheet as filled by the independent annotator (item comments in Portuguese) |
| `auditoria_h5*.csv` | Manual check of 50 holistic problems (first author) and the matching automatic labels |
| `PREREGISTRATION.md` | Preregistration as frozen before the main run, with amendments 1 and 2 and the post-run notes |

## Changes in v1.1.0
- Amendment 2: three holistic variants (compliance-only criterion, per-sentence output, per-sentence output with norms) on all four open models.
- Exploratory run of every judge except the no-retrieval ablation on Claude Haiku 5.5 (Message Batches API; `haiku_lote.py`, prompts and responses in `resultados/haiku_*.jsonl`).
- `analise_emenda2.py`: one localisation measure for all judges, citation accuracy, two-level bootstrap (dialogues × norm facts), exactly matched comparison on the ROC convex hull, H6/H7 tests and the sensitivity analysis without the 15 dialogues that contain ambiguous planted errors.
- Independent validation of the ground truth (`planilha_anotador.py`, `concordancia_anotador.py`).

## Reproducing
Python ≥ 3.10 with `numpy` and `openpyxl` (and `matplotlib` for the figure; `anthropic` only to resend the Haiku batch, which needs an API key). Judges run on a local [Ollama](https://ollama.com) server
(models `qwen3.5:9b`, `gemma4:12b`, `llama3.1:8b`, `gpt-oss:20b`; embeddings `bge-m3`).

```bash
python fatos_norma.py                      # rebuild the facts and check every excerpt against the norm text
python gerar_dialogos.py                   # regenerate dialogos.jsonl (deterministic)
python densa.py --avaliar dialogos.jsonl   # retrieval recall@k
python regras.py --avaliar dialogos.jsonl --oraculo
./rodar_principal.sh                       # all judges (local Ollama; cached prompts are not re-sent)
python analise.py                          # preregistered analysis -> resultados/analise.md
python analise_emenda2.py                  # amendment 2 and block-2 analyses -> resultados/analise_emenda2.md
python concordancia_anotador.py anotador/validacao_gabarito_preenchida.xlsx
python figura_curvas.py                    # Fig. 1
```

The prompt caches (`resultados/cache__*.jsonl`) return the original LLM outputs, so rerunning `rodar_principal.sh`
reproduces the published judge outputs exactly. Ollama is still needed for the query embeddings (`bge-m3`) used by
retrieval. `analise.py` and `metricas.py` need only the files in `resultados/`.

## Licences
Code: MIT (`LICENSE`). Data, norm facts, dialogues and outputs: CC BY 4.0 (`LICENSE-DATA`). The norm texts are
Brazilian official acts, which are not subject to copyright (Law 9,610/1998, art. 8, IV).
