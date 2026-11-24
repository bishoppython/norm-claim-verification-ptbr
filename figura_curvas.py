"""Figura 1: curvas de operação (falso alarme x FAR-crítico) por modelo.

Holístico e holístico + normas: reprova se nota <= t (t = 0..5).
Por afirmação + regras: reprova se >= k afirmações contestadas (k = 1..8, mais "nunca").
Grava ../latex/Fig1.eps (Applied Intelligence pede EPS) e ../latex/Fig1.png (prévia).
Requer matplotlib (não está no ambiente do experimento; ver README).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import metricas as M
from analise import carregar, GAB, MODELOS

SAIDA = Path(__file__).parent.parent / "latex"
NOMES = {"qwen3.5-9b": "qwen3.5:9b", "gemma4-12b": "gemma4:12b", "llama3.1-8b": "llama3.1:8b", "gpt-oss-20b": "gpt-oss:20b"}
# cor + marcador + traço: a identidade nunca depende só da cor (impressão em cinza, daltonismo)
JUIZES = [("holistico", "Holistic", "#1c5cab", "o", "-"),
          ("holistico_normas", "Holistic + norms", "#b4461a", "s", "--"),
          ("afirmacao_regras", "Claim-level + rules (proposed)", "#0b7a52", "^", "-")]


def pontos(us, holistico):
    crit = [u for u in us if u["tem_critico"]]
    limpo = [u for u in us if u["sem_erro"]]
    if holistico:
        reprova = [lambda u, t=t: float(u["nota"]) <= t for t in range(0, 6)]
    else:
        reprova = [lambda u, k=k: u["susp"] >= k for k in range(1, 10)] + [lambda u: True]
    out = []
    for f in reprova:
        fa = sum(f(u) for u in limpo) / len(limpo)
        far = sum(not f(u) for u in crit) / len(crit)
        out.append((fa, far))
    return sorted(set(out))


def main():
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
                         "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 8,
                         "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.edgecolor": "#555555",
                         "axes.linewidth": 0.6, "xtick.color": "#333333", "ytick.color": "#333333"})
    fig, axs = plt.subplots(2, 2, figsize=(6.3, 5.6), sharex=True, sharey=True)
    for ax, m in zip(axs.flat, MODELOS):
        for j, rot, cor, mk, ls in JUIZES:
            us = M.unidades(carregar(j, m), GAB)
            p = pontos(us, j.startswith("holistico"))
            ax.plot([x for x, _ in p], [y for _, y in p], ls=ls, lw=1.5, color=cor, marker=mk, ms=5,
                    mfc="white", mew=1.2, label=rot, zorder=3)
            if j == "afirmacao_regras":  # ponto padrão (k = 1)
                fa = sum(u["susp"] >= 1 for u in us if u["sem_erro"]) / sum(u["sem_erro"] for u in us)
                far = sum(u["susp"] < 1 for u in us if u["tem_critico"]) / sum(u["tem_critico"] for u in us)
                ax.plot([fa], [far], marker=mk, ms=6, color=cor, zorder=4)
                ax.annotate("k = 1", (fa, far), xytext=(5, -13), textcoords="offset points", fontsize=7.5,
                            color="#222222", ha="left")
        ax.set_title(NOMES[m], loc="left", color="#111111")
        ax.grid(True, lw=0.4, color="#dddddd", zorder=0)
        ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    for ax in axs[1]:
        ax.set_xlabel("False alarm (error-free answers rejected)")
    for ax in axs[:, 0]:
        ax.set_ylabel("FAR-critical (critical answers approved)")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(SAIDA / "Fig1.eps", format="eps")
    fig.savefig(SAIDA / "Fig1.png", dpi=200)
    print("ok", SAIDA / "Fig1.eps")


if __name__ == "__main__":
    main()
