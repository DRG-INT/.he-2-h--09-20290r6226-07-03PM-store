# eBPF Adatgyűjtő Agent Implementáció
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Agent architektúra

### 1.1 Komponensek
- **eBPF program:** kernel események gyűjtése
- **Perf event buffer:** események átvitele user space-be
- **Python agent:** adatfeldolgozás, küldés collector-nak
- **Health check:** agent állapot monitorozás

### 1.2 Adatfolyam
```
Kernel → eBPF → Perf buffer → Python agent → Collector
```

## 2. eBPF program

### 2.1 Syscall trace
```c
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#define MAX_EVENTS 4096

struct event_t {
    u64 ts;
    u32 pid;
    u32 tid;
    u32 cpu;
    u32 event_type;
    u64 duration_ns;
    s64 retval;
    char comm[16];
    char filename[256];
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

### 2.2 Processz események
```c
int trace_process_fork(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = bpf_get_current_pid_tgid() >> 32;
    evt.tid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_PROCESS_FORK;
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}
```

### 2.3 Memória események
```c
int trace_kmalloc(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = bpf_get_current_pid_tgid() >> 32;
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_KMALLOC;
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}
```

## 3. Python agent

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
    char filename[256];
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

### 4.1 Előfeldolgozás pipeline
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

## 5. InfluxDB séma

### 5.1 Measurement
```
kernel_events
  - tags: pid, tid, cpu, comm, event_type
  - fields: ts, duration_ns, retval
  - timestamp: ns
```

### 5.2 Lekérdezések
```sql
-- 5 perces ablak, események száma
SELECT count("event_type") FROM "kernel_events"
WHERE time > now() - 5m
GROUP BY time(1m), "event_type"
```

## 6. Rendszertervezés

### 6.1 Komponensek
- **Agent:** eBPF program + Python agent
- **Collector:** InfluxDB
- **Processor:** Python script
- **Model:** PyTorch LSTM
- **Alert:** Python script + webhook
- **Dashboard:** Grafana

### 6.2 Adatfolyam
```
Kernel → eBPF → Perf buffer → Python agent → InfluxDB
InfluxDB → Processor → Sequences → LSTM → Anomaly → Alert
```

## 7. Hibakeresés

### 7.1 eBPF hibák
- `perf_buffer_poll()` timeout
- Események elvesztése
- Memóriaszivárgás

### 7.2 Adatfeldolgozás hibák
- Hiányzó események
- Időbélyeg hibák
- Feature kódolás hibák

### 7.3 LSTM hibák
- Overfitting
- Underfitting
- Gradient vanishing/exploding

## 8. Teljesítmény optimalizálás

### 8.1 eBPF optimalizálás
- Esemény szűrés kernelben
- Perf buffer méret optimalizálás
- CPU affinitás beállítása

### 8.2 Python optimalizálás
- Batch feldolgozás
- Multiprocessing
- Async I/O

### 8.3 LSTM optimalizálás
- Model quantization
- Pruning
- Knowledge distillation

## 9. Skálázhatóság

### 9.1 Horizontális skálázás
- Több agent
- Több InfluxDB node
- Több processor

### 9.2 Vertikális skálázás
- Több CPU
- Több memória
- GPU gyorsítás

## 10. Összefoglalás
A kernel-LSTM pipeline implementációja konkrét lépéseket követ. Az eBPF adatgyűjtő agent, az előfeldolgozás pipeline, az LSTM modellek és a riasztó rendszer kombinálásával teljes rendszer építhető.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
