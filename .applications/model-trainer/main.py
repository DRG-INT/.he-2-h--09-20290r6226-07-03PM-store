#!/usr/bin/env python3
"""
Model Trainer
LSTM modellek tanítása és hiperparaméter optimalizálás.
"""


import pandas as pd
import requests
import torch
from sklearn.model_selection import train_test_split
from torch import nn

from models import KernelLSTMTrainer, LSTMPredictor
from preprocessor import KernelEventPreprocessor

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DATABASE = "kernel_events"

class ModelTrainer:
    """Modellek tanítása és optimalizálása"""

    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.preprocessor = KernelEventPreprocessor()
        self.best_model = None
        self.best_score = -float('inf')

    def fetch_training_data(self, limit=500000):
        """Adatok lekérdezése ClickHouse-ból tanításhoz"""
        try:
            query = f"""
            SELECT timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm
            FROM kernel_events.kernel_events
            WHERE timestamp > now() - INTERVAL 7 DAY
            ORDER BY timestamp ASC
            LIMIT {limit}
            """

            response = requests.post(
                f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
                params={"query": query},
                timeout=60
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
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')
                df['duration_ns'] = pd.to_numeric(df['duration_ns'], errors='coerce')
                df['pid'] = pd.to_numeric(df['pid'], errors='coerce')
                df['tid'] = pd.to_numeric(df['tid'], errors='coerce')
                df['cpu'] = pd.to_numeric(df['cpu'], errors='coerce')
                df['retval'] = pd.to_numeric(df['retval'], errors='coerce')
                df = df.dropna()
                return df
        except Exception as e:
            print(f"[!] Error fetching training data: {e}")

        return pd.DataFrame()

    def prepare_data(self, df):
        """Adatok előkészítése tanításhoz"""
        # Tisztítás
        df = self.preprocessor.clean_events(df)

        # Kódolás
        df = self.preprocessor.encode_events(df)

        # Szekvenciák építése
        X, y = self.preprocessor.build_sequences(
            df,
            window_size=self.config['window_size'],
            step=10
        )

        return X, y

    def train_model(self, X, y):
        """Modell tanítása"""
        # Train/Validation/Test split
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42
        )

        # Tensor konverzió
        X_train = torch.tensor(X_train, dtype=torch.float32)
        y_train = torch.tensor(y_train, dtype=torch.float32)
        X_val = torch.tensor(X_val, dtype=torch.float32)
        y_val = torch.tensor(y_val, dtype=torch.float32)

        # DataLoader
        from torch.utils.data import DataLoader, TensorDataset
        train_dataset = TensorDataset(X_train, y_train)
        val_dataset = TensorDataset(X_val, y_val)
        train_loader = DataLoader(train_dataset, batch_size=self.config['batch_size'], shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config['batch_size'], shuffle=False)

        # Modell
        model = LSTMPredictor(
            input_dim=self.config['input_dim'],
            hidden_dim=self.config['hidden_dim'],
            num_layers=self.config['num_layers'],
            dropout=self.config['dropout']
        )

        # Tanítás
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=self.config['learning_rate'])

        trainer = KernelLSTMTrainer(model, criterion, optimizer, self.device)
        trainer.fit(train_loader, val_loader, epochs=self.config['epochs'])

        # Evaluáció
        model.eval()
        with torch.no_grad():
            X_test = X_test.to(self.device)
            pred = model(X_test)
            y_pred = (pred.cpu().numpy() > 0.5).astype(int)
            y_true = y_test.cpu().numpy()

            from sklearn.metrics import f1_score, precision_score, recall_score
            precision = precision_score(y_true, y_pred, average='weighted')
            recall = recall_score(y_true, y_pred, average='weighted')
            f1 = f1_score(y_true, y_pred, average='weighted')

            print("\n[*] Model Performance:")
            print(f"    Precision: {precision:.4f}")
            print(f"    Recall: {recall:.4f}")
            print(f"    F1 Score: {f1:.4f}")

        # Legjobb modell mentése
        if f1 > self.best_score:
            self.best_score = f1
            self.best_model = model

            # Mentés
            torch.save(model.state_dict(), 'models/best_model.pth')
            self.preprocessor.save_preprocessor('models/preprocessor.pkl')

            print(f"[+] Best model saved (F1: {f1:.4f})")

        return model, f1

    def hyperparameter_optimization(self, X, y):
        """Hiperparaméter optimalizálás"""
        from itertools import product

        param_grid = {
            'hidden_dim': [32, 64, 128],
            'num_layers': [1, 2, 3],
            'dropout': [0.1, 0.2, 0.5],
            'learning_rate': [0.001, 0.0001]
        }

        best_score = -float('inf')
        best_params = None

        print("[*] Starting hyperparameter optimization...")

        for hidden_dim, num_layers, dropout, lr in product(
            param_grid['hidden_dim'],
            param_grid['num_layers'],
            param_grid['dropout'],
            param_grid['learning_rate']
        ):
            params = {
                'input_dim': self.config['input_dim'],
                'hidden_dim': hidden_dim,
                'num_layers': num_layers,
                'dropout': dropout,
                'window_size': self.config['window_size'],
                'batch_size': self.config['batch_size'],
                'epochs': self.config['epochs'],
                'learning_rate': lr
            }

            print(f"\n[*] Testing params: hidden_dim={hidden_dim}, "
                  f"num_layers={num_layers}, dropout={dropout}, lr={lr}")

            try:
                _model, score = self.train_model(X, y)

                if score > best_score:
                    best_score = score
                    best_params = params
                    print(f"[+] New best score: {best_score:.4f}")
            except Exception as e:
                print(f"[!] Error with params {params}: {e}")
                continue

        print("\n[*] Hyperparameter optimization completed")
        print(f"[*] Best params: {best_params}")
        print(f"[*] Best score: {best_score:.4f}")

        return best_params, best_score

    def run(self):
        """Teljes tanítási folyamat"""
        print("[*] Model Trainer started...")
        print(f"[*] Device: {self.device}")

        # Adatok lekérdezése
        print("[*] Fetching training data from ClickHouse...")
        df = self.fetch_training_data(limit=500000)

        if df.empty:
            print("[!] No training data available")
            return

        print(f"[*] Loaded {len(df)} events")

        # Adatok előkészítése
        print("[*] Preparing data...")
        X, y = self.prepare_data(df)
        print(f"[*] Sequences shape: {X.shape}")
        print(f"[*] Labels shape: {y.shape}")

        # Ellenőrzés, hogy van-e elég adat
        if len(X) < 100:
            print("[!] Not enough data for training")
            return

        # Hiperparaméter optimalizálás
        if self.config.get('hyperparameter_optimization', False):
            _best_params, _best_score = self.hyperparameter_optimization(X, y)
        else:
            # Egyszerű tanítás
            _model, _score = self.train_model(X, y)

        print("\n[+] Model training completed!")

def main():
    """Példa konfiguráció"""
    config = {
        'input_dim': 100,
        'hidden_dim': 64,
        'num_layers': 2,
        'dropout': 0.2,
        'window_size': 50,
        'batch_size': 64,
        'epochs': 50,
        'learning_rate': 0.001,
        'hyperparameter_optimization': False
    }

    trainer = ModelTrainer(config)
    trainer.run()

if __name__ == "__main__":
    main()
