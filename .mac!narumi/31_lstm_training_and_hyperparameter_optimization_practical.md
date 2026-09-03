# LSTM Modellek Tanítása – Gyakorlati Implementációs Útmutató
Verzió: 1.0-stable
Forrás: UNICAGD-Core Analízis
Státusz: TUDNIVALÓ

## 1. Miért fontos a hyperparaméter optimalizálás?
Az LSTM modellek pontossága erősen függ a hyperparaméterektől: rejtett méret, rétegek száma, dropout, tanítási rátája, batch méret. A helyes hiperparaméterekkel 10-20%-kal pontosabb modell kapható.

## 2. Gyakorlati példa: Autoencoder tanítás

### 2.1 Modell építés
```python
import torch
import torch.nn as nn

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

### 2.2 Tanítási ciklus
```python
model = LSTMAutoencoder(input_dim=100, hidden_dim=64, num_layers=2)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(50):
    model.train()
    train_loss = 0.0
    for batch in train_loader:
        optimizer.zero_grad()
        recon = model(batch)
        loss = criterion(recon, batch)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for batch in val_loader:
            recon = model(batch)
            loss = criterion(recon, batch)
            val_loss += loss.item()
    
    print(f"Epoch {epoch}, Train loss: {train_loss/len(train_loader):.4f}, Val loss: {val_loss/len(val_loader):.4f}")
```

## 3. Gyakorlati példa: Predikciós modell tanítás

### 3.1 Modell építés
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

### 3.2 Tanítás
```python
model = LSTMPredictor(input_dim=100, hidden_dim=64, num_layers=2)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(50):
    model.train()
    train_loss = 0.0
    for batch, target in train_loader:
        optimizer.zero_grad()
        pred = model(batch)
        loss = criterion(pred, target)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
```

## 4. Hyperparaméter optimalizálás

### 4.1 Grid search
```python
from itertools import product

param_grid = {
    'hidden_dim': [32, 64, 128],
    'num_layers': [1, 2, 3],
    'dropout': [0.1, 0.2, 0.5],
    'lr': [0.001, 0.0001]
}

best_score = -float('inf')
best_params = None

for params in product(*param_grid.values()):
    param_dict = dict(zip(param_grid.keys(), params))
    model = LSTMPredictor(**param_dict)
    score = train_and_evaluate(model)
    if score > best_score:
        best_score = score
        best_params = param_dict
```

### 4.2 Random search
```python
from scipy.stats import randint
from sklearn.model_selection import RandomizedSearchCV

param_dist = {
    'hidden_dim': randint(32, 128),
    'num_layers': randint(1, 3),
    'dropout': [0.1, 0.2, 0.5],
    'lr': [0.001, 0.0001]
}
```

### 4.3 Bayesian optimization
```python
from skopt import BayesSearchCV
from skopt.space import Integer, Real

opt = BayesSearchCV(
    LSTMPredictor(),
    {
        'hidden_dim': Integer(32, 128),
        'num_layers': Integer(1, 3),
        'dropout': Real(0.1, 0.5),
        'lr': Real(0.0001, 0.001)
    },
    n_iter=50
)
opt.fit(X_train, y_train)
```

## 5. Adatbővítés

### 5.1 Noise injection
```python
def add_noise(seq, noise_scale=0.01):
    noise = np.random.normal(0, noise_scale, seq.shape)
    return seq + noise
```

### 5.2 Time warping
```python
def time_warp(seq, max_warp=0.2):
    warp = 1 + np.random.uniform(-max_warp, max_warp)
    return seq[::int(1/warp)]
```

### 5.3 Window slicing
```python
def window_slice(seq, window_size=50):
    start = np.random.randint(0, len(seq) - window_size)
    return seq[start:start+window_size]
```

## 6. Regularizáció

### 6.1 Early stopping
```python
best_val_loss = float('inf')
patience = 10
patience_counter = 0

for epoch in range(100):
    val_loss = validate(model, val_loader)
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        torch.save(model.state_dict(), 'best_model.pth')
    else:
        patience_counter += 1
        if patience_counter >= patience:
            break
```

### 6.2 Dropout
```python
self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
```

### 6.3 L2 regularizáció
```python
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
```

## 7. Modellek összehasonlítása

### 7.1 Metrikák
- Precision, Recall, F1
- ROC AUC
- Confusion Matrix
- Latency (inference time)
- Throughput (samples/sec)

### 7.2 Összehasonlítás
```python
import pandas as pd

results = []
for name, model in models.items():
    start = time.time()
    preds = model(X_test)
    latency = time.time() - start
    results.append({
        'model': name,
        'latency': latency,
        'throughput': len(X_test) / latency,
        'precision': precision_score(y_test, preds),
        'recall': recall_score(y_test, preds),
        'f1': f1_score(y_test, preds)
    })

df_results = pd.DataFrame(results)
```

## 8. Model exportálás

### 8.1 PyTorch save
```python
torch.save(model.state_dict(), 'model.pth')
torch.save(model, 'model_full.pt')
```

### 8.2 ONNX export
```python
import torch.onnx

dummy_input = torch.randn(1, 50, 100)
torch.onnx.export(model, dummy_input, "model.onnx")
```

## 9. Összefoglalás
Az LSTM modellek tanítása és hyperparaméter optimalizálása strukturált pipeline-t követ. Az adatbővítés, regularizáció, ensemble modellek és modellek összehasonlítása révén megbízható, prediktív modell kapható.

---

*Dokumentum státusz: STABIL. Nincs félreértés. Nincs feltételezés bizonyítás nélkül.*
