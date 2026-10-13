# Como rodar

## Executar na máquina local

```bash
python3 app.py
curl "localhost:8000/?mb=100&hold_ms=1000"
```

## Deploy na máquina virtual

1. Com a VM desligada, em Configurações -> Rede -> Avançado -> Redirecionamento de
   portas, crie as regras `8000 -> 8000` (aplicação) e `9090 -> 9090` (Prometheus).
2. Ligue a VM, entre com `osboxes` / `osboxes.org` e rode:

```bash
sudo apt update && sudo apt install -y docker.io git
git clone <url-do-repositorio> && cd <pasta-do-repositorio>/MemoryBound

sudo docker build -t memory-bound .
sudo docker run -d --name app --network host --restart always memory-bound
sudo docker run -d --name node-exporter --network host --pid host --restart always prom/node-exporter
sudo docker run -d --name prometheus --network host --restart always \
  -v "$PWD/prometheus.yml:/etc/prometheus/prometheus.yml" prom/prometheus
```

3. Na máquina hospedeira: `curl localhost:8000` e `http://localhost:9090` no navegador.

Com `--restart always` os containers sobem sozinhos a cada boot da VM e a
aplicação volta se o Linux matá-la por falta de memória.

## Experimentos

Na máquina hospedeira, instale o ab (`sudo apt install apache2-utils`). Para
cada cenário: desligue a VM, mude a memória em Configurações -> Sistema, ligue a
VM e rode:

```bash
./loadtest.sh "1 GB"
```

O script testa 5, 10, 20, 40 e 80 clientes simultâneos e acrescenta uma linha por
nível em resultados.csv (vazão, latência média e p95, falhas, uso de CPU e picos
de memória e swap da VM, esses três lidos do Prometheus). Durante
o teste, acompanhe memória, swap e CPU no Prometheus e tire prints.

## Gráficos

```bash
pip install matplotlib
python3 plot.py
```

## Experimento extra: sem swap

Para testar o cenário de 1 GB sem swap, depois de ligar a VM rode
`sudo swapoff -a` dentro dela (o swap volta no próximo boot) e, na máquina
hospedeira, `./loadtest.sh "1 GB sem swap"`. Os resultados entram no mesmo
`resultados.csv` e nos mesmos gráficos.
