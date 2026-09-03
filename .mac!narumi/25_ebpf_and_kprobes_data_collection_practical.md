# eBPF és Kprobes Alapú Adatgyűjtés – Gyakorlati Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért fontos az eBPF és kprobes?
Az eBPF és kprobes lehetővé teszik a kernel események valós időben való figyelését anélkül, hogy módosítanánk a kernel forráskódját. Az LSTM modellek számára ez a szükséges adatforrás.

## 2. eBPF gyakorlati használata

### 2.1 bpftrace
```bash
# Syscall trace
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'

# Memória allokáció
bpftrace -e 'kprobe:kmalloc { @alloc[pid] = count(); }'

# Page fault
bpftrace -e 'kprobe:handle_mm_fault { @fault[pid] = count(); }'
```

### 2.2 bcc
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

## 3. Kprobes gyakorlati használata

### 3.1 Kernel modul
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

### 3.2 Kernel modul fordítása
```bash
make -C /lib/modules/$(uname -r)/build M=$(pwd) modules
sudo insmod my_module.ko
sudo rmmod my_module
```

## 4. Adatgyűjtés és tárolás

### 4.1 Adat formátum
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

### 4.2 Tárolási lehetőségek
- InfluxDB: idő sorozat adatbázis
- Prometheus: metrikák
- TimescaleDB: SQL-alapú idő sorozat
- Elasticsearch: szöveges keresés

## 5. Integráció LSTM modellekkel

### 5.1 Adat betöltése
```python
import pandas as pd

df = pd.read_csv('kernel_events.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')
```

### 5.2 Szekvencia építése
```python
from tensorflow.keras.preprocessing.sequence import pad_sequences

sequences = []
for i in range(0, len(df) - window_size, time_step):
    seq = df.iloc[i:i+window_size]['event_id'].values
    sequences.append(seq)

X = pad_sequences(sequences, maxlen=window_size)
```

### 5.3 LSTM input
```python
model.predict(X)
```

## 6. Gyakorlati tippek

### 6.1 Adatgyűjtés
- eBPF és kprobes használata
- Syscall trace
- Kernel naplók

### 6.2 Adatfeldolgozás
- Tisztítás, normalizálás, tokenizálás
- Szekvencia építés
- Feature engineering

### 6.3 Modell tanítása
- LSTM autoencoder
- Predikciós modell
- Hyperparaméter optimalizálás

## 7. Összefoglalás
Az eBPF és kprobes alapú adatgyűjtés lehetővé teszi a kernel események valós időben való figyelését. Az adatok strukturálása és előfeldolgozása után LSTM modellek használhatók a kernel anomália detektálására és predikciójára.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
