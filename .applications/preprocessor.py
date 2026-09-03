"""
Preprocessor
Kernel események előfeldolgozása: tisztítás, kódolás, szekvenciák.
"""

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


class KernelEventPreprocessor:
    """Kernel események előfeldolgozása"""

    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = [
            'duration_ns', 'pid', 'tid', 'cpu', 'retval',
            'event_type_encoded', 'comm_encoded'
        ]

    def clean_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """Események tisztítása"""
        df = df.copy()

        # Duplikátumok eltávolítása
        df = df.drop_duplicates()

        # Hiányzó értékek kezelése
        df['duration_ns'] = pd.to_numeric(df['duration_ns'], errors='coerce')
        df['pid'] = pd.to_numeric(df['pid'], errors='coerce')
        df['tid'] = pd.to_numeric(df['tid'], errors='coerce')
        df['cpu'] = pd.to_numeric(df['cpu'], errors='coerce')
        df['retval'] = pd.to_numeric(df['retval'], errors='coerce')

        # Nullák eltávolítása
        df = df.dropna(subset=['timestamp', 'event_type', 'duration_ns', 'pid'])

        # Negatív időtartamok kijavítása
        df.loc[df['duration_ns'] < 0, 'duration_ns'] = 0

        # Rendezés idő alapján
        df = df.sort_values('timestamp').reset_index(drop=True)

        return df

    def encode_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """Események kódolása numerikus értékekre"""
        df = df.copy()

        # Event type kódolás
        if 'event_type_encoder' not in self.encoders:
            self.encoders['event_type_encoder'] = LabelEncoder()
            df['event_type_encoded'] = self.encoders['event_type_encoder'].fit_transform(
                df['event_type'].astype(str)
            )
        else:
            df['event_type_encoded'] = self.encoders['event_type_encoder'].transform(
                df['event_type'].astype(str)
            )

        # Comm kódolás
        if 'comm_encoder' not in self.encoders:
            self.encoders['comm_encoder'] = LabelEncoder()
            df['comm_encoded'] = self.encoders['comm_encoder'].fit_transform(
                df['comm'].fillna('unknown').astype(str)
            )
        else:
            df['comm_encoded'] = self.encoders['comm_encoder'].transform(
                df['comm'].fillna('unknown').astype(str)
            )

        # Skálázás
        numeric_cols = ['duration_ns', 'pid', 'tid', 'cpu', 'retval']
        for col in numeric_cols:
            if col not in self.scalers:
                self.scalers[col] = StandardScaler()
                df[f'{col}_scaled'] = self.scalers[col].fit_transform(df[[col]])
            else:
                df[f'{col}_scaled'] = self.scalers[col].transform(df[[col]])

        return df

    def build_sequences(self,
                        df: pd.DataFrame,
                        window_size: int = 50,
                        step: int = 10) -> tuple[np.ndarray, np.ndarray]:
        """Időszekvenciák építése LSTM-hez"""

        # Feature mátrix kiválasztása
        scaled_cols = [c for c in df.columns if c.endswith('_scaled')]
        feature_matrix = df[scaled_cols].values

        sequences = []
        labels = []

        # Egyszerű címke: jelenlegi és jövőbeli értékek összehasonlítása
        for i in range(0, len(feature_matrix) - window_size - 1, step):
            seq = feature_matrix[i:i + window_size]
            target = feature_matrix[i + window_size]

            sequences.append(seq)
            labels.append(target)

        X = np.array(sequences)
        y = np.array(labels)

        return X, y

    def save_preprocessor(self, path: str):
        """Előfeldolgozó mentése"""
        save_data = {
            'scalers': self.scalers,
            'encoders': self.encoders,
            'feature_columns': self.feature_columns
        }
        joblib.dump(save_data, path)
        print(f"[+] Preprocessor saved to {path}")

    def load_preprocessor(self, path: str):
        """Előfeldolgozó betöltése"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Preprocessor file not found: {path}")

        save_data = joblib.load(path)
        self.scalers = save_data['scalers']
        self.encoders = save_data['encoders']
        self.feature_columns = save_data['feature_columns']
        print(f"[+] Preprocessor loaded from {path}")
