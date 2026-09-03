#!/usr/bin/env python3
"""
Test Suite
Alapvető komponensek tesztelése.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Importálások tesztelése"""
    print("[*] Testing imports...")

    try:
        import torch
        print(f"  [+] PyTorch: {torch.__version__}")
    except ImportError as e:
        print(f"  [-] PyTorch not found: {e}")

    try:
        import pandas as pd
        print(f"  [+] Pandas: {pd.__version__}")
    except ImportError as e:
        print(f"  [-] Pandas not found: {e}")

    try:
        import numpy as np
        print(f"  [+] NumPy: {np.__version__}")
    except ImportError as e:
        print(f"  [-] NumPy not found: {e}")

    try:
        import requests
        print(f"  [+] Requests: {requests.__version__}")
    except ImportError as e:
        print(f"  [-] Requests not found: {e}")

    try:
        import importlib.util
        if importlib.util.find_spec("clickhouse_driver"):
            print("  [+] ClickHouse driver: installed")
        else:
            print("  [-] ClickHouse driver not found")
    except Exception as e:
        print(f"  [-] ClickHouse driver check failed: {e}")

    try:
        import importlib.util
        if importlib.util.find_spec("flask"):
            print("  [+] Flask: installed")
        else:
            print("  [-] Flask not found")
    except Exception as e:
        print(f"  [-] Flask check failed: {e}")

    try:
        import importlib.util
        if importlib.util.find_spec("PyQt5.QtWidgets"):
            print("  [+] PyQt5: installed")
        else:
            print("  [-] PyQt5 not found")
    except Exception as e:
        print(f"  [-] PyQt5 check failed: {e}")

    print()

def test_models():
    """Modellek tesztelése"""
    print("[*] Testing models...")

    try:
        import torch

        from models import LSTMAutoencoder, LSTMPredictor

        # LSTM Predictor teszt
        model = LSTMPredictor(
            input_dim=100,
            hidden_dim=64,
            num_layers=2,
            dropout=0.2
        )

        x = torch.randn(4, 50, 100)  # (batch, seq_len, input_dim)
        output = model(x)
        print(f"  [+] LSTMPredictor: input {x.shape} -> output {output.shape}")

        # LSTM Autoencoder teszt
        autoencoder = LSTMAutoencoder(
            input_dim=100,
            hidden_dim=64,
            num_layers=2,
            dropout=0.2,
            seq_len=50
        )

        reconstructed = autoencoder(x)
        print(f"  [+] LSTMAutoencoder: input {x.shape} -> output {reconstructed.shape}")

        # Reconstruction error teszt
        error = autoencoder.get_reconstruction_error(x)
        print(f"  [+] Reconstruction error shape: {error.shape}")

    except Exception as e:
        print(f"  [-] Model test failed: {e}")
        import traceback
        traceback.print_exc()

    print()

def test_preprocessor():
    """Preprocessor tesztelése"""
    print("[*] Testing preprocessor...")

    try:
        import numpy as np
        import pandas as pd

        from preprocessor import KernelEventPreprocessor

        # Teszt adatok
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=1000, freq='1s'),
            'pid': np.random.randint(1, 100, 1000),
            'tid': np.random.randint(1, 1000, 1000),
            'cpu': np.random.randint(0, 8, 1000),
            'event_type': np.random.choice(['sys_enter_open', 'sys_enter_read', 'do_fork'], 1000),
            'duration_ns': np.random.randint(100, 100000, 1000),
            'retval': np.random.randint(-1, 100, 1000),
            'comm': np.random.choice(['python', 'chrome', 'kernel'], 1000)
        })

        preprocessor = KernelEventPreprocessor()

        # Clean
        df_clean = preprocessor.clean_events(df)
        print(f"  [+] Cleaned events: {len(df_clean)}")

        # Encode
        df_encoded = preprocessor.encode_events(df_clean)
        print(f"  [+] Encoded events: {len(df_encoded)}")

        # Build sequences
        X, y = preprocessor.build_sequences(df_encoded, window_size=50, step=10)
        print(f"  [+] Sequences: {X.shape}, Labels: {y.shape}")

    except Exception as e:
        print(f"  [-] Preprocessor test failed: {e}")
        import traceback
        traceback.print_exc()

    print()

def test_clickhouse_connection():
    """ClickHouse kapcsolat tesztelése"""
    print("[*] Testing ClickHouse connection...")

    try:
        from clickhouse_driver import Client

        client = Client(
            host='localhost',
            port=8123,
            user='default',
            password=''
        )

        result = client.execute("SELECT version()")
        print(f"  [+] ClickHouse connected: version {result[0][0]}")

        # Database list
        databases = client.execute("SHOW DATABASES")
        db_names = [db[0] for db in databases]
        print(f"  [+] Databases: {db_names}")

    except Exception as e:
        print(f"  [-] ClickHouse connection failed: {e}")
        print("  [!] Make sure ClickHouse is running: docker-compose up -d clickhouse")

    print()

def test_config():
    """Konfiguráció tesztelése"""
    print("[*] Testing configuration...")

    try:
        from config import (
            ANOMALY_DETECTOR_CONFIG,
            CLICKHOUSE_CONFIG,
            MODEL_TRAINER_CONFIG,
            STREAMER_CONFIG,
        )

        print(f"  [+] ClickHouse config: {CLICKHOUSE_CONFIG['host']}:{CLICKHOUSE_CONFIG['port']}")
        print(f"  [+] Streamer batch size: {STREAMER_CONFIG['batch_size']}")
        print(f"  [+] Anomaly threshold: {ANOMALY_DETECTOR_CONFIG['threshold']}")
        print(f"  [+] Model hidden dim: {MODEL_TRAINER_CONFIG['hidden_dim']}")

    except Exception as e:
        print(f"  [-] Config test failed: {e}")
        import traceback
        traceback.print_exc()

    print()

def main():
    """Összes teszt futtatása"""
    print("=" * 60)
    print("KERNEL PANIC ANALYSIS - TEST SUITE")
    print("=" * 60)
    print()

    test_imports()
    test_config()
    test_models()
    test_preprocessor()
    test_clickhouse_connection()

    print("=" * 60)
    print("[+] Test suite completed")
    print("=" * 60)

if __name__ == "__main__":
    main()
