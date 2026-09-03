# eBPF Collector Agent – Gyakorlati Implementációs Útmutató
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért fontos az eBPF agent?
Az eBPF agent a kernel események valós időben való gyűjtéséért felelős. Nincs szükség kernel módosításra, és nem zavarja a rendszer futását.

## 2. Gyakorlati példa: eBPF program

### 2.1 Syscall trace
```c
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
```

### 2.2 bpftrace használata
```bash
# Syscall trace
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'

# Memória allokáció
bpftrace -e 'kprobe:kmalloc { @alloc[pid] = count(); }'

# Page fault
bpftrace -e 'kprobe:handle_mm_fault { @fault[pid] = count(); }'
```

## 3. Gyakorlati példa: Python agent

### 3.1 bcc használata
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

## 4. Adatfeldolgozás

### 4.1 Előfeldolgozás
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_events(df):
    # Időbélyeg normalizálás
    df['ts'] = pd.to_datetime(df['ts'], unit='ns')
    df = df.sort_values('ts')
    
    # Esemény típus kódolás
    le = LabelEncoder()
    df['event_type_encoded'] = le.fit_transform(df['event_type'])
    
    # Feature engineering
    df['duration_ms'] = df['duration_ns'] / 1e6
    df['hour'] = df['ts'].dt.hour
    df['minute'] = df['ts'].dt.minute
    
    # Normalizálás
    scaler = StandardScaler()
    df['duration_scaled'] = scaler.fit_transform(df[['duration_ms']])
    
    return df, le, scaler
```

### 4.2 Szekvencia építés
```python
def build_sequences(df, window_size=50, step=10):
    sequences = []
    for i in range(0, len(df) - window_size, step):
        seq = df.iloc[i:i+window_size]['event_type_encoded'].values
        sequences.append(seq)
    return np.array(sequences)
```

## 5. Docker környezet

### 5.1 Dockerfile
```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y linux-headers-$(uname -r)
RUN pip install bcc torch pandas numpy influxdb-client
COPY agent.py /app/
WORKDIR /app
ENTRYPOINT ["python", "agent.py"]
```

### 5.2 docker-compose.yml
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
      - INFLUXDB_HOST=influxdb
    depends_on:
      - influxdb
  
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

### 6.2 Python hibák
```bash
# Python naplók
docker logs kernel-lstm-agent

# InfluxDB adatok
influx -host influxdb -port 8086 -database kernel_events -execute 'SELECT * FROM kernel_events LIMIT 10'
```

## 7. Teljesítmény optimalizálás

### 7.1 eBPF optimalizálás
- Esemény szűrés kernelben
- Perf buffer méret növelése
- CPU affinitás beállítása

### 7.2 Python optimalizálás
```python
# Batch feldolgozás
batch_size = 1000
for i in range(0, len(events), batch_size):
    batch = events[i:i+batch_size]
    process_batch(batch)

# Async I/O
import asyncio
async def send_to_collector(events):
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=events)
```

## 8. Összefoglalás
Az eBPF collector agent gyakorlati implementációja konkrét lépéseket követ. Az eBPF program, a Python agent és az InfluxDB kombinálásával valós időben gyűjthetők és tárolhatók a kernel események.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
