"""Recuperação densa (bge-m3 via Ollama) e híbrida (BM25 + densa por RRF).

Embeddings dos artigos ficam em cache (fontes/emb_<modelo>.npz). Usa GPU (Ollama).

Uso:
  python densa.py --avaliar dialogos.jsonl     # recall@k de BM25, densa e híbrida
"""
import argparse
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np

from recuperar import carregar_indice

AQUI = Path(__file__).parent
MODELO = "bge-m3"
RRF_K = 60


def embed(textos: list[str], modelo=MODELO, lote=16) -> np.ndarray:
    vs = []
    for i in range(0, len(textos), lote):
        corpo = {"model": modelo, "input": textos[i:i + lote], "truncate": True}
        req = urllib.request.Request("http://localhost:11434/api/embed", data=json.dumps(corpo).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=900) as r:
            vs += json.loads(r.read())["embeddings"]
    m = np.array(vs, dtype=np.float32)
    return m / np.linalg.norm(m, axis=1, keepdims=True)


def trechos(texto: str, alvo=700) -> list[str]:
    """Divide o artigo em parágrafos/incisos (quebra antes de "§", "I -", "a)") e
    junta pedaços pequenos até ~alvo caracteres. O caput vai como prefixo curto de
    cada trecho, para o trecho não perder o assunto do artigo."""
    t = re.sub(r"\s+", " ", texto).strip()
    partes = re.split(r"\s(?=§ ?\d|[IVXL]+ ?[-–] |[a-z]\) )", t)
    caput = partes[0][:250]
    out, atual = [], ""
    for p in partes:
        if len(atual) + len(p) > alvo and atual:
            out.append(atual); atual = ""
        atual = (atual + " " + p).strip()
    if atual:
        out.append(atual)
    return [o if o.startswith(caput[:40]) else caput + " … " + o for o in out]


class Densa:
    """Índice denso; com chunk=True o artigo vira vários trechos e a nota do artigo
    é a do seu melhor trecho (max)."""

    def __init__(self, docs: list[dict], modelo=MODELO, chunk=False):
        self.docs, self.modelo, self.chunk = docs, modelo, chunk
        cache = AQUI / "fontes" / f"emb_{modelo}{'_chunk' if chunk else ''}.npz"
        textos, dono = [], []
        for i, d in enumerate(docs):
            ts = trechos(d["texto"]) if chunk else [d["texto"]]
            textos += ts; dono += [i] * len(ts)
        self.dono = np.array(dono)
        chaves = [f"{docs[i]['norma']}|{docs[i]['artigo']}|{docs[i]['ordem']}|{j}" for j, i in enumerate(dono)]
        if cache.exists():
            z = np.load(cache, allow_pickle=False)
            if list(z["chaves"]) == chaves:
                self.M = z["M"]
                return
        self.M = embed(textos, modelo)
        np.savez(cache, M=self.M, chaves=np.array(chaves))

    def ranking(self, qv: np.ndarray, k: int) -> list[int]:
        s = self.M @ qv
        melhor = np.full(len(self.docs), -9.0, dtype=np.float32)
        np.maximum.at(melhor, self.dono, s)
        return list(np.argsort(-melhor)[:k])


def rrf(*rankings, n=50) -> list[int]:
    c = Counter()
    for r in rankings:
        for p, i in enumerate(r):
            c[i] += 1 / (RRF_K + p + 1)
    return [i for i, _ in c.most_common(n)]


def avaliar(arquivo: str, ks=(1, 3, 5, 10)):
    bm = carregar_indice()
    de = Densa(bm.docs)
    dc = Densa(bm.docs, chunk=True)
    afs = [a for l in (AQUI / arquivo).open(encoding="utf-8") for a in json.loads(l)["afirmacoes"]]
    unicos = sorted({a["texto"] for a in afs})
    Q = dict(zip(unicos, embed(unicos)))
    pos_doc = {(d["norma"], d["artigo"]): i for i, d in enumerate(bm.docs)}
    acc = {m: Counter() for m in ("bm25", "densa", "hibrida", "densa_trechos", "hibrida_trechos")}
    for a in afs:
        alvo = pos_doc[(a["norma"], a["artigo"])]
        r_bm = [bm.docs.index(d) for _, d in bm.buscar(a["texto"], k=50)]
        r_de = de.ranking(Q[a["texto"]], 50)
        r_dc = dc.ranking(Q[a["texto"]], 50)
        r_hi, r_hc = rrf(r_bm, r_de), rrf(r_bm, r_dc)
        for nome, r in (("bm25", r_bm), ("densa", r_de), ("hibrida", r_hi),
                        ("densa_trechos", r_dc), ("hibrida_trechos", r_hc)):
            for k in ks:
                acc[nome][k] += alvo in r[:k]
    n = len(afs)
    return {nome: {f"recall@{k}": round(c[k] / n, 3) for k in ks} for nome, c in acc.items()} | {"n": n}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--avaliar", default="dialogos.jsonl")
    print(json.dumps(avaliar(ap.parse_args().avaliar), indent=1))
