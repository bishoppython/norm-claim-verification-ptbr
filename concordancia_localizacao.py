"""M7-localização (exploratório, emenda 3): rotulador independente (anotador com formação jurídica) da H5.

Lê ../submissao/anotador/localizacao_rotulador.xlsx (100 problemas; o rotulador diz a que afirmação o problema
se refere — coluna E — e se diz que ela está errada — coluna F) e a chave localizacao_chave.csv (afirmações
erradas do gabarito). Categoria do rotulador, no esquema da auditoria do autor:
  erro  = refere-se a pelo menos uma afirmação errada do gabarito
  certa = refere-se só a afirmações corretas
  outro = E = 0
Compara (a) com o autor nos 50 itens em comum (auditoria_h5.csv) e (b) com a medida automática (sobreposição de
tokens >= 0,4, a mesma de auditoria_h5.py) nos 100. Saída: resultados/localizacao_concordancia.json.
Roda com ~/.venvs/ragas/bin/python (openpyxl).
"""
import csv
import json
import re
from collections import Counter
from math import sqrt
from pathlib import Path

from openpyxl import load_workbook

import metricas as M

AQUI = Path(__file__).parent
ANOT = AQUI.parent / "submissao" / "anotador"
CATS = ["erro", "certa", "outro"]
GAB = M.carregar_gabarito()
norm = lambda x: str(x or "").strip().lower().replace("ã", "a")


def kappa(a, b, cats):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b); pe = sum(ca[c] * cb[c] for c in cats) / n ** 2
    return round((po - pe) / (1 - pe), 3), round(po, 3)


def wilson(k, n, z=1.96):
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def auto(d, p):
    tp = M._tok(p); bate = lambda af: af and len(af & tp) / len(af) >= 0.4
    if any(bate(M._tok(a["texto"])) for a in d["afirmacoes"] if not a["correta"]):
        return "erro"
    return "certa" if any(bate(M._tok(a["texto"])) for a in d["afirmacoes"] if a["correta"]) else "outro"


def conf(a, b):
    return {x: {y: sum(1 for u, v in zip(a, b) if u == x and v == y) for y in CATS} for x in CATS}


def main():
    chave = {int(r["n"]): r for r in csv.DictReader((ANOT / "localizacao_chave.csv").open(encoding="utf-8"))}
    ws = load_workbook(ANOT / "localizacao_rotulador.xlsx")["Itens"]
    autor = {int(r[0]): norm(r[4]) for r in csv.reader((AQUI / "auditoria_h5.csv").open(encoding="utf-8")) if r[0].isdigit()}
    autos_velhos = {int(r["n"]): r["rotulo_auto"] for r in csv.DictReader((AQUI / "auditoria_h5_auto.csv").open(encoding="utf-8"))}
    itens, invalidos = [], []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        n = int(row[0]); k = chave[n]
        refs = {int(x) for x in re.findall(r"\d+", str(row[4] if row[4] is not None else ""))} - {0}
        diz = norm(row[5])
        erradas = {int(x) for x in k["afirmacoes_erradas"].split(";") if x}
        if row[4] is None or diz not in ("sim", "nao", "na"):
            invalidos.append(n)
        cat = "outro" if not refs else ("erro" if refs & erradas else "certa")
        na = k["n_na_auditoria_do_autor"]
        itens.append({"n": n, "origem": k["origem"], "n_autor": int(na) if na else None, "juiz": k["juiz"],
                      "modelo": k["modelo"], "cat": cat, "diz_errada": diz,
                      "auto": autos_velhos[int(na)] if na else auto(GAB[k["id"]], str(row[3]))})
    N = len(itens); c = Counter(x["cat"] for x in itens)
    acusa_certa = sum(1 for x in itens if x["cat"] == "certa" and x["diz_errada"] == "sim")
    erro_diz = sum(1 for x in itens if x["cat"] == "erro" and x["diz_errada"] == "sim")
    com = [x for x in itens if x["n_autor"]]
    ra, au = [x["cat"] for x in com], [autor[x["n_autor"]] for x in com]
    out = {"n": N, "invalidos": invalidos,
           "rotulador": {k2: {"n": c[k2], "prop": round(c[k2] / N, 3), "ic95": wilson(c[k2], N)} for k2 in CATS},
           "erro_e_diz_errada": {"n": erro_diz, "ic95": wilson(erro_diz, N)},
           "certa_e_diz_errada": {"n": acusa_certa, "ic95": wilson(acusa_certa, N)},
           "rotulador_x_autor_50": dict(zip(["kappa", "acordo"], kappa(ra, au, CATS)), confusao_rot_x_autor=conf(ra, au)),
           "rotulador_x_auto_100": dict(zip(["kappa", "acordo"], kappa([x["cat"] for x in itens], [x["auto"] for x in itens], CATS)),
                                        confusao_rot_x_auto=conf([x["cat"] for x in itens], [x["auto"] for x in itens])),
           "por_origem": {o: dict(Counter(x["cat"] for x in itens if x["origem"] == o)) for o in ("auditoria_autor", "nova")},
           "por_juiz": {j: dict(Counter(x["cat"] for x in itens if x["juiz"] == j)) for j in sorted({x["juiz"] for x in itens})}}
    (AQUI / "resultados" / "localizacao_concordancia.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
