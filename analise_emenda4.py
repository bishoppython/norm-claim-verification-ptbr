"""Análise da emenda 4 (parecer do Prof. Carlo, 28/11/2026): frases compostas. Escrita ANTES de rodar.

Condições (todas nas 300 respostas de dialogos_compostos.jsonl, com 2–3 afirmações por frase, divididas
automaticamente pela pontuação):
  C1  juiz configurado, recuperação pela afirmação do gabarito (isola o efeito da frase composta no julgamento)
  C2  juiz configurado, recuperação pela frase (condição realista)
  V   verificador fim a fim (o próprio modelo extrai as afirmações da resposta composta)
Referência: juiz configurado no benchmark original (uma afirmação por frase; emenda 3).

Uma afirmação conta como apontada quando o juiz aponta uma frase que contém (parte d)ela. Assim a precisão
cai quando o juiz aponta uma frase com afirmações corretas junto da errada: é o custo para o revisor.

H11 (contaminação): em C1, o recall das afirmações erradas (a frase que a contém é apontada) é MENOR que no
     original. Diferença pareada, IC bootstrap em dois níveis (diálogo × fato), p bootstrap bicaudal, Holm nos 4.
H12 (recomendação): em respostas compostas, o juiz configurado (C2) localiza pior (F1 por afirmação) que o
     verificador fim a fim (V). Mesmo teste. REGRA DE DECISÃO: se H12 valer em >= 3 de 4 modelos após Holm, a
     recomendação passa a ser condicional (juiz configurado só com respostas já segmentadas em uma afirmação por
     frase; verificador para texto livre), e o título e a Discussão mudam.
Descritivo: falso alarme, FAR-crítico, FAR-crítico no falso alarme exatamente pareado contra o original e
contra V, precisão por frase (frase apontada contém erro), custo.
Exploratório: o "motivo" de uma frase apontada com erro e mais de uma afirmação aponta a afirmação errada
(sobreposição de tokens >= 0,4 com a errada e < 0,4 com as corretas)?
Saída: resultados/analise_emenda4.md e .json. Roda com ~/.venvs/ragas/bin/python. Condições sem arquivo
completo são puladas.
"""
import json
import math

import numpy as np

import analise_emenda2 as A
import analise_emenda3 as E
import metricas as M

RES, IDS, LOCAIS = E.RES, E.IDS, E.LOCAIS
JC = "holistico_conformidade_sentencas_normas"
f = A.f


def carregar(juiz, modelo, seg, rec):
    p = RES / f"{juiz}__{modelo}__{seg}__{rec}__dialogos_compostos.jsonl"
    if not p.exists():
        return None
    R = {r["id"]: r for r in map(json.loads, p.open(encoding="utf-8"))}
    return [R[i] for i in IDS] if sorted(R) == IDS else None


def condicoes(m):
    return {"original": E.carregar(JC, m), "C1": carregar(JC, m, "pontuacao", "hibrida"),
            "C2": carregar(JC, m, "pontuacao", "hibrida-frase"), "V": carregar("afirmacao_regras", m, "llm", "hibrida")}


def tab(nome, R):
    return E.tabela_por_gold(R) if nome == "V" else A.tabela_afirmacoes(R)


def teste(Ta, Tb, idx):
    """Diferença (a − b) da métrica idx (0 precisão, 1 recall, 2 F1) com IC e p bootstrap bicaudal."""
    la, ba = A.loc(Ta); lb, bb = A.loc(Tb)
    k = ("precisao", "recall", "F1")[idx]
    db = ba[idx] - bb[idx]
    ic = E.ic(db); db = db[~np.isnan(db)]
    p = min(1.0, 2 * min(np.mean(db <= 0), np.mean(db >= 0)))
    return {"a": la[k][0], "b": lb[k][0], "dif": la[k][0] - lb[k][0], "ic": ic, "p": p}


def precisao_frase(R):
    gab = {d["id"]: d for d in map(json.loads, (E.AQUI / "dialogos_compostos.jsonl").open(encoding="utf-8"))}
    ap = com_erro = 0
    for r in R:
        d = gab[r["id"]]
        for s in r.get("frases_apontadas") or []:
            ap += 1
            com_erro += any(s in ss and not a["correta"] for a, ss in zip(d["afirmacoes"], r["mapa"]))
    return com_erro / ap if ap else math.nan


def motivo_aponta(R):
    """Exploratório: em frases apontadas com erro e >1 afirmação, o motivo aponta só a errada?"""
    gab = {d["id"]: d for d in map(json.loads, (E.AQUI / "dialogos_compostos.jsonl").open(encoding="utf-8"))}
    n = ok = 0
    for r in R:
        d = gab[r["id"]]
        for x in (r["bruto"].get("sentencas_nao_conformes") or []):
            if not isinstance(x, dict):
                continue
            mm = [int(c) for c in __import__("re").findall(r"\d+", str(x.get("id", "")))[:1]]
            if not mm:
                continue
            s = mm[0]
            afs = [a for a, ss in zip(d["afirmacoes"], r["mapa"]) if s in ss]
            if len(afs) < 2 or all(a["correta"] for a in afs):
                continue
            tm = M._tok(str(x.get("motivo", "")))
            cobre = lambda a: (t := M._tok(a["texto"])) and len(t & tm) / len(t) >= 0.4
            n += 1
            ok += any(cobre(a) for a in afs if not a["correta"]) and not any(cobre(a) for a in afs if a["correta"])
    return ok / n if n else math.nan, n


def main():
    J, L = {}, ["# Análise da emenda 4 — frases compostas (gerado por analise_emenda4.py)", ""]
    L += ["| Modelo | Condição | falso alarme | FAR-crítico | precisão | recall | F1 | precisão por frase | motivo aponta a errada |",
          "|---|---|---|---|---|---|---|---|---|"]
    C, T, V = {}, {}, {}
    for m in LOCAIS:
        for nome, R in condicoes(m).items():
            if R is None:
                continue
            C[(m, nome)] = R; T[(m, nome)] = tab(nome, R); V[(m, nome)] = E.vet(R)
            r = A.resp_metricas(V[(m, nome)]); lo, _ = A.loc(T[(m, nome)])
            pf = precisao_frase(R) if nome in ("C1", "C2") else math.nan
            mo = motivo_aponta(R) if nome in ("C1", "C2") else (math.nan, 0)
            J.setdefault("descritivo", {})[f"{m}|{nome}"] = {"resp": r, "loc": lo, "precisao_frase": pf, "motivo": mo}
            L.append(f"| {m} | {nome} | {A.fic(r['falso_alarme'])} | {A.fic(r['FAR_crit'])} | {A.fic(lo['precisao'])} | "
                     f"{A.fic(lo['recall'])} | {A.fic(lo['F1'])} | {f(pf)} | {f(mo[0])} (n = {mo[1]}) |")
    for h, (a, b, idx, rot) in {"H11": ("C1", "original", 1, "recall, C1 − original"),
                                 "H12": ("C2", "V", 2, "F1, C2 − verificador fim a fim")}.items():
        linhas = [(m, teste(T[(m, a)], T[(m, b)], idx), E.hull_dif(V[(m, a)], V[(m, b)]))
                  for m in LOCAIS if (m, a) in T and (m, b) in T]
        if not linhas:
            continue
        for (m, t, hd), pa in zip(linhas, A.holm([t["p"] for _, t, _ in linhas])):
            t["p_holm"] = pa; J.setdefault(h, {})[m] = {**t, "far_pareado": hd}
        L += ["", f"## {h} ({rot})", "", "| Modelo | a | b | diferença [IC 95%] | p | p Holm | ΔFAR-crítico no FA pareado [IC] |",
              "|---|---|---|---|---|---|---|"]
        for m, t, hd in linhas:
            L.append(f"| {m} | {f(t['a'])} | {f(t['b'])} | {f(t['dif'])} [{f(t['ic'][0])}; {f(t['ic'][1])}] | {f(t['p'], 3)} | "
                     f"{f(t['p_holm'], 3)} | {f(hd['dif'])} [{f(hd['ic'][0])}; {f(hd['ic'][1])}] |")
        if h == "H12":
            n = sum(1 for m, t, _ in linhas if t["p_holm"] < 0.05 and t["dif"] < 0)
            L += ["", f"Regra de decisão: H12 vale em {n} de {len(linhas)} modelos -> "
                  + ("DISPARADA (recomendação condicional)" if n >= 3 else "não disparada") + "."]
    (RES / "analise_emenda4.json").write_text(json.dumps(J, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    (RES / "analise_emenda4.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
