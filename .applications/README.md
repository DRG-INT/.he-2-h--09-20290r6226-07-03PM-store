# Kernel Panic Applications

Kernel eseményfigyelő és elemző rendszer. ClickHouse-t használ adattárként, LSTM modelleket anomáliafelismeréshez.

## Alkalmazások

| Alkalmazás | Leírás | Indítás |
|------------|--------|---------|
| `kernel-panic-logger` | Kernel események gyűjtése | `./run.sh logger` |
| `kernel-event-streamer` | Események streamelése ClickHouse-be | `./run.sh streamer` |
| `anomaly-detector` | Valósidejű anomáliafelismerés | `./run.sh anomaly` |
| `model-trainer` | LSTM modellek tanítása | `./run.sh trainer` |
| `dashboard-server` | Grafana-szintű dashboard | `./run.sh dashboard` |
| `alert-dispatcher` | Riasztások kiküldése (email, Slack, webhook) | `./run.sh dispatcher` |
| `data-exporter` | Adatok exportálása JSON/CSV/Parquet/STIX | `./run.sh exporter` |
| `reporter` | Automatikus jelentések generálása | `./run.sh reporter` |

## Gyors indítás

```bash
# Virtuális környezet létrehozása
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Összes komponens indítása
./run.sh all

# Vagy egyesével
./run.sh logger
./run.sh streamer
./run.sh dashboard
```

## Konfiguráció

Környezeti változók:

```bash
export CLICKHOUSE_HOST=localhost
export CLICKHOUSE_PORT=8123
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## Projektstruktúra

```
.applications/
├── kernel-panic-logger/   # Eseménygyűjtő
├── kernel-event-streamer/ # Streamfeldolgozó
├── anomaly-detector/      # Valósidejű detektálás
├── model-trainer/         # LSTM tanítás
├── dashboard-server/      # Webes felület
├── alert-dispatcher/      # Riasztáskezelő
├── data-exporter/         # Export eszköz
├── reporter/              # Jelentéskészítő
├── config.py              # Közös konfiguráció
├── preprocessor.py        # Adatelőfeldolgozás
├── requirements.txt       # Függőségek
└── run.sh                 # Indító szkript
```

## Architektúra

```
[Kernel Trace] → [logger] → [streamer] → [ClickHouse]
                                          ↓
                              [anomaly-detector] → [model-trainer]
                                          ↓
                              [alert-dispatcher] → [email/Slack/webhook]
                                          ↓
                              [dashboard-server] ← API
                                          ↓
                              [reporter] → JSON/CSV/Parquet/STIX
```

## License

MIT
