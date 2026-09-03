# Kernel-LSTM Alkalmazás – Rendszerterv és Telepítés
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Cél
Egy teljes, zárt, futtatható kernel monitorozó és predikciós rendszer, amely:
- Gyűjti a kernel eseményeket eBPF segítségével
- Előfeldolgozza és szekvenciákat épít
- LSTM modellekkel anomáliákat detektál és kernel panics prediktálja
- Riasztásokat generál (Slack, email, lokális napló)
- Dashboardot és jelentéseket készít
- Automatikusan fut, nincs szükség folyamatos beavatkozásra

## 2. Architektúra

### 2.1 Komponensek
- **install.sh** – telepítő script
- **agent/** – eBPF agent, kernel események gyűjtése
- **processor/** – előfeldolgozó, szekvencia építő
- **model/** – LSTM modellek tanítása és predikció
- **alertmanager/** – riasztó rendszer
- **dashboard/** – Grafana dashboard és jelentéskészítő
- **docker-compose.yml** – teljes környezet egy parancsra
- **config.yaml** – központi konfiguráció

### 2.2 Adatfolyam
```
Kernel → eBPF → Perf buffer → Agent → ClickHouse
ClickHouse → Processor → Sequences → LSTM → Anomaly → Alert → Dashboard
```

## 3. Telepítés

### 3.1 Előkészületek
- Linux kernel 5.x+ (eBPF támogatással)
- Docker és Docker Compose
- 4+ CPU mag
- 8+ GB RAM
- 50+ GB tárhely

### 3.2 Telepítés lépései
```bash
# 1. Repository klónozása
git clone <repository-url>
cd kernel-lstm-app

# 2. Konfiguráció
cp config.yaml.example config.yaml
# Szerkeszd a config.yaml-t a saját beállításaiddal

# 3. Telepítés
sudo ./install.sh

# 4. Indítás
docker compose up -d
```

## 4. Konfiguráció

### 4.1 config.yaml
```yaml
agent:
  poll_interval_ms: 10
  buffer_size: 1048576
  events:
    - sys_enter_open
    - sys_enter_read
    - sys_enter_write
    - sys_enter_close
    - do_fork
    - do_exit
    - kmalloc
    - kfree
    - handle_mm_fault

processor:
  window_size: 50
  time_step: 10
  overlap: 0.25

model:
  input_dim: 100
  hidden_dim: 64
  num_layers: 2
  dropout: 0.2
  batch_size: 64
  epochs: 50
  learning_rate: 0.001
  threshold_percentile: 95

clickhouse:
  host: clickhouse
  port: 8123
  database: kernel_events
  user: default
  password: ""

alertmanager:
  slack_webhook: ""
  email_host: ""
  email_port: 587
  email_user: ""
  email_pass: ""

dashboard:
  grafana_port: 3000
  prometheus_port: 9090
```

## 5. Futtatás

### 5.1 Indítás
```bash
docker compose up -d
```

### 5.2 Állapot ellenőrzés
```bash
docker compose ps
docker logs kernel-lstm-agent
docker logs kernel-lstm-model
```

### 5.3 Leállítás
```bash
docker compose down
```

## 6. Dashboard

### 6.1 Grafana
- http://localhost:3000
- Alapértelmezett felhasználó: admin
- Alapértelmezett jelszó: admin123

### 6.2 Prometheus
- http://localhost:9090

### 6.3 Metrikák
- Kernel események száma másodpercenként
- Anomália detektálási arány
- CPU és memória használat
- Riasztások száma

## 7. Jelentések

### 7.1 Automatikus jelentések
- Napi összefoglaló
- Heti trend elemzés
- Anomália jelentés

### 7.2 Jelentés formátum
- PDF
- HTML
- CSV

## 8. Hibakeresés

### 8.1 Agent hibák
```bash
docker logs kernel-lstm-agent
```

### 8.2 Model hibák
```bash
docker logs kernel-lstm-model
```

### 8.3 ClickHouse hibák
```bash
curl http://localhost:8123/ping
```

## 9. Backup és helyreállítás

### 9.1 Modell backup
```bash
./backup.sh models
```

### 9.2 Adatbackup
```bash
./backup.sh clickhouse
```

### 9.3 Helyreállítás
```bash
./restore.sh
```

## 10. Összefoglalás
A kernel-LSTM alkalmazás teljes, zárt, futtatható rendszer, amely automatikusan gyűjti, elemzi és prediktálja a kernel eseményeket. Nincs szükség folyamatos beavatkozásra, a rendszer önállóan működik.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
