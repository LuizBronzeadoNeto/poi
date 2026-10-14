import csv
import os

import matplotlib.pyplot as plt

METRICAS = [
    ("vazao_rps", "Vazão (req/s)"),
    ("latencia_media_ms", "Latência média (ms)"),
    ("latencia_p95_ms", "Latência p95 (ms)"),
    ("falhas", "Requisições com falha"),
    ("cpu_pct", "Uso médio de CPU da VM (%)"),
    ("mem_pico_mb", "Pico de memória usada na VM (MB)"),
    ("swap_pico_mb", "Pico de swap usado na VM (MB)"),
    ("concluidas_pct", "Requisições concluídas (%)"),
]

with open("resultados.csv") as f:
    linhas = list(csv.DictReader(f))
cenarios = list(dict.fromkeys(l["cenario"] for l in linhas))

os.makedirs("graficos", exist_ok=True)
for coluna, titulo in METRICAS:
    plt.figure(figsize=(7, 4))
    for cenario in cenarios:
        dados = [l for l in linhas if l["cenario"] == cenario and l[coluna]]
        x = [int(l["clientes"]) for l in dados]
        y = [float(l[coluna]) for l in dados]
        estilo = "--" if "CPUs" in cenario else ":" if "sem swap" in cenario else "-"
        plt.plot(x, y, marker="o", label=cenario, linestyle=estilo)
    plt.title(titulo)
    plt.xlabel("Clientes simultâneos")
    plt.xscale("log", base=2)
    plt.xticks([5, 10, 20, 40, 80], ["5", "10", "20", "40", "80"])
    plt.ylim(bottom=0)
    plt.grid(alpha=0.3)
    plt.legend(title="Cenário")
    plt.savefig(f"graficos/{coluna}.png", dpi=150, bbox_inches="tight")
    plt.close()
