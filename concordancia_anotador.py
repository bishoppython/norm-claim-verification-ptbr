"""Concordância do segundo anotador (item 1e) com o gabarito.

Lê ../submissao/anotador/validacao_gabarito.xlsx (preenchida) e escreve resultados/concordancia_anotador.md:
  Fatos: % "sim" (correta) e kappa da gravidade (crítica / não crítica) contra o gabarito;
  Erros: % "sim" (contradiz), lista de "não"/"ambíguo" (candidatos à sensibilidade, como o F26);
  Rejeitadas: % das frases contestadas pela IA que o anotador confirma como corretas.
Kappa de Cohen com IC por bootstrap (10.000, semente 7). Requer openpyxl.
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np
from openpyxl import load_workbook

AQUI = Path(__file__).parent
import sys
ARQ = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI.parent / "submissao" / "anotador" / "validacao_gabarito_v2_preenchida.xlsx"


def kappa(a, b):
    cats = sorted(set(a) | set(b))
    a, b = np.array(a), np.array(b)
    po = (a == b).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def linhas(ws):
    cab = [c.value for c in ws[1]]
    return [dict(zip(cab, [c.value for c in r])) for r in ws.iter_rows(min_row=2)]


def main():
    wb = load_workbook(ARQ)
    F = {json.loads(l)["id"]: json.loads(l) for l in (AQUI / "fatos_norma.jsonl").open(encoding="utf-8")}
    L = ["# Concordância do segundo anotador (gerado por concordancia_anotador.py)", ""]
    fa = [r for r in linhas(wb["Fatos"]) if r["Está correta pela norma vigente?"]]
    cont = Counter(r["Está correta pela norma vigente?"] for r in fa)
    L += [f"## Fatos ({len(fa)} preenchidos de {len(F)})", f"- correta: {dict(cont)}"]
    g = [(("critica" if F[r["ID"]]["gravidade"] == "critica" else "nao_critica"),
          ("critica" if r["Gravidade se estivesse errada"] == "crítica" else "nao_critica"))
         for r in fa if r["Gravidade se estivesse errada"]]
    if g:
        a, b = zip(*g)
        rng = np.random.default_rng(7)
        bs = [kappa(*zip(*[g[i] for i in rng.integers(0, len(g), len(g))])) for _ in range(10_000)]
        L.append(f"- gravidade: concordância {np.mean(np.array(a) == np.array(b)):.2f}, kappa {kappa(a, b):.2f} "
                 f"[{np.nanpercentile(bs, 2.5):.2f}; {np.nanpercentile(bs, 97.5):.2f}] (n = {len(g)})")
    L += ["", "### Fatos não marcados como corretos"] + \
         [f"- {r['ID']}: {r['Está correta pela norma vigente?']} — {r.get('Comentário') or ''}" for r in fa
          if r["Está correta pela norma vigente?"] != "sim"]
    er = [r for r in linhas(wb["Erros"]) if r["Contradiz a norma?"]]
    L += ["", f"## Erros ({len(er)} preenchidos de 84)", f"- contradiz: {dict(Counter(r['Contradiz a norma?'] for r in er))}",
          "", "### Erros não confirmados (candidatos à sensibilidade)"] + \
         [f"- {r['ID do fato']}: \"{r['Versão errada (a avaliar)']}\" → {r['Contradiz a norma?']} — {r.get('Comentário') or ''}"
          for r in er if r["Contradiz a norma?"] != "sim"]
    rj = [r for r in linhas(wb["Rejeitadas"]) if r["A frase está correta?"]]
    c = Counter(r["A frase está correta?"] for r in rj)
    L += ["", f"## Rejeitadas pela IA ({len(rj)} preenchidas)", f"- anotador: {dict(c)}",
          f"- falsos alarmes confirmados (frase correta): {c.get('sim', 0)}/{len(rj)}", "",
          "### Frases que o anotador considera erradas ou ambíguas"] + \
         [f"- {r['Frase (considerada correta)']} → {r['A frase está correta?']} — {r.get('Comentário') or ''}"
          for r in rj if r["A frase está correta?"] != "sim"]
    (AQUI / "resultados" / "concordancia_anotador.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
