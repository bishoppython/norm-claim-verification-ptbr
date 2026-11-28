"""Emenda 4 (parecer do Prof. Carlo, 28/11/2026): respostas com frases compostas.

No benchmark original cada frase da resposta é uma afirmação, e o juiz configurado recebe a resposta já
numerada por afirmação. Aqui as afirmações de cada resposta são juntadas, na ordem, em frases de 2 (ou 3,
quando sobra uma) afirmações: "A, e b." / "A, b e c.". O gabarito continua exato: cada afirmação guarda
o trecho (início, fim) que ocupa na resposta nova.

Determinístico, sem LLM. Saída: dialogos_compostos.jsonl (mesmos ids, pergunta e afirmações; resposta nova;
"frases" = afirmações de cada frase construída; "spans" = trecho de cada afirmação na resposta).
"""
import json
import re
from pathlib import Path

AQUI = Path(__file__).parent


def minuscula(t):
    # não rebaixa sigla ("CDC", "LGPD") nem nome próprio em sequência de maiúsculas
    return t if len(t) > 1 and t[1].isupper() else t[:1].lower() + t[1:]


def grupos(n):
    g = [[i, i + 1] for i in range(0, n - 1, 2)]
    if n % 2:
        g[-1].append(n - 1)
    return g


def compor(d):
    afs = [a["texto"].strip().rstrip(".?!").strip() for a in d["afirmacoes"]]
    resposta, spans, frases = "", [None] * len(afs), []
    for g in grupos(len(afs)):
        partes = [afs[g[0]]] + [minuscula(afs[i]) for i in g[1:]]
        sep = [", e "] if len(g) == 2 else [", ", " e "]
        if resposta:
            resposta += " "
        for k, (i, p) in enumerate(zip(g, partes)):
            if k:
                resposta += sep[k - 1]
            spans[i] = (len(resposta), len(resposta) + len(p))
            resposta += p
        resposta += "."
        frases.append(g)
    return dict(d, resposta=resposta, frases=frases, spans=spans, resposta_original=d["resposta"])


def main():
    D = [json.loads(l) for l in (AQUI / "dialogos.jsonl").open(encoding="utf-8")]
    with (AQUI / "dialogos_compostos.jsonl").open("w", encoding="utf-8") as f:
        for d in D:
            c = compor(d)
            for a, (i, j) in zip(c["afirmacoes"], c["spans"]):  # o trecho bate com a afirmação (a menos da 1ª letra)
                assert c["resposta"][i + 1:j] == a["texto"].strip().rstrip(".?!").strip()[1:], (d["id"], a["texto"])
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"ok: {len(D)} respostas, {sum(len(compor(d)['frases']) for d in D)} frases construídas")


if __name__ == "__main__":
    main()
