"""Juiz comercial (Claude Haiku 5.5) pela Message Batches API, com teto de custo.

Uso:
  python haiku_lote.py gravar   # roda os juízes em modo gravação e junta os prompts únicos
  python haiku_lote.py enviar   # estima o custo, aborta se passar do teto, cria o lote
  python haiku_lote.py coletar  # espera o lote e grava resultados/haiku_respostas.jsonl
  depois: HAIKU_MODO=ler python juizes.py --juiz <j> --modelo claude-haiku-5-5 ...
A chave fica em ~/.config/anthropic/haiku.key (permissão 600) e nunca é impressa.
Teto: US$ 1,00 (o do Bispo é US$ 1,11). Preço do lote: metade do padrão (US$ 0,10/0,50 por MTok).
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).parent
RES = AQUI / "resultados"
MODELO = "claude-haiku-5-5"
TETO_USD = 1.00
P_IN, P_OUT = 0.10 / 2 / 1e6, 0.50 / 2 / 1e6  # lote = 50% do preço padrão
MAX_TOKENS = 1024
JUIZES = ["holistico", "holistico_normas", "holistico_conformidade", "holistico_sentencas",
          "holistico_sentencas_normas", "afirmacao", "afirmacao_regras"]
ESTADO = RES / "haiku_lote_estado.json"


def cliente():
    import anthropic
    chave = (Path.home() / ".config/anthropic/haiku.key").read_text().strip()
    chave = chave.split("=", 1)[1].strip().strip("\"'") if "=" in chave[:20] else chave  # aceita "API_KEY=..."
    return anthropic.Anthropic(api_key=chave)


def prompts():
    vistos = {}
    for l in (RES / "haiku_pendentes.jsonl").open(encoding="utf-8"):
        x = json.loads(l)
        vistos.setdefault(x["h"], x["prompt"])
    return vistos


def gravar():
    (RES / "haiku_pendentes.jsonl").unlink(missing_ok=True)
    for j in JUIZES:
        subprocess.run([sys.executable, "juizes.py", "--juiz", j, "--modelo", MODELO, "--dialogos", "dialogos.jsonl",
                        "--recuperacao", "hibrida"], cwd=AQUI, check=True, env=dict(os.environ, HAIKU_MODO="gravar"))
    print("prompts únicos:", len(prompts()))


def params(prompt):
    from juizes import SISTEMA
    return {"model": MODELO, "max_tokens": MAX_TOKENS, "system": SISTEMA,
            "thinking": {"type": "disabled"},
            "messages": [{"role": "user", "content": prompt}]}


def enviar():
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    P = prompts()
    c = cliente()
    # estimativa conservadora: conta os tokens de uma amostra com a API e extrapola por caracteres
    amostra = list(P.items())[:: max(1, len(P) // 15)]
    tok = chars = 0
    for _, p in amostra:
        tok += c.messages.count_tokens(model=MODELO, system=params(p)["system"], messages=params(p)["messages"]).input_tokens
        chars += len(p)
    t_in = tok / chars * sum(len(p) for p in P.values()) + 0 * len(P)
    custo = t_in * P_IN + len(P) * MAX_TOKENS * P_OUT  # saída no pior caso (todas no teto)
    print(f"{len(P)} pedidos; ~{t_in/1e6:.2f} MTok de entrada; custo máximo estimado US$ {custo:.3f} (teto {TETO_USD})")
    if custo > TETO_USD:
        sys.exit("ABORTADO: passaria do teto")
    lote = c.messages.batches.create(requests=[
        Request(custom_id=h, params=MessageCreateParamsNonStreaming(**params(p))) for h, p in P.items()])
    ESTADO.write_text(json.dumps({"id": lote.id, "n": len(P), "custo_max_est": custo,
                                  "criado": time.strftime("%Y-%m-%d %H:%M:%S")}))
    print("lote criado:", lote.id)


def extrair_json(txt):
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.S)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return {"_erro_json": txt[:500]}


def coletar():
    c = cliente()
    est = json.loads(ESTADO.read_text())
    while True:
        b = c.messages.batches.retrieve(est["id"])
        if b.processing_status == "ended":
            break
        print("processando:", b.request_counts.processing, flush=True)
        time.sleep(60)
    tin = tout = 0
    n_ok = n_err = 0
    with (RES / "haiku_respostas.jsonl").open("w", encoding="utf-8") as f:
        for r in c.messages.batches.results(est["id"]):
            if r.result.type != "succeeded":
                n_err += 1
                continue
            m = r.result.message
            txt = "".join(b.text for b in m.content if b.type == "text")
            out = extrair_json(txt) if m.stop_reason != "refusal" else {"_erro_json": "refusal"}
            u = m.usage
            tin += u.input_tokens; tout += u.output_tokens; n_ok += 1
            f.write(json.dumps({"h": r.custom_id, "out": out, "meta": {
                "tokens_in": u.input_tokens, "tokens_out": u.output_tokens, "seg": 0.0,
                "stop": m.stop_reason}}, ensure_ascii=False) + "\n")
    custo = tin * P_IN + tout * P_OUT
    est.update({"ok": n_ok, "erros": n_err, "tokens_in": tin, "tokens_out": tout, "custo_usd": round(custo, 4)})
    ESTADO.write_text(json.dumps(est))
    print(f"ok {n_ok}, erros {n_err}; tokens {tin} in / {tout} out; custo US$ {custo:.4f}")


if __name__ == "__main__":
    {"gravar": gravar, "enviar": enviar, "coletar": coletar}[sys.argv[1]]()
