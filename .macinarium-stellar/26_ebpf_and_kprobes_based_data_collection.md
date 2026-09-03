# eBPF és Kprobes Alapú Adatgyűjtés LSTM Modellekhez
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Miért eBPF és kprobes?
Az eBPF (extended Berkeley Packet Filter) és a kprobes lehetővé teszik a kernel események valós időben való figyelését anélkül, hogy módosítanánk a kernel forráskódját. Az LSTM modellek számára ez a szükséges adatforrás.

## 2. eBPF Alapok

### 2.1 Mi az eBPF?
- Kernelben futó, biztonságos, JIT-kompilált programok
- Nincs kernel módosítás
- Dinamikus betöltés és futás

### 2.2 eBPF programok
- Tracepoint-ok
- kprobes
- uprobes
- XDP (Express Data Path)

### 2.3 eBPF eszközök
- bpftrace
- bcc
- libbpf

## 3. Kprobes

### 3.1 Mi az a kprobes?
- Dinamikus breakpointok a kernel függvényeibe
- Futás közben történő beszúrás
- Nincs kernel újrafordítás

### 3.2 Kprobes típusok
- kprobe: kernel függvény belépés
- kretprobe: kernel függvény kilépés
- jprobe: kernel függvény argumentumok

### 3.3 Kprobes korlátok
- Csak nem-inline függvények
- Nem minden architektúra támogatja
- Teljesítmény overhead

## 4. Adatgyűjtési Pipeline

### 4.1 Kernel események
- Syscall trace
- Processz létrehozás
- Memória allokáció
- I/O műveletek

### 4.2 Feature extrakció
- Időbélyeg
- PID, TID
- Esemény típus
- Paraméterek

### 4.3 Adat formázás
- JSON
- CSV
- Protobuf

## 5. eBPF Implementáció

### 5.1 bpftrace példa
```bash
# Syscall trace
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'

# Memória allokáció
bpftrace -e 'kprobe:kmalloc { @alloc[pid] = count(); }'

# Page fault
bpftrace -e 'kprobe:handle_mm_fault { @fault[pid] = count(); }'
```

### 5.2 bcc példa
```python
from bcc import BPF

bpf_text = """
#include <uapi/linux/ptrace.h>

BPF_HASH(events, u64, u64);

int trace_sys_enter(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    events.update(&pid, &pid);
    return 0;
}
"""

b = BPF(text=bpf_text)
b.attach_kprobe(event="sys_enter", fn_name="trace_sys_enter")
```

## 6. Kprobes Implementáció

### 6.1 Kernel modul példa
```c
#include <linux/kprobes.h>

static int handler_pre(struct kprobe *p, struct pt_regs *regs) {
    printk(KERN_INFO "kprobe triggered at %p\n", p->addr);
    return 0;
}

static struct kprobe kp = {
    .symbol_name = "do_fork",
    .pre_handler = handler_pre,
};

static int __init my_init(void) {
    int ret = register_kprobe(&kp);
    if (ret < 0) {
        printk(KERN_INFO "register_probe failed\n");
        return ret;
    }
    return 0;
}
```

## 7. Adatgyűjtés és Tárolás

### 7.1 Adat formátum
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "pid": 1234,
  "tid": 5678,
  "event": "sys_enter_open",
  "args": {
    "filename": "/etc/passwd",
    "flags": 0
  }
}
```

### 7.2 Tárolási lehetőségek
- InfluxDB: idő sorozat adatbázis
- Prometheus: metrikák
- TimescaleDB: SQL-alapú idő sorozat
- Elasticsearch: szöveges keresés

## 8. Adatfeldolgozás

### 8.1 Előfeldolgozás
- Tisztítás
- Normalizálás
- Tokenizálás

### 8.2 Feature engineering
- Események száma időegység alatt
- Memóriahasználat átlag, szórás
- CPU terhelés átlag, szórás

### 8.3 Szekvencia építés
- Ablak mérete: 10, 50, 100, 200
- Időlépés: 1, 5, 10 perc

## 9. Integráció LSTM Modellekkel

### 9.1 Adat betöltése
```python
import pandas as pd

df = pd.read_csv('kernel_events.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')
```

### 9.2 Szekvencia építése
```python
from tensorflow.keras.preprocessing.sequence import pad_sequences

sequences = []
for i in range(0, len(df) - window_size, time_step):
    seq = df.iloc[i:i+window_size]['event_id'].values
    sequences.append(seq)

X = pad_sequences(sequences, maxlen=window_size)
```

### 9.3 LSTM input
```python
model.predict(X)
```

## 10. Összefoglalás
Az eBPF és kprobes alapú adatgyűjtés lehetővé teszi a kernel események valós időben való figyelését. Az adatok strukturálása és előfeldolgozása után LSTM modellek használhatók a kernel anomália detektálására és predikciójára.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
