#!/bin/bash
CENARIO=$1
URL="http://localhost:8000/?mb=50&hold_ms=500"

prom() {
  curl -s -G "http://localhost:9090/api/v1/query" --data-urlencode "query=$1" | grep -o '"[0-9.e+-]*"\]' | tr -d '"]'
}

[ -f resultados.csv ] || echo "cenario,clientes,vazao_rps,latencia_media_ms,latencia_p95_ms,falhas,cpu_pct,mem_pico_mb,swap_pico_mb,concluidas_pct" > resultados.csv

for c in 5 10 20 40 80; do
  inicio=$SECONDS
  ab -r -l -s 60 -n $((c * 10)) -c $c "$URL" > saida.txt
  janela=$((SECONDS - inicio + 1))s
  sleep 3

  vazao=$(grep "Requests per second" saida.txt | awk '{print $4}')
  media=$(grep "^Total:" saida.txt | awk '{print $3}')
  p95=$(grep " 95%" saida.txt | awk '{print $2}')
  falhas=$(grep "Failed requests" saida.txt | awk '{print $3}')
  concluidas=$(grep -E "Complete requests|requests completed" saida.txt | grep -o "[0-9]*" | head -1)
  concluidas_pct=$(awk "BEGIN {printf \"%.1f\", 100 * ${concluidas:-0} / ($c * 10)}")

  cpu=$(prom "100 * (1 - avg(rate(node_cpu_seconds_total{mode=\"idle\"}[$janela] offset 3s)))")
  mem=$(prom "max_over_time(((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024^2)[$janela:2s] offset 3s)")
  swap=$(prom "max_over_time(((node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes) / 1024^2)[$janela:2s] offset 3s)")
  cpu=$(printf "%.0f" "$cpu"); mem=$(printf "%.0f" "$mem"); swap=$(printf "%.0f" "$swap")

  echo "$CENARIO,$c,$vazao,$media,$p95,$falhas,$cpu,$mem,$swap,$concluidas_pct" >> resultados.csv
  echo "$CENARIO | $c clientes | $vazao req/s | media $media ms | p95 $p95 ms | $falhas falhas | CPU $cpu% | mem $mem MB | swap $swap MB | $concluidas_pct% concluidas"
  sleep 10
done
