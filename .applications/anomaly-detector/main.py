"""
Anomaly Detector
Kernel anomáliák detektálása és riasztás generálás.
"""

import os
import time
import json
from datetime import datetime

import pandas as pd
import requests
import torch

from models import LSTMPredictor
from preprocessor import KernelEventPreprocessor

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DATABASE = "kernel_events"

class AnomalyDetector:
    """Anomália detektálás és riasztás"""

    def __init__(self, model_path, preprocessor_path, config):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.config = config
        self.running = True

        # Modell betöltése
        self.model = LSTMPredictor(
            input_dim=config['input_dim'],
            hidden_dim=config['hidden_dim'],
            num_layers=config['num_layers'],
            dropout=config.get('dropout', 0.2)
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        # Előfeldolgozó betöltése
        self.preprocessor = KernelEventPreprocessor()
        self.preprocessor.load_preprocessor(preprocessor_path)

        # Riasztási szűrő
        self.alert_cooldown = 60  # másodperc
        self.last_alert_time = {}

    def fetch_events(self, time_range='5m'):
        """Események lekérdezése ClickHouse-ból"""
        try:
            query = f"""
            SELECT timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm
            FROM kernel_events.kernel_events
            WHERE timestamp > now() - INTERVAL {time_range}
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

                if data:
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
            print(f"[!] Error fetching events: {e}")

        return pd.DataFrame()

    def build_sequence(self, df):
        """Szekvencia építése predikcióhoz"""
        window_size = self.config['window_size']

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

    def predict(self, X):
        """Predikció"""
        with torch.no_grad():
            pred = self.model(X)
            probability = pred.item()
            is_anomaly = probability > 0.8

        return probability, is_anomaly

    def should_alert(self, alert_type, probability):
        """Ellenőrzi, hogy kell-e riasztást küldeni"""
        now = time.time()

        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = 0

        if now - self.last_alert_time[alert_type] > self.alert_cooldown:
            self.last_alert_time[alert_type] = now
            return True

        return False

    def send_alert(self, probability, events):
        """Riasztás küldése"""
        alert_level = "CRITICAL" if probability > 0.9 else "WARNING"
        alert_type = "kernel_panic" if probability > 0.9 else "anomaly"

        if not self.should_alert(alert_type, probability):
            return

        message = {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_level": alert_level,
            "panic_probability": probability,
            "events": events[-10:] if len(events) > 10 else events
        }

        # Console riasztás
        print(f"\n{'=' * 60}")
        print(f"[!] {alert_level} ALERT!")
        print(f"    Panic probability: {probability:.2%}")
        print(f"    Time: {message['timestamp']}")
        print(f"    Recent events: {message['events'][:5]}")
        print(f"{'=' * 60}\n")

        # Itt küldheted email, Slack, stb.
        self.send_slack_alert(message)
        self.save_alert_to_clickhouse(message)

    def send_slack_alert(self, message):
        """Slack riasztás (ha konfigurálva van)"""
        try:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
            if not webhook_url:
                return

            payload = {
                "text": "🚨 *Kernel Anomaly Alert*",
                "attachments": [{
                    "color": "danger" if message['alert_level'] == "CRITICAL" else "warning",
                    "fields": [
                        {"title": "Level", "value": message['alert_level']},
                        {"title": "Probability", "value": f"{message['panic_probability']:.2%}"},
                        {"title": "Time", "value": message['timestamp']}
                    ]
                }]
            }

            requests.post(webhook_url, json=payload, timeout=5)
        except Exception as e:
            print(f"[!] Slack error: {e}")

    def save_alert_to_clickhouse(self, message):
        """Riasztás mentése ClickHouse-ba"""
        try:
            query = f"""
            INSERT INTO kernel_alerts
            (timestamp, alert_level, panic_probability, events_count, events)
            VALUES
            ('{message['timestamp']}', '{message['alert_level']}', {message['panic_probability']}, {len(message['events'])}, '{json.dumps(message['events'])}')
            """

            requests.post(
                f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
                params={"query": query},
                timeout=5
            )
        except Exception as e:
            print(f"[!] ClickHouse error: {e}")

    def run(self, interval=10):
        """Futtatási ciklus"""
        print("[*] Anomaly Detector started...")
        print(f"[*] Model: {self.model_path}")
        print(f"[*] Preprocessor: {self.preprocessor_path}")
        print(f"[*] Device: {self.device}")

        while self.running:
            try:
                # Események lekérdezése
                df = self.fetch_events(time_range='5m')

                if not df.empty:
                    # Szekvencia építése
                    X = self.build_sequence(df)

                    if X is not None:
                        # Predikció
                        probability, is_anomaly = self.predict(X)

                        # Riasztás szükséges?
                        if is_anomaly:
                            self.send_alert(probability, df['event_type'].tolist())

                time.sleep(interval)
            except Exception as e:
                print(f"[!] Error: {e}")
                time.sleep(interval)

        print("[*] Anomaly Detector stopped")

def main():
    """Példa konfiguráció"""
    config = {
        'input_dim': 100,
        'hidden_dim': 64,
        'num_layers': 2,
        'dropout': 0.2,
        'window_size': 50
    }

    detector = AnomalyDetector(
        model_path='models/best_model.pth',
        preprocessor_path='models/preprocessor.pkl',
        config=config
    )

    detector.run(interval=10)

if __name__ == "__main__":
    main()
