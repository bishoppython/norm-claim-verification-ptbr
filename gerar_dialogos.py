"""Gerador de diálogos sintéticos de atendimento com erros plantados (Dia 3).

Determinístico (semente fixa), sem LLM: cada resposta do atendente é montada a
partir de fatos-norma (fatos_norma.jsonl). Cada afirmação sai na versão correta
ou, com probabilidade P_ERRO, numa das versões erradas do fato. O gabarito é
conhecido por construção (fato, correta/errada, categoria, gravidade, dispositivo).

Uso:
  python gerar_dialogos.py                 # principal: sementes 101-103 x 100 diálogos
  python gerar_dialogos.py --n 30 --sementes 1 --semente-inicial 1 --sem-estratos --saida piloto.jsonl

Regras:
- um fato aparece no máximo uma vez por diálogo;
- 6 a 8 afirmações por resposta: até k-1 do foco da pergunta, o resto do mesmo
  produto (mais as gerais, "todos");
- consignado usa também os fatos de crédito (o produto tem poucos fatos);
- estratos (emenda de 23/11/2026, após o piloto): 1/3 "limpo" (nenhum erro),
  1/3 "um_erro" (exatamente uma afirmação errada) e 1/3 "misto" (cada afirmação
  errada com P_ERRO = 0,30, independente). O piloto mostrou um juiz holístico que
  reprova tudo; sem respostas corretas suficientes, o falso alarme não é medível.
  Com --sem-estratos, todos os diálogos são "misto" (desenho do piloto);
- as respostas "naturais" dos modelos (sem erro plantado) são outro experimento.
"""
import argparse
import json
import random
from pathlib import Path

AQUI = Path(__file__).parent
P_ERRO = 0.30
MIN_AF, MAX_AF = 6, 8

POOLS = {
    "conta": ["conta", "todos"],
    "cartao": ["cartao", "todos"],
    "credito": ["credito", "todos"],
    "consignado": ["consignado", "credito", "todos"],
}

# Cada pergunta traz os fatos do seu foco: a resposta usa até k-1 deles e
# completa com fatos do mesmo produto, para não fugir do assunto.
PERGUNTAS = {
    "conta": [
        ("O que é de graça na minha conta corrente?", ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F56"]),
        ("Quero mudar o pacote de serviços da minha conta. Como funciona?", ["F11", "F53", "F54", "F55", "F52", "F25", "F09", "F56"]),
        ("Quero encerrar minha conta corrente e a conta digital. O que eu preciso saber?", ["F16", "F60", "F61", "F33", "F35", "F37", "F56"]),
        ("Tenho poupança. O que é gratuito nela?", ["F57", "F58", "F59", "F03", "F07", "F06"]),
        ("A tarifa da minha conta aumentou. Pode isso?", ["F09", "F25", "F11", "F56", "F54", "F47"]),
        ("Vocês podem usar os dados do meu cadastro pra me mandar ofertas?", ["F33", "F34", "F35", "F36", "F37", "F38", "F39"]),
    ],
    "cartao": [
        ("Não consegui pagar a fatura inteira do cartão. O que acontece agora?", ["F12", "F13", "F14", "F15", "F50", "F51", "F22"]),
        ("A anuidade e as tarifas do meu cartão subiram. Pode isso?", ["F08", "F10", "F52", "F48", "F56", "F47"]),
        ("Tem uma compra que não reconheço na fatura do cartão. Como faço?", ["F42", "F47", "F51", "F15", "F14"]),
        ("Chegou em casa um cartão de crédito que eu não pedi.", ["F48", "F08", "F10", "F52", "F38", "F36"]),
        ("Quero renegociar a dívida do cartão.", ["F15", "F14", "F50", "F12", "F13", "F44", "F45"]),
    ],
    "credito": [
        ("Estou pensando em pegar um empréstimo. O que eu preciso saber antes?", ["F17", "F24", "F40", "F41", "F43", "F49", "F22", "F23"]),
        ("Quero levar meu empréstimo pra outro banco.", ["F18", "F19", "F20", "F17", "F23", "F43"]),
        ("Quero quitar meu empréstimo antes do prazo.", ["F23", "F22", "F17", "F18", "F43", "F47"]),
        ("Estou muito endividado. Quais são os meus direitos?", ["F44", "F45", "F46", "F15", "F14", "F40", "F23"]),
        ("Contratei um crédito por telefone e me arrependi.", ["F21", "F43", "F24", "F49", "F41", "F17"]),
    ],
    "consignado": [
        ("Sou aposentado do INSS e quero fazer um consignado. Quanto posso comprometer?", ["F27", "F28", "F17", "F24", "F21", "F49", "F40"]),
        ("Sou CLT e quero um consignado. Como funciona o desconto?", ["F26", "F30", "F31", "F32", "F17", "F23"]),
        ("Recebo BPC. Posso fazer consignado? Qual o limite?", ["F29", "F27", "F28", "F40", "F41", "F49"]),
        ("Tenho consignado e vou ser demitido. O que acontece?", ["F30", "F26", "F31", "F23", "F22"]),
        ("Quero levar meu consignado pra outro banco. E meus dados?", ["F31", "F32", "F18", "F19", "F20", "F38"]),
    ],
}

CONECTORES = ["", "Olha, ", "Além disso, ", "E também: ", "Outra coisa: ", "Ah, e ", "Importante: ", "Só pra você saber: "]


def carregar_fatos() -> list[dict]:
    return [json.loads(l) for l in (AQUI / "fatos_norma.jsonl").open(encoding="utf-8")]


ESTRATOS = ("limpo", "um_erro", "misto")


def gerar(fatos: list[dict], n: int, semente: int, estratos: bool = True) -> list[dict]:
    rng = random.Random(semente)
    por_id = {f["id"]: f for f in fatos}
    por_produto = {p: [f for f in fatos if f["produto"] in grupos] for p, grupos in POOLS.items()}
    produtos = list(POOLS)
    dialogos = []
    for i in range(n):
        produto = produtos[i % len(produtos)]  # equilíbrio entre produtos
        pool = por_produto[produto]
        pergunta, foco_ids = rng.choice(PERGUNTAS[produto])
        foco = [por_id[x] for x in foco_ids]
        k = rng.randint(MIN_AF, MAX_AF)
        escolhidos = rng.sample(foco, min(k - 1, len(foco)))
        resto = [f for f in pool if f not in escolhidos]
        escolhidos += rng.sample(resto, k - len(escolhidos))
        # foco primeiro (ordem aleatória), complemento no fim
        ids_foco = set(foco_ids)
        escolhidos.sort(key=lambda f: (f["id"] not in ids_foco, rng.random()))
        # produto gira a cada diálogo; estrato gira a cada ciclo de produtos -> 12 células equilibradas
        estrato = ESTRATOS[(i // len(produtos)) % 3] if estratos else "misto"
        pos_erro = rng.randrange(len(escolhidos)) if estrato == "um_erro" else None
        afirmacoes, partes = [], []
        for pos, f in enumerate(escolhidos):
            sorteio = rng.random()  # sorteado sempre, para o estrato não mudar o resto da sequência
            errada = {"limpo": False, "um_erro": pos == pos_erro, "misto": sorteio < P_ERRO}[estrato]
            if errada:
                e = rng.choice(f["erros"])
                texto, categoria, nota = e["texto"], e["categoria"], e.get("nota")
            else:
                texto, categoria, nota = f["afirmacao"], None, None
            conector = "" if pos == 0 else rng.choice(CONECTORES[1:])
            frase = conector + (texto[0].lower() + texto[1:] if conector else texto)
            partes.append(frase)
            afirmacoes.append({
                "pos": pos, "texto": texto, "fato_id": f["id"], "correta": not errada,
                "categoria_erro": categoria, "gravidade": f["gravidade"] if errada else None,
                "norma": f["norma"], "artigo": f["artigo"], "dispositivo": f["dispositivo"],
                "dificil": bool(nota and ("difícil" in nota or "traiçoeiro" in nota)),
            })
        dialogos.append({
            "id": f"s{semente}-d{i:03d}", "semente": semente, "produto": produto, "estrato": estrato,
            "pergunta": pergunta,
            "resposta": " ".join(partes),
            "afirmacoes": afirmacoes,
            "n_afirmacoes": len(afirmacoes),
            "n_erros": sum(not a["correta"] for a in afirmacoes),
            "n_erros_criticos": sum((not a["correta"]) and a["gravidade"] == "critica" for a in afirmacoes),
        })
    return dialogos


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100, help="diálogos por semente")
    ap.add_argument("--sementes", type=int, default=3)
    ap.add_argument("--semente-inicial", type=int, default=101,
                    help="conjunto principal começa em 101: o piloto (semente 1) fica fora da análise")
    ap.add_argument("--saida", default="dialogos.jsonl")
    ap.add_argument("--sem-estratos", action="store_true", help="desenho do piloto: todos 'misto'")
    a = ap.parse_args()
    fatos = carregar_fatos()
    todos = []
    for s in range(a.semente_inicial, a.semente_inicial + a.sementes):
        todos += gerar(fatos, a.n, semente=s, estratos=not a.sem_estratos)
    with (AQUI / a.saida).open("w", encoding="utf-8") as f:
        for d in todos:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    af = [x for d in todos for x in d["afirmacoes"]]
    erradas = [x for x in af if not x["correta"]]
    print(f"{len(todos)} diálogos, {len(af)} afirmações, {len(erradas)} erradas ({len(erradas)/len(af):.1%}), "
          f"{sum(x['gravidade'] == 'critica' for x in erradas)} críticas; "
          f"diálogos sem erro: {sum(d['n_erros'] == 0 for d in todos)}; "
          f"estratos: { {e: sum(d['estrato'] == e for d in todos) for e in ESTRATOS} }; "
          f"fatos usados: {len({x['fato_id'] for x in af})}/{len(fatos)} -> {a.saida}")


if __name__ == "__main__":
    main()
