#!/usr/bin/env python3
"""
Kernel-LSTM Preprocessor
Előfeldolgozza a kernel eseményeket és szekvenciákat épít az LSTM modellekhez.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

class KernelEventPreprocessor:
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.event_types = []
    
    def load_events(self, filepath):
        """Események betöltése CSV fájlból"""
        df = pd.read_csv(filepath)
        df['ts'] = pd.to_datetime(df['ts'], unit='ns')
        df = df.sort_values('ts')
        return df
    
    def clean_events(self, df):
        """Események tisztítása"""
        # Duplikátumok eltávolítása
        df = df.drop_duplicates(subset=['pid', 'tid', 'event_type', 'ts'])
        
        # Hibás rekordok szűrése
        df = df[df['event_type'].notna()]
        df = df[df['pid'] > 0]
        
        # Időbélyeg normalizálása
        df = df.sort_values('ts')
        
        return df
    
    def encode_events(self, df):
        """Események kódolása"""
        # Esemény típusok kódolása
        df['event_type_encoded'] = self.label_encoder.fit_transform(df['event_type'])
        self.event_types = list(self.label_encoder.classes_)
        
        # Feature engineering
        df['duration_ms'] = df['duration_ns'] / 1e6
        df['hour'] = df['ts'].dt.hour
        df['minute'] = df['ts'].dt.minute
        df['second'] = df['ts'].dt.second
        
        # Normalizálás
        df['duration_scaled'] = self.scaler.fit_transform(df[['duration_ms']])
        
        return df
    
    def build_sequences(self, df, window_size=50, step=10):
        """Szekvenciák építése"""
        sequences = []
        labels = []
        
        for i in range(0, len(df) - window_size, step):
            seq = df.iloc[i:i+window_size]['event_type_encoded'].values
            sequences.append(seq)
            
            # Címke: anomália vagy normális
            # Itt egyszerű szabály: ha van OOM vagy kernel panic event, anomália
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
    
    # Események betöltése
    df = preprocessor.load_events('kernel_events.csv')
    print(f"[*] Loaded {len(df)} events")
    
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
