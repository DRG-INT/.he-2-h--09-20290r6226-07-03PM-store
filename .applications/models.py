"""
LSTM Models
Predikciós és autoencoder modellek kernel eseményekhez.
"""


import torch
import torch.nn.functional as F
from torch import nn


class LSTMPredictor(nn.Module):
    """LSTM alapú predikciós modell"""

    def __init__(self,
                 input_dim: int = 100,
                 hidden_dim: int = 64,
                 num_layers: int = 2,
                 dropout: float = 0.2,
                 output_dim: int = 100):
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout

        # LSTM réteg
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )

        # Fully connected rétegek
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, output_dim)
        self.dropout_layer = nn.Dropout(dropout)

        # Batch normalization
        self.batch_norm = nn.BatchNorm1d(hidden_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        Args:
            x: Input tensor of shape (batch_size, seq_len, input_dim)
        Returns:
            Output tensor of shape (batch_size, output_dim)
        """
        # LSTM
        lstm_out, (_hidden, _cell) = self.lstm(x)

        # Utolsó időlépés kivétele
        last_hidden = lstm_out[:, -1, :]

        # Batch norm
        last_hidden = self.batch_norm(last_hidden)

        # Fully connected
        out = F.relu(self.fc1(last_hidden))
        out = self.dropout_layer(out)
        out = torch.sigmoid(self.fc2(out))

        return out

class LSTMAutoencoder(nn.Module):
    """LSTM autoencoder anomáliafelismeréshez"""

    def __init__(self,
                 input_dim: int = 100,
                 hidden_dim: int = 64,
                 num_layers: int = 2,
                 dropout: float = 0.2,
                 seq_len: int = 50):
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.seq_len = seq_len

        # Encoder
        self.encoder_lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )

        # Decoder
        self.decoder_lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )

        # Output layer
        self.output_layer = nn.Linear(hidden_dim, input_dim)
        self.dropout_layer = nn.Dropout(dropout)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Kódolás"""
        _, (hidden, _) = self.encoder_lstm(x)
        return hidden[-1]

    def decode(self, encoded: torch.Tensor, seq_len: int) -> torch.Tensor:
        """Dekódolás"""
        # Replikálás a szekvencia hosszára
        decoder_input = encoded.unsqueeze(1).repeat(1, seq_len, 1)

        # Dekódolás
        decoded, _ = self.decoder_lstm(decoder_input)

        # Output
        output = self.output_layer(decoded)
        return output

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        Args:
            x: Input tensor of shape (batch_size, seq_len, input_dim)
        Returns:
            Reconstructed tensor of shape (batch_size, seq_len, input_dim)
        """
        encoded = self.encode(x)
        decoded = self.decode(encoded, x.size(1))
        return decoded

    def get_reconstruction_error(self, x: torch.Tensor) -> torch.Tensor:
        """Rekonstrukciós hiba számítása"""
        reconstructed = self.forward(x)
        error = F.mse_loss(reconstructed, x, reduction='none')
        return error.mean(dim=(1, 2))

class KernelLSTMTrainer:
    """LSTM modellek tanítása"""

    def __init__(self,
                 model: nn.Module,
                 criterion: nn.Module,
                 optimizer: torch.optim.Optimizer,
                 device: torch.device):
        self.model = model.to(device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.history = {
            'train_loss': [],
            'val_loss': []
        }

    def train_epoch(self, train_loader) -> float:
        """Egy epoch tanítása"""
        self.model.train()
        total_loss = 0

        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(self.device)
            batch_y = batch_y.to(self.device)

            # Zero gradients
            self.optimizer.zero_grad()

            # Forward pass
            output = self.model(batch_x)
            loss = self.criterion(output, batch_y)

            # Backward pass
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

            # Update weights
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(train_loader)

    def validate(self, val_loader) -> float:
        """Validáció"""
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)

                output = self.model(batch_x)
                loss = self.criterion(output, batch_y)
                total_loss += loss.item()

        return total_loss / len(val_loader)

    def fit(self,
            train_loader,
            val_loader,
            epochs: int = 50,
            patience: int = 5,
            save_path: str | None = None):
        """
        Teljes tanítási folyamat

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            patience: Early stopping patience
            save_path: Path to save best model
        """
        best_val_loss = float('inf')
        patience_counter = 0

        print(f"[*] Starting training for {epochs} epochs...")
        print(f"[*] Device: {self.device}")

        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)

            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)

            print(f"Epoch {epoch + 1}/{epochs}")
            print(f"  Train Loss: {train_loss:.4f}")
            print(f"  Val Loss: {val_loss:.4f}")

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0

                # Best model mentése
                if save_path:
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': self.model.state_dict(),
                        'optimizer_state_dict': self.optimizer.state_dict(),
                        'loss': best_val_loss,
                    }, save_path)
                    print(f"  [+] Best model saved to {save_path}")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"\n[!] Early stopping triggered at epoch {epoch + 1}")
                    break

        print(f"\n[*] Training completed. Best validation loss: {best_val_loss:.4f}")

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Predikció"""
        self.model.eval()
        with torch.no_grad():
            x = x.to(self.device)
            return self.model(x).cpu()

class AnomalyDetectorModel:
    """Anomália detektáló wrapper"""

    def __init__(self, model_path: str, device: torch.device, threshold: float = 0.8):
        self.device = device
        self.threshold = threshold
        self.model = self._load_model(model_path)

    def _load_model(self, model_path: str) -> LSTMAutoencoder:
        """Modell betöltése"""
        checkpoint = torch.load(model_path, map_location=self.device)

        # Modell inicializálás (paraméterek a checkpointból)
        model = LSTMAutoencoder(
            input_dim=checkpoint.get('input_dim', 100),
            hidden_dim=checkpoint.get('hidden_dim', 64),
            num_layers=checkpoint.get('num_layers', 2),
            dropout=0.2,
            seq_len=checkpoint.get('seq_len', 50)
        )

        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        model.eval()

        return model

    def detect(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Anomália detektálás

        Returns:
            Tuple of (reconstruction_error, is_anomaly)
        """
        errors = self.model.get_reconstruction_error(x)
        is_anomaly = errors > self.threshold
        return errors, is_anomaly
