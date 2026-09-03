"""
Konfiguráció
Globális beállítások minden alkalmazás számára.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
APPLICATIONS_DIR = BASE_DIR / ".applications"

# ClickHouse beállítások
CLICKHOUSE_CONFIG = {
    'host': os.getenv('CLICKHOUSE_HOST', 'localhost'),
    'port': int(os.getenv('CLICKHOUSE_PORT', 8123)),
    'username': os.getenv('CLICKHOUSE_USER', 'default'),
    'password': os.getenv('CLICKHOUSE_PASSWORD', ''),
    'database': 'kernel_events',
}

# Kernel Event Streamer beállítások
STREAMER_CONFIG = {
    'batch_size': int(os.getenv('STREAMER_BATCH_SIZE', 1000)),
    'flush_interval_ms': int(os.getenv('STREAMER_FLUSH_INTERVAL_MS', 5000)),
    'enable_raw_dedup': os.getenv('STREAMER_RAW_DEDUP', 'true').lower() == 'true',
    'enable_vnode_hash': os.getenv('STREAMER_VNODE_HASH', 'true').lower() == 'true',
}

# Anomaly Detector beállítások
ANOMALY_DETECTOR_CONFIG = {
    'window_size': int(os.getenv('ANOMALY_WINDOW_SIZE', 100)),
    'threshold': float(os.getenv('ANOMALY_THRESHOLD', 0.8)),
    'model_path': str(APPLICATIONS_DIR / "anomaly-detector" / "models"),
    'retrain_interval_hours': int(os.getenv('ANOMALY_RETRAIN_HOURS', 24)),
}

# Model Trainer beállítások
MODEL_TRAINER_CONFIG = {
    'input_dim': int(os.getenv('MODEL_INPUT_DIM', 100)),
    'hidden_dim': int(os.getenv('MODEL_HIDDEN_DIM', 64)),
    'num_layers': int(os.getenv('MODEL_NUM_LAYERS', 2)),
    'dropout': float(os.getenv('MODEL_DROPOUT', 0.2)),
    'window_size': int(os.getenv('MODEL_WINDOW_SIZE', 50)),
    'batch_size': int(os.getenv('MODEL_BATCH_SIZE', 64)),
    'epochs': int(os.getenv('MODEL_EPOCHS', 50)),
    'learning_rate': float(os.getenv('MODEL_LEARNING_RATE', 0.001)),
    'hyperparameter_optimization': os.getenv('MODEL_HPO', 'false').lower() == 'true',
}

# Alert Dispatcher beállítások
ALERT_DISPATCHER_CONFIG = {
    'channels': os.getenv('ALERT_CHANNELS', 'email,slack,webhook').split(','),
    'email': {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'from_address': os.getenv('EMAIL_FROM', ''),
        'to_address': os.getenv('EMAIL_TO', ''),
    },
    'slack': {
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
    },
    'webhook': {
        'url': os.getenv('WEBHOOK_URL', ''),
    },
}

# Data Exporter beállítások
DATA_EXPORTER_CONFIG = {
    'export_dir': os.getenv('EXPORT_DIR', str(APPLICATIONS_DIR / "data-exporter" / "exports")),
    'default_days': int(os.getenv('EXPORT_DAYS', 1)),
    'default_limit': int(os.getenv('EXPORT_LIMIT', 100000)),
}

# Dashboard Server beállítások
DASHBOARD_CONFIG = {
    'host': os.getenv('DASHBOARD_HOST', '0.0.0.0'),
    'port': int(os.getenv('DASHBOARD_PORT', 5000)),
    'debug': os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true',
}

# Kernel Panic Logger beállítások
LOGGER_CONFIG = {
    'log_dir': os.getenv('LOG_DIR', str(APPLICATIONS_DIR / "kernel-panic-logger" / "logs")),
    'max_log_size_mb': int(os.getenv('MAX_LOG_SIZE_MB', 100)),
    'compression': os.getenv('LOG_COMPRESSION', 'true').lower() == 'true',
}
