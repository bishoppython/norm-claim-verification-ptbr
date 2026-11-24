"""Juízes (Dia 4): holístico, holístico com normas e verificação por afirmação.

Juízes:
  holistico        nota 1-5 + aprova/reprova a resposta inteira (estilo G-Eval simples)
  holistico_normas o mesmo, recebendo os artigos recuperados (ablação "sem extração")
  afirmacao        por afirmação: recupera a norma (BM25) e o LLM dá o veredito
  afirmacao_regras igual, mas as regras determinísticas decidem primeiro (método proposto)
  afirmacao_sem_rag por afirmação sem norma (ablação "sem recuperação")

Segmentação: por padrão usa as afirmações do gabarito (--segmentacao oraculo), o que
isola a qualidade do veredito; --segmentacao llm pede ao modelo para extrair as
afirmações (fim a fim) e alinha com o gabarito por sobreposição de palavras.

Modelos: --modelo mock (teste, sem GPU) ou nome de um modelo do Ollama.
**Rodar com modelo do Ollama usa a GPU: só com autorização do Bispo.**

Saída: resultados/<juiz>__<modelo>.jsonl, um diálogo por linha; retoma de onde parou.
"""
import argparse
import hashlib
import json
import random
import re
import time
import urllib.request
from pathlib import Path

from recuperar import carregar_indice, tokens
from regras import decidir

AQUI = Path(__file__).parent
RES = AQUI / "resultados"

SISTEMA = "Você é auditor de conformidade de um banco brasileiro. Responda só com JSON válido."

P_HOLISTICO = """Avalie a resposta do atendente bancário abaixo quanto à correção perante a regulação brasileira
(BCB/CMN, CDC, LGPD, lei do consignado) e à adequação ao cliente.

Pergunta do cliente: {pergunta}
Resposta do atendente: {resposta}
{normas}
Responda em JSON: {{"nota": <1 a 5>, "aprovada": <true se pode ir ao cliente sem correção>, "problemas": [<frases curtas>]}}"""

P_EXTRAIR = """Divida a resposta do atendente em afirmações atômicas verificáveis, uma por item, sem mudar o sentido.
Resposta: {resposta}
Responda em JSON: {{"afirmacoes": [<texto>, ...]}}"""

P_VERIFICAR = """Verifique a afirmação de um atendente bancário contra os trechos de norma abaixo.
Afirmação: {afirmacao}
{normas}
Regras: "confirma" se a norma sustenta a afirmação; "contesta" se a norma a contradiz ou se a afirmação
promete, nega ou altera algo (valor, prazo, direito, conceito, uso de dados) em desacordo com a norma;
"insuficiente" se os trechos não permitem decidir.
Equivalências usuais de quantidade contam como iguais (seis meses = 180 dias; um ano = 365 dias; mil = 1.000).
Responda em JSON: {{"veredito": "confirma|contesta|insuficiente", "motivo": <frase curta>, "dispositivo": <artigo citado ou "">}}"""


# ----------------------------------------------------------------- modelos
class Mock:
    """Modelo simulado: respostas aleatórias mas bem formadas (só para testar o pipeline)."""
    nome = "mock"

    def __init__(self, semente=0):
        self.rng = random.Random(semente)

    def gerar(self, prompt: str) -> tuple[dict, dict]:
        t0 = time.time()
        if '"afirmacoes"' in prompt:
            resp = prompt.split("Resposta: ", 1)[1].split("\nResponda", 1)[0]
            out = {"afirmacoes": [s.strip() for s in re.split(r"(?<=[.?!])\s+", resp) if s.strip()]}
        elif '"veredito"' in prompt:
            out = {"veredito": self.rng.choice(["confirma", "contesta", "insuficiente"]), "motivo": "mock", "dispositivo": ""}
        else:
            out = {"nota": self.rng.randint(1, 5), "aprovada": self.rng.random() < 0.5, "problemas": []}
        return out, {"tokens_in": len(prompt) // 4, "tokens_out": 20, "seg": time.time() - t0}


class Ollama:
    def __init__(self, nome: str, url="http://localhost:11434", temperatura=0.0, semente=42):
        self.nome, self.url, self.temp, self.semente = nome, url, temperatura, semente
        # gpt-oss não desliga o raciocínio (think=False devolve texto quebrado, teste de 23/11/2026);
        # usa o nível mínimo, "low". Os demais modelos rodam sem raciocínio.
        self.think = "low" if nome.startswith("gpt-oss") else False

    def gerar(self, prompt: str) -> tuple[dict, dict]:
        corpo = {"model": self.nome, "stream": False, "format": "json", "think": self.think,
                 "messages": [{"role": "system", "content": SISTEMA}, {"role": "user", "content": prompt}],
                 "options": {"temperature": self.temp, "seed": self.semente, "num_ctx": 8192}}
        t0 = time.time()
        req = urllib.request.Request(self.url + "/api/chat", data=json.dumps(corpo).encode(),
                                     headers={"Content-Type": "application/json"})
        # Pré-registro (Exclusões): falha de execução é refeita com a mesma configuração e reportada.
        # Timeout (> 600 s; llama3.1 em 23/11/2026) tenta 2 vezes; persistindo, a saída conta como
        # JSON inválido (= aprovado / não contestado, o pior caso para o juiz) e fica marcada.
        for tentativa in (1, 2):
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    d = json.loads(r.read())
                break
            except (TimeoutError, OSError) as e:
                if "timed out" not in str(e) and not isinstance(e, TimeoutError):
                    raise
                print(f"  TIMEOUT {self.nome} (tentativa {tentativa})", flush=True)
                if tentativa == 2:
                    return {"_erro_json": "timeout", "_timeout": True}, \
                        {"tokens_in": 0, "tokens_out": 0, "seg": time.time() - t0}
        meta = {"tokens_in": d.get("prompt_eval_count", 0), "tokens_out": d.get("eval_count", 0),
                "seg": time.time() - t0}
        try:
            return json.loads(d["message"]["content"]), meta
        except json.JSONDecodeError:
            return {"_erro_json": d["message"]["content"][:500]}, meta


# ----------------------------------------------------------------- cache
class Cache:
    """Cache de chamadas por prompt (modelo + sistema + prompt + opções).

    Com temperatura 0 e semente fixa, o mesmo prompt dá a mesma saída; a verificação
    de uma afirmação depende só do texto dela e das normas recuperadas, e os 300
    diálogos têm ~140 afirmações distintas. Um acerto de cache devolve a saída e o
    custo (tokens, latência) da chamada original, para o custo reportado continuar
    sendo o de um sistema sem cache.
    """

    def __init__(self, modelo):
        self.modelo = modelo
        self.ativo = modelo.nome != "mock"
        self.arq = RES / f"cache__{re.sub(r'[^a-zA-Z0-9.-]+', '-', modelo.nome)}.jsonl"
        self.mem, self.acertos = {}, 0
        if self.ativo and self.arq.exists():
            for l in self.arq.open(encoding="utf-8"):
                x = json.loads(l)
                self.mem[x["chave"]] = (x["out"], x["meta"])

    def gerar(self, prompt: str) -> tuple[dict, dict]:
        if not self.ativo:
            return self.modelo.gerar(prompt)
        opc = [getattr(self.modelo, "temp", None), getattr(self.modelo, "semente", None)]
        if getattr(self.modelo, "think", False):
            opc.append(self.modelo.think)
        opc = json.dumps(opc)
        k = hashlib.sha256((self.modelo.nome + "\x00" + SISTEMA + "\x00" + prompt + "\x00" + opc).encode()).hexdigest()
        if k in self.mem:
            self.acertos += 1
            out, meta = self.mem[k]
            return json.loads(json.dumps(out)), dict(meta, cache=True)
        out, meta = self.modelo.gerar(prompt)
        if "_erro_json" not in out:  # erro de JSON não entra no cache: tenta de novo na próxima
            self.mem[k] = (out, meta)
            with self.arq.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"chave": k, "out": out, "meta": meta}, ensure_ascii=False) + "\n")
        return out, meta


# ----------------------------------------------------------------- recuperação
class Recuperador:
    """bm25 (léxica) ou hibrida (BM25 + bge-m3 em trechos, por RRF; melhor no teste:
    recall@3 0,705 contra 0,586 do BM25). A híbrida usa GPU para embutir as consultas."""

    def __init__(self, modo: str):
        self.modo = modo
        self.bm = carregar_indice()
        self.docs = self.bm.docs
        self._memo = {}
        if modo == "hibrida":
            from densa import Densa
            self.de = Densa(self.docs, chunk=True)
            self._pos = {id(d): i for i, d in enumerate(self.docs)}

    def buscar(self, texto: str, k: int) -> list[tuple[float, dict]]:
        if self.modo == "bm25":
            return self.bm.buscar(texto, k=k)
        from densa import embed, rrf
        if texto not in self._memo:
            self._memo[texto] = embed([texto])[0]
        r_bm = [self._pos[id(d)] for _, d in self.bm.buscar(texto, k=50)]
        r_de = self.de.ranking(self._memo[texto], 50)
        return [(0.0, self.docs[i]) for i in rrf(r_bm, r_de)[:k]]


# ----------------------------------------------------------------- utilidades
def fmt_normas(docs: list[dict], limite=1800) -> str:
    if not docs:
        return ""
    partes = [f"[{d['norma']}, art. {d['artigo']}] {re.sub(r'\\s+', ' ', d['texto'])[:limite]}" for d in docs]
    return "Trechos de norma:\n" + "\n".join(partes) + "\n"


def alinhar(extraidas: list[str], gold: list[dict]) -> list[int | None]:
    """Para cada afirmação do gabarito, o índice da extraída mais parecida (Jaccard ≥ 0,5)."""
    te = [set(tokens(x)) for x in extraidas]
    out = []
    for g in gold:
        tg = set(tokens(g["texto"]))
        notas = [(len(tg & t) / max(1, len(tg | t)), i) for i, t in enumerate(te)]
        melhor = max(notas, default=(0, None))
        out.append(melhor[1] if melhor[0] >= 0.5 else None)
    return out


def contestada(v: dict) -> bool:
    return str(v.get("veredito", "")).lower().startswith("contest")


# ----------------------------------------------------------------- juízes
def julgar(dialogo: dict, juiz: str, modelo, idx, k: int, segmentacao: str) -> dict:
    custo = {"tokens_in": 0, "tokens_out": 0, "seg": 0.0, "chamadas": 0, "cache": 0}

    def chamar(prompt):
        out, meta = modelo.gerar(prompt)
        for c in ("tokens_in", "tokens_out", "seg"):
            custo[c] += meta[c]
        custo["chamadas"] += 1
        custo["cache"] += bool(meta.get("cache"))
        return out

    r = {"id": dialogo["id"], "juiz": juiz, "modelo": getattr(modelo, "modelo", modelo).nome, "segmentacao": segmentacao}
    if juiz.startswith("holistico"):
        normas = ""
        if juiz == "holistico_normas":
            docs, vistos = [], set()
            for a in dialogo["afirmacoes"]:
                for _, d in idx.buscar(a["texto"], k=1):
                    if (d["norma"], d["artigo"]) not in vistos:
                        vistos.add((d["norma"], d["artigo"])); docs.append(d)
            normas = fmt_normas(docs, limite=900)
        out = chamar(P_HOLISTICO.format(pergunta=dialogo["pergunta"], resposta=dialogo["resposta"], normas=normas))
        r.update({"aprovada": bool(out.get("aprovada")), "nota": out.get("nota"), "bruto": out})
    else:
        if segmentacao == "llm":
            ext = chamar(P_EXTRAIR.format(resposta=dialogo["resposta"])).get("afirmacoes") or []
            ext = [str(x) for x in ext]
            textos, mapa = ext, alinhar(ext, dialogo["afirmacoes"])
        else:
            textos = [a["texto"] for a in dialogo["afirmacoes"]]
            mapa = list(range(len(textos)))
        vereditos = []
        for t in textos:
            docs = [] if juiz == "afirmacao_sem_rag" else [d for _, d in idx.buscar(t, k=k)]
            if juiz == "afirmacao_regras":
                v, motivo = decidir(t, [d["texto"] for d in docs])
                if v != "abstem":
                    vereditos.append({"veredito": v, "motivo": "regra: " + motivo, "fonte": "regra"})
                    continue
            out = chamar(P_VERIFICAR.format(afirmacao=t, normas=fmt_normas(docs)))
            out["fonte"] = "llm"
            vereditos.append(out)
        r.update({
            "extraidas": textos if segmentacao == "llm" else None,
            "vereditos": vereditos,
            "por_gold": [None if m is None else contestada(vereditos[m]) for m in mapa],
            "aprovada": not any(contestada(v) for v in vereditos),
        })
    r["custo"] = custo
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--juiz", required=True,
                    choices=["holistico", "holistico_normas", "afirmacao", "afirmacao_regras", "afirmacao_sem_rag"])
    ap.add_argument("--modelo", default="mock")
    ap.add_argument("--dialogos", default="dialogos.jsonl")
    ap.add_argument("--limite", type=int, default=0, help="só os N primeiros diálogos")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--segmentacao", choices=["oraculo", "llm"], default="oraculo")
    ap.add_argument("--recuperacao", choices=["bm25", "hibrida"], default="hibrida")
    a = ap.parse_args()

    modelo = Cache(Mock() if a.modelo == "mock" else Ollama(a.modelo))
    modelo.nome = modelo.modelo.nome
    idx = Recuperador(a.recuperacao)
    RES.mkdir(exist_ok=True)
    rotulo = re.sub(r"[^a-zA-Z0-9.-]+", "-", a.modelo)
    saida = RES / f"{a.juiz}__{rotulo}__{a.segmentacao}__{a.recuperacao}__{Path(a.dialogos).stem}.jsonl"
    feitos = {json.loads(l)["id"] for l in saida.open(encoding="utf-8")} if saida.exists() else set()
    dialogos = [json.loads(l) for l in (AQUI / a.dialogos).open(encoding="utf-8")]
    if a.limite:
        dialogos = dialogos[: a.limite]
    pend = [d for d in dialogos if d["id"] not in feitos]
    print(f"{a.juiz} / {a.modelo}: {len(pend)} pendentes de {len(dialogos)} -> {saida.name}")
    with saida.open("a", encoding="utf-8") as f:
        for i, d in enumerate(pend, 1):
            r = julgar(d, a.juiz, modelo, idx, a.k, a.segmentacao)
            f.write(json.dumps(r, ensure_ascii=False) + "\n"); f.flush()
            if i % 10 == 0 or i == len(pend):
                print(f"  {i}/{len(pend)}", flush=True)


if __name__ == "__main__":
    main()
