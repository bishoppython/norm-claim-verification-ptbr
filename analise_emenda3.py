"""Análise da emenda 3 (parecer simulado da Applied Intelligence). Escreve resultados/analise_emenda3.md e .json.

Juízes novos (pré-registrados na emenda 3, antes de rodar):
  H8   holístico só conformidade + por sentença + normas x verificador (ΔF1 de localização; regra de decisão:
       IC contendo 0 ou a favor do holístico em >= 3 de 4 modelos muda a recomendação).
  H3b  holístico + normas com top-3 x verificador (FAR-crítico em falso alarme exatamente pareado; ΔF1).
  H9   verificador com recuperação oráculo x híbrida (FAR-crítico por afirmação, pareado, dois níveis) e
       acurácia do veredito condicionada a acerto/erro da recuperação híbrida.
  H10  verificador x RAGAs faithfulness e x MiniCheck (ΔF1; FAR-crítico pareado; falso alarme; AUC).
  M8   fim a fim nos 4 modelos (descritivo).
Exploratórias (decididas depois de ver as emendas 1 e 2):
  M5   bootstrap em dois níveis também por resposta; erros críticos distintos.
  M6   FAR-crítico em falso alarme fixo; VPP e carga de revisão por prevalência; barreira de três saídas.
  M7   FAR-crítico com a gravidade da anotadora e com a união.
  menores: fail-closed; limiares de localização (30/40/50%) e de alinhamento (Jaccard 0,4/0,5/0,6);
           precisão sobre as 300 respostas.
Roda com o python do venv ~/.venvs/ragas (numpy + openpyxl). Juízes sem arquivo completo são pulados.
"""
import json
import math
from pathlib import Path

import numpy as np

import analise_emenda2 as A
import metricas as M

RES = A.RES
AQUI = A.AQUI
IDS, GAB, WD, WF, B = A.IDS, A.GAB, A.WD, A.WF, A.B
LOCAIS = ["qwen3.5-9b", "gemma4-12b", "llama3.1-8b", "gpt-oss-20b"]
f, fic, ic = A.f, A.fic, A.ic
NOME = dict(A.NOME, holistico_conformidade_sentencas_normas="holístico só conformidade + por sentença + normas",
            holistico_normas_k3="holístico + normas (top-3)", ragas="RAGAs faithfulness", minicheck="MiniCheck",
            afirmacao_regras_oraculo="verificador, recuperação oráculo", afirmacao_regras_e2e="verificador, fim a fim")


def carregar(juiz, modelo, seg="oraculo", rec="hibrida"):
    p = RES / f"{juiz}__{modelo}__{seg}__{rec}__dialogos.jsonl"
    if not p.exists():
        return None
    R = {r["id"]: r for r in (json.loads(l) for l in p.open(encoding="utf-8"))}
    return [R[i] for i in IDS] if sorted(R) == IDS else None


def todos():
    """{(juiz, modelo): lista de saídas}, com nomes únicos para as variantes."""
    D = {}
    for m in LOCAIS + ["claude-haiku-5-5"]:
        for j in A.JUIZES + ["holistico_conformidade_sentencas_normas", "holistico_normas_k3", "ragas"]:
            r = carregar(j, m)
            if r is not None:
                D[(j, m)] = r
        r = carregar("afirmacao_regras", m, rec="oraculo")
        if r is not None:
            D[("afirmacao_regras_oraculo", m)] = r
        r = carregar("afirmacao_regras", m, seg="llm")
        if r is not None:
            D[("afirmacao_regras_e2e", m)] = r
    r = carregar("minicheck", "bespoke-minicheck")
    if r is not None:
        for m in LOCAIS:  # mesmo baseline (modelo único) comparado ao verificador de cada modelo
            D[("minicheck", m)] = r
    return D


# ----------------------------------------------------------------- vetores por resposta
def invalida(r):
    """Saída que o juiz não conseguiu produzir (JSON inválido, timeout, ragas sem afirmações)."""
    if r.get("juiz") == "ragas":
        return r.get("erro") is not None or r.get("nota") is None
    if "vereditos" in r:
        return any(("_erro_json" in v) or v.get("veredito") == "invalido" for v in r["vereditos"])
    b = r.get("bruto") or {}
    return "_erro_json" in b or not b or r.get("nota") is None


def vet(R, crit_fatos=None, fail_closed=False, fail_open=False):
    v = A.vet_resposta(R)
    if R and R[0].get("juiz") == "ragas":  # escore pré-registrado: 1 - faithfulness (sem afirmação = 0)
        v["susp"] = np.array([1 - r["nota"] if r.get("nota") is not None else 0.0 for r in R])
    if crit_fatos is not None:  # gravidade alternativa (M7): crítica se o fato do erro estiver no conjunto
        v["crit"] = np.array([any((not a["correta"]) and a["fato_id"] in crit_fatos for a in GAB[i]["afirmacoes"])
                              for i in IDS], float)
    if fail_closed or fail_open:
        inv = np.array([invalida(r) for r in R], float)
        if fail_closed:
            v["rej"] = np.maximum(v["rej"], inv)
            v["susp"] = np.where(inv > 0, v["susp"].max() + 1, v["susp"])
        else:
            v["rej"] = v["rej"] * (1 - inv)
    return v


def taxas(v, w):
    return A.taxa(v["limpo"] * v["rej"], v["limpo"], w), A.taxa(v["crit"] * (1 - v["rej"]), v["crit"], w)


def hull_dif(vh, vp, W=None):
    """FAR-crítico de vh no falso alarme exato de vp (envelope convexo da ROC); diferença vh - vp com IC."""
    W = WD if W is None else W
    um = np.ones(len(IDS))
    fa_pt, fc_pt = (float(x) for x in taxas(vp, um))
    fa_b, fc_b = taxas(vp, W)
    ts = np.unique(vh["susp"])
    Ind = (vh["susp"][:, None] >= ts[None, :]).astype(float)
    def curva(w):
        return (((w * vh["limpo"]) @ Ind) / np.expand_dims(w @ vh["limpo"], -1),
                ((w * vh["crit"]) @ Ind) / np.expand_dims(w @ vh["crit"], -1))
    fpr, tpr = curva(um)
    pt = 1 - A._hull_tpr(list(fpr), list(tpr), fa_pt)
    fb, tb = curva(W)
    bt = np.array([1 - A._hull_tpr(list(fb[b]), list(tb[b]), fa_b[b]) for b in range(B)])
    return {"fa_prop": fa_pt, "far_prop": fc_pt, "far_outro": pt, "dif": pt - fc_pt, "ic": ic(bt - fc_b)}


def far_em_fa(v, alvo, W=None):
    """FAR-crítico do juiz no falso alarme alvo, pela própria curva (envelope convexo)."""
    W = WD if W is None else W
    ts = np.unique(v["susp"])
    Ind = (v["susp"][:, None] >= ts[None, :]).astype(float)
    def curva(w):
        return (((w * v["limpo"]) @ Ind) / np.expand_dims(w @ v["limpo"], -1),
                ((w * v["crit"]) @ Ind) / np.expand_dims(w @ v["crit"], -1))
    fpr, tpr = curva(np.ones(len(IDS)))
    pt = 1 - A._hull_tpr(list(fpr), list(tpr), alvo)
    fb, tb = curva(W[:2000])
    bt = np.array([1 - A._hull_tpr(list(fb[b]), list(tb[b]), alvo) for b in range(len(fb))])
    return pt, ic(bt)


def auc(v):
    pos, neg = v["susp"][v["crit"] > 0], v["susp"][v["limpo"] > 0]
    return float(((pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])).mean())


# ----------------------------------------------------------------- M5: pesos de dois níveis por resposta
def pesos_dois_niveis():
    """Peso de cada resposta = peso do diálogo x média dos pesos dos seus fatos (bootstrap cruzado)."""
    Fm = np.zeros((len(IDS), len(A.FATOS)))
    for i in IDS:
        for a in GAB[i]["afirmacoes"]:
            Fm[A.IX[i], A.FX[a["fato_id"]]] = 1
    Fm /= Fm.sum(1, keepdims=True)
    return WD * (WF @ Fm.T)


# ----------------------------------------------------------------- localização com limiar variável
def tabela_af(R, lim=0.4):
    if lim == 0.4:
        return A.tabela_afirmacoes(R)
    velho = A.apontadas
    def apontadas(r, d):
        if "vereditos" in r or "por_gold_sent" in r:
            return velho(r, d)
        probs = [M._tok(p) for p in (r.get("bruto", {}).get("problemas") or [])]
        return [((bool(t := M._tok(a["texto"])) and any(len(t & p) / len(t) >= lim for p in probs)), None)
                for a in d["afirmacoes"]]
    A.apontadas = apontadas
    try:
        return A.tabela_afirmacoes(R)
    finally:
        A.apontadas = velho


def tabela_por_gold(R):
    """Juízes cujas saídas não são por afirmação do gabarito (RAGAs, fim a fim): usa o alinhamento por_gold."""
    L = []
    for r in R:
        d = GAB[r["id"]]
        for a, ap in zip(d["afirmacoes"], r["por_gold"]):
            L.append({"d": A.IX[r["id"]], "f": A.FX[a["fato_id"]], "erro": not a["correta"], "ap": bool(ap),
                      "resp_com_erro": d["n_erros"] > 0, "cit": None, "amb": a["texto"] in A.AMBIGUO,
                      "crit": (not a["correta"]) and a.get("gravidade") == "critica"})
    return L


def tab(j, R):
    return tabela_por_gold(R) if j in ("ragas", "afirmacao_regras_e2e") else A.tabela_afirmacoes(R)


def precisao_300(T):
    ap = [x for x in T if x["ap"]]
    return sum(x["erro"] for x in ap) / len(ap) if ap else math.nan


def jaccard_realinhar(R, limiar):
    from recuperar import tokens
    out = []
    for r in R:
        ext = [set(tokens(x)) for x in (r.get("extraidas") or [])]
        mapa = []
        for g in GAB[r["id"]]["afirmacoes"]:
            tg = set(tokens(g["texto"]))
            notas = [(len(tg & t) / max(1, len(tg | t)), k) for k, t in enumerate(ext)]
            mel = max(notas, default=(0, None))
            mapa.append(mel[1] if mel[0] >= limiar else None)
        r2 = dict(r, por_gold=[None if m is None else M_cont(r["vereditos"][m]) for m in mapa])
        out.append(r2)
    return out


def M_cont(v):
    return str(v.get("veredito", "")).lower().startswith("contest")


# ----------------------------------------------------------------- M9: recuperação acertou?
def acertos_recuperacao():
    arq = RES / "recuperacao_top3.json"
    if arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    from juizes import Recuperador
    idx = Recuperador("hibrida")
    out = {}
    for i in IDS:
        out[i] = [any((d["norma"], str(d["artigo"])) == (a["norma"], str(a["artigo"])) for _, d in idx.buscar(a["texto"], k=3))
                  for a in GAB[i]["afirmacoes"]]
    arq.write_text(json.dumps(out), encoding="utf-8")
    return out


def gravidade_anotadora():
    from openpyxl import load_workbook
    wb = load_workbook(AQUI.parent / "submissao" / "anotador" / "validacao_gabarito_v2_preenchida.xlsx", read_only=True)
    rows = list(wb["Fatos"].iter_rows(values_only=True))
    h = rows[0]
    i_id, i_g = h.index("ID"), h.index("Gravidade se estivesse errada")
    anot = {r[i_id] for r in rows[1:] if r[i_id] and str(r[i_g]).strip().lower().startswith("crít")}
    nossa = {a["fato_id"] for d in GAB.values() for a in d["afirmacoes"] if a.get("gravidade") == "critica"}
    return anot, nossa


# ----------------------------------------------------------------- principal
def main():
    D = todos()
    J, L = {}, ["# Análise da emenda 3 (gerado por analise_emenda3.py)", "",
                "IC 95% por bootstrap (10.000 réplicas, semente 7): por diálogo nas métricas por resposta, "
                "salvo indicação; dois níveis (diálogo × fato) nas métricas por afirmação e de localização.", ""]
    V = {k: vet(R) for k, R in D.items()}
    T = {k: tab(k[0], R) for k, R in D.items()}

    # ---------------- respostas e localização de todos os juízes
    L += ["## Por resposta (decisão como devolvida) e localização", "",
          "| Modelo | Juiz | falso alarme | FAR-crítico | AUC | precisão loc. | recall loc. | F1 loc. | precisão (300 resp.) |",
          "|---|---|---|---|---|---|---|---|---|"]
    F1B = {}
    for m in LOCAIS + ["claude-haiku-5-5"]:
        for j in A.JUIZES + ["holistico_conformidade_sentencas_normas", "holistico_normas_k3", "ragas", "minicheck",
                             "afirmacao_regras_oraculo", "afirmacao_regras_e2e"]:
            if (j, m) not in D:
                continue
            r = A.resp_metricas(V[(j, m)])
            lo, bt = A.loc(T[(j, m)])
            F1B[(j, m)] = bt[2]
            p300 = precisao_300(T[(j, m)]) if j not in ("holistico", "holistico_normas", "holistico_conformidade", "holistico_normas_k3") else math.nan
            J.setdefault("resposta_loc", {})[f"{j}|{m}"] = {"resp": r, "auc": auc(V[(j, m)]), "loc": lo, "precisao_300": p300}
            L.append(f"| {m} | {NOME[j]} | {fic(r['falso_alarme'])} | {fic(r['FAR_crit'])} | {f(auc(V[(j, m)]))} | "
                     f"{fic(lo['precisao'])} | {fic(lo['recall'])} | {fic(lo['F1'])} | {f(p300)} |")
    L.append("")

    # ---------------- H8, H3b, H10: ΔF1 e FAR-crítico pareado contra o verificador
    for nome_h, js in (("H8", ["holistico_conformidade_sentencas_normas"]), ("H3b", ["holistico_normas_k3"]),
                       ("H10", ["ragas", "minicheck"])):
        L += [f"## {nome_h}. Contra o verificador proposto (afirmacao_regras)", "",
              "| Modelo | Juiz | ΔF1 (juiz − proposto) [IC] | p ΔF1 | p Holm | FAR-crítico do proposto | FAR-crítico do juiz no mesmo falso alarme | diferença (juiz − proposto) [IC] |",
              "|---|---|---|---|---|---|---|---|"]
        linhas = []
        for m in LOCAIS + ["claude-haiku-5-5"]:
            for j in js:
                if (j, m) not in D or ("afirmacao_regras", m) not in D:
                    continue
                dF1 = A.loc(T[(j, m)])[0]["F1"][0] - A.loc(T[("afirmacao_regras", m)])[0]["F1"][0]
                db = F1B[(j, m)] - F1B[("afirmacao_regras", m)]
                icF1 = ic(db)
                db = db[~np.isnan(db)]
                p = min(1.0, 2 * min(np.mean(db <= 0), np.mean(db >= 0)))  # p bootstrap bicaudal (percentil)
                h = hull_dif(V[(j, m)], V[("afirmacao_regras", m)])
                linhas.append((j, m, dF1, icF1, p, h))
        # Holm dentro da família (por juiz, nos 4 modelos locais; o Haiku é exploratório e fica fora)
        padj = {}
        for j in js:
            fam = [x for x in linhas if x[0] == j and x[1] in LOCAIS]
            for x, a in zip(fam, A.holm([x[4] for x in fam])):
                padj[(x[0], x[1])] = a
        for j, m, dF1, icF1, p, h in linhas:
            pa = padj.get((j, m), math.nan)
            J.setdefault(nome_h, {})[f"{j}|{m}"] = {"dF1": dF1, "ic_dF1": icF1, "p_dF1": p, "p_holm_dF1": pa, **h}
            L.append(f"| {m} | {NOME[j]} | {f(dF1)} [{f(icF1[0])}; {f(icF1[1])}] | {f(p, 3)} | {f(pa, 3)} | {f(h['far_prop'])} | "
                     f"{f(h['far_outro'])} | {f(h['dif'])} [{f(h['ic'][0])}; {f(h['ic'][1])}] |")
        L.append("")

    # ---------------- H9: oráculo x híbrida
    if any(k[0] == "afirmacao_regras_oraculo" for k in D):
        hit = acertos_recuperacao()
        L += ["## H9. Recuperação oráculo x híbrida (verificador, por afirmação; dois níveis)", "",
              "| Modelo | FAR-crít. afirm. híbrida | FAR-crít. afirm. oráculo | diferença (oráculo − híbrida) [IC] | falso alarme afirm. híbrida | oráculo | "
              "acurácia do veredito: recuperação acertou | errou |", "|---|---|---|---|---|---|---|---|"]
        for m in LOCAIS + ["claude-haiku-5-5"]:
            if ("afirmacao_regras_oraculo", m) not in D or ("afirmacao_regras", m) not in D:
                continue
            Th, To = T[("afirmacao_regras", m)], T[("afirmacao_regras_oraculo", m)]
            th, to = A.tab4(Th), A.tab4(To)
            d = np.array([x["d"] for x in Th]); fa = np.array([x["f"] for x in Th])
            cr = np.array([x["crit"] for x in Th], float)
            aph, apo = np.array([x["ap"] for x in Th], float), np.array([x["ap"] for x in To], float)
            Wb = WD[..., d] * WF[..., fa]
            dif_b = (Wb @ (cr * (1 - apo))) / (Wb @ cr) - (Wb @ (cr * (1 - aph))) / (Wb @ cr)
            # acurácia do veredito (contesta erro / não contesta correta) por acerto da recuperação híbrida
            h = np.array([x for i in IDS for x in hit[i]])
            er = np.array([x["erro"] for x in Th])
            certo = (aph.astype(bool) == er)
            acc_h, acc_m = certo[h].mean(), certo[~h].mean()
            db = dif_b[~np.isnan(dif_b)]
            p9 = min(1.0, 2 * min(np.mean(db <= 0), np.mean(db >= 0)))
            J.setdefault("H9", {})[m] = {"hib": th, "ora": to, "dif": to["FAR_crit"][0] - th["FAR_crit"][0], "ic": ic(dif_b), "p": p9,
                                         "acc_rec_acertou": float(acc_h), "acc_rec_errou": float(acc_m), "recall3": float(h.mean())}
            L.append(f"| {m} | {fic(th['FAR_crit'])} | {fic(to['FAR_crit'])} | {f(to['FAR_crit'][0] - th['FAR_crit'][0])} "
                     f"[{f(ic(dif_b)[0])}; {f(ic(dif_b)[1])}] | {f(th['falso_alarme'][0])} | {f(to['falso_alarme'][0])} | "
                     f"{f(acc_h)} | {f(acc_m)} |")
        loc9 = [m for m in LOCAIS if m in J.get("H9", {})]
        for m, a in zip(loc9, A.holm([J["H9"][m]["p"] for m in loc9])):
            J["H9"][m]["p_holm"] = a
        L += ["", "p bootstrap da diferença (bicaudal) e Holm nos 4 modelos locais: " +
              "; ".join(f"{m} p = {f(J['H9'][m]['p'], 3)}, Holm {f(J['H9'][m]['p_holm'], 3)}" for m in loc9) + "."]
        L += ["", f"Recall@3 da recuperação híbrida nas 2.113 afirmações: {f(float(np.mean([x for i in IDS for x in hit[i]])))}.", ""]

    # ---------------- M8: fim a fim
    L += ["## M8. Fim a fim (segmentação pelo LLM)", "",
          "| Modelo | afirmações do gabarito alinhadas | extraídas por resposta | falso alarme | FAR-crítico | AUC | FAR-crít. afirm. |",
          "|---|---|---|---|---|---|---|"]
    for m in LOCAIS:
        if ("afirmacao_regras_e2e", m) not in D:
            continue
        R = D[("afirmacao_regras_e2e", m)]
        al = np.mean([x is not None for r in R for x in r["por_gold"]])
        ne = np.mean([len(r.get("extraidas") or []) for r in R])
        r = A.resp_metricas(V[("afirmacao_regras_e2e", m)])
        t4 = A.tab4(T[("afirmacao_regras_e2e", m)])
        J.setdefault("M8", {})[m] = {"alinhadas": float(al), "extraidas": float(ne), "resp": r, "auc": auc(V[("afirmacao_regras_e2e", m)]), "af": t4}
        L.append(f"| {m} | {f(al)} | {f(ne, 1)} | {fic(r['falso_alarme'])} | {fic(r['FAR_crit'])} | "
                 f"{f(auc(V[('afirmacao_regras_e2e', m)]))} | {fic(t4['FAR_crit'])} |")
    L.append("")

    # ---------------- M5
    W2 = pesos_dois_niveis()
    crit_err = {a["texto"] for i in IDS for a in GAB[i]["afirmacoes"] if (not a["correta"]) and a.get("gravidade") == "critica"
                and GAB[i]["n_erros_criticos"] > 0}
    crit_fat = {a["fato_id"] for i in IDS for a in GAB[i]["afirmacoes"] if (not a["correta"]) and a.get("gravidade") == "critica"}
    L += ["## M5. Dependência por fato no nível de resposta", "",
          f"As 135 respostas com erro crítico contêm {len(crit_err)} erros críticos distintos, de {len(crit_fat)} fatos-norma.", "",
          "| Modelo | Juiz | FAR-crítico [IC diálogo] | [IC dois níveis] | falso alarme [IC diálogo] | [IC dois níveis] |",
          "|---|---|---|---|---|---|"]
    J["M5"] = {"erros_criticos_distintos": len(crit_err), "fatos_criticos": len(crit_fat)}
    for m in LOCAIS:
        for j in ("holistico", "holistico_conformidade", "holistico_sentencas_normas", "afirmacao_regras"):
            if (j, m) not in V:
                continue
            v = V[(j, m)]
            fa1, fc1 = taxas(v, WD); fa2, fc2 = taxas(v, W2)
            fa0, fc0 = (float(x) for x in taxas(v, np.ones(len(IDS))))
            J["M5"][f"{j}|{m}"] = {"far": fc0, "ic_d": ic(fc1), "ic_2": ic(fc2), "fa": fa0, "ic_fa_d": ic(fa1), "ic_fa_2": ic(fa2)}
            L.append(f"| {m} | {NOME[j]} | {f(fc0)} [{f(ic(fc1)[0])}; {f(ic(fc1)[1])}] | [{f(ic(fc2)[0])}; {f(ic(fc2)[1])}] | "
                     f"{f(fa0)} [{f(ic(fa1)[0])}; {f(ic(fa1)[1])}] | [{f(ic(fa2)[0])}; {f(ic(fa2)[1])}] |")
    L += ["", "Diferenças pareadas com IC de dois níveis por resposta (H1 exato e H7):", "",
          "| Modelo | comparação | diferença | IC diálogo | IC dois níveis |", "|---|---|---|---|---|"]
    for m in LOCAIS:
        if ("afirmacao_regras", m) in V and ("holistico", m) in V:
            h1, h2 = hull_dif(V[("holistico", m)], V[("afirmacao_regras", m)]), hull_dif(V[("holistico", m)], V[("afirmacao_regras", m)], W2)
            J["M5"][f"H1exato|{m}"] = {"dif": h1["dif"], "ic_d": h1["ic"], "ic_2": h2["ic"]}
            L.append(f"| {m} | H1 exato: FAR-crít. holístico − proposto | {f(h1['dif'])} | [{f(h1['ic'][0])}; {f(h1['ic'][1])}] | [{f(h2['ic'][0])}; {f(h2['ic'][1])}] |")
        if ("holistico", m) in V and ("holistico_conformidade", m) in V:
            a, b = V[("holistico", m)], V[("holistico_conformidade", m)]
            def dfa(w):
                return A.taxa(b["limpo"] * b["rej"], b["limpo"], w) - A.taxa(a["limpo"] * a["rej"], a["limpo"], w)
            pt = float(dfa(np.ones(len(IDS))))
            J["M5"][f"H7|{m}"] = {"dif": pt, "ic_d": ic(dfa(WD)), "ic_2": ic(dfa(W2))}
            L.append(f"| {m} | H7: falso alarme só conformidade − holístico | {f(pt)} | [{f(ic(dfa(WD))[0])}; {f(ic(dfa(WD))[1])}] | "
                     f"[{f(ic(dfa(W2))[0])}; {f(ic(dfa(W2))[1])}] |")
    L.append("")

    # ---------------- M6
    L += ["## M6. Pontos de operação realistas", "",
          "FAR-crítico de cada juiz no falso alarme fixo (envelope convexo da própria curva; IC por diálogo, 2.000 réplicas).", "",
          "| Modelo | Juiz | FA 0,05 | FA 0,10 | FA 0,20 |", "|---|---|---|---|---|"]
    J["M6"] = {}
    for m in LOCAIS + ["claude-haiku-5-5"]:
        for j in ("holistico", "holistico_normas", "holistico_conformidade", "holistico_sentencas_normas",
                  "holistico_conformidade_sentencas_normas", "afirmacao_regras", "ragas", "minicheck"):
            if (j, m) not in V:
                continue
            cel = []
            for alvo in (0.05, 0.10, 0.20):
                pt, c = far_em_fa(V[(j, m)], alvo)
                J["M6"].setdefault(f"{j}|{m}", {})[str(alvo)] = {"far": pt, "ic": c}
                cel.append(f"{f(pt)} [{f(c[0])}; {f(c[1])}]")
            L.append(f"| {m} | {NOME[j]} | " + " | ".join(cel) + " |")
    L += ["", "VPP (fração dos bloqueios que têm erro crítico) e carga de revisão (fração das respostas bloqueadas), "
          "pela sensibilidade e pelo falso alarme medidos, em prevalências de erro crítico de 1%, 2% e 5%.", "",
          "| Modelo | Juiz e ponto | sensibilidade | falso alarme | VPP 1% | VPP 2% | VPP 5% | carga 2% |", "|---|---|---|---|---|---|---|---|"]
    for m in LOCAIS:
        pontos = []
        if ("afirmacao_regras", m) in V:
            fa, fc = (float(x) for x in taxas(V[("afirmacao_regras", m)], np.ones(len(IDS))))
            pontos.append(("proposto, m = 1", 1 - fc, fa))
            for alvo in (0.10, 0.20):
                pt = J["M6"][f"afirmacao_regras|{m}"][str(alvo)]["far"]
                pontos.append((f"proposto, FA {f(alvo)}", 1 - pt, alvo))
        if ("holistico_conformidade", m) in V:
            fa, fc = (float(x) for x in taxas(V[("holistico_conformidade", m)], np.ones(len(IDS))))
            pontos.append(("holístico só conformidade", 1 - fc, fa))
        for nome_p, sens, fa in pontos:
            vpp = [sens * p / (sens * p + fa * (1 - p)) if (sens * p + fa * (1 - p)) else math.nan for p in (0.01, 0.02, 0.05)]
            carga = sens * 0.02 + fa * 0.98
            J["M6"].setdefault("vpp", {})[f"{m}|{nome_p}"] = {"sens": sens, "fa": fa, "vpp": vpp, "carga2": carga}
            L.append(f"| {m} | {nome_p} | {f(sens)} | {f(fa)} | {f(vpp[0], 3)} | {f(vpp[1], 3)} | {f(vpp[2], 3)} | {f(carga)} |")
    L += ["", "Barreira de três saídas do verificador: bloqueia se alguma afirmação é contestada; escala se nenhuma é "
          "contestada mas alguma é \"insuficiente\"; aprova o resto.", "",
          "| Modelo | sem erro: aprova / escala / bloqueia | erro crítico: aprova / escala / bloqueia | automação (aprova+bloqueia) | FAR-crítico só nos aprovados |",
          "|---|---|---|---|---|"]
    for m in LOCAIS + ["claude-haiku-5-5"]:
        if ("afirmacao_regras", m) not in D:
            continue
        R = D[("afirmacao_regras", m)]
        sai = []
        for r in R:
            vs = [str(v.get("veredito", "")).lower() for v in r["vereditos"]]
            sai.append("bloqueia" if any(x.startswith("contest") for x in vs) else
                       ("escala" if any(x.startswith("insuf") for x in vs) else "aprova"))
        sai = np.array(sai)
        v = V[("afirmacao_regras", m)]
        lim, cri = v["limpo"] > 0, v["crit"] > 0
        pl = [np.mean(sai[lim] == s) for s in ("aprova", "escala", "bloqueia")]
        pc = [np.mean(sai[cri] == s) for s in ("aprova", "escala", "bloqueia")]
        auto = np.mean(sai != "escala")
        J["M6"].setdefault("tres_saidas", {})[m] = {"limpo": pl, "critico": pc, "automacao": float(auto)}
        L.append(f"| {m} | {' / '.join(f(x) for x in pl)} | {' / '.join(f(x) for x in pc)} | {f(auto)} | {f(pc[0])} |")
    L.append("")

    # ---------------- M7
    anot, nossa = gravidade_anotadora()
    L += ["## M7. FAR-crítico com a gravidade da anotadora", "",
          f"Fatos críticos: nossos {len(nossa & {a['fato_id'] for d in GAB.values() for a in d['afirmacoes']})}, "
          f"da anotadora {len(anot)}, união {len(anot | nossa)}.", "",
          "| Modelo | Juiz | nossa gravidade | anotadora | união | H1 exato (hol. − prop.), anotadora [IC] |", "|---|---|---|---|---|---|"]
    J["M7"] = {}
    for m in LOCAIS:
        for j in ("holistico", "holistico_conformidade", "holistico_sentencas_normas", "afirmacao_regras"):
            if (j, m) not in D:
                continue
            res = []
            for cf in (None, anot, anot | nossa):
                v = vet(D[(j, m)], crit_fatos=cf)
                res.append(float(taxas(v, np.ones(len(IDS)))[1]))
            h1 = ""
            if j == "holistico" and ("afirmacao_regras", m) in D:
                hh = hull_dif(vet(D[(j, m)], crit_fatos=anot), vet(D[("afirmacao_regras", m)], crit_fatos=anot))
                h1 = f"{f(hh['dif'])} [{f(hh['ic'][0])}; {f(hh['ic'][1])}]"
                J["M7"][f"H1|{m}"] = hh
            J["M7"][f"{j}|{m}"] = res
            n_crit_anot = int(vet(D[(j, m)], crit_fatos=anot)["crit"].sum())
            L.append(f"| {m} | {NOME[j]} | {f(res[0])} | {f(res[1])} | {f(res[2])} | {h1} |")
    L += ["", f"Respostas com erro crítico: nossa gravidade 135; anotadora {n_crit_anot}; "
          f"união {int(vet(D[('holistico', LOCAIS[0])], crit_fatos=anot | nossa)['crit'].sum())}.", ""]

    # ---------------- fail-closed
    L += ["## Saídas inválidas: como implementado x fail-open (aprova) x fail-closed (bloqueia)", "",
          "Como implementado: na decisão binária, o holístico com saída inválida fica com aprovada = False (bloqueia); "
          "na nota, vale 5 (aprova); no verificador, veredito inválido não contesta (aprova).", "",
          "| Modelo | Juiz | inválidas | inválidas bloqueadas como implementado | falso alarme (impl. / open / closed) | FAR-crítico (impl. / open / closed) |",
          "|---|---|---|---|---|---|"]
    for (j, m), R in sorted(D.items(), key=lambda x: (x[0][1], x[0][0])):
        inv = np.array([invalida(r) for r in R], bool)
        if not inv.any() or (j == "minicheck" and m != LOCAIS[0]):
            continue
        um = np.ones(len(IDS))
        a, o, c = taxas(V[(j, m)], um), taxas(vet(R, fail_open=True), um), taxas(vet(R, fail_closed=True), um)
        bloq = int(V[(j, m)]["rej"][inv].sum())
        J.setdefault("invalidas", {})[f"{j}|{m}"] = {"n": int(inv.sum()), "bloqueadas_impl": bloq,
                                                     "fa": [float(a[0]), float(o[0]), float(c[0])], "far": [float(a[1]), float(o[1]), float(c[1])]}
        L.append(f"| {m} | {NOME[j]} | {int(inv.sum())} | {bloq} | {f(a[0])} / {f(o[0])} / {f(c[0])} | {f(a[1])} / {f(o[1])} / {f(c[1])} |")
    L.append("")

    # ---------------- limiares
    L += ["## Sensibilidade do limiar de localização em texto livre (F1 nas respostas com erro)", "",
          "| Modelo | Juiz | 30% | 40% | 50% |", "|---|---|---|---|---|"]
    for m in LOCAIS:
        for j in ("holistico", "holistico_normas", "holistico_conformidade"):
            if (j, m) not in D:
                continue
            vals = [A.loc_somas(tabela_af(D[(j, m)], lim), np.ones(len(IDS)), np.ones(len(A.FATOS)))[2] for lim in (0.3, 0.4, 0.5)]
            J.setdefault("limiar_loc", {})[f"{j}|{m}"] = [float(x) for x in vals]
            L.append(f"| {m} | {NOME[j]} | " + " | ".join(f(float(x)) for x in vals) + " |")
    L += ["", "## Sensibilidade do Jaccard do alinhamento fim a fim", "",
          "| Modelo | Jaccard | alinhadas | FAR-crítico resp. | falso alarme resp. | FAR-crít. afirm. |", "|---|---|---|---|---|---|"]
    for m in LOCAIS:
        if ("afirmacao_regras_e2e", m) not in D:
            continue
        for lim in (0.4, 0.5, 0.6):
            R = jaccard_realinhar(D[("afirmacao_regras_e2e", m)], lim)
            al = np.mean([x is not None for r in R for x in r["por_gold"]])
            fa, fc = (float(x) for x in taxas(vet(R), np.ones(len(IDS))))
            t4 = A.tab4(tabela_por_gold(R))
            J.setdefault("jaccard", {})[f"{m}|{lim}"] = {"alinhadas": float(al), "fa": fa, "far": fc, "far_af": t4["FAR_crit"][0]}
            L.append(f"| {m} | {f(lim, 1)} | {f(al)} | {f(fc)} | {f(fa)} | {f(t4['FAR_crit'][0])} |")
    L.append("")

    (RES / "analise_emenda3.md").write_text("\n".join(L), encoding="utf-8")
    (RES / "analise_emenda3.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
