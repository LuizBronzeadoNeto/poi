import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

CSV_FILE = sys.argv[1] if len(sys.argv) > 1 else "resultados_cpu.csv"

if not os.path.exists(CSV_FILE):
    print(f"Erro: Arquivo '{CSV_FILE}' nao encontrado.")
    sys.exit(1)

df = pd.read_csv(CSV_FILE)
df = df.sort_values(by=["vcpus", "cenario", "clientes"])

metrics = [
    ("vazao_rps", "Vazão (Throughput) vs. Clientes", "Vazão (req/s)", "grafico_vazao.png"),
    ("latencia_media_ms", "Latência Média vs. Clientes", "Latência Média (ms)", "grafico_latencia_media.png"),
    ("latencia_p50_ms", "Latência Mediana (p50) vs. Clientes", "Latência p50 (ms)", "grafico_latencia_p50.png"),
    ("latencia_p95_ms", "Latência p95 vs. Clientes", "Latência p95 (ms)", "grafico_latencia_p95.png"),
    ("falhas", "Falhas vs. Clientes", "Número de Falhas", "grafico_falhas.png"),
    ("cpu_pct", "Uso de CPU vs. Clientes", "Uso de CPU (%)", "grafico_cpu.png"),
]

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
colors = plt.cm.tab10.colors
markers = ["o", "s", "^", "D", "v", "p", "*"]

scenarios = df["cenario"].unique()

for col, title, ylabel, filename in metrics:
    plt.figure(figsize=(8, 5), dpi=150)
    
    for idx, cenario in enumerate(scenarios):
        sub = df[df["cenario"] == cenario].sort_values("clientes")
        vcpu_val = sub["vcpus"].iloc[0]
        label = f"{cenario} ({vcpu_val} vCPU)" if str(vcpu_val) not in str(cenario) else str(cenario)
        
        plt.plot(
            sub["clientes"],
            sub[col],
            marker=markers[idx % len(markers)],
            color=colors[idx % len(colors)],
            linewidth=2.2,
            markersize=7,
            label=label
        )

    plt.title(title, fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Número de Clientes Concorrentes", fontsize=11)
    plt.ylabel(ylabel, fontsize=11)
    plt.xticks(sorted(df["clientes"].unique()))
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(title="Cenário", frameon=True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Salvo: {filename}")

fig, axes = plt.subplots(2, 3, figsize=(18, 10), dpi=150)
axes = axes.flatten()

for i, (col, title, ylabel, _) in enumerate(metrics):
    ax = axes[i]
    for idx, cenario in enumerate(scenarios):
        sub = df[df["cenario"] == cenario].sort_values("clientes")
        vcpu_val = sub["vcpus"].iloc[0]
        label = f"{cenario} ({vcpu_val} vCPU)" if str(vcpu_val) not in str(cenario) else str(cenario)
        
        ax.plot(
            sub["clientes"],
            sub[col],
            marker=markers[idx % len(markers)],
            color=colors[idx % len(colors)],
            linewidth=2,
            markersize=6,
            label=label
        )
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Clientes Concorrentes")
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(df["clientes"].unique()))
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(title="Cenário", fontsize=9)

plt.suptitle("Benchmark de Provisionamento de CPU", fontsize=16, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("dashboard_cpu.png", bbox_inches="tight")
plt.close()
print("Salvo: dashboard_cpu.png")