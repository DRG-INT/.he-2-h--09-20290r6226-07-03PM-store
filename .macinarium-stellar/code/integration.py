#!/usr/bin/env python3
"""
Kernel-LSTM Integration Layer
ClickHouse backend-rel.
"""

import time
import signal
import sys
import pandas as pd
import torch
import numpy as np
import requests
from models import LSTMPredictor, KernelLSTMTrainer
from preprocessor import KernelEventPreprocessor

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DATABASE = "kernel_events"

class KernelLSTMIntegration:
    def __init__(self):
        self.preprocessor = KernelEventPreprocessor()
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.running = True
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"[!] Signal {signum} received, shutting down...")
        self.running = False
        sys.exit(0)
    
    def load_model(self, model_path: str, config: dict):
        """Modell betöltése"""
        self.model = LSTMPredictor(
            input_dim=config['input_dim'],
            hidden_dim=config['hidden_dim'],
            num_layers=config['num_layers'],
            dropout=config.get('dropout', 0.2)
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        print(f"[+] Model loaded from {model_path}")
    
    def load_preprocessor(self, preprocessor_path: str):
        """Előfeldolgozó betöltése"""
        self.preprocessor.load_preprocessor(preprocessor_path)
        print(f"[+] Preprocessor loaded from {preprocessor_path}")
    
    def fetch_events(self, time_range: str = '1m') -> pd.DataFrame:
        """Események lekérdezése ClickHouse-ból"""
        if isinstance(time_range, str) and time_range.endswith('m'):
            interval_minutes = int(time_range[:-1] or 1)
        else:
            interval_minutes = int(time_range)

        query = f"""
        SELECT timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm 
        FROM kernel_events 
        WHERE timestamp > now() - INTERVAL {interval_minutes} MINUTE
        ORDER BY timestamp ASC
        """
        
        response = requests.post(
            f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
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
            
            df = pd.DataFrame(data, columns=['timestamp', 'pid', 'tid', 'cpu', 'event_type', 'duration_ns', 'retval', 'comm'])
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
    
    def build_sequence(self, df: pd.DataFrame, window_size: int = 50) -> torch.Tensor:
        """Szekvencia építése predikcióhoz"""
        if len(df) < window_size:
            return None
        
        event_types = df['event_type'].values
        encoded = []
        for event in event_types:
            try:
                encoded.append(self.preprocessor.label_encoder.transform([event])[0])
            except ValueError:
                encoded.append(0)
        
        seq = encoded[-window_size:]
        X = torch.tensor([seq], dtype=torch.float32)
        X = X.to(self.device)
        
        return X
    
    def predict(self, X: torch.Tensor) -> tuple:
        """Predikció"""
        if self.model is None or X is None:
            return 0.0, False
        
        with torch.no_grad():
            pred = self.model(X)
            probability = pred.item()
            is_anomaly = probability > 0.8
        
        return probability, is_anomaly
    
    def send_alert(self, probability: float, events: list):
        """Riasztás küldése"""
        alert_level = "CRITICAL" if probability > 0.9 else "WARNING"
        
        message = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "alert_level": alert_level,
            "panic_probability": probability,
            "events": events[-10:] if len(events) > 10 else events
        }
        
        print(f"[!] ALERT: {alert_level} - Panic probability: {probability:.2%}")
        print(f"    Events: {message['events']}")
    
    def run(self, config: dict):
        """Futtatási ciklus"""
        print("[*] Starting Kernel-LSTM Integration with ClickHouse...")
        
        self.load_model('best_model.pth', config)
        self.load_preprocessor('preprocessor.pkl')
        
        print("[*] Integration running, monitoring kernel events...")
        
        while self.running:
            try:
                df = self.fetch_events(time_range='1m')
                
                if not df.empty:
                    X = self.build_sequence(df, window_size=config['window_size'])
                    
                    if X is not None:
                        probability, is_anomaly = self.predict(X)
                        
                        if is_anomaly:
                            self.send_alert(probability, df['event_type'].tolist())
                
                time.sleep(10)
            except Exception as e:
                print(f"[!] Error: {e}")
                time.sleep(10)
        
        print("[*] Integration stopped")

def main():
    config = {
        'input_dim': 1,
        'hidden_dim': 64,
        'num_layers': 2,
        'dropout': 0.2,
        'window_size': 50
    }
    
    integration = KernelLSTMIntegration()
    integration.run(config)

if __name__ == "__main__":
    main()
