# Kernel-LSTM Rendszer Integráció és Telepítés – Gyakorlati Útmutató
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért fontos az integráció és telepítés?
A kernel-LSTM pipeline nem csak modellek tanítása, hanem egy teljes rendszer integrálása és telepítése. Az eBPF agent, az adatfeldolgozó, az LSTM modell és a dashboard komponensek kombinálásával valós, skálázható rendszer kapható.

## 2. Gyakorlati példa: Docker környezet

### 2.1 Agent Dockerfile
```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y linux-headers-$(uname -r)
RUN pip install bcc torch pandas numpy influxdb-client
COPY agent.py /app/
WORKDIR /app
ENTRYPOINT ["python", "agent.py"]
```

### 2.2 Processor Dockerfile
```dockerfile
FROM python:3.9-slim
RUN pip install torch pandas numpy scikit-learn influxdb-client
COPY processor.py /app/
WORKDIR /app
ENTRYPOINT ["python", "processor.py"]
```

### 2.3 Model Dockerfile
```dockerfile
FROM python:3.9-slim
RUN pip install torch pandas numpy influxdb-client
COPY model.py /app/
COPY model.pth /app/
WORKDIR /app
ENTRYPOINT ["python", "model.py"]
```

### 2.4 docker-compose.yml
```yaml
version: '3.8'
services:
  agent:
    build: ./agent
    volumes:
      - /sys/kernel/debug:/sys/kernel/debug
      - /proc:/proc
    privileged: true
    environment:
      - KAFKA_BROKER=kafka:9092
    depends_on:
      - kafka
  
  processor:
    build: ./processor
    environment:
      - KAFKA_BROKER=kafka:9092
      - INFLUXDB_HOST=influxdb
    depends_on:
      - kafka
      - influxdb
  
  model:
    build: ./model
    environment:
      - INFLUXDB_HOST=influxdb
    depends_on:
      - influxdb
  
  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
  
  influxdb:
    image: influxdb:latest
    ports:
      - "8086:8086"
    volumes:
      - influxdb:/var/lib/influxdb
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - influxdb

volumes:
  influxdb:
```

## 3. Gyakorlati példa: Kubernetes telepítés

### 3.1 Agent Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kernel-lstm-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kernel-lstm-agent
  template:
    metadata:
      labels:
        app: kernel-lstm-agent
    spec:
      hostPID: true
      hostNetwork: true
      containers:
      - name: agent
        image: kernel-lstm-agent:latest
        securityContext:
          privileged: true
        volumeMounts:
        - name: kernel-debug
          mountPath: /sys/kernel/debug
        - name: proc
          mountPath: /proc
        env:
        - name: KAFKA_BROKER
          value: "kafka:9092"
      volumes:
      - name: kernel-debug
        hostPath:
          path: /sys/kernel/debug
      - name: proc
        hostPath:
          path: /proc
```

### 3.2 InfluxDB StatefulSet
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: influxdb
spec:
  serviceName: "influxdb"
  replicas: 1
  selector:
    matchLabels:
      app: influxdb
  template:
    metadata:
      labels:
        app: influxdb
    spec:
      containers:
      - name: influxdb
        image: influxdb:latest
        ports:
        - containerPort: 8086
        volumeMounts:
        - name: influxdb-storage
          mountPath: /var/lib/influxdb
  volumeClaimTemplates:
  - metadata:
      name: influxdb-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

## 4. Konfiguráció

### 4.1 Agent konfiguráció
```yaml
# agent_config.yaml
kernel_events:
  - sys_enter_open
  - sys_enter_read
  - sys_enter_write
  - sys_enter_close
  - do_fork
  - do_exit
  - kmalloc
  - kfree
  - handle_mm_fault

buffer_size: 1048576
poll_interval_ms: 10

kafka:
  broker: "kafka:9092"
  topic: "kernel-events"

influxdb:
  host: "influxdb"
  port: 8086
  database: "kernel_events"
```

### 4.2 Model konfiguráció
```yaml
# model_config.yaml
model:
  input_dim: 100
  hidden_dim: 64
  num_layers: 2
  dropout: 0.2
  window_size: 50
  time_step: 10

training:
  batch_size: 64
  epochs: 50
  lr: 0.001
  optimizer: "adam"
  loss: "mse"

anomaly:
  threshold_percentile: 95
  min_sequence_length: 10

influxdb:
  host: "influxdb"
  port: 8086
  database: "kernel_events"
```

## 5. Monitorozás

### 5.1 Agent metrikák
- Események száma másodpercenként
- Buffer overflow események
- Feldolgozási késleltetés

### 5.2 Model metrikák
- Rekonstrukciós hiba
- Anomália száma időegység alatt
- False positive arány

### 5.3 Rendszer metrikák
- CPU kihasználtság
- Memóriahasználat
- I/O terhelés

## 6. Hibakeresés

### 6.1 eBPF hibák
```bash
# eBPF programok listázása
bpftool prog list

# eBPF map-ek listázása
bpftool map list

# Perf buffer statisztikák
cat /sys/kernel/debug/tracing/trace_pipe
```

### 6.2 Adatfeldolgozás hibák
```bash
# Kafka topicok
kafka-topics.sh --list --bootstrap-server kafka:9092

# Kafka consumer group
kafka-consumer-groups.sh --bootstrap-server kafka:9092 --describe

# InfluxDB adatok
influx -host influxdb -port 8086 -database kernel_events -execute 'SELECT * FROM kernel_events LIMIT 10'
```

### 6.3 Model hibák
```bash
# Model logok
docker logs kernel-lstm-model

# Grafana dashboard
http://grafana:3000
```

## 7. Backup és helyreállítás

### 7.1 Model backup
```bash
# Modell exportálása
python export_model.py --model model.pth --output model.onnx

# Modell verziókezelés
git tag v1.0.0
git push origin v1.0.0
```

### 7.2 Adatbackup
```bash
# InfluxDB backup
influxd backup -portable /backup/influxdb

# Kafka backup
kafka-backup --topic kernel-events --bootstrap-server kafka:9092
```

## 8. Összefoglalás
A kernel-LSTM rendszer integrációja és telepítése Docker és Kubernetes környezetben történik. Az eBPF agent, az adatfeldolgozó, az LSTM modell és a dashboard komponensek kombinálásával teljes, skálázható rendszer építhető.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
