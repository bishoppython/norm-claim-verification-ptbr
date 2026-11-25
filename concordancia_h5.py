"""Concordância entre o rótulo do autor (auditoria_h5.csv) e o automático (auditoria_h5_auto.csv). H5."""
import collections
import csv
from math import sqrt
from pathlib import Path

AQUI = Path(__file__).parent
CATS = ["erro", "certa", "outro"]
norm = lambda x: x.strip().lower().replace("ã", "a")


def wilson(k, n, z=1.96):
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


A = list(csv.reader((AQUI / "auditoria_h5.csv").open(encoding="utf-8")))[1:]
B = {r["n"]: r["rotulo_auto"] for r in csv.DictReader((AQUI / "auditoria_h5_auto.csv").open(encoding="utf-8"))}
pares = [(norm(a[4]), B[a[0]], norm(a[5])) for a in A]
N = len(pares)
po = sum(x == y for x, y, _ in pares) / N
pa = collections.Counter(x for x, _, _ in pares)
pb = collections.Counter(y for _, y, _ in pares)
pe = sum(pa[c] * pb[c] for c in CATS) / N ** 2
print(f"n = {N}; concordância {po:.2f}; kappa de Cohen {(po - pe) / (1 - pe):.2f}")
print("matriz (linhas = autor, colunas = automático):", CATS)
for x in CATS:
    print(f"  {x:6}", [sum(1 for a, b, _ in pares if a == x and b == y) for y in CATS])
for c in CATS:
    lo, hi = wilson(pa[c], N)
    print(f"autor {c:6} {pa[c]:2}/{N} = {pa[c] / N:.2f} [IC Wilson {lo:.2f}; {hi:.2f}]  automático {pb[c]}/{N}")
m = collections.Counter(z for x, _, z in pares if x == "erro")
print("motivo certo (quando erro):", dict(m))
