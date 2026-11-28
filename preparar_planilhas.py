"""Planilhas de rotulagem manual da emenda 3 (exploratórias). Gera em ../submissao/anotador/:

1. localizacao_rotulador.xlsx (M7, rotulador independente da H5): 100 problemas listados pelos juízes
   holísticos em texto livre. Os 50 da auditoria do autor (auditoria_h5.csv, mesma ordem de sorteio) e 50 novos
   (semente 8; holístico, holístico + normas e holístico só conformidade; 4 modelos). Mais cega que a auditoria
   original: as afirmações erradas NÃO vêm marcadas. O rotulador diz a que afirmação o problema se refere e se
   o problema diz que ela está errada; erro/certa/outro sai do gabarito. A chave fica em localizacao_chave.csv.
2. motivos_rotulador.xlsx (M2): 60 problemas do holístico (texto livre) em respostas SEM erro que ele rejeitou
   (semente 7; 4 modelos), para classificar o motivo. A classe automática (classificar_motivos.py) só existe
   depois da fila da GPU e não aparece aqui; a chave fica em motivos_chave.csv.
Ordem dos itens embaralhada (semente 11) nas duas planilhas.
Roda com o python do venv ~/.venvs/ragas (openpyxl).
"""
import csv
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

AQUI = Path(__file__).parent
RES = AQUI / "resultados"
OUT = AQUI.parent / "submissao" / "anotador"
MODELOS = ["qwen3.5-9b", "gemma4-12b", "llama3.1-8b", "gpt-oss-20b"]
GAB = {d["id"]: d for d in (json.loads(l) for l in (AQUI / "dialogos.jsonl").open(encoding="utf-8"))}


def problemas(juizes, filtro):
    itens = []
    for j in juizes:
        for m in MODELOS:
            for r in map(json.loads, (RES / f"{j}__{m}__oraculo__hibrida__dialogos.jsonl").open(encoding="utf-8")):
                d = GAB[r["id"]]
                if not filtro(r, d):
                    continue
                for k, p in enumerate((r.get("bruto") or {}).get("problemas") or []):
                    itens.append({"juiz": j, "modelo": m, "id": r["id"], "k": k, "problema": str(p)})
    return itens


def afirmacoes_numeradas(d):
    return "\n".join(f"{i}: {a['texto']}" for i, a in enumerate(d["afirmacoes"], 1))


def planilha(arq, instrucoes, cab, linhas, larguras, validacoes):
    wb = Workbook()
    ws = wb.active; ws.title = "Instrucoes"
    for t in instrucoes:
        ws.append([t])
    ws.column_dimensions["A"].width = 120
    for c in ws["A"]:
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws["A1"].font = Font(bold=True, size=13)
    it = wb.create_sheet("Itens")
    it.append(cab)
    for c in it[1]:
        c.font = Font(bold=True); c.alignment = Alignment(wrap_text=True, vertical="top")
        c.fill = PatternFill("solid", fgColor="DDEBF7")
    for l in linhas:
        it.append(l)
    for col, w in larguras.items():
        it.column_dimensions[col].width = w
    for row in it.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for col, opcoes in validacoes.items():
        dv = DataValidation(type="list", formula1='"' + ",".join(opcoes) + '"', allow_blank=True)
        it.add_data_validation(dv); dv.add(f"{col}2:{col}{len(linhas) + 1}")
    it.freeze_panes = "A2"
    wb.save(arq)


def localizacao():
    # 50 da auditoria do autor: texto e diálogo vêm dos CSVs (o sorteio original dependia dos arquivos da época)
    txt = {int(r["n"]): r for r in csv.DictReader((AQUI / "auditoria_h5.csv").open(encoding="utf-8"))}
    aut = {int(r["n"]): r for r in csv.DictReader((AQUI / "auditoria_h5_auto.csv").open(encoding="utf-8"))}
    velhos = [{"origem": "auditoria_autor", "n_autor": n, "juiz": aut[n]["juiz"], "modelo": aut[n]["modelo"],
               "id": aut[n]["id"], "problema": txt[n]["problema apontado pelo juiz"]} for n in sorted(txt)]
    ja = {(x["id"], x["problema"]) for x in velhos}
    pool = [x for x in problemas(["holistico", "holistico_normas", "holistico_conformidade"], lambda r, d: True)
            if (x["id"], x["problema"]) not in ja]
    novos = [dict(x, origem="nova", n_autor="") for x in random.Random(8).sample(pool, 50)]
    itens = velhos + novos
    random.Random(11).shuffle(itens)
    linhas, chave = [], []
    for n, x in enumerate(itens, 1):
        d = GAB[x["id"]]
        linhas.append([n, d["pergunta"], afirmacoes_numeradas(d), x["problema"], "", "", ""])
        chave.append([n, x["origem"], x["n_autor"], x["juiz"], x["modelo"], x["id"],
                      ";".join(str(i) for i, a in enumerate(d["afirmacoes"], 1) if not a["correta"])])
    instr = [
        "Rotulagem de problemas apontados por juízes automáticos (atendimento bancário)",
        "Obrigado! São 100 itens, em torno de 1h30. Não é preciso consultar normas: a tarefa é só de leitura.",
        "Em cada item há a pergunta de um cliente, a resposta de um atendente dividida em afirmações numeradas e UM problema "
        "que um juiz automático (uma IA) apontou nessa resposta.",
        "Coluna E — A que afirmação o problema se refere? Escreva o número da afirmação (ex.: 3). Se ele se referir a mais de uma, "
        "separe por vírgula (ex.: 2,5). Escreva 0 se o problema for genérico, de estilo, sobre algo que a resposta não diz, "
        "ou se não der para identificar a afirmação.",
        "Coluna F — O problema diz que essa(s) afirmação(ões) está(ão) ERRADA(S) ou contraria(m) a norma? "
        "sim = afirma que está errada, é ilegal ou não corresponde à regra; "
        "nao = só pede complemento, ressalva, clareza ou outra melhoria; "
        "na = quando a coluna E for 0.",
        "Coluna G — Comentário livre, opcional.",
        "Não julgue se a afirmação está de fato certa ou errada, nem se o juiz tem razão: só a que afirmação o problema se refere "
        "e o que ele diz dela. Algumas respostas trazem erros de propósito; isso não importa para esta tarefa.",
        "Os itens são independentes e estão em ordem aleatória. Ao terminar, salve e devolva o arquivo.",
    ]
    planilha(OUT / "localizacao_rotulador.xlsx", instr,
             ["n", "Pergunta do cliente", "Afirmações da resposta (numeradas)", "Problema apontado pelo juiz",
              "E. Afirmação(ões) a que se refere (nº; 0 = nenhuma)", "F. Diz que está errada? (sim/nao/na)", "G. Comentário"], linhas,
             {"A": 5, "B": 30, "C": 70, "D": 45, "E": 18, "F": 16, "G": 25}, {"F": ["sim", "nao", "na"]})
    with (OUT / "localizacao_chave.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "origem", "n_na_auditoria_do_autor", "juiz", "modelo", "id", "afirmacoes_erradas"])
        w.writerows(chave)


def motivos():
    pool = problemas(["holistico"], lambda r, d: d["n_erros"] == 0 and not r["aprovada"])
    am = random.Random(7).sample(pool, 60)
    random.Random(11).shuffle(am)
    linhas = [[n, GAB[x["id"]]["pergunta"], GAB[x["id"]]["resposta"], x["problema"], "", ""] for n, x in enumerate(am, 1)]
    instr = [
        "Classificação dos motivos de rejeição (respostas SEM erro rejeitadas pelo juiz holístico)",
        "São 60 itens, em torno de 30 min. Todas as respostas abaixo estão corretas pela norma; o juiz as rejeitou mesmo assim. "
        "Classifique o PROBLEMA APONTADO (coluna D), não a resposta.",
        "contradicao = diz que alguma afirmação está errada, é ilegal ou contraria a norma/lei",
        "omissao = diz que falta informação, ressalva, condição, prazo ou detalhe (resposta incompleta)",
        "relevancia = diz que a resposta foge da pergunta ou traz informação que não foi pedida",
        "estilo = tom, clareza, linguagem, formalidade, organização ou empatia",
        "outro = nada disso",
        "Escolha uma classe só (a predominante). Comentário opcional na coluna F.",
    ]
    planilha(OUT / "motivos_rotulador.xlsx", instr,
             ["n", "Pergunta do cliente", "Resposta do atendente", "Problema apontado pelo juiz", "E. Classe", "F. Comentário"], linhas,
             {"A": 5, "B": 30, "C": 70, "D": 45, "E": 16, "F": 25},
             {"E": ["contradicao", "omissao", "relevancia", "estilo", "outro"]})
    with (OUT / "motivos_chave.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "juiz", "modelo", "id", "k"])
        w.writerows([[n, x["juiz"], x["modelo"], x["id"], x["k"]] for n, x in enumerate(am, 1)])


if __name__ == "__main__":
    localizacao()
    motivos()
    print("ok:", sorted(p.name for p in OUT.glob("*rotulador.xlsx")), sorted(p.name for p in OUT.glob("*chave.csv")))
