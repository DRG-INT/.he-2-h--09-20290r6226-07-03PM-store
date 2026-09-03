#!/usr/bin/env python3
"""
Kernel-LSTM Preprocessor
ClickHouse backend-rel.
"""

import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DATABASE = "kernel_events"

class KernelEventPreprocessor:
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.event_types = []
    
    def load_events_from_clickhouse(self, limit=100000):
        """Események betöltése ClickHouse-ból"""
        query = f"""
        SELECT timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm 
        FROM kernel_events 
        ORDER BY timestamp ASC 
        LIMIT {limit}
        """
        
        response = requests.post(
            f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
            params={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            # ClickHouse TSV formátum
            lines = response.text.strip().split('\n')
            data = []
            for line in lines[1:]:  # Első sor a fejléc
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
    
    def clean_events(self, df):
        """Események tisztítása"""
        df = df.drop_duplicates(subset=['pid', 'tid', 'event_type', 'timestamp'])
        df = df[df['event_type'].notna()]
        df = df[df['pid'] > 0]
        df = df.sort_values('timestamp')
        return df
    
    def encode_events(self, df):
        """Események kódolása"""
        df = df.copy()
        df['event_type_encoded'] = self.label_encoder.fit_transform(df['event_type'])
        self.event_types = list(self.label_encoder.classes_)

        df['duration_ms'] = df['duration_ns'] / 1e6
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['second'] = df['timestamp'].dt.second

        df['duration_scaled'] = self.scaler.fit_transform(df[['duration_ms']]).ravel()

        return df
    
    def build_sequences(self, df, window_size=50, step=10):
        """Szekvenciák építése"""
        sequences = []
        labels = []
        
        for i in range(0, len(df) - window_size, step):
            seq = df.iloc[i:i+window_size]['event_type_encoded'].values
            sequences.append(seq)
            
            window_events = df.iloc[i:i+window_size]['event_type'].values
            if any('oom' in str(e).lower() or 'panic' in str(e).lower() for e in window_events):
                labels.append(1)
            else:
                labels.append(0)
        
        return np.array(sequences), np.array(labels)
    
    def save_preprocessor(self, path):
        """Előfeldolgozó mentése"""
        joblib.dump({
            'label_encoder': self.label_encoder,
            'scaler': self.scaler,
            'event_types': self.event_types
        }, path)
    
    def load_preprocessor(self, path):
        """Előfeldolgozó betöltése"""
        data = joblib.load(path)
        self.label_encoder = data['label_encoder']
        self.scaler = data['scaler']
        self.event_types = data['event_types']

def main():
    preprocessor = KernelEventPreprocessor()
    
    # Események betöltése ClickHouse-ból
    df = preprocessor.load_events_from_clickhouse(limit=100000)
    print(f"[*] Loaded {len(df)} events from ClickHouse")
    
    if df.empty:
        print("[!] No events found in ClickHouse")
        return
    
    # Tisztítás
    df = preprocessor.clean_events(df)
    print(f"[*] After cleaning: {len(df)} events")
    
    # Kódolás
    df = preprocessor.encode_events(df)
    print(f"[*] Event types: {len(preprocessor.event_types)}")
    
    # Szekvenciák építése
    X, y = preprocessor.build_sequences(df, window_size=50, step=10)
    print(f"[*] Sequences shape: {X.shape}")
    print(f"[*] Labels shape: {y.shape}")
    
    # Előfeldolgozó mentése
    preprocessor.save_preprocessor('preprocessor.pkl')
    print("[*] Preprocessor saved")
    
    # Adatok mentése
    np.save('X_sequences.npy', X)
    np.save('y_labels.npy', y)
    print("[*] Sequences saved")

if __name__ == "__main__":
    main()
