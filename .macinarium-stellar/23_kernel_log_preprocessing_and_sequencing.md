# Kernel Logok Előfeldolgozása és Szekvencia Formázása LSTM-hez
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Miért fontos az előfeldolgozás?
A kernel naplók rendezetlen, szöveges formátumúak. Az LSTM számára strukturált, időbeli szekvenciára van szükség. Az előfeldolgozás során tisztítjuk, normalizáljuk és vektorosítjuk a naplóbejegyzéseket.

## 2. Naplóforrások

### 2.1 Kernel naplók
- `/var/log/kern.log`
- `/var/log/dmesg`
- `journalctl -k`
- `printk` buffer

### 2.2 Syscall trace
- `strace`
- `perf trace`
- `bpftrace`
- `auditd`

### 2.3 Rendszeresemények
- `systemd journal`
- `audit.log`
- `wtmp`, `btmp`

## 3. Előfeldolgozási lépések

### 3.1 Tisztítás
- Időbélyeg normalizálása (ISO 8601)
- Felesleges szóközök, üres sorok eltávolítása
- Kódolási hibák javítása
- Duplikált bejegyzések eltávolítása

### 3.2 Tokenizálás
- Szavak, számok, események különválogatása
- Syscall azonosítók kinyerése
- PID, TID, eszköznév kinyerése
- Hozzáférési szintek kinyerése

### 3.3 Normalizálás
- Kisbetűs konverzió
- Szinonimák helyettesítése
- Időbeli egység: 1 perc, 5 perc, 10 perc

## 4. Szekvencia építés

### 4.1 Időbeli ablakok
- Ablak mérete: 10, 50, 100, 200 esemény
- Időlépés: 1, 5, 10 perc
- Overlap: 0%, 25%, 50%

### 4.2 Feature embedding
- Egyedi események száma
- Események gyakorisága
- Időbeli jellemzők: átlag, szórás, trend

### 4.3 Címkék
- Normal: 0
- Anomália: 1
- Kernel panic: 2
- OOM: 3
- IOMMU fault: 4

## 5. Adatfeldolgozás

### 5.1 Tokenizer
- Egyedi események száma
- Szókincs mérete: 1000, 5000, 10000
- Out-of-vocabulary kezelés

### 5.2 Padding és truncation
- Fix szekvencia hossz: 50, 100, 200
- Padding: 0
- Truncation: hosszú szekvenciák rövidítése

### 5.3 Normalizálás
- Min-max normalizálás
- Z-score normalizálás
- Logaritmikus transzformáció

## 6. LSTM input formátum

### 6.1 Numpy array
```python
# (num_samples, timesteps, num_features)
X = np.array([
    [[0.1, 0.2, ...], [0.3, 0.4, ...], ...],  # szekvencia 1
    [[0.5, 0.6, ...], [0.7, 0.8, ...], ...],  # szekvencia 2
])
```

### 6.2 TensorFlow / PyTorch
```python
# PyTorch
import torch
X = torch.tensor(X, dtype=torch.float32)

# TensorFlow
import tensorflow as tf
X = tf.constant(X, dtype=tf.float32)
```

## 7. Feature Engineering

### 7.1 Időbeli jellemzők
- Események száma időegység alatt
- Memóriahasználat átlag, szórás
- CPU terhelés átlag, szórás
- I/O műveletek száma

### 7.2 Eseménymintázat
- Syscall sorozatok
- Processz létrehozás és befejezés
- Memória allokáció és felszabadítás

### 7.3 Korrelációk
- Események közötti időbeli távolság
- Ismétlődő minták
- Ritka események

## 8. Adatbővítés

### 8.1 Shuffle
- Szekvenciák véletlenszerű keverése
- Overlap elkerülése

### 8.2 Noise injection
- Kis zaj hozzáadása a feature-ekhez
- Robusztusság növelése

### 8.3 Synthetic data
- Normális működés szintetikus adatokkal bővítése
- Anomália szintetikus adatokkal bővítése

## 9. Adatfelosztás

### 9.1 Train / Validation / Test
- Train: 70%
- Validation: 15%
- Test: 15%

### 9.2 Stratified split
- Osztályok aránya megtartása
- Anomália minták aránya megtartása

### 9.3 Time series split
- Időrendi sorrend megtartása
- Ne jövőbeli adatokat a tanításba

## 10. Összefoglalás
A kernel logok előfeldolgozása és szekvencia formázása kritikus lépés az LSTM modellek tanításához. A tisztítás, tokenizálás, normalizálás és feature engineering révén strukturált, időbeli szekvenciákat készítünk, amelyeket az LSTM hatékonyan feldolgozhat.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
