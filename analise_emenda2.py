"""Análise da emenda 2 e do bloco 2 do orientador. Escreve resultados/analise_emenda2.md e .json.

1b  Localização única para todos os juízes, só nas respostas com erro:
      precisão = afirmações apontadas que são erros reais; recall = erros apontados; F1.
    Como cada juiz "aponta" uma afirmação:
      - verificador: veredito "contesta";
      - holístico por sentença: id listado em sentencas_nao_conformes;
      - holístico em texto livre: um problema listado cobre >= 40% dos termos da afirmação (o critério da H5).
    Acurácia de citação: entre os erros apontados com dispositivo citado, a fração em que o artigo citado
    é o do gabarito (estrita: artigo e número da norma; branda: só o artigo).
B2  IC por bootstrap em dois níveis (diálogo x fato; 10.000 réplicas, semente 7) nas métricas por afirmação;
    IC por diálogo nas métricas por resposta.
B2  Falso alarme pareado por limiar aleatorizado no envelope convexo da curva ROC do holístico (nota 1-5).
H6  F1 de localização: holístico por sentença com normas x verificador (pareado por modelo).
H7  Holístico x holístico restrito à conformidade: rejeição de respostas sem erro (McNemar exato, Holm).
1d/1e  Sensibilidade: tudo de novo sem os 15 diálogos com os 5 erros que o segundo anotador marcou como ambíguos (inclui o F26, "35%").
Juízes ou modelos sem arquivo completo são pulados (a análise roda de novo quando a GPU terminar).
"""
import json
import math
import re
from pathlib import Path

import numpy as np

import metricas as M

AQUI = Path(__file__).parent
RES = AQUI / "resultados"
MODELOS = ["qwen3.5-9b", "gemma4-12b", "llama3.1-8b", "gpt-oss-20b", "claude-haiku-5-5"]
JUIZES = ["holistico", "holistico_normas", "holistico_conformidade", "holistico_sentencas",
          "holistico_sentencas_normas", "afirmacao", "afirmacao_regras", "afirmacao_sem_rag"]
NOME = {"holistico": "holístico", "holistico_normas": "holístico + normas",
        "holistico_conformidade": "holístico (só conformidade)", "holistico_sentencas": "holístico por sentença",
        "holistico_sentencas_normas": "holístico por sentença + normas", "afirmacao": "por afirmação, sem regras",
        "afirmacao_regras": "por afirmação + regras (proposto)", "afirmacao_sem_rag": "por afirmação, sem recuperação"}
# erros que o segundo anotador marcou como "ambíguo" (item 1e; inclui o F26 da revisão 1d)
AMBIGUO = {"O limite do consignado CLT é 35% da sua remuneração.",
           "A segunda via do cartão é sempre gratuita, mesmo em caso de perda ou roubo.",
           "Se a parcela não couber no mês, ela pode entrar no rotativo normalmente.",
           "A poupança tem os mesmos quatro saques grátis da conta corrente.",
           "As duas transferências grátis da poupança valem pra qualquer conta, de qualquer pessoa."}
B = 10_000

GAB = M.carregar_gabarito()
IDS = sorted(GAB)
IX = {i: k for k, i in enumerate(IDS)}
FATOS = sorted({a["fato_id"] for d in GAB.values() for a in d["afirmacoes"]})
FX = {f: k for k, f in enumerate(FATOS)}
rng = np.random.default_rng(7)
WD = rng.multinomial(len(IDS), [1 / len(IDS)] * len(IDS), size=B).astype(float)
WF = rng.multinomial(len(FATOS), [1 / len(FATOS)] * len(FATOS), size=B).astype(float)
SEM_AMB = np.array([not any(a["texto"] in AMBIGUO for a in GAB[i]["afirmacoes"]) for i in IDS], dtype=float)


def carregar(juiz, modelo):
    f = RES / f"{juiz}__{modelo}__oraculo__hibrida__dialogos.jsonl"
    if not f.exists():
        return None
    R = {r["id"]: r for r in (json.loads(l) for l in f.open(encoding="utf-8"))}
    return [R[i] for i in IDS] if sorted(R) == IDS else None


# ----------------------------------------------------------------- o que cada juiz aponta
def _num(s):
    return re.sub(r"[.\s]", "", s)


def cita_certo(citado, a):
    """(estrita, branda): o dispositivo citado é o do gabarito?"""
    if not citado:
        return None
    c = str(citado).lower()
    arts = {m.group(1) + (m.group(2) or "").upper() for m in re.finditer(r"art(?:igo)?\.?\s*(\d+)\s*[º°o]?\s*(-[a-z])?", c)}
    gold = a["artigo"].upper().replace("º", "")
    branda = gold in arts
    numero = _num(a["norma"].split("-")[1])
    estrita = branda and numero in _num(c)
    return estrita, branda


def apontadas(r, d):
    """Lista por afirmação do gabarito: (apontada?, dispositivo citado ou None)."""
    afs = d["afirmacoes"]
    if "vereditos" in r:
        return [(M.contestada(v) if hasattr(M, "contestada") else str(v.get("veredito", "")).lower().startswith("contest"),
                 v.get("dispositivo") or None) for v in r["vereditos"]]
    if "por_gold_sent" in r:
        cit = {}
        for x in (r["bruto"].get("sentencas_nao_conformes") or []):
            if isinstance(x, dict):
                m = re.search(r"\d+", str(x.get("id", "")))
                if m:
                    cit[int(m.group())] = x.get("dispositivo") or None
        return [(bool(f), cit.get(k + 1)) for k, f in enumerate(r["por_gold_sent"])]
    probs = [M._tok(p) for p in (r.get("bruto", {}).get("problemas") or [])]
    out = []
    for a in afs:
        t = M._tok(a["texto"])
        out.append((bool(t) and any(len(t & p) / len(t) >= 0.4 for p in probs), None))
    return out


def tabela_afirmacoes(R):
    """Uma linha por afirmação do gabarito: diálogo, fato, erro?, apontada?, citação."""
    L = []
    for r in R:
        d = GAB[r["id"]]
        for a, (ap, cit) in zip(d["afirmacoes"], apontadas(r, d)):
            L.append({"d": IX[r["id"]], "f": FX[a["fato_id"]], "erro": not a["correta"], "ap": ap,
                      "resp_com_erro": d["n_erros"] > 0, "cit": cita_certo(cit, a) if (ap and not a["correta"]) else None,
                      "amb": a["texto"] in AMBIGUO,
                      "crit": (not a["correta"]) and a.get("gravidade") == "critica"})
    return L


def tab4(L):
    """Tabela 4 (todas as afirmações): FAR-crítico, falso alarme, precisão, recall, IC de dois níveis."""
    d = np.array([x["d"] for x in L]); f = np.array([x["f"] for x in L])
    ap = np.array([x["ap"] for x in L], float); er = np.array([x["erro"] for x in L], float)
    cr = np.array([x["crit"] for x in L], float)
    def m(w_d, w_f):
        W = w_d[..., d] * w_f[..., f]
        with np.errstate(invalid="ignore", divide="ignore"):
            return ((W @ (cr * (1 - ap))) / (W @ cr), (W @ ((1 - er) * ap)) / (W @ (1 - er)),
                    (W @ (ap * er)) / (W @ ap), (W @ (ap * er)) / (W @ er))
    pt, bt = m(np.ones(len(IDS)), np.ones(len(FATOS))), m(WD, WF)
    return {k: (float(a), ic(b)) for k, a, b in zip(("FAR_crit", "falso_alarme", "precisao", "recall"), pt, bt)}


def loc_somas(L, w_d, w_f, sem_amb=False):
    """Somas ponderadas (B x ...) para precisão/recall/F1 nas respostas com erro."""
    sel = [x for x in L if x["resp_com_erro"] and not (sem_amb and x["amb"])]
    d = np.array([x["d"] for x in sel]); f = np.array([x["f"] for x in sel])
    ap = np.array([x["ap"] for x in sel], float); er = np.array([x["erro"] for x in sel], float)
    W = w_d[..., d] * w_f[..., f]
    tp, fl, ee = W @ (ap * er), W @ ap, W @ er
    with np.errstate(invalid="ignore", divide="ignore"):
        p, rc = tp / fl, tp / ee
        f1 = 2 * p * rc / (p + rc)
    return p, rc, f1


def loc(L, sem_amb=False):
    um_d, um_f = np.ones(len(IDS)), np.ones(len(FATOS))
    if sem_amb:
        um_d = SEM_AMB
    pt = loc_somas(L, um_d, um_f, sem_amb)
    bt = loc_somas(L, WD * (SEM_AMB if sem_amb else 1), WF, sem_amb)
    return {k: (float(a), ic(b)) for k, a, b in zip(("precisao", "recall", "F1"), pt, bt)}, bt


def citacao(L):
    c = [x["cit"] for x in L if x["ap"] and x["erro"]]
    com = [x for x in c if x is not None]
    if not c:
        return None
    return {"erros_apontados": len(c), "com_dispositivo": len(com),
            "estrita": sum(x[0] for x in com) / len(com) if com else None,
            "branda": sum(x[1] for x in com) / len(com) if com else None}


# ----------------------------------------------------------------- por resposta
def vet_resposta(R):
    us = M.unidades(R, GAB)
    return {"crit": np.array([u["tem_critico"] for u in us], float), "limpo": np.array([u["sem_erro"] for u in us], float),
            "rej": np.array([not u["aprovada"] for u in us], float), "susp": np.array([u["susp"] for u in us], float)}


def taxa(num, den, w):
    with np.errstate(invalid="ignore", divide="ignore"):
        return (w @ num) / (w @ den)


def ic(b):
    b = np.asarray(b)
    b = b[~np.isnan(b)]
    return (float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))) if len(b) else (math.nan, math.nan)


def resp_metricas(v, mask=None):
    m = np.ones(len(IDS)) if mask is None else mask
    fa = taxa(v["limpo"] * v["rej"], v["limpo"], m); fab = taxa(v["limpo"] * v["rej"], v["limpo"], WD * m)
    fc = taxa(v["crit"] * (1 - v["rej"]), v["crit"], m); fcb = taxa(v["crit"] * (1 - v["rej"]), v["crit"], WD * m)
    return {"falso_alarme": (float(fa), ic(fab)), "FAR_crit": (float(fc), ic(fcb))}


# ----------------------------------------------------------------- ROC: envelope convexo
def _hull_tpr(fpr, tpr, alvo):
    """TPR no envelope convexo superior da ROC, no FPR alvo (limiar aleatorizado entre dois vértices)."""
    pts = sorted(set(zip(fpr, tpr)) | {(0.0, 0.0), (1.0, 1.0)})
    H = []
    for p in pts:
        while len(H) >= 2 and (H[-1][0] - H[-2][0]) * (p[1] - H[-2][1]) - (H[-1][1] - H[-2][1]) * (p[0] - H[-2][0]) >= 0:
            H.pop()
        H.append(p)
    for (x0, y0), (x1, y1) in zip(H, H[1:]):
        if x0 <= alvo <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (alvo - x0) / (x1 - x0)
    return math.nan


def far_pareado_hull(vh, fa_alvo_pt, fa_alvo_boot):
    """FAR-crítico do holístico com o mesmo falso alarme do verificador (por réplica)."""
    ts = np.unique(vh["susp"])
    Ind = (vh["susp"][:, None] >= ts[None, :]).astype(float)  # reprova se suspeita >= t
    def curva(w):
        fpr = ((w * vh["limpo"]) @ Ind) / np.expand_dims(w @ vh["limpo"], -1)
        tpr = ((w * vh["crit"]) @ Ind) / np.expand_dims(w @ vh["crit"], -1)
        return fpr, tpr
    fpr, tpr = curva(np.ones(len(IDS)))
    pt = 1 - _hull_tpr(list(fpr), list(tpr), fa_alvo_pt)
    fb, tb = curva(WD)
    boot = np.array([1 - _hull_tpr(list(fb[b]), list(tb[b]), fa_alvo_boot[b]) for b in range(B)])
    return pt, boot


def mcnemar(a, b):
    """a, b: vetores 0/1 pareados. Teste exato bilateral sobre os discordantes."""
    n01 = int(((a == 0) & (b == 1)).sum()); n10 = int(((a == 1) & (b == 0)).sum())
    n = n01 + n10
    if n == 0:
        return n01, n10, 1.0
    k = min(n01, n10)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
    return n01, n10, p


def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, mx = [0.0] * len(ps), 0.0
    for r, i in enumerate(o):
        mx = max(mx, (len(ps) - r) * ps[i]); adj[i] = min(1.0, mx)
    return adj


def f(x, p=2):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{p}f}".replace(".", ",")


def fic(t):
    v, (a, b) = t
    return f"{f(v)} [{f(a)}; {f(b)}]"


# ----------------------------------------------------------------- principal
def main():
    D = {(j, m): carregar(j, m) for j in JUIZES for m in MODELOS}
    D = {k: v for k, v in D.items() if v is not None}
    modelos = [m for m in MODELOS if any(k[1] == m for k in D)]
    J = {"modelos": modelos, "juizes": sorted({k[0] for k in D})}
    L = ["# Análise da emenda 2 e do bloco 2 (gerado por analise_emenda2.py)", "",
         f"Juízes/modelos com arquivo completo: {len(D)}. IC 95% por bootstrap (10.000 réplicas, semente 7): "
         "dois níveis (diálogo × fato) nas métricas por afirmação; por diálogo nas métricas por resposta.", ""]

    # 1b: localização
    L += ["## 1b. Localização (respostas com erro)", "",
          "| Modelo | Juiz | precisão | recall | F1 | citação estrita | citação branda | erros apontados com dispositivo |",
          "|---|---|---|---|---|---|---|---|"]
    TAB, F1B = {}, {}
    for m in modelos:
        for j in JUIZES:
            if (j, m) not in D:
                continue
            T = TAB[(j, m)] = tabela_afirmacoes(D[(j, m)])
            lo, bt = loc(T)
            F1B[(j, m)] = bt[2]
            c = citacao(T) or {}
            J.setdefault("localizacao", {})[f"{j}|{m}"] = {"loc": lo, "citacao": c}
            L.append(f"| {m} | {NOME[j]} | {fic(lo['precisao'])} | {fic(lo['recall'])} | {fic(lo['F1'])} | "
                     f"{f(c.get('estrita'))} | {f(c.get('branda'))} | "
                     f"{c.get('com_dispositivo', '—')}/{c.get('erros_apontados', '—')} |")
    L.append("")

    # Tabela 4 com IC de dois níveis
    L += ["## Tabela 4. Por afirmação, todas as respostas (IC de dois níveis)", "",
          "| Modelo | Juiz | FAR-crítico | falso alarme | precisão | recall |", "|---|---|---|---|---|---|"]
    for m in modelos:
        for j in ("afirmacao", "afirmacao_regras", "afirmacao_sem_rag"):
            if (j, m) in TAB:
                t = tab4(TAB[(j, m)])
                J.setdefault("tabela4", {})[f"{j}|{m}"] = t
                L.append(f"| {m} | {NOME[j]} | {fic(t['FAR_crit'])} | {fic(t['falso_alarme'])} | "
                         f"{fic(t['precisao'])} | {fic(t['recall'])} |")
    L.append("")

    # H6
    L += ["## H6. F1 de localização: holístico por sentença com normas − verificador proposto", "",
          "| Modelo | ΔF1 (holístico sent.+normas − proposto) | IC 95% | ΔF1 (holístico sent. − proposto) | IC 95% |", "|---|---|---|---|---|"]
    for m in modelos:
        lin = [m]
        for j in ("holistico_sentencas_normas", "holistico_sentencas"):
            if (j, m) in TAB and ("afirmacao_regras", m) in TAB:
                pt = loc(TAB[(j, m)])[0]["F1"][0] - loc(TAB[("afirmacao_regras", m)])[0]["F1"][0]
                lin += [f(pt), "[{}; {}]".format(*map(f, ic(F1B[(j, m)] - F1B[("afirmacao_regras", m)])))]
                J.setdefault("H6", {})[f"{j}|{m}"] = {"dF1": pt, "ic": ic(F1B[(j, m)] - F1B[("afirmacao_regras", m)])}
            else:
                lin += ["—", "—"]
        L.append("| " + " | ".join(lin) + " |")
    L.append("")

    # por resposta + sensibilidade 1d
    L += ["## Por resposta (com e sem os 15 diálogos dos 5 erros ambíguos)", "",
          "| Modelo | Juiz | falso alarme | FAR-crítico | falso alarme (sem amb.) | FAR-crítico (sem amb.) |", "|---|---|---|---|---|---|"]
    V = {}
    for m in modelos:
        for j in JUIZES:
            if (j, m) not in D:
                continue
            v = V[(j, m)] = vet_resposta(D[(j, m)])
            a, s = resp_metricas(v), resp_metricas(v, SEM_AMB)
            J.setdefault("resposta", {})[f"{j}|{m}"] = {"todos": a, "sem_ambiguo": s}
            L.append(f"| {m} | {NOME[j]} | {fic(a['falso_alarme'])} | {fic(a['FAR_crit'])} | "
                     f"{fic(s['falso_alarme'])} | {fic(s['FAR_crit'])} |")
    L.append("")

    # H7
    L += ["## H7. Rejeição de respostas sem erro: holístico x holístico só conformidade (McNemar exato, Holm na família de 4)", "",
          "| Modelo | falso alarme holístico | falso alarme só conformidade | discordantes (só hol. / só conf.) | p | p Holm |", "|---|---|---|---|---|---|"]
    lin, ps = [], []
    for m in modelos:
        if ("holistico", m) in V and ("holistico_conformidade", m) in V:
            a, b = V[("holistico", m)], V[("holistico_conformidade", m)]
            sel = a["limpo"].astype(bool)
            n01, n10, p = mcnemar(a["rej"][sel], b["rej"][sel])
            lin.append((m, a["rej"][sel].mean(), b["rej"][sel].mean(), n10, n01, p)); ps.append(p)
    pre = [i for i, x in enumerate(lin) if x[0] != "claude-haiku-5-5"]
    adj = holm([ps[i] for i in pre]); adj_d = {pre[k]: adj[k] for k in range(len(pre))}
    for i, (m, fa_h, fa_c, n10, n01, p) in enumerate(lin):
        L.append(f"| {m} | {f(fa_h)} | {f(fa_c)} | {n10} / {n01} | {f(p, 4)} | {f(adj_d.get(i), 4) if i in adj_d else 'exploratório'} |")
        J.setdefault("H7", {})[m] = {"fa_hol": fa_h, "fa_conf": fa_c, "so_hol": n10, "so_conf": n01, "p": p, "p_holm": adj_d.get(i)}
    L.append("")

    # Falso alarme pareado pelo envelope convexo
    L += ["## Comparação pareada pelo envelope convexo da ROC (H1 refeita)", "",
          "FAR-crítico do holístico no **mesmo falso alarme** do verificador proposto, com limiar aleatorizado entre "
          "dois vértices do envelope convexo da curva ROC da nota 1-5.", "",
          "| Modelo | Juiz holístico | falso alarme do proposto | FAR-crítico do proposto | FAR-crítico do holístico pareado | diferença (hol. − prop.) [IC 95%] |",
          "|---|---|---|---|---|---|"]
    for m in modelos:
        if ("afirmacao_regras", m) not in V:
            continue
        vp = V[("afirmacao_regras", m)]
        fa_pt = float(taxa(vp["limpo"] * vp["rej"], vp["limpo"], np.ones(len(IDS))))
        fa_b = taxa(vp["limpo"] * vp["rej"], vp["limpo"], WD)
        fc_pt = float(taxa(vp["crit"] * (1 - vp["rej"]), vp["crit"], np.ones(len(IDS))))
        fc_b = taxa(vp["crit"] * (1 - vp["rej"]), vp["crit"], WD)
        for j in ("holistico", "holistico_normas", "holistico_conformidade", "holistico_sentencas", "holistico_sentencas_normas"):
            if (j, m) not in V:
                continue
            pt, bt = far_pareado_hull(V[(j, m)], fa_pt, fa_b)
            d = bt - fc_b
            J.setdefault("hull", {})[f"{j}|{m}"] = {"fa_prop": fa_pt, "far_prop": fc_pt, "far_hol": pt, "dif": pt - fc_pt, "ic": ic(d)}
            L.append(f"| {m} | {NOME[j]} | {f(fa_pt)} | {f(fc_pt)} | {f(pt)} | {f(pt - fc_pt)} [{f(ic(d)[0])}; {f(ic(d)[1])}] |")
    L.append("")

    # Ablação de recuperação
    L += ["## Ablação: sem recuperação x por afirmação sem regras (por afirmação, todas as respostas)", "",
          "| Modelo | juiz | falso alarme por afirmação | recall de erros |", "|---|---|---|---|"]
    for m in modelos:
        for j in ("afirmacao", "afirmacao_sem_rag"):
            if (j, m) not in TAB:
                continue
            T = TAB[(j, m)]
            ok = [x for x in T if not x["erro"]]; er = [x for x in T if x["erro"]]
            L.append(f"| {m} | {NOME[j]} | {f(sum(x['ap'] for x in ok) / len(ok))} | {f(sum(x['ap'] for x in er) / len(er))} |")
    L.append("")

    (RES / "analise_emenda2.md").write_text("\n".join(L), encoding="utf-8")
    (RES / "analise_emenda2.json").write_text(json.dumps(J, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
