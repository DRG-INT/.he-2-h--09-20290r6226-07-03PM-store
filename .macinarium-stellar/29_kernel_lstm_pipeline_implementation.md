# Kernel-LSTM Pipeline: Implementációs Útmutató
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Implementációs áttekintés

### 1.1 Összetevők
- **Agent:** kernel események gyűjtése (eBPF/kprobes)
- **Collector:** adatfolyam központosítása
- **Processor:** előfeldolgozás, feature engineering
- **Model:** LSTM tanítás és predikció
- **Alert:** riasztás és automatikus válasz
- **Dashboard:** megjelenítés és naplózás

### 1.2 Technológiák
- Python 3.9+
- PyTorch vagy TensorFlow
- eBPF/bcc, bpftrace
- InfluxDB vagy TimescaleDB
- Grafana
- Docker/Kubernetes (opcionális)

## 2. Adatgyűjtés

### 2.1 Kernel események listája
- Syscall trace (open, close, read, write, execve, fork, exit)
- Processz létrehozás/kilépés
- Memória allokáció/felszabadítás (kmalloc, kfree)
- Page fault (major/minor)
- I/O műveletek (read, write, ioctl)
- Network események (socket, bind, connect)
- IRQ események
- CPU ütemező események

### 2.2 eBPF programok
```c
// Syscall trace
BPF_PERF_OUTPUT(events);

int trace_sys_enter(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    u64 ts = bpf_ktime_get_ns();
    struct event_t evt = {};
    evt.pid = pid;
    evt.ts = ts;
    evt.type = EVENT_SYSCALL;
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}
```

### 2.3 Adatformátum
```json
{
  "timestamp": 1709452800000000000,
  "pid": 1234,
  "tid": 1234,
  "cpu": 0,
  "event_type": "sys_enter_open",
  "duration_ns": 0,
  "retval": 0,
  "args": {
    "filename": "/etc/passwd",
    "flags": 0
  }
}
```

## 3. Előfeldolgozás

### 3.1 Tisztítás
- Időbélyeg normalizálás (nanosec → másodperc)
- Duplikátumok eltávolítása
- Hibás rekordok szűrése
- Időrendi sorrend rendezés

### 3.2 Tokenizálás
- Esemény típus: sys_enter_open, sys_enter_read, ...
- PID/TID hash
- CPU azonosító
- Esemény kódolás: integer mapping

### 3.3 Normalizálás
- Z-score: (x - μ) / σ
- Min-max: (x - min) / (max - min)
- Log transzformáció: log(1 + x)

## 4. Szekvencia építés

### 4.1 Ablak mérete
- 10, 50, 100, 200 esemény/ablak
- Időlépés: 1, 5, 10, 60 másodperc
- Overlap: 0%, 25%, 50%

### 4.2 Feature embedding
- One-hot encoding: esemény típusok
- Integer encoding: PID, CPU
- Float embedding: időbélyeg, duration

### 4.3 Címkék
- 0: normális
- 1: anomália
- 2: kernel panic
- 3: OOM
- 4: IOMMU fault

## 5. LSTM modell

### 5.1 Autoencoder architektúra
```python
class LSTMAutoencoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, dropout=0.2):
        super().__init__()
        self.encoder = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        self.decoder = nn.LSTM(
            hidden_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        self.linear = nn.Linear(hidden_dim, input_dim)
    
    def forward(self, x):
        _, (hidden, cell) = self.encoder(x)
        x_recon, _ = self.decoder(
            hidden.repeat(x.size(1), 1, 1)
        )
        x_recon = self.linear(x_recon)
        return x_recon
```

### 5.2 Predikciós modell
```python
class LSTMPredictor(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        out, (hidden, cell) = self.lstm(x)
        out = self.fc(out[:, -1, :])
        out = self.sigmoid(out)
        return out
```

## 6. Tanítási pipeline

### 6.1 Adatbetöltés
```python
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader

class KernelSequenceDataset(Dataset):
    def __init__(self, sequences, labels=None):
        self.sequences = sequences
        self.labels = labels
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        x = torch.tensor(self.sequences[idx], dtype=torch.float32)
        if self.labels is not None:
            y = torch.tensor(self.labels[idx], dtype=torch.float32)
            return x, y
        return x
```

### 6.2 DataLoader
```python
dataset = KernelSequenceDataset(X_train, y_train)
loader = DataLoader(dataset, batch_size=64, shuffle=True)
```

### 6.3 Tanítási ciklus
```python
model = LSTMAutoencoder(input_dim=100, hidden_dim=64, num_layers=2)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(50):
    for batch in loader:
        optimizer.zero_grad()
        recon = model(batch)
        loss = criterion(recon, batch)
        loss.backward()
        optimizer.step()
```

## 7. Anomália detektálás

### 7.1 Rekonstrukciós hiba
```python
model.eval()
with torch.no_grad():
    recon = model(X_test)
    errors = torch.mean((recon - X_test) ** 2, dim=(1, 2))
```

### 7.2 Küszöb beállítás
```python
threshold = np.percentile(train_errors, 95)
```

### 7.3 Detektálás
```python
anomalies = errors > threshold
```

## 8. Riasztás

### 8.1 Riasztási szintek
- INFO: normális esemény
- WARNING: anomália detektálva
- CRITICAL: kernel panic előrejelzése

### 8.2 Riasztási csatornák
- Email
- Slack webhook
- PagerDuty
- SMS

## 9. Docker környezet

### 9.1 Dockerfile
```dockerfile
FROM python:3.9-slim
RUN pip install torch pandas numpy influxdb grafana
COPY agent.py /app/
WORKDIR /app
CMD ["python", "agent.py"]
```

### 9.2 docker-compose.yml
```yaml
version: '3.8'
services:
  agent:
    build: .
    volumes:
      - /sys/kernel/debug:/sys/kernel/debug
      - /proc:/proc
    privileged: true
  collector:
    image: influxdb:latest
    volumes:
      - influxdb:/var/lib/influxdb
  dashboard:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

## 10. Összefoglalás
A kernel-LSTM pipeline implementációja konkrét lépéseket követ: adatgyűjtés eBPF/kprobes segítségével, előfeldolgozás, LSTM autoencoder és predikciós modell tanítása, anomália detektálás és riasztás. A technológiák: Python, PyTorch, eBPF, InfluxDB, Grafana, Docker.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
