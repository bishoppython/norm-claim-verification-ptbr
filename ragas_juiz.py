"""Baseline RAGAs faithfulness (emenda 3, M1 do parecer simulado da Applied Intelligence).

Roda o Faithfulness do pacote ragas (0.4.4) como foi publicado, com os prompts dele, num modelo
local do Ollama. Único ajuste ao nosso problema: o contexto ("retrieved_contexts") é o mesmo top-3
por afirmação, deduplicado e com até 700 caracteres por artigo, que o juiz holístico por sentença
+ normas recebe (a recuperação usa as afirmações do gabarito, como nos outros juízes).

Saída por diálogo: as afirmações que o RAGAs extraiu, o veredito de cada uma (1 = sustentada pelo
contexto), a nota (fração sustentada) e, para a localização, o alinhamento das afirmações do
gabarito com as extraídas (Jaccard >= 0,5, o mesmo da variante fim a fim).
Decisão: aprova só se todas as afirmações forem sustentadas (nota = 1); a curva ROC usa 1 - nota.

Roda no venv ~/.venvs/ragas (ragas + langchain-ollama):
  ~/.venvs/ragas/bin/python ragas_juiz.py --modelo qwen3.5:9b
**Usa a GPU: só com autorização do Bispo.**
"""
import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
from juizes import Recuperador, alinhar, fmt_normas  # noqa: E402

RES = AQUI / "resultados"
LIMITE_SEG = 1800


def contexto(dialogo, idx, k=3):
    docs, vistos = [], set()
    for a in dialogo["afirmacoes"]:
        for _, d in idx.buscar(a["texto"], k=k):
            if (d["norma"], d["artigo"]) not in vistos:
                vistos.add((d["norma"], d["artigo"])); docs.append(d)
    # um trecho por artigo, no mesmo formato e limite do holístico por sentença + normas
    return [l for l in fmt_normas(docs, limite=700).splitlines()[1:] if l.strip()]


async def julgar(metric, dialogo, ctx):
    row = {"user_input": dialogo["pergunta"], "response": dialogo["resposta"], "retrieved_contexts": ctx}
    t0 = time.time()
    try:
        async def _rodar():
            st = (await metric._create_statements(row, None)).statements
            return st, ((await metric._create_verdicts(row, st, None)).statements if st else [])
        # limite por diálogo (desvio declarado, 27/11/2026): sem ele, uma geração descontrolada no Ollama
        # (o contexto desliza e a geração não termina) trava a fila; estouro = exceção = pior caso.
        # 1.800 s ficam acima do máximo observado antes (878 s no qwen3.5), então não muda o que já rodou.
        st, ver = await asyncio.wait_for(_rodar(), timeout=LIMITE_SEG)
        erro = None
    except Exception as e:  # saída que o ragas não consegue analisar: pior caso (aprovada, nada apontado)
        st, ver, erro = [], [], f"{type(e).__name__}: {str(e)[:200]}"
    seg = time.time() - t0
    afs = [v.statement for v in ver]
    vs = [int(v.verdict) for v in ver]
    nota = (sum(vs) / len(vs)) if vs else None
    mapa = alinhar(afs, dialogo["afirmacoes"]) if afs else [None] * len(dialogo["afirmacoes"])
    por_gold = [None if m is None else (vs[m] == 0) for m in mapa]
    return {"id": dialogo["id"], "juiz": "ragas", "afirmacoes_ragas": afs, "vereditos": vs,
            "motivos": [v.reason for v in ver], "nota": nota, "aprovada": (nota is None) or nota >= 1.0,
            "por_gold": por_gold, "erro": erro, "custo": {"seg": seg}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--dialogos", default="dialogos.jsonl")
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args()

    from langchain_ollama import ChatOllama
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import Faithfulness

    # mesmas opções dos outros juízes: temperatura 0, semente fixa, contexto 8.192, sem raciocínio
    # (gpt-oss no nível mínimo, "low", porque não desliga).
    raciocinio = "low" if a.modelo.startswith("gpt-oss") else False
    llm = ChatOllama(model=a.modelo, temperature=0, seed=42, num_ctx=8192, reasoning=raciocinio)
    metric = Faithfulness(llm=LangchainLLMWrapper(llm))

    idx = Recuperador("hibrida")
    rotulo = re.sub(r"[^a-zA-Z0-9.-]+", "-", a.modelo)
    saida = RES / f"ragas__{rotulo}__oraculo__hibrida__{Path(a.dialogos).stem}.jsonl"
    feitos = {json.loads(l)["id"] for l in saida.open(encoding="utf-8")} if saida.exists() else set()
    dialogos = [json.loads(l) for l in (AQUI / a.dialogos).open(encoding="utf-8")]
    if a.limite:
        dialogos = dialogos[: a.limite]
    pend = [d for d in dialogos if d["id"] not in feitos]
    print(f"ragas / {a.modelo}: {len(pend)} pendentes de {len(dialogos)} -> {saida.name}", flush=True)
    with saida.open("a", encoding="utf-8") as f:
        for i, d in enumerate(pend, 1):
            r = asyncio.run(julgar(metric, d, contexto(d, idx)))
            r["modelo"] = a.modelo
            f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush()
            if i % 10 == 0 or i == len(pend):
                print(f"  {i}/{len(pend)}", flush=True)


if __name__ == "__main__":
    main()
