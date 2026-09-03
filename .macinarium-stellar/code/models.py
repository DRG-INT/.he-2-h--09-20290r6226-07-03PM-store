#!/usr/bin/env python3
"""
Kernel-LSTM Models
LSTM Autoencoder és Prediktor modellek implementációja.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple

class LSTMAutoencoder(nn.Module):
    """LSTM Autoencoder anomália detektáláshoz"""
    
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Encoder
        self.encoder = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        
        # Decoder
        self.decoder = nn.LSTM(
            hidden_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        
        # Linear layer
        self.linear = nn.Linear(hidden_dim, input_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Encoder
        _, (hidden, cell) = self.encoder(x)
        
        # Decoder
        x_recon, _ = self.decoder(
            hidden.repeat(x.size(1), 1, 1)
        )
        
        # Linear
        x_recon = self.linear(x_recon)
        
        return x_recon
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Tömörített reprezentáció kinyerése"""
        _, (hidden, cell) = self.encoder(x)
        return hidden, cell
    
    def decode(self, hidden: torch.Tensor, cell: torch.Tensor, seq_len: int) -> torch.Tensor:
        """Dekódolás tömörített reprezentációból"""
        x_recon, _ = self.decoder(
            hidden.repeat(seq_len, 1, 1)
        )
        x_recon = self.linear(x_recon)
        return x_recon


class LSTMPredictor(nn.Module):
    """LSTM Prediktor kernel panic előrejelzéshez"""
    
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout
        )
        
        # Fully connected
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        out, (hidden, cell) = self.lstm(x)
        
        # Utolsó időlépés kimenet
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
            
            self.optimizer.zero_grad()
            
            if isinstance(self.model, LSTMAutoencoder):
                recon = self.model(x)
                loss = self.criterion(recon, x)
            else:
                # Prediktor esetén x és y külön
                y = batch[1].to(self.device)
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
                
                if isinstance(self.model, LSTMAutoencoder):
                    recon = self.model(x)
                    loss = self.criterion(recon, x)
                else:
                    y = batch[1].to(self.device)
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
            
            # Early stopping
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
            if isinstance(self.model, LSTMAutoencoder):
                recon = self.model(X)
                errors = torch.mean((recon - X) ** 2, dim=(1, 2))
                return errors.cpu().numpy()
            else:
                pred = self.model(X)
                return pred.cpu().numpy()


def main():
    """Példa használat"""
    # Hyperparaméterek
    input_dim = 100
    hidden_dim = 64
    num_layers = 2
    dropout = 0.2
    batch_size = 64
    epochs = 50
    learning_rate = 0.001
    
    # Eszköz
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[*] Using device: {device}")
    
    # Adatok betöltése
    X = np.load('X_sequences.npy')
    y = np.load('y_labels.npy')
    
    # Train/Validation split
    split_idx = int(0.8 * len(X))
    X_train, X_val = torch.tensor(X[:split_idx], dtype=torch.float32), torch.tensor(X[split_idx:], dtype=torch.float32)
    y_train, y_val = torch.tensor(y[:split_idx], dtype=torch.float32), torch.tensor(y[split_idx:], dtype=torch.float32)
    
    # DataLoader
    from torch.utils.data import DataLoader, TensorDataset
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Modell
    model = LSTMPredictor(input_dim, hidden_dim, num_layers, dropout)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    # Tanítás
    trainer = KernelLSTMTrainer(model, criterion, optimizer, device)
    trainer.fit(train_loader, val_loader, epochs)
    
    print("[*] Training completed")

if __name__ == "__main__":
    main()
