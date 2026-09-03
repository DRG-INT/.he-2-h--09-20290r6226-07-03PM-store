# LSTM Autoencoder Anomália Detektálás – Gyakorlati Ismertetők
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért érdemes LSTM Autoencodert használni?
Az LSTM Autoencoder tanulja a normális kernel viselkedését, és anomáliákat detektál a rekonstrukciós hiba alapján. Nem kell címkézett hibák, felügyeletlen tanulás.

## 2. Hogyan működik?

### 2.1 Tanítás
- Normális kernel naplók betöltése
- Autoencoder betanítása
- Rekonstrukciós hiba számítása

### 2.2 Detektálás
- Új adat → rekonstrukciós hiba
- Ha hiba > küszöb → anomália
- Riasztás generálása

## 3. Gyakorlati példa

### 3.1 Modell építés
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

### 3.2 Tanítás
```python
model = LSTMAutoencoder(input_dim=100, hidden_dim=64, num_layers=2)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(num_epochs):
    for batch in train_loader:
        optimizer.zero_grad()
        recon = model(batch)
        loss = criterion(recon, batch)
        loss.backward()
        optimizer.step()
```

### 3.3 Anomália detektálás
```python
recon_error = torch.mean((recon - x) ** 2, dim=(1, 2))
threshold = np.percentile(train_errors, 95)
anomalies = recon_error > threshold
```

## 4. Gyakorlati tippek

### 4.1 Adatgyűjtés
- Kernel naplók
- Syscall trace
- Rendszeresemények

### 4.2 Adatfeldolgozás
- Tisztítás, normalizálás, tokenizálás
- Szekvencia építés
- Feature engineering

### 4.3 Modell tanítása
- Hyperparaméter optimalizálás
- Adatbővítés
- Cross-validation

## 5. Összefoglalás
Az LSTM Autoencoder hatékony eszköz a kernel anomália detektálásához. Tanulja a normális viselkedést, és anomáliákat detektál a rekonstrukciós hiba alapján. A kernel hibák korai detektálása és predikciója lehetséges.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
