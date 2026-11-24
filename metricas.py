"""Métricas (Dia 5): compara juízes contra o gabarito dos erros plantados.

Nível da resposta (todos os juízes):
  FAR-crítico   = fração das respostas COM erro crítico que o juiz aprovou (falso aprovado)
  falso alarme  = fração das respostas SEM erro que o juiz reprovou
Nível da afirmação (juízes por afirmação):
  FAR-crítico   = fração das afirmações com erro crítico não contestadas
  falso alarme  = fração das afirmações corretas contestadas
  recall por categoria de erro; precisão e F1 da contestação
IC 95% por bootstrap com reamostragem por diálogo (cluster), 10.000 réplicas.
McNemar exato pareado entre dois juízes (nível da resposta, respostas com erro crítico).

Emenda de 23/11/2026 (após o piloto, em que o holístico reprovou tudo):
  - suspeição contínua por resposta: holístico = 6 - nota; por afirmação = nº de
    afirmações contestadas. AUC (respostas com erro crítico x respostas sem erro).
  - varredura do corte da nota do holístico (reprova se nota <= t), para comparar
    o FAR-crítico com o mesmo falso alarme do outro juiz ("pareado em falso alarme").
  - localização: a lista de problemas do holístico aponta a afirmação errada?
    (sobreposição de palavras: ≥ 40% das palavras da afirmação no texto do problema)

Uso:
  python metricas.py resultados/*.jsonl
  python metricas.py resultados/A.jsonl resultados/B.jsonl --mcnemar
"""
import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).parent
B = 10_000


def carregar_gabarito(arquivo="dialogos.jsonl") -> dict:
    return {d["id"]: d for d in (json.loads(l) for l in (AQUI / arquivo).open(encoding="utf-8"))}


def unidades(res: list[dict], gab: dict) -> list[dict]:
    """Um registro por diálogo com o necessário para todas as métricas."""
    out = []
    for r in res:
        d = gab[r["id"]]
        cont = r.get("por_gold") or []
        nota = r.get("nota")
        if "por_gold" not in r and nota is None:
            nota = 5  # JSON inválido/timeout no holístico = aprovado com nota máxima (pior caso, pré-registro)
        susp = (6 - float(nota)) if "por_gold" not in r else float(sum(bool(x) for x in cont))
        u = {"id": r["id"], "aprovada": r["aprovada"], "nota": nota if "por_gold" not in r else None, "susp": susp,
             "estrato": d.get("estrato", "misto"),
             "tem_critico": d["n_erros_criticos"] > 0, "sem_erro": d["n_erros"] == 0, "afs": [],
             "localizacao": localizar(r, d) if r.get("bruto", {}).get("problemas") is not None else None}
        if r.get("por_gold") is not None:
            for a, cont in zip(d["afirmacoes"], r["por_gold"]):
                u["afs"].append({"correta": a["correta"], "critica": a["gravidade"] == "critica",
                                 "cat": a["categoria_erro"], "contestada": bool(cont), "dificil": a["dificil"]})
        out.append(u)
    return out


def _tok(s):
    from recuperar import tokens
    return set(tokens(str(s)))


def localizar(r: dict, d: dict) -> dict:
    """Problemas listados pelo holístico x afirmações erradas do gabarito."""
    probs = [_tok(p) for p in (r["bruto"].get("problemas") or [])]
    erradas = [_tok(a["texto"]) for a in d["afirmacoes"] if not a["correta"]]
    certas = [_tok(a["texto"]) for a in d["afirmacoes"] if a["correta"]]
    bate = lambda af, p: af and len(af & p) / len(af) >= 0.4
    achou = sum(any(bate(e, p) for p in probs) for e in erradas)
    prob_em_erro = sum(any(bate(e, p) for e in erradas) for p in probs)
    prob_em_certa = sum(any(bate(c, p) for c in certas) and not any(bate(e, p) for e in erradas) for p in probs)
    return {"erradas": len(erradas), "localizadas": achou, "problemas": len(probs),
            "problemas_em_erro": prob_em_erro, "problemas_em_certa": prob_em_certa}


def auc(us: list[dict]) -> float:
    pos = [u["susp"] for u in us if u["tem_critico"]]
    neg = [u["susp"] for u in us if u["sem_erro"]]
    if not pos or not neg:
        return float("nan")
    ganha = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return ganha / (len(pos) * len(neg))


def varredura_nota(us: list[dict]) -> list[dict]:
    """Holístico: reprova se nota <= t. Devolve FAR-crítico e falso alarme por corte."""
    if not us or us[0]["nota"] is None:
        return []
    crit = [u for u in us if u["tem_critico"]]
    limpo = [u for u in us if u["sem_erro"]]
    out = []
    for t in range(0, 6):
        far = sum(float(u["nota"]) > t for u in crit) / len(crit) if crit else float("nan")
        fa = sum(float(u["nota"]) <= t for u in limpo) / len(limpo) if limpo else float("nan")
        out.append({"reprova_se_nota<=": t, "FAR_critico": round(far, 3), "falso_alarme": round(fa, 3)})
    return out


def metricas(us: list[dict]) -> dict:
    m = {}
    crit = [u for u in us if u["tem_critico"]]
    limpo = [u for u in us if u["sem_erro"]]
    m["resp_FAR_critico"] = sum(u["aprovada"] for u in crit) / len(crit) if crit else float("nan")
    m["resp_falso_alarme"] = sum(not u["aprovada"] for u in limpo) / len(limpo) if limpo else float("nan")
    m["resp_AUC"] = auc(us)
    loc = [u["localizacao"] for u in us if u["localizacao"]]
    if loc:
        e = sum(x["erradas"] for x in loc)
        p = sum(x["problemas"] for x in loc)
        m["loc_erros_localizados"] = sum(x["localizadas"] for x in loc) / e if e else float("nan")
        m["loc_problemas_que_apontam_erro"] = sum(x["problemas_em_erro"] for x in loc) / p if p else float("nan")
        m["loc_problemas_que_acusam_certa"] = sum(x["problemas_em_certa"] for x in loc) / p if p else float("nan")
    afs = [a for u in us for a in u["afs"]]
    if afs:
        ec = [a for a in afs if not a["correta"] and a["critica"]]
        ok = [a for a in afs if a["correta"]]
        err = [a for a in afs if not a["correta"]]
        tp = sum(a["contestada"] for a in err)
        fp = sum(a["contestada"] for a in ok)
        m["af_FAR_critico"] = sum(not a["contestada"] for a in ec) / len(ec) if ec else float("nan")
        m["af_falso_alarme"] = fp / len(ok) if ok else float("nan")
        prec = tp / (tp + fp) if tp + fp else float("nan")
        rec = tp / len(err) if err else float("nan")
        m["af_precisao"], m["af_recall"] = prec, rec
        m["af_F1"] = 2 * prec * rec / (prec + rec) if prec + rec and not math.isnan(prec) else float("nan")
        cats = defaultdict(list)
        for a in err:
            cats[a["cat"]].append(a["contestada"])
        for c, v in cats.items():
            m[f"af_recall_{c}"] = sum(v) / len(v)
        dif = [a["contestada"] for a in err if a["dificil"]]
        if dif:
            m["af_recall_dificeis"] = sum(dif) / len(dif)
    return m


def bootstrap(us: list[dict], semente=7) -> dict:
    rng = random.Random(semente)
    base = metricas(us)
    amostras = defaultdict(list)
    for _ in range(B):
        mb = metricas([rng.choice(us) for _ in us])
        for k, v in mb.items():
            if not math.isnan(v):
                amostras[k].append(v)
    ic = {}
    for k, v in base.items():
        a = sorted(amostras[k])
        ic[k] = (v, a[int(0.025 * len(a))], a[int(0.975 * len(a)) - 1]) if a else (v, None, None)
    return ic


def mcnemar(ua: list[dict], ub: list[dict]) -> dict:
    """Respostas com erro crítico: b = A pega e B não; c = B pega e A não. Binomial exato bicaudal."""
    pa = {u["id"]: not u["aprovada"] for u in ua if u["tem_critico"]}
    pb = {u["id"]: not u["aprovada"] for u in ub if u["tem_critico"]}
    ids = pa.keys() & pb.keys()
    b = sum(pa[i] and not pb[i] for i in ids)
    c = sum(pb[i] and not pa[i] for i in ids)
    n = b + c
    p = min(1.0, 2 * sum(math.comb(n, x) for x in range(0, min(b, c) + 1)) / 2 ** n) if n else 1.0
    return {"n_pares": len(ids), "A_pega_B_nao": b, "B_pega_A_nao": c, "p_exato": p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--gabarito", default="dialogos.jsonl")
    ap.add_argument("--mcnemar", action="store_true")
    a = ap.parse_args()
    gab = carregar_gabarito(a.gabarito)
    todos = {}
    for arq in a.arquivos:
        res = [json.loads(l) for l in open(arq, encoding="utf-8")]
        us = unidades(res, gab)
        todos[arq] = us
        custo = [r["custo"] for r in res]
        print(f"\n== {Path(arq).stem}  (n={len(us)} diálogos)")
        for k, (v, lo, hi) in bootstrap(us).items():
            ic = f"[{lo:.3f}; {hi:.3f}]" if lo is not None else ""
            print(f"  {k:24} {v:.3f} {ic}")
        for v in varredura_nota(us):
            print("  corte:", v)
        porest = {}
        for u in us:
            porest.setdefault(u["estrato"], []).append(u)
        if len(porest) > 1:
            for e, x in sorted(porest.items()):
                me = metricas(x)
                print(f"  estrato {e:8} n={len(x):3}  FAR_crit={me['resp_FAR_critico']:.3f}  "
                      f"falso_alarme={me['resp_falso_alarme']:.3f}")
        seg = [c["seg"] for c in custo]
        s = sorted(seg)
        print(f"  latência/diálogo: p50 {s[len(s)//2]:.2f} s, p95 {s[int(0.95*len(s))-1]:.2f} s; "
              f"tokens/diálogo: {sum(c['tokens_in'] + c['tokens_out'] for c in custo)/len(custo):.0f}")
    if a.mcnemar and len(a.arquivos) == 2:
        print("\nMcNemar (A x B):", mcnemar(*todos.values()))


if __name__ == "__main__":
    main()
