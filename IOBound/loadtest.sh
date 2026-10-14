#!/bin/bash
set -euo pipefail
export LC_ALL=C
CENARIO=${1:?Uso: bash loadtest.sh "1 CPU 1 GiB"}
URL="http://127.0.0.1:8082/io"

prom() {
  curl -fsS --max-time 15 -G "http://127.0.0.1:9090/api/v1/query" \
    --data-urlencode "query=$1" --data-urlencode "time=$fim" |
    jq -er 'select(.status == "success" and (.data.result | length) == 1)
      | .data.result[0].value[1] | tonumber | select(isfinite)'
}

HEADER="cenario,clientes,vazao_rps,latencia_media_ms,latencia_p95_ms,falhas,nao_2xx,cpu_pct,mem_pico_mib,swap_pico_mib,iowait_pct,escrita_mib_s,latencia_escrita_ms"
[ -f resultados.csv ] || echo "$HEADER" > resultados.csv
[ "$(head -n 1 resultados.csv)" = "$HEADER" ] || { echo "CSV existente tem outro formato." >&2; exit 1; }

for c in 1 5 10; do
  inicio=$(date +%s)
  ab -m POST -l -t 60 -c "$c" -s 60 "$URL" > saida.txt 2>&1
  fim=$(date +%s)
  janela=$((fim - inicio + 1))s
  sleep 3

  vazao=$(awk '/Requests per second/ {print $4}' saida.txt)
  media=$(awk '/^Total:/ {print $3}' saida.txt)
  p95=$(awk '$1 == "95%" {print $2}' saida.txt)
  falhas=$(awk '/Failed requests/ {print $3}' saida.txt)
  nao_2xx=$(awk '/Non-2xx responses/ {print $3; encontrado=1} END {if (!encontrado) print 0}' saida.txt)

  cpu=$(prom "100 * sum(rate(node_cpu_seconds_total{job=\"vm\",mode=~\"user|nice|system|irq|softirq\"}[$janela])) / count(node_cpu_seconds_total{job=\"vm\",mode=\"idle\"})")
  mem=$(prom "max_over_time(((node_memory_MemTotal_bytes{job=\"vm\"} - node_memory_MemAvailable_bytes{job=\"vm\"}) / 1024^2)[$janela:2s])")
  swap=$(prom "max_over_time(((node_memory_SwapTotal_bytes{job=\"vm\"} - node_memory_SwapFree_bytes{job=\"vm\"}) / 1024^2)[$janela:2s])")
  iowait=$(prom "100 * avg(rate(node_cpu_seconds_total{job=\"vm\",mode=\"iowait\"}[$janela]))")
  escrita=$(prom "rate(node_disk_written_bytes_total{job=\"vm\",device=\"sda\"}[$janela]) / 1024^2")
  latencia=$(prom "1000 * rate(node_disk_write_time_seconds_total{job=\"vm\",device=\"sda\"}[$janela]) / rate(node_disk_writes_completed_total{job=\"vm\",device=\"sda\"}[$janela])")

  jq -nr --args '$ARGS.positional | @csv' "$CENARIO" "$c" "$vazao" "$media" "$p95" \
    "$falhas" "$nao_2xx" "$cpu" "$mem" "$swap" "$iowait" "$escrita" "$latencia" >> resultados.csv
  echo "$CENARIO | $c clientes | $vazao req/s | média $media ms | p95 $p95 ms | falhas $falhas | não-2xx $nao_2xx | CPU $cpu% | iowait $iowait%"
  sleep 10
done
