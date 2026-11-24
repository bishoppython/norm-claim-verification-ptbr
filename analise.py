"""Análise pré-registrada da rodada principal (preregistro.md, emenda 1).

Lê resultados/*__oraculo__hibrida__dialogos.jsonl (4 modelos x 5 juízes) e a rodada
fim a fim (qwen, segmentação por LLM) e escreve resultados/analise.md + analise.json.

- IC 95%: bootstrap por diálogo, 10.000 réplicas, semente 7 (pesos multinomiais,
  as mesmas réplicas para todos os juízes => diferenças pareadas).
- H1: proposto (afirmacao_regras) x holístico no corte de nota com falso alarme mais
  próximo sem passar do proposto; McNemar exato; Holm na família 1 (4 modelos).
- H2: IC da diferença de falso alarme (decisão binária como veio e no corte pareado).
- H3 (família 2, Holm): sem RAG x proposto (FAR-crítico por afirmação, McNemar nas
  afirmações com erro crítico); sem regras x proposto (precisão, IC da diferença);
  holístico com normas x proposto (H1 pareado).
- H5: localização dos problemas do holístico.
- H4: custo (tokens, latência p50/p95).
- Sensibilidade: "insuficiente" = contestado.
"""
import json
import math
from pathlib import Path

import numpy as np

import metricas as M

AQUI = Path(__file__).parent
RES = AQUI / "resultados"
MODELOS = ["qwen3.5-9b", "gemma4-12b", "llama3.1-8b", "gpt-oss-20b"]
JUIZES = ["holistico", "holistico_normas", "afirmacao", "afirmacao_regras", "afirmacao_sem_rag"]
B, SEMENTE = 10_000, 7
GAB = M.carregar_gabarito()
IDS = sorted(GAB)
rng = np.random.default_rng(SEMENTE)
W = rng.multinomial(len(IDS), [1 / len(IDS)] * len(IDS), size=B).astype(float)  # B x n


def carregar(juiz, modelo, seg="oraculo"):
    f = RES / f"{juiz}__{modelo}__{seg}__hibrida__dialogos.jsonl"
    R = {r["id"]: r for r in (json.loads(l) for l in f.open(encoding="utf-8"))}
    assert sorted(R) == IDS, f
    return [R[i] for i in IDS]


def insuf_contesta(R):
    """Sensibilidade: refaz por_gold/aprovada com 'insuficiente' contado como contestado."""
    out = []
    for r in R:
        r = dict(r)
        c = lambda v: str(v.get("veredito", "")).lower().startswith(("contest", "insuf"))
        r["por_gold"] = [c(v) for v in r["vereditos"]]
        r["aprovada"] = not any(r["por_gold"])
        out.append(r)
    return out


def vetores(R, aprovada=None):
    """Somas por diálogo para métricas-razão; aprovada pode ser sobrescrita (corte de nota)."""
    us = M.unidades(R, GAB)
    ap = [u["aprovada"] for u in us] if aprovada is None else aprovada
    v = {
        "crit": [u["tem_critico"] for u in us], "limpo": [u["sem_erro"] for u in us],
        "crit_aprov": [u["tem_critico"] and a for u, a in zip(us, ap)],
        "limpo_reprov": [u["sem_erro"] and not a for u, a in zip(us, ap)],
        "ec": [], "ec_nc": [], "ok": [], "fp": [], "err": [], "tp": [],
    }
    for u in us:
        afs = u["afs"]
        v["ec"].append(sum(not a["correta"] and a["critica"] for a in afs))
        v["ec_nc"].append(sum(not a["correta"] and a["critica"] and not a["contestada"] for a in afs))
        v["ok"].append(sum(a["correta"] for a in afs))
        v["fp"].append(sum(a["correta"] and a["contestada"] for a in afs))
        v["err"].append(sum(not a["correta"] for a in afs))
        v["tp"].append(sum(not a["correta"] and a["contestada"] for a in afs))
    v = {k: np.array(x, dtype=float) for k, x in v.items()}
    v["susp"] = np.array([u["susp"] for u in us], dtype=float)
    v["us"] = us
    return v


RAZOES = {
    "FAR_crit": ("crit_aprov", "crit"), "falso_alarme": ("limpo_reprov", "limpo"),
    "af_FAR_crit": ("ec_nc", "ec"), "af_falso_alarme": ("fp", "ok"),
    "af_precisao": ("tp", None), "af_recall": ("tp", "err"),
}


def razao(v, nome, w=None):
    num, den = RAZOES[nome]
    w = np.ones(len(IDS)) if w is None else w
    a = w @ v[num]
    b = w @ (v["tp"] + v["fp"]) if nome == "af_precisao" else w @ v[den]
    with np.errstate(invalid="ignore", divide="ignore"):
        return a / b


def auc(v, w=None):
    pos, neg = v["crit"].astype(bool), v["limpo"].astype(bool)
    sp, sn = v["susp"][pos], v["susp"][neg]
    C = (sp[:, None] > sn[None, :]) + 0.5 * (sp[:, None] == sn[None, :])
    if w is None:
        return C.mean()
    wp, wn = w[:, pos], w[:, neg]
    return ((wp @ C) * wn).sum(1) / (wp.sum(1) * wn.sum(1))


def ic(boot):
    b = boot[~np.isnan(boot)]
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def est(v, nome):
    if nome == "AUC":
        return float(auc(v)), ic(auc(v, W))
    return float(razao(v, nome)), ic(razao(v, nome, W))


def dif(va, vb, nome):
    if nome == "AUC":
        return float(auc(va) - auc(vb)), ic(auc(va, W) - auc(vb, W))
    return float(razao(va, nome) - razao(vb, nome)), ic(razao(va, nome, W) - razao(vb, nome, W))


def mcnemar_bool(a, b):
    """a, b: listas de 'pegou' pareadas. Binomial exato bicaudal."""
    x = sum(p and not q for p, q in zip(a, b))
    y = sum(q and not p for p, q in zip(a, b))
    n = x + y
    p = min(1.0, 2 * sum(math.comb(n, k) for k in range(min(x, y) + 1)) / 2 ** n) if n else 1.0
    return {"A_pega_B_nao": x, "B_pega_A_nao": y, "p": p}


def holm(ps):
    ordem = sorted(range(len(ps)), key=lambda i: ps[i])
    aj, mx = [0.0] * len(ps), 0.0
    for r, i in enumerate(ordem):
        mx = max(mx, min(1.0, (len(ps) - r) * ps[i]))
        aj[i] = mx
    return aj


def corte_pareado(hol_us, fa_alvo):
    """Corte t (reprova se nota <= t) com falso alarme mais próximo de fa_alvo sem passar."""
    cs = [c for c in M.varredura_nota(hol_us) if c["falso_alarme"] <= fa_alvo + 1e-9]
    return max(cs, key=lambda c: (c["falso_alarme"], -c["FAR_critico"])) if cs else None


def fmt(x, c=None, p=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    s = f"{x:.{p}f}"
    return s + (f" [{c[0]:.{p}f}; {c[1]:.{p}f}]" if c else "")


def main():
    L, J = [], {}
    dados = {(j, m): carregar(j, m) for m in MODELOS for j in JUIZES}
    V = {k: vetores(R) for k, R in dados.items()}

    # ---------------------------------------------------------- tabela principal
    L += ["# Análise pré-registrada: rodada principal", "",
          "300 diálogos (108 limpos, 96 com um erro, 96 mistos); 135 respostas com erro crítico, 120 sem erro;",
          "2.113 afirmações. IC 95% por bootstrap por diálogo (10.000 réplicas, semente 7).", "",
          "## Tabela 1. Nível da resposta (decisão binária como veio)", "",
          "| Modelo | Juiz | FAR-crítico | Falso alarme | AUC |", "|---|---|---|---|---|"]
    for m in MODELOS:
        for j in JUIZES:
            v = V[(j, m)]
            r = {n: est(v, n) for n in ("FAR_crit", "falso_alarme", "AUC")}
            J[f"{m}|{j}"] = r
            L.append(f"| {m} | {j} | {fmt(*r['FAR_crit'])} | {fmt(*r['falso_alarme'])} | {fmt(*r['AUC'])} |")
    L += ["", "## Tabela 2. Nível da afirmação (juízes por afirmação)", "",
          "| Modelo | Juiz | FAR-crítico | Falso alarme | Precisão | Recall | F1 | Recall difíceis |",
          "|---|---|---|---|---|---|---|---|"]
    for m in MODELOS:
        for j in JUIZES[2:]:
            v = V[(j, m)]
            r = {n: est(v, n) for n in ("af_FAR_crit", "af_falso_alarme", "af_precisao", "af_recall")}
            mm = M.metricas(v["us"])
            J[f"{m}|{j}"].update(r)
            L.append(f"| {m} | {j} | {fmt(*r['af_FAR_crit'])} | {fmt(*r['af_falso_alarme'])} | "
                     f"{fmt(*r['af_precisao'])} | {fmt(*r['af_recall'])} | {fmt(mm['af_F1'])} | "
                     f"{fmt(mm.get('af_recall_dificeis'))} |")

    # recall por categoria
    cats = sorted({k[len('af_recall_'):] for m in MODELOS for k in M.metricas(V[('afirmacao_regras', m)]['us'])
                   if k.startswith("af_recall_") and k != "af_recall_dificeis"})
    L += ["", "### Recall por categoria de erro (proposto)", "",
          "| Modelo | " + " | ".join(cats) + " |", "|---|" + "---|" * len(cats)]
    for m in MODELOS:
        mm = M.metricas(V[("afirmacao_regras", m)]["us"])
        L.append(f"| {m} | " + " | ".join(fmt(mm.get(f"af_recall_{c}")) for c in cats) + " |")

    # ---------------------------------------------------------- H1 / H2
    def comparar_pareado(jh, m):
        vp = V[("afirmacao_regras", m)]
        fa_p = float(razao(vp, "falso_alarme"))
        c = corte_pareado(V[(jh, m)]["us"], fa_p)
        ap_h = [float(u["nota"]) > c["reprova_se_nota<="] for u in V[(jh, m)]["us"]]
        vh = vetores(dados[(jh, m)], aprovada=ap_h)
        crit = [u["tem_critico"] for u in vp["us"]]
        pega_p = [not u["aprovada"] for u, k in zip(vp["us"], crit) if k]
        pega_h = [not a for a, k in zip(ap_h, crit) if k]
        mc = mcnemar_bool(pega_p, pega_h)
        return {"corte": c["reprova_se_nota<="], "FA_prop": fa_p, "FA_hol": float(razao(vh, "falso_alarme")),
                "FAR_prop": est(vp, "FAR_crit"), "FAR_hol": est(vh, "FAR_crit"),
                "dif_FAR": dif(vp, vh, "FAR_crit"), "dif_FA": dif(vp, vh, "falso_alarme"),
                "dif_AUC": dif(vp, V[(jh, m)], "AUC"), **mc}

    L += ["", "## H1. Proposto x holístico com o mesmo falso alarme", "",
          "Corte do holístico: reprova se nota ≤ t, com o falso alarme mais próximo do proposto sem passar.", "",
          "| Modelo | t | FA proposto | FA holístico | FAR-crít. proposto | FAR-crít. holístico | Δ FAR (prop − hol) | só prop. pega | só hol. pega | p | p Holm |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    h1 = {m: comparar_pareado("holistico", m) for m in MODELOS}
    for m, a in zip(MODELOS, holm([h1[m]["p"] for m in MODELOS])):
        h1[m]["p_holm"] = a
        x = h1[m]
        L.append(f"| {m} | {x['corte']} | {x['FA_prop']:.2f} | {x['FA_hol']:.2f} | {fmt(*x['FAR_prop'])} | "
                 f"{fmt(*x['FAR_hol'])} | {fmt(*x['dif_FAR'])} | {x['A_pega_B_nao']} | {x['B_pega_A_nao']} | "
                 f"{x['p']:.4f} | {a:.4f} |")
    J["H1"] = h1
    L += ["", "### AUC: proposto − holístico (IC pareado)", "", "| Modelo | Δ AUC |", "|---|---|"]
    for m in MODELOS:
        L.append(f"| {m} | {fmt(*h1[m]['dif_AUC'])} |")

    L += ["", "## H2. Diferença de falso alarme (proposto − holístico), limite 10 p.p.", "",
          "| Modelo | Decisão binária como veio | No corte pareado da H1 |", "|---|---|---|"]
    for m in MODELOS:
        d0 = dif(V[("afirmacao_regras", m)], V[("holistico", m)], "falso_alarme")
        J.setdefault("H2", {})[m] = {"binaria": d0, "pareado": h1[m]["dif_FA"]}
        L.append(f"| {m} | {fmt(*d0)} | {fmt(*h1[m]['dif_FA'])} |")

    # ---------------------------------------------------------- H3 (família 2)
    L += ["", "## H3. Ablações (família 2, Holm sobre os 12 testes)", ""]
    testes = []
    for m in MODELOS:
        vp, vs = V[("afirmacao_regras", m)], V[("afirmacao_sem_rag", m)]
        pp = [a["contestada"] for u in vp["us"] for a in u["afs"] if not a["correta"] and a["critica"]]
        ps = [a["contestada"] for u in vs["us"] for a in u["afs"] if not a["correta"] and a["critica"]]
        mc = mcnemar_bool(pp, ps)
        testes.append((m, "sem RAG: FAR-crít. por afirmação (sem RAG − proposto)",
                       dif(vs, vp, "af_FAR_crit"), mc["p"], f"{mc['A_pega_B_nao']}/{mc['B_pega_A_nao']}"))
        va = V[("afirmacao", m)]
        pa_ = [a["contestada"] for u in va["us"] for a in u["afs"]]
        pr_ = [a["contestada"] for u in vp["us"] for a in u["afs"]]
        corr = [not a["correta"] for u in vp["us"] for a in u["afs"]]
        # precisão: contestações corretas; McNemar sobre afirmações corretas (falsos positivos) como apoio
        mfp = mcnemar_bool([c and not e for c, e in zip(pa_, corr)], [c and not e for c, e in zip(pr_, corr)])
        testes.append((m, "sem regras: precisão (sem regras − proposto)", dif(va, vp, "af_precisao"), mfp["p"],
                       f"FP só s/ regras {mfp['A_pega_B_nao']} / só proposto {mfp['B_pega_A_nao']}"))
        x = comparar_pareado("holistico_normas", m)
        testes.append((m, "holístico+normas no FA pareado: FAR-crít. (proposto − hol.+normas)",
                       x["dif_FAR"], x["p"], f"{x['A_pega_B_nao']}/{x['B_pega_A_nao']} (t={x['corte']}, FA {x['FA_hol']:.2f})"))
    aj = holm([t[3] for t in testes])
    L += ["| Modelo | Comparação | Δ [IC 95%] | discordantes | p | p Holm |", "|---|---|---|---|---|---|"]
    for t, a in zip(testes, aj):
        L.append(f"| {t[0]} | {t[1]} | {fmt(*t[2])} | {t[4]} | {t[3]:.4f} | {a:.4f} |")
    J["H3"] = [{"modelo": t[0], "teste": t[1], "dif": t[2], "p": t[3], "p_holm": a} for t, a in zip(testes, aj)]

    # ---------------------------------------------------------- estratos
    L += ["", "## Por estrato (FAR-crítico / falso alarme por resposta, decisão como veio)", "",
          "| Modelo | Juiz | limpo: FA | um_erro: FAR | um_erro: FA | misto: FAR |", "|---|---|---|---|---|---|"]
    for m in MODELOS:
        for j in JUIZES:
            us = V[(j, m)]["us"]
            cel = []
            for e, k in (("limpo", "resp_falso_alarme"), ("um_erro", "resp_FAR_critico"),
                         ("um_erro", "resp_falso_alarme"), ("misto", "resp_FAR_critico")):
                x = [u for u in us if u["estrato"] == e]
                cel.append(fmt(M.metricas(x)[k]))
            L.append(f"| {m} | {j} | " + " | ".join(cel) + " |")

    # ---------------------------------------------------------- sensibilidade
    L += ["", "## Sensibilidade: \"insuficiente\" conta como contestado", "",
          "| Modelo | Juiz | % insuficiente | FAR-crít. resp. | FA resp. | FAR-crít. afirm. | FA afirm. |",
          "|---|---|---|---|---|---|---|"]
    for m in MODELOS:
        for j in JUIZES[2:]:
            R = dados[(j, m)]
            vv = [v for r in R for v in r["vereditos"]]
            pin = sum(str(v.get("veredito", "")).lower().startswith("insuf") for v in vv) / len(vv)
            vs = vetores(insuf_contesta(R))
            L.append(f"| {m} | {j} | {pin:.1%} | {fmt(razao(vs, 'FAR_crit'))} | {fmt(razao(vs, 'falso_alarme'))} | "
                     f"{fmt(razao(vs, 'af_FAR_crit'))} | {fmt(razao(vs, 'af_falso_alarme'))} |")

    # ---------------------------------------------------------- H5
    L += ["", "## H5. Localização pelos juízes holísticos", "",
          "| Modelo | Juiz | erros localizados | problemas que apontam erro | problemas que acusam afirmação correta | problemas/resposta |",
          "|---|---|---|---|---|---|"]
    for m in MODELOS:
        for j in JUIZES[:2]:
            mm = M.metricas(V[(j, m)]["us"])
            loc = [u["localizacao"] for u in V[(j, m)]["us"] if u["localizacao"]]
            ppr = sum(x["problemas"] for x in loc) / len(IDS)
            L.append(f"| {m} | {j} | {fmt(mm.get('loc_erros_localizados'))} | {fmt(mm.get('loc_problemas_que_apontam_erro'))} | "
                     f"{fmt(mm.get('loc_problemas_que_acusam_certa'))} | {ppr:.1f} |")

    # ---------------------------------------------------------- H4 custo
    L += ["", "## H4. Custo por diálogo (chamada original; cache não reduz o custo reportado)", "",
          "| Modelo | Juiz | tokens | chamadas LLM | latência p50 (s) | p95 (s) | regras decidiram |", "|---|---|---|---|---|---|---|"]
    for m in MODELOS:
        for j in JUIZES:
            R = dados[(j, m)]
            seg = np.array([r["custo"]["seg"] for r in R])
            tok = np.mean([r["custo"]["tokens_in"] + r["custo"]["tokens_out"] for r in R])
            ch = np.mean([r["custo"]["chamadas"] for r in R])
            reg = "—"
            if j == "afirmacao_regras":
                vv = [v for r in R for v in r["vereditos"]]
                reg = f"{sum(v.get('fonte') == 'regra' for v in vv) / len(vv):.1%}"
            L.append(f"| {m} | {j} | {tok:.0f} | {ch:.1f} | {np.percentile(seg, 50):.1f} | {np.percentile(seg, 95):.1f} | {reg} |")

    # ---------------------------------------------------------- JSON inválido / timeout
    L += ["", "## JSON inválido e timeout", "", "| Modelo | Juiz | chamadas com JSON inválido | timeouts |", "|---|---|---|---|"]
    for m in MODELOS:
        for j in JUIZES:
            R = dados[(j, m)]
            outs = [r["bruto"] for r in R] if j.startswith("holistico") else [v for r in R for v in r["vereditos"]]
            L.append(f"| {m} | {j} | {sum('_erro_json' in o for o in outs)} / {len(outs)} | "
                     f"{sum(bool(o.get('_timeout')) for o in outs)} |")

    # ---------------------------------------------------------- fim a fim
    R = carregar("afirmacao_regras", "qwen3.5-9b", "llm")
    al = [x is not None for r in R for x in r["por_gold"]]
    ve, vo = vetores(R), V[("afirmacao_regras", "qwen3.5-9b")]
    nex = np.mean([len(r["extraidas"]) for r in R])
    L += ["", "## Fim a fim (qwen3.5:9b, afirmações extraídas pelo LLM)", "",
          f"- Taxa de alinhamento (afirmação do gabarito com extraída de Jaccard ≥ 0,5): {np.mean(al):.1%}",
          f"- Afirmações extraídas por resposta: {nex:.1f} (gabarito: {2113 / 300:.1f})",
          "", "| Segmentação | FAR-crítico resp. | Falso alarme resp. | AUC | FAR-crít. afirm. |", "|---|---|---|---|---|"]
    for nome, v in (("gabarito (oráculo)", vo), ("LLM (fim a fim)", ve)):
        L.append(f"| {nome} | {fmt(*est(v, 'FAR_crit'))} | {fmt(*est(v, 'falso_alarme'))} | {fmt(*est(v, 'AUC'))} | "
                 f"{fmt(*est(v, 'af_FAR_crit'))} |")

    (RES / "analise.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (RES / "analise.json").write_text(json.dumps(J, indent=1, default=float), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
