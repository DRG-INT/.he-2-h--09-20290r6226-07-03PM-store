# LSTM Autoencoder Anomália Detektálás a Kernelben
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: HASZNÁLHATÓ

## 1. Mi az a LSTM Autoencoder?
Az LSTM Autoencoder egy olyan neurális hálózat, amely tanulja a normális kernel viselkedését, és anomáliákat detektál a rekonstrukciós hiba alapján. A hibák nagyobbak, ha a bemenet nem hasonlít a tanult mintázatokhoz.

## 2. Autoencoder Architektúra

### 2.1 Encoder
- Bemeneti szekvencia → látens reprezentáció
- LSTM rétegek csökkentik a dimenziót
- Kontextus kompresszió

### 2.2 Decoder
- Látens reprezentáció → kimeneti szekvencia
- LSTM rétegek visszaállítják az eredeti dimenziót
- Rekonstrukciós hiba számítása

### 2.3 Loss Function
- MSE (Mean Squared Error)
- MAE (Mean Absolute Error)
- Cosine similarity

## 3. Anomália Detektálás

### 3.1 Tanítási folyamat
1. Normális kernel naplók betöltése
2. Autoencoder betanítása
3. Rekonstrukciós hiba számítása
4. Küszöb beállítása

### 3.2 Küszöb beállítás
- Percentilis: 95, 99
- IQR (Interquartile Range)
- Gaussián eloszlás

### 3.3 Detektálás
- Új adat → rekonstrukciós hiba
- Ha hiba > küszöb → anomália
- Riasztás generálása

## 4. Kernel Anomáliák Típusai

### 4.1 Memória anomáliák
- OOM (Out of Memory)
- Memory leak
- Page fault storm
- TLB shootdown

### 4.2 CPU anomáliák
- RCU stall
- CPU hang
- IRQ storm
- Scheduler lockup

### 4.3 I/O anomáliák
- Disk hang
- I/O timeout
- DMA fault
- IOMMU fault

### 4.4 Hálózati anomáliák
- Network hang
- Packet loss
- DNS failure
- Firewall block

## 5. LSTM Autoencoder Implementáció

### 5.1 PyTorch példa
```python
class LSTMAutoencoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers):
        self.encoder = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.decoder = nn.LSTM(hidden_dim, hidden_dim, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_dim, input_dim)
    
    def forward(self, x):
        # Encoder
        _, (hidden, cell) = self.encoder(x)
        # Decoder
        x_recon, _ = self.decoder(hidden.repeat(x.size(1), 1, 1))
        x_recon = self.linear(x_recon)
        return x_recon
```

### 5.2 Tanítási ciklus
```python
for epoch in range(num_epochs):
    for batch in train_loader:
        optimizer.zero_grad()
        recon = model(batch)
        loss = criterion(recon, batch)
        loss.backward()
        optimizer.step()
```

## 6. Rekonstrukciós hiba

### 6.1 MSE
```python
mse = F.mse_loss(recon, x, reduction='mean')
```

### 6.2 MAE
```python
mae = F.l1_loss(recon, x, reduction='mean')
```

### 6.3 Cosine similarity
```python
cos = F.cosine_similarity(recon, x, dim=-1)
```

## 7. Küszöb beállítás

### 7.1 Percentilis
```python
threshold = np.percentile(train_errors, 95)
```

### 7.2 IQR
```python
Q1 = np.percentile(train_errors, 25)
Q3 = np.percentile(train_errors, 75)
IQR = Q3 - Q1
threshold = Q3 + 1.5 * IQR
```

### 7.3 Gaussián
```python
mu = np.mean(train_errors)
sigma = np.std(train_errors)
threshold = mu + 3 * sigma
```

## 8. Teljesítménymetrikák

### 8.1 Precision, Recall, F1
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1: 2 * (Precision * Recall) / (Precision + Recall)

### 8.2 ROC AUC
- True Positive Rate vs False Positive Rate
- AUC érték: 0.5 (random) – 1.0 (tökéletes)

### 8.3 Confusion Matrix
- TP, TN, FP, FN
- False positive rate
- False negative rate

## 9. Gyakorlati tippek

### 9.1 Adatbővítés
- Noise injection
- Time warping
- Window slicing

### 9.2 Modell finomhangolás
- Hyperparaméter keresés
- Grid search, random search, Bayesian optimization

### 9.3 Monitorozás
- TensorBoard
- Weights & Biases
- MLflow

## 10. Összefoglalás
Az LSTM Autoencoder hatékony eszköz a kernel anomália detektálásához. Tanulja a normális viselkedést, és anomáliákat detektál a rekonstrukciós hiba alapján. A kernel hibák korai detektálása és predikciója lehetséges.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
