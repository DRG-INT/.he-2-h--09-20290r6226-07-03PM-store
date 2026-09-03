#!/usr/bin/env python3
"""
Kernel-LSTM Integration Layer
Összeköti a collector, processor, model és alert rendszereket.
"""

import time
import json
import signal
import sys
from datetime import datetime
from influxdb import InfluxDBClient
import torch
import numpy as np
from models import LSTMPredictor, KernelLSTMTrainer
from preprocessor import KernelEventPreprocessor

class KernelLSTMIntegration:
    def __init__(self):
        self.influx_client = InfluxDBClient(
            host='localhost',
            port=8086
        )
        self.influx_client.switch_database('kernel_events')
        self.preprocessor = KernelEventPreprocessor()
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.running = True
        
        # Signal handler
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
        """Események lekérdezése InfluxDB-ből"""
        query = f"""
        SELECT * FROM kernel_events
        WHERE time > now() - {time_range}
        ORDER BY time ASC
        """
        result = self.influx_client.query(query)
        
        if result:
            df = pd.DataFrame(list(result.get_points()))
            return df
        return pd.DataFrame()
    
    def build_sequence(self, df: pd.DataFrame, window_size: int = 50) -> torch.Tensor:
        """Szekvencia építése predikcióhoz"""
        if len(df) < window_size:
            return None
        
        # Események kódolása
        event_types = df['event_type'].values
        encoded = []
        for event in event_types:
            try:
                encoded.append(self.preprocessor.label_encoder.transform([event])[0])
            except ValueError:
                encoded.append(0)
        
        # Utolsó window_size esemény
        seq = encoded[-window_size:]
        X = torch.tensor([seq], dtype=torch.float32)
        X = X.to(self.device)
        
        return X
    
    def predict(self, X: torch.Tensor) -> Tuple[float, bool]:
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
            "timestamp": datetime.utcnow().isoformat(),
            "alert_level": alert_level,
            "panic_probability": probability,
            "events": events[-10:] if len(events) > 10 else events
        }
        
        # Itt küldheted email, Slack, PagerDuty, stb.
        print(f"[!] ALERT: {alert_level} - Panic probability: {probability:.2%}")
        print(f"    Events: {message['events']}")
    
    def run(self, config: dict):
        """Futtatási ciklus"""
        print("[*] Starting Kernel-LSTM Integration...")
        
        # Modell és előfeldolgozó betöltése
        self.load_model('best_model.pth', config)
        self.load_preprocessor('preprocessor.pkl')
        
        print("[*] Integration running, monitoring kernel events...")
        
        while self.running:
            try:
                # Események lekérdezése
                df = self.fetch_events(time_range='1m')
                
                if not df.empty:
                    # Szekvencia építése
                    X = self.build_sequence(df, window_size=config['window_size'])
                    
                    if X is not None:
                        # Predikció
                        probability, is_anomaly = self.predict(X)
                        
                        # Riasztás szükséges?
                        if is_anomaly:
                            self.send_alert(probability, df['event_type'].tolist())
                
                time.sleep(10)  # 10 másodperc várakozás
            except Exception as e:
                print(f"[!] Error: {e}")
                time.sleep(10)
        
        print("[*] Integration stopped")

def main():
    """Példa konfiguráció"""
    config = {
        'input_dim': 100,
        'hidden_dim': 64,
        'num_layers': 2,
        'dropout': 0.2,
        'window_size': 50
    }
    
    integration = KernelLSTMIntegration()
    integration.run(config)

if __name__ == "__main__":
    main()
