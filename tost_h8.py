"""Exploratório (pós-parecer, NÃO pré-registrado): teste de equivalência (TOST) do juiz configurado
(holístico só conformidade + por sentença + normas) contra o verificador, por modelo.

TOST no nível 0,05 = IC 90% bootstrap da diferença inteiramente dentro de [−δ, +δ]. Reporta o IC 90% e a
menor margem δ que o IC admite (max |limite|), para F1 de localização (dois níveis, diálogo × fato) e para
FAR-crítico no falso alarme exatamente pareado (por diálogo). Saída: resultados/tost_h8.json e .md.
Roda com ~/.venvs/ragas/bin/python.
"""
import json

import numpy as np

import analise_emenda2 as A
import analise_emenda3 as E

J8, JV = "holistico_conformidade_sentencas_normas", "afirmacao_regras"


def ic90(b):
    b = np.asarray(b); b = b[~np.isnan(b)]
    return float(np.percentile(b, 5)), float(np.percentile(b, 95))


def far_boot(vh, vp):
    um = np.ones(len(E.IDS)); W = E.WD
    fa_b, fc_b = E.taxas(vp, W)
    ts = np.unique(vh["susp"]); Ind = (vh["susp"][:, None] >= ts[None, :]).astype(float)
    fb = ((W * vh["limpo"]) @ Ind) / np.expand_dims(W @ vh["limpo"], -1)
    tb = ((W * vh["crit"]) @ Ind) / np.expand_dims(W @ vh["crit"], -1)
    bt = np.array([1 - A._hull_tpr(list(fb[b]), list(tb[b]), fa_b[b]) for b in range(E.B)])
    return bt - fc_b


def main():
    D = E.todos(); out = {}
    L = ["# TOST do juiz configurado contra o verificador (exploratório, não pré-registrado)", "",
         "| Modelo | ΔF1 | IC 90% | menor δ equivalente | ΔFAR-crít. (FA pareado) | IC 90% | menor δ equivalente |", "|---|---|---|---|---|---|---|"]
    for m in E.LOCAIS:
        lh, bh = A.loc(E.tab(J8, D[(J8, m)])); lv, bv = A.loc(E.tab(JV, D[(JV, m)]))
        dF1 = lh["F1"][0] - lv["F1"][0]; c1 = ic90(bh[2] - bv[2])
        vh, vp = E.vet(D[(J8, m)]), E.vet(D[(JV, m)])
        h = E.hull_dif(vh, vp); c2 = ic90(far_boot(vh, vp))
        out[m] = {"dF1": dF1, "ic90_dF1": c1, "delta_min_F1": max(map(abs, c1)),
                  "dFAR": h["dif"], "ic90_dFAR": c2, "delta_min_FAR": max(map(abs, c2))}
        L.append(f"| {m} | {dF1:+.2f} | [{c1[0]:+.2f}; {c1[1]:+.2f}] | {max(map(abs, c1)):.2f} | {h['dif']:+.2f} | "
                 f"[{c2[0]:+.2f}; {c2[1]:+.2f}] | {max(map(abs, c2)):.2f} |")
    (E.RES / "tost_h8.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (E.RES / "tost_h8.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
