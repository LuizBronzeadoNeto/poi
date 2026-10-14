import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

ARQUIVO_CSV = Path("results.csv")
PASTA_SAIDA = Path("graficos")

METRICAS = [
    ("vazao_rps", "Vazão (req/s)"),
    ("latencia_media_ms", "Latência média (ms)"),
    ("latencia_p95_ms", "Latência p95 (ms)"),
    ("falhas", "Requisições com falha"),
    ("cpu_pct", "Uso médio de CPU da VM (%)"),
    ("mem_pico_mb", "Pico de memória usada na VM (MB)"),
    ("swap_pico_mb", "Pico de swap usado na VM (MB)"),
]


def ler_resultados(caminho: Path) -> list[dict]:
    with caminho.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def montar_series(linhas: list[dict], coluna: str) -> dict[str, list[tuple[int, float]]]:
    series: dict[str, list[tuple[int, float]]] = {}
    for linha in linhas:
        if not linha.get(coluna):
            continue
        ponto = (int(linha["clientes"]), float(linha[coluna]))
        series.setdefault(linha["cenario"], []).append(ponto)
    return {cenario: sorted(pontos) for cenario, pontos in series.items()}


def estilo_linha(cenario: str) -> str:
    return "--" if "CPUs" in cenario else "-"


def plotar_metrica(linhas: list[dict], coluna: str, titulo: str, destino: Path) -> bool:
    series = montar_series(linhas, coluna)
    if not series:
        return False

    fig, ax = plt.subplots(figsize=(7, 4))
    for cenario, pontos in series.items():
        x, y = zip(*pontos)
        ax.plot(x, y, marker="o", label=cenario, linestyle=estilo_linha(cenario))

    clientes = sorted({x for pontos in series.values() for x, _ in pontos})
    ax.set_xscale("log", base=2)
    ax.set_xticks(clientes)
    ax.set_xticklabels([str(c) for c in clientes])
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_ylim(bottom=0)
    ax.set_title(titulo)
    ax.set_xlabel("Clientes simultâneos")
    ax.grid(alpha=0.3)
    ax.legend(title="Cenário")

    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return True


def main() -> None:
    linhas = ler_resultados(ARQUIVO_CSV)
    PASTA_SAIDA.mkdir(exist_ok=True)
    for coluna, titulo in METRICAS:
        if not plotar_metrica(linhas, coluna, titulo, PASTA_SAIDA / f"{coluna}.png"):
            print(f"Sem dados para '{coluna}', gráfico ignorado.")


if __name__ == "__main__":
    main()