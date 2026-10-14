import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

METRICAS = [
    ("vazao_rps", "Vazão (req/s)"),
    ("latencia_media_ms", "Latência média (ms)"),
    ("latencia_p95_ms", "Latência p95 por execução (ms)"),
    ("falhas", "Falhas reportadas pelo AB"),
    ("nao_2xx", "Respostas HTTP não-2xx"),
    ("cpu_pct", "CPU em processamento na VM (%)"),
    ("mem_pico_mib", "Pico de memória usada na VM (MiB)"),
    ("swap_pico_mib", "Pico de swap usado na VM (MiB)"),
    ("iowait_pct", "Tempo médio em iowait (%)"),
    ("escrita_mib_s", "Escrita no disco da VM (MiB/s)"),
    ("latencia_escrita_ms", "Latência média de escrita no disco (ms)"),
]

base = Path(__file__).resolve().parent
with (base / "resultados.csv").open(newline="", encoding="utf-8") as arquivo:
    linhas = list(csv.DictReader(arquivo))
if not linhas:
    raise SystemExit("O CSV não contém resultados. Execute loadtest.sh primeiro.")

(base / "graficos").mkdir(exist_ok=True)
for coluna, titulo in METRICAS:
    grupos = defaultdict(lambda: defaultdict(list))
    for linha in linhas:
        grupos[linha["cenario"]][int(linha["clientes"])].append(float(linha[coluna]))

    plt.figure(figsize=(7, 4))
    for cenario, dados in grupos.items():
        clientes = sorted(dados)
        valores = [mean(dados[c]) for c in clientes]
        plt.plot(clientes, valores, marker="o", label=cenario)
    plt.title(titulo)
    plt.xlabel("Clientes simultâneos")
    plt.ylabel(titulo)
    plt.xticks([1, 5, 10])
    plt.ylim(bottom=0)
    plt.grid(alpha=0.3)
    plt.legend(title="Cenário")
    plt.savefig(base / "graficos" / f"{coluna}.png", dpi=150, bbox_inches="tight")
    plt.close()

print(f"Gráficos salvos em {base / 'graficos'}")
