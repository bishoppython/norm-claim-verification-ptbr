"""Segmenta as normas de fontes/*.json em artigos (unidade de recuperação do RAG
e de citação dos fatos-norma).

Saída: fontes/artigos.jsonl, uma linha por artigo:
  {norma, artigo, ordem, texto, n_chars, duplicado, revogado_marcado}

Cuidado com os textos compilados do Planalto: eles trazem a redação antiga junto
da nova (o tachado some na extração). Por isso:
- `duplicado` marca a 2ª, 3ª... ocorrência do mesmo número de artigo na norma;
- `revogado_marcado` marca artigo cujo texto diz "(Revogado" ou "(Vide ...)".
Fato-norma só pode citar artigo vigente, conferido à mão no texto da fonte.
"""
import json
import re
from pathlib import Path

FONTES = Path(__file__).parent / "fontes"
RE_ART = re.compile(r"\n\s*(Art\.\s?(\d+)\s?[º°o]?(?:\s?-\s?([A-Z]))?\.?)")


def normalizar(num: str, letra: str | None) -> str:
    return f"{int(num)}" + (f"-{letra}" if letra else "")


def segmentar(norma_id: str, texto: str) -> list[dict]:
    marcas = list(RE_ART.finditer("\n" + texto))
    saida, vistos = [], {}
    for i, m in enumerate(marcas):
        ini = m.start(1)
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto) + 1
        trecho = re.sub(r"[ \t]+", " ", ("\n" + texto)[ini:fim]).strip()
        art = normalizar(m.group(2), m.group(3))
        vistos[art] = vistos.get(art, 0) + 1
        saida.append({
            "norma": norma_id,
            "artigo": art,
            "ordem": i,
            "texto": trecho,
            "n_chars": len(trecho),
            "duplicado": vistos[art] > 1,
            "revogado_marcado": bool(re.search(r"\(Revogad[oa]", trecho[:400])),
        })
    return saida


def main() -> None:
    todos = []
    for arq in sorted(FONTES.glob("*.json")):
        d = json.loads(arq.read_text(encoding="utf-8"))
        arts = segmentar(d["id"], d["texto"])
        todos += arts
        dup = sum(a["duplicado"] for a in arts)
        rev = sum(a["revogado_marcado"] for a in arts)
        print(f"{d['id']:16} artigos={len(arts):4}  duplicados={dup:3}  revogados_marcados={rev:3}")
    with (FONTES / "artigos.jsonl").open("w", encoding="utf-8") as f:
        for a in todos:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
    print(f"total: {len(todos)} artigos -> fontes/artigos.jsonl")


if __name__ == "__main__":
    main()
