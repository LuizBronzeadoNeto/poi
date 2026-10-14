#!/usr/bin/env bash
VM="Ubuntu lts"
OUT=results.csv
echo "cpus,ram_mb,rps,mean_ms,p50_ms,p95_ms,failed,prom_avg_latency_s" > "$OUT"

for cpus in 1 2 4; do
  for ram in 1024 2048 4096; do
    VBoxManage modifyvm "$VM" --cpus $cpus --memory $ram
    VBoxManage startvm "$VM" --type headless

    until curl -sf localhost:9090/-/ready >/dev/null; do sleep 2; done
    sleep 10

    start=$(date +%s)
    ab -n 100 -c 10 -s 300 -e "ab_${cpus}_${ram}.csv" http://localhost:8000/ > "ab_${cpus}_${ram}.txt"
    end=$(date +%s)

    sleep 10 
    win=$((end - start + 10))
    prom=$(curl -s localhost:9090/api/v1/query \
    --data-urlencode "query=100 - avg(rate(node_cpu_seconds_total{mode=\"idle\"}[${win}s])) * 100" \
    | jq -r '.data.result[0].value[1]')

    f="ab_${cpus}_${ram}.txt"
    rps=$(grep "Requests per second" "$f" | awk '{print $4}')
    mean=$(grep -m1 "Time per request" "$f" | awk '{print $4}')
    p50=$(grep "^  50%" "$f" | awk '{print $2}')
    p95=$(grep "^  95%" "$f" | awk '{print $2}')
    failed=$(grep "Failed requests" "$f" | awk '{print $3}')
    echo "$cpus,$ram,$rps,$mean,$p50,$p95,$failed,$prom" >> "$OUT"

    VBoxManage controlvm "$VM" acpipowerbutton
    until VBoxManage showvminfo "$VM" --machinereadable | grep -q 'VMState="poweroff"'; do sleep 2; done
  done
done