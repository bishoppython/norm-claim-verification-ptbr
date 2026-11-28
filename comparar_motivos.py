"""M2 (exploratório, emenda 3): concordância entre a conferência manual do autor (motivos_rotulador.xlsx,
60 problemas, cega a modelo e juiz) e o classificador automático (resultados/motivos_rejeicao.jsonl).
Junta pela chave (juiz, modelo, id, k) de ../submissao/anotador/motivos_chave.csv.
Saída: resultados/motivos_concordancia.json. Roda com ~/.venvs/ragas/bin/python (openpyxl).
"""
import csv
import json
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

AQUI = Path(__file__).parent
RES = AQUI / "resultados"
ANOT = AQUI.parent / "submissao" / "anotador"
CLASSES = ["contradicao", "omissao", "relevancia", "estilo", "outro"]


def kappa(a, b, classes):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[c] * cb[c] for c in classes) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, po


def main():
    ws = load_workbook(ANOT / "motivos_rotulador.xlsx")["Itens"]
    manual = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        c = str(row[4] or "").strip().lower()
        c = next((x for x in CLASSES if c.startswith(x[:5])), c)
        manual[int(row[0])] = c
    chave = {int(r["n"]): (r["juiz"], r["modelo"], r["id"], int(r["k"]))
             for r in csv.DictReader((ANOT / "motivos_chave.csv").open(encoding="utf-8"))}
    auto = {(x["juiz"], x["modelo"], x["id"], x["k"]): x["classe"]
            for x in map(json.loads, (RES / "motivos_rejeicao.jsonl").open(encoding="utf-8"))}
    vazios = [n for n, c in manual.items() if c not in CLASSES]
    pares = [(manual[n], auto[chave[n]]) for n in sorted(manual) if manual[n] in CLASSES and chave[n] in auto]
    faltam = [n for n in sorted(manual) if chave[n] not in auto]
    a, b = zip(*pares)
    k, po = kappa(a, b, CLASSES)
    # binário: omissão contra o resto (a afirmação central do texto)
    kb, pob = kappa(["o" if x == "omissao" else "-" for x in a], ["o" if x == "omissao" else "-" for x in b], ["o", "-"])
    conf = {m: {c: sum(1 for x, y in pares if x == m and y == c) for c in CLASSES} for m in CLASSES}
    out = {"n": len(pares), "sem_rotulo_manual": vazios, "sem_classe_auto": faltam,
           "acordo": round(po, 3), "kappa": round(k, 3),
           "omissao_vs_resto": {"acordo": round(pob, 3), "kappa": round(kb, 3)},
           "dist_manual": {c: a.count(c) for c in CLASSES}, "dist_auto": {c: b.count(c) for c in CLASSES},
           "confusao_manual_x_auto": conf}
    (RES / "motivos_concordancia.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
