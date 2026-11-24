"""Recuperação da norma para cada afirmação (componente do verificador).

BM25 puro em Python, sem dependências, sobre fontes/artigos.jsonl (a unidade é
o artigo). Artigos duplicados (redação antiga que sobrou) ficam de fora.

Também avalia a recuperação contra o gabarito: para cada afirmação dos
diálogos, o artigo-fonte do fato está entre os k primeiros? (recall@k).
Não usa LLM nem GPU.

Uso:
  python recuperar.py --avaliar dialogos.jsonl
"""
import argparse
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent

STOP = set("""a o e é de do da dos das em no na nos nas um uma uns umas que se por pra para com
sem ao aos à às ou mais menos como seu sua seus suas te você vocês voce eu me meu minha isso esse essa
este esta aqui lá ja já só so tá ta não nao sim também tambem olha ah além alem disso outra coisa importante
saber pode podem tem ter tiver ser foi vai vão quando qual quais até ate depois antes mas porque então entao
lhe nem há ha dá da""".split())

# sinônimos de linguagem de atendente -> termos da norma (expansão leve da consulta)
EXPANSAO = {
    "grátis": "gratuito vedada cobrança tarifas", "gratis": "gratuito vedada cobrança tarifas",
    "caixa eletrônico": "terminal autoatendimento", "aplicativo": "internet meios eletrônicos",
    "app": "internet meios eletrônicos", "empréstimo": "operação crédito", "parcela": "prestação",
    "quitar": "liquidação antecipada", "consignado": "desconto folha pagamento consignação",
    "aposentado": "benefícios aposentadoria previdência", "dados": "dados pessoais tratamento titular",
    "levar o empréstimo pra outro banco": "portabilidade", "demitido": "verbas rescisórias",
    "atraso": "mora inadimplemento", "desistir": "desistir contrato arrependimento",
}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def tokens(s: str) -> list[str]:
    s = fold(s)
    return [t for t in re.findall(r"[a-z0-9]+", s) if t not in STOP and len(t) > 1]


def expandir(consulta: str) -> str:
    c = consulta.lower()
    extra = [v for k, v in EXPANSAO.items() if k in c]
    return consulta + " " + " ".join(extra)


class BM25:
    def __init__(self, docs: list[dict], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.toks = [tokens(d["texto"]) for d in docs]
        self.k1, self.b = k1, b
        self.avg = sum(map(len, self.toks)) / len(self.toks)
        df = Counter(t for ts in self.toks for t in set(ts))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.tf = [Counter(ts) for ts in self.toks]

    def buscar(self, consulta: str, k: int = 5) -> list[tuple[float, dict]]:
        q = tokens(expandir(consulta))
        notas = []
        for i, tf in enumerate(self.tf):
            L = len(self.toks[i])
            s = 0.0
            for t in q:
                if t in tf:
                    f = tf[t]
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * L / self.avg))
            notas.append((s, i))
        notas.sort(reverse=True)
        return [(s, self.docs[i]) for s, i in notas[:k]]


def carregar_indice() -> BM25:
    docs = [json.loads(l) for l in (AQUI / "fontes" / "artigos.jsonl").open(encoding="utf-8")]
    docs = [d for d in docs if not d["duplicado"]]
    return BM25(docs)


def avaliar(arquivo: str, ks=(1, 3, 5, 10)) -> dict:
    idx = carregar_indice()
    afs = [a for l in (AQUI / arquivo).open(encoding="utf-8") for a in json.loads(l)["afirmacoes"]]
    acertos = {k: 0 for k in ks}
    por_norma = Counter()
    erro_norma = Counter()
    for a in afs:
        res = idx.buscar(a["texto"], k=max(ks))
        alvo = (a["norma"], a["artigo"])
        pos = next((i for i, (_, d) in enumerate(res) if (d["norma"], d["artigo"]) == alvo), None)
        for k in ks:
            acertos[k] += pos is not None and pos < k
        por_norma[a["norma"]] += 1
        if pos is None or pos >= 5:
            erro_norma[a["norma"]] += 1
    out = {f"recall@{k}": round(acertos[k] / len(afs), 3) for k in ks}
    out["n"] = len(afs)
    out["falha@5_por_norma"] = {n: f"{erro_norma[n]}/{por_norma[n]}" for n in por_norma}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--avaliar", default="dialogos.jsonl")
    print(json.dumps(avaliar(ap.parse_args().avaliar), ensure_ascii=False, indent=1))
