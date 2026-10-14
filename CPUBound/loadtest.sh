#!/bin/bash
export LC_NUMERIC=C

URL="http://localhost:8000/"
PROM_URL="http://localhost:9090/api/v1/query"
CSV="resultados_cpu.csv"

prom() {
  local val
  val=$(curl -s -G "$PROM_URL" --data-urlencode "query=$1" \
    | grep -o '"[0-9.e+-]*"\]' | tr -d '"]' | head -n 1)
  echo "${val:-0}"
}

if ! curl -s --max-time 10 "$URL" > /dev/null; then
  echo "ERRO: Nao foi possivel conectar em $URL (verifique se a VM e o container 'app' estao rodando)."
  exit 1
fi

VCPUS=$(prom 'count(node_cpu_seconds_total{mode="idle"})')
VCPUS=$(printf "%.0f" "$VCPUS" 2>/dev/null || echo 0)
CENARIO=${1:-"${VCPUS}_vcpu"}

if [ ! -f "$CSV" ]; then
  echo "cenario,vcpus,clientes,total_requests,vazao_rps,latencia_media_ms,latencia_p50_ms,latencia_p95_ms,latencia_max_ms,falhas,cpu_pct" > "$CSV"
fi

for c in 5 10 20 40 80; do
  n=$((c * 4))
  
  inicio=$SECONDS
  ab -l -r -s 120 -n "$n" -c "$c" "$URL" > saida.txt 2>&1
  duracao=$((SECONDS - inicio + 1))

  if [ "$duracao" -lt 10 ]; then
    janela="10s"
  else
    janela="${duracao}s"
  fi

  sleep 3

  vazao=$(grep "Requests per second:" saida.txt | awk '{print $4}')
  media=$(grep "^Total:" saida.txt | awk '{print $3}')
  p50=$(grep " 50%" saida.txt | awk '{print $2}')
  p95=$(grep " 95%" saida.txt | awk '{print $2}')
  max=$(grep " 100%" saida.txt | awk '{print $2}')
  falhas=$(grep "Failed requests:" saida.txt | awk '{print $3}')

  vazao=${vazao:-0}; media=${media:-0}; p50=${p50:-0}; p95=${p95:-0}; max=${max:-0}; falhas=${falhas:-0}

  cpu_raw=$(prom "100 * (1 - avg(rate(node_cpu_seconds_total{mode=\"idle\"}[$janela] offset 3s)))")
  cpu=$(printf "%.0f" "$cpu_raw" 2>/dev/null || echo 0)

  echo "$CENARIO,$VCPUS,$c,$n,$vazao,$media,$p50,$p95,$max,$falhas,$cpu" >> "$CSV"
  echo "$CENARIO ($VCPUS vCPU) | $c clientes | $vazao req/s | media ${media}ms | p95 ${p95}ms | max ${max}ms | $falhas falhas | CPU ${cpu}%"

  sleep 5
done