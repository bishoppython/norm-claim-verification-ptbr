"""Planilha do segundo anotador (item 1e do orientador): validação jurídica independente do gabarito.

Gera ../submissao/anotador/validacao_gabarito.xlsx com 4 abas:
  Instrucoes  - o que fazer, em linguagem simples
  Fatos       - 61 afirmações corretas: estão de acordo com a norma vigente? gravidade adequada?
  Erros       - 84 erros plantados: contradizem mesmo a norma? (sim / não / ambíguo)
  Rejeitadas  - até 50 afirmações corretas contestadas por algum juiz (42 distintas): estão mesmo corretas?
O anotador NÃO vê a resposta dos juízes como "certa": só a afirmação, a norma e o motivo do juiz.
Requer openpyxl.
"""
import json
import random
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

AQUI = Path(__file__).parent
SAIDA = AQUI.parent / "submissao" / "anotador" / "validacao_gabarito.xlsx"
NORMA = {"cmn-3919-2010": "Resolução CMN 3.919/2010", "cmn-4753-2019": "Resolução CMN 4.753/2019",
         "bcb-96-2021": "Resolução BCB 96/2021", "cmn-4881-2020": "Resolução CMN 4.881/2020",
         "cmn-4549-2017": "Resolução CMN 4.549/2017", "cmn-5112-2023": "Resolução CMN 5.112/2023",
         "lei-14690-2023": "Lei 14.690/2023", "cmn-5057-2022": "Resolução CMN 5.057/2022",
         "lei-8078-1990": "Lei 8.078/1990 (CDC)", "lei-14181-2021": "Lei 14.181/2021",
         "lei-10820-2003": "Lei 10.820/2003", "lei-13709-2018": "Lei 13.709/2018 (LGPD)"}
GRAV = {"critica": "crítica", "nao_critica": "não crítica"}
AMARELO = PatternFill("solid", fgColor="FFF4CC")

INSTRUCOES = [
    "Validação do gabarito — artigo sobre verificação de respostas de atendimento bancário por IA",
    "",
    "O que é: um conjunto de frases que um atendente de banco poderia dizer a um cliente. Algumas estão corretas "
    "segundo a norma; outras foram alteradas de propósito para ficarem erradas. Precisamos de uma segunda opinião, "
    "de alguém com formação jurídica ou de compliance, para saber se o nosso gabarito está certo.",
    "",
    "Preencha só as colunas AMARELAS. Use as opções da lista (clique na célula). A coluna 'Comentário' é livre e opcional.",
    "",
    "Aba 'Fatos' (61 linhas): cada linha é uma frase que consideramos CORRETA, com a norma e o texto integral do "
    "dispositivo em que se apoia (inciso, alínea ou parágrafo, com o cabeçalho que o introduz; '[…]' marca o trecho omitido "
    "entre eles; notas de redação do Planalto foram retiradas).",
    "  - 'Está correta pela norma vigente?': sim / não / parcialmente.",
    "  - 'Gravidade se estivesse errada': crítica (pode causar perda financeira, perda de direito ou descumprimento "
    "regulatório) ou não crítica.",
    "",
    "Aba 'Erros' (84 linhas): cada linha é uma versão que consideramos ERRADA de um fato da aba anterior.",
    "  - 'Contradiz a norma?': sim / não / ambíguo (quando depende de interpretação, de outra norma ou do caso).",
    "",
    "Aba 'Rejeitadas' (42 linhas): frases que consideramos CORRETAS, mas que algum sistema de IA contestou. "
    "Mostramos o motivo dado pela IA.",
    "  - 'A frase está correta?': sim / não / ambíguo. Se 'não' ou 'ambíguo', explique em uma linha no comentário.",
    "",
    "Considere a legislação vigente em novembro de 2026. Se souber de norma mais recente que mude a resposta, indique no comentário.",
    "Não há resposta 'esperada': se discordar de nós, marque o que achar correto. É exatamente isso que queremos medir.",
    "Tempo estimado: 3 a 4 horas. Nenhum dado pessoal real: todas as frases são fictícias.",
]


# ----------------------------------------------------------------- dispositivo completo
# O "trecho" de cada fato é só a âncora curta que o validador procura no artigo. Para o anotador,
# mostra-se a unidade inteira (inciso, alínea ou parágrafo) com o cabeçalho que a introduz ("...:"),
# sem as notas de redação do Planalto. Ex.: F01 mostra "em guichê de caixa, inclusive (...) ou em
# terminal de autoatendimento", que a âncora cortava.
_DOCS = None
NOTA=re.compile(r"\s*\((?:Redação|Incluíd|Revogad|Vide|Vigência|Regulamento)[^)]*\)")
norm=lambda s: re.sub(r"\s+"," ",NOTA.sub("",s)).strip()
FRONT=r"(?:; |\.\s(?=[A-ZÁ-Ú§])|\s(?=§ \d)|\s(?=[IVX]+ [-–] )|\s(?=[a-z]\) ))"
def completo(f):
    global _DOCS
    if _DOCS is None:
        from recuperar import carregar_indice
        _DOCS = carregar_indice().docs
    docs = _DOCS
    a=norm(f["trecho"])
    for d in (d for d in docs if d["norma"]==f["norma"] and d["artigo"]==f["artigo"]):
        t=norm(d["texto"]); i=t.find(a)
        if i<0: continue
        cs=[m.end() for m in re.finditer(FRONT+"|: ",t[:i])]
        ini=cs[-1] if cs else 0
        m=re.search(r";|\.\s(?=[A-ZÁ-Ú§IVX])|\.$",t[i+len(a):])
        fim=i+len(a)+(m.end() if m else len(t)-i-len(a))
        uni=t[ini:fim].strip()
        lead=""
        j=t.rfind(":",0,ini)
        if (j>0 and ini-j<=2 and not t[ini:].startswith("§")) or (j>0 and not re.search(r"\.\s(?=[A-ZÁ-Ú§])|\s§ \d",t[j:ini+3])):
            k=[m.end() for m in re.finditer(FRONT,t[:j])]
            lead=t[(k[-1] if k else 0):j+1].strip()
        txt=((lead+(" " if ini-j<=2 else " […] ")+uni) if lead and lead not in uni else uni)
        if re.match(r"^(?:[IVX]+ [-–] |[a-z]\) )", txt):  # cabeçalho é um inciso: acrescenta o caput do artigo
            k = t.find(":")
            cap = t[:k + 1] if 0 < k < 500 else re.split(r"(?<=\.)\s(?=[A-ZÁ-Ú§])", t, 1)[0]
            if not re.match(r"^Art\. ?\d+[º°o]?\.?$", cap.strip()) and cap not in txt:
                txt = cap + " […] " + txt
        return txt if len(txt)<=1200 else txt[:1200].rsplit(" ",1)[0]+" […]"
    return None


def cabecalho(ws, cols, larguras):
    ws.append(cols)
    for c, w in zip(ws[1], larguras):
        c.font = Font(bold=True)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[c.column_letter].width = w
    ws.freeze_panes = "A2"


def lista(ws, col, opcoes, n):
    dv = DataValidation(type="list", formula1='"' + ",".join(opcoes) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col}2:{col}{n + 1}")
    for r in range(2, n + 2):
        ws[f"{col}{r}"].fill = AMARELO


def main():
    F = [json.loads(l) for l in (AQUI / "fatos_norma.jsonl").open(encoding="utf-8")]
    wb = Workbook()
    ws = wb.active
    ws.title = "Instrucoes"
    for l in INSTRUCOES:
        ws.append([l])
    ws.column_dimensions["A"].width = 150
    for c in ws["A"]:
        c.alignment = Alignment(wrap_text=True)
    ws["A1"].font = Font(bold=True, size=13)

    ws = wb.create_sheet("Fatos")
    cabecalho(ws, ["ID", "Produto", "Frase (considerada correta)", "Norma", "Dispositivo", "Texto do dispositivo (íntegra)",
                   "Está correta pela norma vigente?", "Gravidade se estivesse errada", "Comentário"],
              [6, 11, 45, 22, 14, 75, 16, 16, 40])
    for f in F:
        ws.append([f["id"], f["produto"], f["afirmacao"], NORMA.get(f["norma"], f["norma"]), f["dispositivo"],
                   completo(f), "", "", ""])
    lista(ws, "G", ["sim", "não", "parcialmente"], len(F))
    lista(ws, "H", ["crítica", "não crítica"], len(F))
    ws.column_dimensions["I"].width = 40

    ws = wb.create_sheet("Erros")
    cabecalho(ws, ["ID do fato", "Frase correta (referência)", "Versão errada (a avaliar)", "Norma e dispositivo",
                   "Texto do dispositivo (íntegra)", "Contradiz a norma?", "Comentário"], [8, 40, 40, 26, 70, 14, 40])
    n = 0
    for f in F:
        for e in f["erros"]:
            ws.append([f["id"], f["afirmacao"], e["texto"], f"{NORMA.get(f['norma'], f['norma'])}, {f['dispositivo']}",
                       completo(f), "", ""])
            n += 1
    lista(ws, "F", ["sim", "não", "ambíguo"], n)

    # até 50 afirmações corretas contestadas por algum juiz por afirmação (com/sem regras/RAG), sorteadas (semente 7)
    gab = {d["id"]: d for d in map(json.loads, (AQUI / "dialogos.jsonl").open(encoding="utf-8"))}
    fato = {f["afirmacao"]: f for f in F}
    rej = {}
    for arq in sorted((AQUI / "resultados").glob("afirmacao*__oraculo__hibrida__dialogos.jsonl")):
        for r in map(json.loads, arq.open(encoding="utf-8")):
            for a, v in zip(gab[r["id"]]["afirmacoes"], r["vereditos"]):
                if a["correta"] and str(v.get("veredito", "")).startswith("contest"):
                    rej.setdefault(a["texto"], []).append(v.get("motivo", ""))
    textos = sorted(rej)
    amostra = random.Random(7).sample(textos, min(50, len(textos)))
    ws = wb.create_sheet("Rejeitadas")
    cabecalho(ws, ["Nº", "Frase (considerada correta)", "Norma e dispositivo de referência", "Motivo dado pela IA ao contestar",
                   "A frase está correta?", "Comentário"], [5, 55, 34, 60, 14, 40])
    for i, t in enumerate(amostra, 1):
        f = fato.get(t)
        ref = f"{NORMA.get(f['norma'], f['norma'])}, {f['dispositivo']}" if f else ""
        ws.append([i, t, ref, rej[t][0], "", ""])
    lista(ws, "E", ["sim", "não", "ambíguo"], len(amostra))
    for w in wb.worksheets[1:]:
        for row in w.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    wb.save(SAIDA)
    print(f"ok: {SAIDA} | fatos {len(F)}, erros {n}, rejeitadas {len(amostra)} (de {len(textos)} distintas)")


if __name__ == "__main__":
    main()
