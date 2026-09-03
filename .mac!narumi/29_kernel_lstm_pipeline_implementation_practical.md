# Kernel-LSTM Pipeline: Gyakorlati Implementációs Útmutató
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért érdemes implementálni?
A kernel-LSTM pipeline lehetőséget ad a kernel anomália detektálására és predikciójára valós időben. Nem csak a jelenlegi állapotot figyeli, hanem a múltbeli mintázatokat is értelmezi.

## 2. Előkészületek

### 2.1 Rendszerkövetelmények
- Linux kernel 5.x+ (eBPF támogatással)
- Python 3.9+
- 4+ CPU mag
- 8+ GB RAM
- 50+ GB tárhely

### 2.2 Függőségek
```bash
# Kernel fejlesztői csomagok
sudo apt install linux-headers-$(uname -r) build-essential

# Python csomagok
pip install torch pandas numpy scikit-learn influxdb-client bcc bpftrace
```

## 3. Gyakorlati példa: eBPF agent

### 3.1 Kernel események gyűjtése
```bash
# Syscall trace
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'

# Memória allokáció
bpftrace -e 'kprobe:kmalloc { @alloc[pid] = count(); }'

# Page fault
bpftrace -e 'kprobe:handle_mm_fault { @fault[pid] = count(); }'
```

### 3.2 Python agent
```python
from bcc import BPF
import json
import time
from influxdb import InfluxDBClient

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct event_t {
    u64 ts;
    u32 pid;
    u32 tid;
    u32 cpu;
    u32 event_type;
    u64 duration_ns;
    s64 retval;
    char comm[16];
};

BPF_PERF_OUTPUT(events);
BPF_HASH(start, u64, u64);

int trace_sys_enter(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    u64 ts = bpf_ktime_get_ns();
    start.update(&pid, &ts);
    return 0;
}

int trace_sys_exit(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    u64 *tsp = start.lookup(&pid);
    if (!tsp) return 0;
    u64 duration = bpf_ktime_get_ns() - *tsp;
    start.delete(&pid);
    
    struct event_t evt = {};
    evt.pid = pid >> 32;
    evt.tid = pid & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.duration_ns = duration;
    evt.retval = PT_REGS_RC(ctx);
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}
"""

b = BPF(text=bpf_text)
b.attach_kprobe(event="sys_enter", fn_name="trace_sys_enter")
b.attach_kprobe(event="sys_exit", fn_name="trace_sys_exit")

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('kernel_events')

def handle_event(cpu, data, size):
    event = b["events"].event(data)
    point = {
        "measurement": "kernel_events",
        "tags": {
            "pid": str(event.pid),
            "tid": str(event.tid),
            "cpu": str(event.cpu),
            "comm": event.comm.decode('utf-8', 'replace')
        },
        "fields": {
            "ts": event.ts,
            "duration_ns": event.duration_ns,
            "retval": event.retval,
            "event_type": event.event_type
        }
    }
    client.write_points([point])

b["events"].open_perf_buffer(handle_event)

while True:
    b.perf_buffer_poll()
    time.sleep(0.01)
```

## 4. Gyakorlati példa: LSTM autoencoder

### 4.1 Modell építés
```python
import torch
import torch.nn as nn

class LSTMAutoencoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers):
        super().__init__()
        self.encoder = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.decoder = nn.LSTM(hidden_dim, hidden_dim, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_dim, input_dim)
    
    def forward(self, x):
        _, (hidden, cell) = self.encoder(x)
        x_recon, _ = self.decoder(hidden.repeat(x.size(1), 1, 1))
        x_recon = self.linear(x_recon)
        return x_recon
```

### 4.2 Tanítás
```python
model = LSTMAutoencoder(input_dim=100, hidden_dim=64, num_layers=2)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(50):
    for batch in train_loader:
        optimizer.zero_grad()
        recon = model(batch)
        loss = criterion(recon, batch)
        loss.backward()
        optimizer.step()
```

### 4.3 Anomália detektálás
```python
model.eval()
with torch.no_grad():
    recon = model(X_test)
    errors = torch.mean((recon - X_test) ** 2, dim=(1, 2))
    threshold = np.percentile(train_errors, 95)
    anomalies = errors > threshold
```

## 5. Gyakorlati példa: Kernel panic predikció

### 5.1 Predikciós modell
```python
class LSTMPredictor(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        out, (hidden, cell) = self.lstm(x)
        out = self.fc(out[:, -1, :])
        out = self.sigmoid(out)
        return out
```

### 5.2 Predikció
```python
model.eval()
with torch.no_grad():
    pred = model(X)
    panic_probability = pred.item()
    if panic_probability > 0.8:
        print("Kernel panic előrejelzve!")
```

## 6. Docker környezet

### 6.1 docker-compose.yml
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

## 7. Gyakorlati tippek

### 7.1 Adatgyűjtés
- eBPF és kprobes használata
- Syscall trace
- Kernel naplók

### 7.2 Adatfeldolgozás
- Tisztítás, normalizálás, tokenizálás
- Szekvencia építés
- Feature engineering

### 7.3 Modell tanítása
- LSTM autoencoder
- Predikciós modell
- Hyperparaméter optimalizálás

## 8. Összefoglalás
A kernel-LSTM pipeline gyakorlati implementációja konkrét lépéseket követ. Az eBPF agent, az előfeldolgozás pipeline, az LSTM modellek és a riasztó rendszer kombinálásával teljes, skálázható rendszer építhető.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
