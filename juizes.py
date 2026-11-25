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
import os
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

# Emenda 2 (24/11/2026, sugestões do orientador, antes de qualquer rodada destes juízes):
# P_SENTENCAS: holístico com saída por sentença numerada (critério igual ao P_HOLISTICO; muda só o formato).
# P_CONFORMIDADE: holístico restrito à conformidade (mesmo formato do P_HOLISTICO; muda só o critério).
P_SENTENCAS = """Avalie a resposta do atendente bancário abaixo quanto à correção perante a regulação brasileira
(BCB/CMN, CDC, LGPD, lei do consignado) e à adequação ao cliente.
A resposta está dividida em sentenças numeradas.

Pergunta do cliente: {pergunta}
Resposta do atendente:
{sentencas}
{normas}
Responda em JSON: {{"decisao": "aprovar|reprovar", "nota": <1 a 5>, "sentencas_nao_conformes": [{{"id": "<S1, S2...>", "dispositivo": <artigo da norma ou "">, "motivo": <frase curta>}}]}}
"aprovar" se a resposta pode ir ao cliente sem correção. Liste em "sentencas_nao_conformes" só as sentenças que precisam ser corrigidas."""

P_CONFORMIDADE = """Avalie a resposta do atendente bancário abaixo apenas quanto à conformidade com a regulação brasileira
(BCB/CMN, CDC, LGPD, lei do consignado).
Aprove se nenhuma afirmação contradiz a norma. Estilo, completude e tom não contam.
Liste problemas só se houver contradição normativa.

Pergunta do cliente: {pergunta}
Resposta do atendente: {resposta}
Responda em JSON: {{"nota": <1 a 5>, "aprovada": <true se nenhuma afirmação contradiz a norma>, "problemas": [<frases curtas, só contradições normativas>]}}"""

# Emenda 3 (25/11/2026, parecer simulado da Applied Intelligence, antes de qualquer rodada destes juízes):
# P_CONF_SENTENCAS: critério do P_CONFORMIDADE + formato do P_SENTENCAS (a célula que faltava no desenho, M3).
P_CONF_SENTENCAS = """Avalie a resposta do atendente bancário abaixo apenas quanto à conformidade com a regulação brasileira
(BCB/CMN, CDC, LGPD, lei do consignado).
Aprove se nenhuma afirmação contradiz a norma. Estilo, completude e tom não contam.
A resposta está dividida em sentenças numeradas.

Pergunta do cliente: {pergunta}
Resposta do atendente:
{sentencas}
{normas}
Responda em JSON: {{"decisao": "aprovar|reprovar", "nota": <1 a 5>, "sentencas_nao_conformes": [{{"id": "<S1, S2...>", "dispositivo": <artigo da norma ou "">, "motivo": <frase curta>}}]}}
"aprovar" se nenhuma sentença contradiz a norma. Liste em "sentencas_nao_conformes" só as sentenças que contradizem a norma."""

# MiniCheck (Tang et al. 2024; Bespoke-MiniCheck-7B no Ollama): formato fixo do modelo, saída "Yes"/"No".
P_MINICHECK = "Document: {documento}\nClaim: {afirmacao}"

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
        # MiniCheck tem formato próprio: sem mensagem de sistema, sem JSON, sem raciocínio.
        self.bruto = nome.startswith("bespoke-minicheck")

    def gerar(self, prompt: str) -> tuple[dict, dict]:
        if self.bruto:
            corpo = {"model": self.nome, "stream": False,
                     "messages": [{"role": "user", "content": prompt}],
                     "options": {"temperature": self.temp, "seed": self.semente, "num_ctx": 8192}}
        else:
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
        if self.bruto:  # MiniCheck: texto livre ("Yes"/"No"), sem JSON
            return {"texto": d["message"]["content"].strip()}, meta
        try:
            return json.loads(d["message"]["content"]), meta
        except json.JSONDecodeError:
            return {"_erro_json": d["message"]["content"][:500]}, meta


class HaikuLote:
    """Claude Haiku 5.5 pela Batch API, em duas fases (ver haiku_lote.py; chave lida só lá).

    modo "gravar": registra cada prompt em resultados/haiku_pendentes.jsonl e devolve um marcador
    (que não entra no cache nem nas saídas: a fase 1 escreve num arquivo descartável).
    modo "ler": devolve a resposta do lote (resultados/haiku_respostas.jsonl), por hash do prompt.
    Sem raciocínio (thinking desligado), como os modelos locais; a API não aceita temperatura.
    """
    nome = "claude-haiku-5-5"
    temp = semente = None

    def __init__(self, modo: str):
        self.modo = modo
        self.pend = RES / "haiku_pendentes.jsonl"
        self.resp = {}
        if modo == "ler" and (RES / "haiku_respostas.jsonl").exists():
            for l in (RES / "haiku_respostas.jsonl").open(encoding="utf-8"):
                x = json.loads(l)
                self.resp[x["h"]] = (x["out"], x["meta"])

    @staticmethod
    def h(prompt):
        return hashlib.sha256((SISTEMA + "\x00" + prompt).encode()).hexdigest()[:32]

    def gerar(self, prompt: str) -> tuple[dict, dict]:
        h = self.h(prompt)
        if self.modo == "gravar":
            with self.pend.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"h": h, "prompt": prompt}, ensure_ascii=False) + "\n")
            return {"_erro_json": "pendente"}, {"tokens_in": 0, "tokens_out": 0, "seg": 0.0}
        if h not in self.resp:
            return {"_erro_json": "sem_resposta_no_lote"}, {"tokens_in": 0, "tokens_out": 0, "seg": 0.0}
        out, meta = self.resp[h]
        return json.loads(json.dumps(out)), dict(meta)


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
        # Emenda 3 (M9): recuperação oráculo = só o artigo do gabarito da afirmação (separa erro de
        # recuperação de erro de veredito). Só vale com segmentação pelo gabarito.
        self._gold = {}
        for d in self.docs:
            self._gold.setdefault((d["norma"], str(d["artigo"])), d)
        if modo == "hibrida":
            from densa import Densa
            self.de = Densa(self.docs, chunk=True)
            self._pos = {id(d): i for i, d in enumerate(self.docs)}

    def gold(self, afirmacao: dict) -> list[dict]:
        return [self._gold[(afirmacao["norma"], str(afirmacao["artigo"]))]]

    def buscar(self, texto: str, k: int) -> list[tuple[float, dict]]:
        if self.modo == "oraculo":
            raise ValueError("recuperação oráculo: use gold(afirmação), não buscar(texto)")
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
    if juiz == "holistico_conformidade":
        out = chamar(P_CONFORMIDADE.format(pergunta=dialogo["pergunta"], resposta=dialogo["resposta"]))
        r.update({"aprovada": bool(out.get("aprovada")), "nota": out.get("nota"), "bruto": out})
    elif juiz.startswith("holistico_sentencas") or juiz == "holistico_conformidade_sentencas_normas":
        afs = dialogo["afirmacoes"]
        normas = ""
        if juiz.endswith("_normas"):  # o mesmo top-k por afirmação que o verificador usa
            docs, vistos = [], set()
            for a in afs:
                for _, d in idx.buscar(a["texto"], k=k):
                    if (d["norma"], d["artigo"]) not in vistos:
                        vistos.add((d["norma"], d["artigo"])); docs.append(d)
            normas = fmt_normas(docs, limite=700)
        sent = "\n".join(f"S{i}: {a['texto']}" for i, a in enumerate(afs, 1))
        tmpl = P_CONF_SENTENCAS if juiz == "holistico_conformidade_sentencas_normas" else P_SENTENCAS
        out = chamar(tmpl.format(pergunta=dialogo["pergunta"], sentencas=sent, normas=normas))
        ids = set()
        for x in out.get("sentencas_nao_conformes") or []:
            m = re.search(r"\d+", str(x.get("id", "") if isinstance(x, dict) else x))
            if m:
                ids.add(int(m.group()))
        r.update({"aprovada": str(out.get("decisao", "")).lower().startswith("aprov"), "nota": out.get("nota"),
                  "por_gold_sent": [i in ids for i in range(1, len(afs) + 1)], "bruto": out})
    elif juiz == "minicheck":
        # Baseline de grounding (M1): cada afirmação do gabarito contra o mesmo top-k do verificador.
        # "No" (não sustentada) = contestada. Não distingue "contradiz" de "não sustenta".
        vereditos = []
        for a in dialogo["afirmacoes"]:
            docs = [d for _, d in idx.buscar(a["texto"], k=k)]
            documento = " ".join(f"[{d['norma']}, art. {d['artigo']}] {re.sub(r'\\s+', ' ', d['texto'])[:1800]}" for d in docs)
            out = chamar(P_MINICHECK.format(documento=documento, afirmacao=a["texto"]))
            txt = str(out.get("texto", "")).strip().lower()
            v = "confirma" if txt.startswith("yes") else ("contesta" if txt.startswith("no") else "invalido")
            vereditos.append({"veredito": v, "bruto": out.get("texto", out.get("_erro_json", ""))[:40],
                              "dispositivos": [f"{d['norma']} art. {d['artigo']}" for d in docs]})
        r.update({"vereditos": vereditos, "por_gold": [contestada(v) for v in vereditos],
                  "aprovada": not any(contestada(v) for v in vereditos)})
    elif juiz.startswith("holistico"):
        normas = ""
        if juiz in ("holistico_normas", "holistico_normas_k3"):
            # holistico_normas: top-1 por afirmação (rodada principal). holistico_normas_k3 (emenda 3, M4):
            # o mesmo top-3 deduplicado, até 700 caracteres, que o verificador e o por sentença + normas recebem.
            kk, lim = (1, 900) if juiz == "holistico_normas" else (k, 700)
            docs, vistos = [], set()
            for a in dialogo["afirmacoes"]:
                for _, d in idx.buscar(a["texto"], k=kk):
                    if (d["norma"], d["artigo"]) not in vistos:
                        vistos.add((d["norma"], d["artigo"])); docs.append(d)
            normas = fmt_normas(docs, limite=lim)
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
        for i_t, t in enumerate(textos):
            if juiz == "afirmacao_sem_rag":
                docs = []
            elif idx.modo == "oraculo":
                assert segmentacao == "oraculo", "recuperação oráculo exige segmentação pelo gabarito"
                docs = idx.gold(dialogo["afirmacoes"][i_t])
            else:
                docs = [d for _, d in idx.buscar(t, k=k)]
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
                    choices=["holistico", "holistico_normas", "afirmacao", "afirmacao_regras", "afirmacao_sem_rag",
                             "holistico_sentencas", "holistico_sentencas_normas", "holistico_conformidade",
                             "holistico_conformidade_sentencas_normas", "holistico_normas_k3", "minicheck"])
    ap.add_argument("--modelo", default="mock")
    ap.add_argument("--dialogos", default="dialogos.jsonl")
    ap.add_argument("--limite", type=int, default=0, help="só os N primeiros diálogos")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--segmentacao", choices=["oraculo", "llm"], default="oraculo")
    ap.add_argument("--recuperacao", choices=["bm25", "hibrida", "oraculo"], default="hibrida")
    a = ap.parse_args()

    if a.modelo == "mock":
        base = Mock()
    elif a.modelo.startswith("claude-haiku"):
        base = HaikuLote(os.environ.get("HAIKU_MODO", "ler"))
    else:
        base = Ollama(a.modelo)
    modelo = Cache(base)
    if a.modelo.startswith("claude-haiku") and base.modo == "gravar":
        modelo.ativo = False
    modelo.nome = modelo.modelo.nome
    idx = Recuperador(a.recuperacao)
    RES.mkdir(exist_ok=True)
    rotulo = re.sub(r"[^a-zA-Z0-9.-]+", "-", a.modelo)
    saida = RES / f"{a.juiz}__{rotulo}__{a.segmentacao}__{a.recuperacao}__{Path(a.dialogos).stem}.jsonl"
    if not modelo.ativo and getattr(base, "modo", "") == "gravar":  # fase 1 do Haiku: saída descartável
        saida = Path(os.environ.get("TMPDIR", "/tmp")) / f"_haiku_gravar__{a.juiz}.jsonl"
        saida.unlink(missing_ok=True)
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
