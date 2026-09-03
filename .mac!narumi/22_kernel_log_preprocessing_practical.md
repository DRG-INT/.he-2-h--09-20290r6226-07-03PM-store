# Kernel Logok Előfeldolgozása és Szekvencia Formázása – Gyakorlati Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért fontos az előfeldolgozás?
A kernel naplók rendezetlen, szöveges formátumúak. Az LSTM számára strukturált, időbeli szekvenciára van szükség. Az előfeldolgozás során tisztítjuk, normalizáljuk és vektorosítjuk a naplóbejegyzéseket.

## 2. Naplóforrások gyakorlati használata

### 2.1 Kernel naplók
```bash
# Kernel naplók
cat /var/log/kern.log
journalctl -k
dmesg
```

### 2.2 Syscall trace
```bash
# Syscall trace
strace -p 1234
perf trace
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'
```

### 2.3 Rendszeresemények
```bash
# Systemd journal
journalctl -u ssh.service
journalctl -p err

# Audit log
ausearch -i
```

## 3. Előfeldolgozási lépések

### 3.1 Tisztítás
```python
import re

def clean_log_line(line):
    # Időbélyeg normalizálása
    line = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'TIMESTAMP', line)
    # Felesleges szóközök eltávolítása
    line = re.sub(r'\s+', ' ', line).strip()
    return line
```

### 3.2 Tokenizálás
```python
def tokenize_log_line(line):
    tokens = re.findall(r'\w+|[^\w\s]', line)
    return tokens
```

### 3.3 Normalizálás
```python
def normalize_tokens(tokens):
    normalized = []
    for token in tokens:
        if token.isdigit():
            normalized.append('<NUM>')
        elif token.startswith('0x'):
            normalized.append('<HEX>')
        else:
            normalized.append(token.lower())
    return normalized
```

## 4. Szekvencia építés

### 4.1 Ablakok
```python
def build_sequences(tokens, window_size=50, step=10):
    sequences = []
    for i in range(0, len(tokens) - window_size, step):
        seq = tokens[i:i+window_size]
        sequences.append(seq)
    return sequences
```

### 4.2 Feature embedding
```python
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
encoded = le.fit_transform(all_tokens)
```

### 4.3 Padding
```python
from tensorflow.keras.preprocessing.sequence import pad_sequences

padded = pad_sequences(sequences, maxlen=window_size, padding='post')
```

## 5. Gyakorlati tippek

### 5.1 Adatgyűjtés
- Kernel naplók
- Syscall trace
- Rendszeresemények

### 5.2 Előfeldolgozás
- Tisztítás, normalizálás, tokenizálás
- Szekvencia építés
- Feature engineering

### 5.3 Modell tanítása
- LSTM autoencoder
- Predikciós modell
- Hyperparaméter optimalizálás

## 6. Összefoglalás
A kernel logok előfeldolgozása és szekvencia formázása kritikus lépés az LSTM modellek tanításához. A tisztítás, tokenizálás, normalizálás és feature engineering révén strukturált, időbeli szekvenciákat készítünk, amelyeket az LSTM hatékonyan feldolgozhat.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
