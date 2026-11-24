"""Amostra de 50 problemas do holístico para a conferência manual da H5 (pré-registro).

Sorteia 50 problemas (semente 7) entre os 2 juízes holísticos x 4 modelos e grava
auditoria_h5.csv com o rótulo automático. O autor preenche 'rotulo_autor' com:
  erro   = o problema aponta uma afirmação errada da resposta
  certa  = acusa uma afirmação correta
  outro  = genérico, de estilo ou sem afirmação identificável
e, quando 'erro', 'motivo_certo' = sim/nao (o juiz disse corretamente o que está errado?).
O rótulo automático vai para auditoria_h5_auto.csv, para o autor não vê-lo antes (cegamento leve).
"""
import csv, json, random
from pathlib import Path
import metricas as M

AQUI = Path(__file__).parent
gab = M.carregar_gabarito()
itens = []
for f in sorted((AQUI / "resultados").glob("holistico*__oraculo__hibrida__dialogos.jsonl")):
    for r in map(json.loads, f.open(encoding="utf-8")):
        d = gab[r["id"]]
        for p in (r.get("bruto") or {}).get("problemas") or []:
            itens.append((f.name.split("__")[0], f.name.split("__")[1], d, str(p)))
rng = random.Random(7)
amostra = rng.sample(itens, 50)
bate = lambda af, p: af and len(af & p) / len(af) >= 0.4
linhas, auto = [], []
for n, (juiz, mod, d, p) in enumerate(amostra, 1):
    tp = M._tok(p)
    errada = any(bate(M._tok(a["texto"]), tp) for a in d["afirmacoes"] if not a["correta"])
    certa = any(bate(M._tok(a["texto"]), tp) for a in d["afirmacoes"] if a["correta"])
    afs = "\n".join(f"{i}{' X' if not a['correta'] else ''}: {a['texto']}" for i, a in enumerate(d["afirmacoes"], 1))
    linhas.append([n, d["pergunta"], afs, p, "", "", ""])
    auto.append([n, "erro" if errada else ("certa" if certa else "outro"), juiz, mod, d["id"]])
with (AQUI / "auditoria_h5.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["n", "pergunta do cliente", "afirmacoes da resposta (X = errada de proposito)",
                "problema apontado pelo juiz", "rotulo_autor (erro / certa / outro)",
                "motivo_certo (sim / nao; so quando erro)", "observacao"])
    w.writerows(linhas)
with (AQUI / "auditoria_h5_auto.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["n", "rotulo_auto", "juiz", "modelo", "id"])
    w.writerows(auto)
print("ok", len(itens), "problemas; amostra de 50 em auditoria_h5.csv")
