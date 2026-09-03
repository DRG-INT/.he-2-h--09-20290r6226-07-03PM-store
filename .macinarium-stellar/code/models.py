#!/usr/bin/env python3
"""
Kernel-LSTM Models
ClickHouse backend-rel.
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import requests
from typing import Tuple

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DATABASE = "kernel_events"

class LSTMAutoencoder(nn.Module):
    """LSTM Autoencoder anomália detektáláshoz"""
    
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.encoder = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        
        self.decoder = nn.LSTM(
            hidden_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        
        self.linear = nn.Linear(hidden_dim, input_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(-1)

        _, (hidden, cell) = self.encoder(x)
        decoder_input = hidden[-1].unsqueeze(1).repeat(1, x.size(1), 1)
        x_recon, _ = self.decoder(decoder_input, (hidden, cell))
        x_recon = self.linear(x_recon)
        return x_recon
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        _, (hidden, cell) = self.encoder(x)
        return hidden, cell
    
    def decode(self, hidden: torch.Tensor, cell: torch.Tensor, seq_len: int) -> torch.Tensor:
        decoder_input = hidden[-1].unsqueeze(1).repeat(1, seq_len, 1)
        x_recon, _ = self.decoder(decoder_input, (hidden, cell))
        x_recon = self.linear(x_recon)
        return x_recon


class LSTMPredictor(nn.Module):
    """LSTM Prediktor kernel panic előrejelzéshez"""
    
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(-1)

        out, (hidden, cell) = self.lstm(x)
        out = self.fc(out[:, -1, :])
        out = self.sigmoid(out)
        return out


class KernelLSTMTrainer:
    """LSTM modellek tanításához és értékeléshez"""
    
    def __init__(self, model, criterion, optimizer, device='cpu'):
        self.model = model.to(device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.history = {
            'train_loss': [],
            'val_loss': []
        }
    
    def train_epoch(self, train_loader):
        """Egy epoch tanítása"""
        self.model.train()
        train_loss = 0.0
        
        for batch in train_loader:
            if isinstance(batch, (list, tuple)):
                x = batch[0]
            else:
                x = batch
            
            x = x.to(self.device)
            if x.dim() == 2:
                x = x.unsqueeze(-1)
            
            self.optimizer.zero_grad()
            
            if isinstance(self.model, LSTMAutoencoder):
                recon = self.model(x)
                loss = self.criterion(recon, x)
            else:
                y = batch[1].to(self.device).float().view(-1, 1)
                pred = self.model(x)
                loss = self.criterion(pred, y)
            
            loss.backward()
            self.optimizer.step()
            
            train_loss += loss.item()
        
        return train_loss / len(train_loader)
    
    def validate(self, val_loader):
        """Validáció"""
        self.model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for batch in val_loader:
                if isinstance(batch, (list, tuple)):
                    x = batch[0]
                else:
                    x = batch
                
                x = x.to(self.device)
                if x.dim() == 2:
                    x = x.unsqueeze(-1)
                
                if isinstance(self.model, LSTMAutoencoder):
                    recon = self.model(x)
                    loss = self.criterion(recon, x)
                else:
                    y = batch[1].to(self.device).float().view(-1, 1)
                    pred = self.model(x)
                    loss = self.criterion(pred, y)
                
                val_loss += loss.item()
        
        return val_loss / len(val_loader)
    
    def fit(self, train_loader, val_loader, epochs: int, patience: int = 10):
        """Teljes tanítási folyamat"""
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)
            
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            
            print(f"Epoch {epoch+1}/{epochs}: "
                  f"Train Loss: {train_loss:.4f}, "
                  f"Val Loss: {val_loss:.4f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                torch.save(self.model.state_dict(), 'best_model.pth')
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"[!] Early stopping at epoch {epoch+1}")
                    break
    
    def predict(self, X: torch.Tensor) -> np.ndarray:
        """Predikció"""
        self.model.eval()
        with torch.no_grad():
            X = X.to(self.device)
            if X.dim() == 2:
                X = X.unsqueeze(-1)
            if isinstance(self.model, LSTMAutoencoder):
                recon = self.model(X)
                errors = torch.mean((recon - X) ** 2, dim=(1, 2))
                return errors.cpu().numpy()
            else:
                pred = self.model(X)
                return pred.cpu().numpy()


class ClickHouseDataLoader:
    """ClickHouse-ból tölti be az adatokat"""
    
    def __init__(self, host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, database=CLICKHOUSE_DATABASE):
        self.host = host
        self.port = port
        self.database = database
    
    def fetch_sequences(self, limit=100000):
        """Szekvenciák betöltése ClickHouse-ból"""
        query = f"""
        SELECT timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm 
        FROM kernel_events 
        ORDER BY timestamp ASC 
        LIMIT {limit}
        """
        
        response = requests.post(
            f"http://{self.host}:{self.port}/",
            params={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            data = []
            for line in lines[1:]:
                parts = line.split('\t')
                if len(parts) >= 8:
                    data.append(parts)
            
            columns = ['timestamp', 'pid', 'tid', 'cpu', 'event_type', 'duration_ns', 'retval', 'comm']
            df = pd.DataFrame(data, columns=columns)
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['duration_ns'] = pd.to_numeric(df['duration_ns'], errors='coerce')
            df['pid'] = pd.to_numeric(df['pid'], errors='coerce')
            df['tid'] = pd.to_numeric(df['tid'], errors='coerce')
            df['cpu'] = pd.to_numeric(df['cpu'], errors='coerce')
            df['retval'] = pd.to_numeric(df['retval'], errors='coerce')
            df = df.dropna()
            return df
        else:
            print(f"[!] ClickHouse query failed: {response.text}")
            return pd.DataFrame()


def main():
    """Példa használat"""
    input_dim = 1
    hidden_dim = 64
    num_layers = 2
    dropout = 0.2
    batch_size = 64
    epochs = 50
    learning_rate = 0.001
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[*] Using device: {device}")
    
    # Adatok betöltése ClickHouse-ból
    loader = ClickHouseDataLoader()
    df = loader.fetch_sequences(limit=100000)
    print(f"[*] Loaded {len(df)} events from ClickHouse")
    
    if df.empty:
        print("[!] No data available")
        return
    
    # Előfeldolgozás
    from preprocessor import KernelEventPreprocessor
    preprocessor = KernelEventPreprocessor()
    df = preprocessor.clean_events(df)
    df = preprocessor.encode_events(df)
    X, y = preprocessor.build_sequences(df, window_size=50, step=10)

    print(f"[*] Sequences shape: {X.shape}")
    print(f"[*] Labels shape: {y.shape}")

    if len(X) == 0:
        print("[!] Not enough data to build training sequences")
        return
    
    # Train/Validation split
    split_idx = int(0.8 * len(X))
    X_train, X_val = torch.tensor(X[:split_idx], dtype=torch.float32), torch.tensor(X[split_idx:], dtype=torch.float32)
    y_train, y_val = torch.tensor(y[:split_idx], dtype=torch.float32), torch.tensor(y[split_idx:], dtype=torch.float32)
    
    from torch.utils.data import DataLoader, TensorDataset
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Modell és tanítás
    model = LSTMPredictor(input_dim, hidden_dim, num_layers, dropout)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    trainer = KernelLSTMTrainer(model, criterion, optimizer, device)
    trainer.fit(train_loader, val_loader, epochs)
    
    print("[*] Training completed")

if __name__ == "__main__":
    main()
