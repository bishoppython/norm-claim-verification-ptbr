"""Regras determinísticas para números e prazos (componente do verificador).

Para cada afirmação: extrai quantidades com unidade (dias, %, saques, folhas,
anos...) da afirmação e do(s) artigo(s) recuperado(s). Decide:
  - "confirma"  se alguma quantidade da afirmação, na mesma unidade, aparece na norma;
  - "contesta"  se a norma tem quantidades nessa unidade e nenhuma bate;
  - "abstem"    se não há quantidade comparável (fica para o juiz LLM).

Não consulta o gabarito: só a afirmação e o texto da norma recuperado.
Avaliação contra o gabarito: python regras.py --avaliar dialogos.jsonl [--oraculo]
(--oraculo usa o artigo-fonte verdadeiro, para separar erro de recuperação de erro de regra.)
"""
import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent

UNID = {
    "dia": "dia", "dias": "dia", "mes": "mes", "meses": "mes", "ano": "ano", "anos": "ano",
    "%": "pct", "por cento": "pct",
    "saque": "saque", "saques": "saque", "transferencia": "transf", "transferencias": "transf",
    "extrato": "extrato", "extratos": "extrato", "folha": "folha", "folhas": "folha",
}
NUM = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
    "oito": 8, "nove": 9, "dez": 10, "quinze": 15, "vinte": 20, "trinta": 30, "quarenta": 40,
    "quarenta e cinco": 45, "trinta e cinco": 35, "sessenta": 60, "noventa": 90, "cem": 100,
    "cento e oitenta": 180, "trezentos e sessenta e cinco": 365,
}
NUM_RE = "|".join(sorted(map(re.escape, NUM), key=len, reverse=True))
UNID_RE = "|".join(sorted(map(re.escape, UNID), key=len, reverse=True))
# (?!\w) no lugar de \b: depois de "%" não há fronteira de palavra
PADRAO = re.compile(rf"(\d+(?:,\d+)?|{NUM_RE})\s*(?:\([^)]*\)\s*)?(?:(?:primeiros?|ultimos?|gratis)\s+)?({UNID_RE})(?!\w)(\s+(?:corridos|uteis))?")


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def para_dias(v: float, u: str) -> tuple[float, str]:
    if u == "mes":
        return v * 30, "dia"
    if u == "ano":
        return v * 365, "dia"
    return v, u


def quantidades(texto: str) -> set[tuple[float, str]]:
    t = fold(texto)
    t = t.replace("uma vez por ano", "365 dias").replace("seis meses", "180 dias")
    out = set()
    for m in PADRAO.finditer(t):
        bruto, u = m.group(1), UNID[m.group(2)]
        v = float(bruto.replace(",", ".")) if bruto[0].isdigit() else NUM[bruto]
        q = para_dias(v, u)
        qual = (m.group(3) or "").strip()
        if q[1] == "dia" and qual == "uteis":
            q = (q[0], "dia_util")
        elif q[1] == "dia" and qual == "corridos":
            out.add((q[0], "dia_corrido"))
        out.add(q)
    return out


def decidir(afirmacao: str, textos_norma: list[str]) -> tuple[str, str]:
    qa = quantidades(afirmacao)
    if not qa:
        return "abstem", "sem quantidade na afirmação"
    qn = set().union(*(quantidades(t) for t in textos_norma)) if textos_norma else set()
    # "N dias úteis" contra norma que diz "N dias corridos": contesta;
    # contra norma que só diz "N dias": a regra não decide (contagem vem de fora do corpus)
    uteis = {v for v, u in qa if u == "dia_util"}
    if uteis:
        if uteis & {v for v, u in qn if u == "dia_corrido"}:
            return "contesta", "norma diz dias corridos; afirmação diz úteis"
        return "abstem", "dias úteis sem qualificação na norma"
    qn = {q for q in qn if q[1] != "dia_corrido"}
    unidades = {u for _, u in qa} & {u for _, u in qn}
    if not unidades:
        return "abstem", "norma sem quantidade na mesma unidade"
    comp_a = {q for q in qa if q[1] in unidades}
    valores_norma = {u: {v for v, uu in qn if uu == u} for u in unidades}
    if comp_a & qn:
        # norma com mais de um valor na mesma unidade (ex.: 45 e 30 dias no art. 18):
        # bater com um deles não prova que é o valor certo para o caso -> escopo é com o LLM
        if any(len(valores_norma[u]) > 1 for _, u in comp_a & qn):
            return "abstem", "norma com vários valores na unidade; escopo decide"
        return "confirma", f"bate: {sorted(comp_a & qn)}"
    return "contesta", f"afirmação {sorted(comp_a)} x norma {sorted(q for q in qn if q[1] in unidades)}"


def avaliar(arquivo: str, oraculo: bool, k: int) -> dict:
    from recuperar import carregar_indice
    idx = carregar_indice()
    por_chave = {(d["norma"], d["artigo"]): d["texto"] for d in idx.docs}
    c = Counter()
    por_cat = Counter()
    for linha in (AQUI / arquivo).open(encoding="utf-8"):
        for a in json.loads(linha)["afirmacoes"]:
            if oraculo:
                textos = [por_chave[(a["norma"], a["artigo"])]]
            else:
                textos = [d["texto"] for _, d in idx.buscar(a["texto"], k=k)]
            v, _ = decidir(a["texto"], textos)
            gold = "errada" if not a["correta"] else "correta"
            c[(v, gold)] += 1
            if not a["correta"]:
                por_cat[(a["categoria_erro"], v)] += 1
    contesta_ok = c[("contesta", "errada")]
    contesta = contesta_ok + c[("contesta", "correta")]
    confirma_ok = c[("confirma", "correta")]
    confirma = confirma_ok + c[("confirma", "errada")]
    total = sum(c.values())
    return {
        "modo": "oráculo" if oraculo else f"BM25 top-{k}",
        "cobertura (não absteve)": round((contesta + confirma) / total, 3),
        "precisão ao contestar": round(contesta_ok / contesta, 3) if contesta else None,
        "precisão ao confirmar": round(confirma_ok / confirma, 3) if confirma else None,
        "erros valor/prazo contestados": f"{por_cat[('valor', 'contesta')] + por_cat[('prazo', 'contesta')]}/"
                                          f"{sum(n for (cat, _), n in por_cat.items() if cat in ('valor', 'prazo'))}",
        "matriz": {f"{v}|{g}": n for (v, g), n in sorted(c.items())},
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--avaliar", default="dialogos.jsonl")
    ap.add_argument("--oraculo", action="store_true")
    ap.add_argument("--k", type=int, default=3)
    a = ap.parse_args()
    print(json.dumps(avaliar(a.avaliar, a.oraculo, a.k), ensure_ascii=False, indent=1))
