"""M2 (exploratório, emenda 3): por que os holísticos rejeitam respostas SEM erro?

Classifica cada problema listado pelo holístico (e pelo holístico só conformidade, para contraste) nas
120 respostas sem erro, em uma de cinco classes:
  contradicao  diz que uma afirmação está errada, é ilegal ou contraria a norma
  omissao      falta informação, ressalva, condição ou detalhe (completude)
  relevancia   a resposta foge da pergunta ou traz informação que não foi pedida
  estilo       tom, clareza, linguagem, formalidade, organização
  outro        nada disso
Classificador: qwen3.5:9b, temperatura 0, semente 42 (mesmo cliente e cache dos juízes). A conferência manual
(60 problemas) é a de preparar_planilhas.py.

Uso: python3 classificar_motivos.py [--modelo-classificador qwen3.5:9b]
**Usa a GPU: só com autorização do Bispo** (autorizada em 25/11/2026 com a emenda 3).
"""
import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

from juizes import Cache, Ollama

AQUI = Path(__file__).parent
RES = AQUI / "resultados"
MODELOS = ["qwen3.5-9b", "gemma4-12b", "llama3.1-8b", "gpt-oss-20b"]
JUIZES = ["holistico", "holistico_conformidade"]
CLASSES = ["contradicao", "omissao", "relevancia", "estilo", "outro"]

P = """Um auditor avaliou a resposta de um atendente bancário e apontou o problema abaixo.
Classifique o PROBLEMA APONTADO (não a resposta) em uma classe:
- contradicao: diz que alguma afirmação está errada, é ilegal ou contraria a norma/lei
- omissao: diz que falta informação, ressalva, condição, prazo ou detalhe (resposta incompleta)
- relevancia: diz que a resposta foge da pergunta ou traz informação que não foi pedida
- estilo: tom, clareza, linguagem, formalidade, organização ou empatia
- outro: nada disso

Pergunta do cliente: {pergunta}
Problema apontado: {problema}
Responda em JSON: {{"classe": "contradicao|omissao|relevancia|estilo|outro"}}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo-classificador", default="qwen3.5:9b")
    a = ap.parse_args()
    gab = {d["id"]: d for d in (json.loads(l) for l in (AQUI / "dialogos.jsonl").open(encoding="utf-8"))}
    modelo = Cache(Ollama(a.modelo_classificador)); modelo.nome = modelo.modelo.nome
    saida = RES / "motivos_rejeicao.jsonl"
    feitos = {(x["juiz"], x["modelo"], x["id"], x["k"]) for x in (json.loads(l) for l in saida.open(encoding="utf-8"))} \
        if saida.exists() else set()
    with saida.open("a", encoding="utf-8") as f:
        for j in JUIZES:
            for m in MODELOS:
                arq = RES / f"{j}__{m}__oraculo__hibrida__dialogos.jsonl"
                for r in (json.loads(l) for l in arq.open(encoding="utf-8")):
                    d = gab[r["id"]]
                    if d["n_erros"] or r["aprovada"]:  # só respostas sem erro que o juiz rejeitou
                        continue
                    for k, prob in enumerate((r.get("bruto") or {}).get("problemas") or []):
                        if (j, m, r["id"], k) in feitos:
                            continue
                        out, _ = modelo.gerar(P.format(pergunta=d["pergunta"], problema=prob))
                        c = str(out.get("classe", "outro")).strip().lower()
                        c = next((x for x in CLASSES if c.startswith(x[:5])), "outro")
                        f.write(json.dumps({"juiz": j, "modelo": m, "id": r["id"], "k": k, "problema": prob, "classe": c},
                                           ensure_ascii=False) + "\n"); f.flush()
    X = [json.loads(l) for l in saida.open(encoding="utf-8")]
    for j in JUIZES:
        for m in MODELOS:
            c = Counter(x["classe"] for x in X if x["juiz"] == j and x["modelo"] == m)
            n = sum(c.values())
            print(j, m, n, {k: round(c[k] / n, 2) for k in CLASSES} if n else {})
    # a amostra da conferência manual sai de preparar_planilhas.py (../submissao/anotador/motivos_rotulador.xlsx);
    # a comparação usa motivos_chave.csv (modelo, id, k) contra este arquivo.


if __name__ == "__main__":
    main()
