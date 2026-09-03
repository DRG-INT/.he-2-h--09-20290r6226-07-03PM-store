#!/bin/bash
set -e

# Kernel Panic Applications Launcher
# Használat: ./run.sh <alkalmazas> [opciók]

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$BASE_DIR/venv"
PYTHON="$VENV_DIR/bin/python"

# Virtuális környezet ellenőrzése
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Virtual environment not found. Creating..."
    python3 -m venv "$VENV_DIR"
    echo "[*] Installing dependencies..."
    "$VENV_DIR/bin/pip" install -r "$BASE_DIR/requirements.txt"
fi

# Alkalmazás indítása
case "$1" in
    logger)
        echo "[*] Starting Kernel Panic Logger..."
        "$PYTHON" "$BASE_DIR/kernel-panic-logger/main.py" "${@:2}"
        ;;
    streamer)
        echo "[*] Starting Kernel Event Streamer..."
        "$PYTHON" "$BASE_DIR/kernel-event-streamer/main.py" "${@:2}"
        ;;
    anomaly)
        echo "[*] Starting Anomaly Detector..."
        "$PYTHON" "$BASE_DIR/anomaly-detector/main.py" "${@:2}"
        ;;
    trainer)
        echo "[*] Starting Model Trainer..."
        "$PYTHON" "$BASE_DIR/model-trainer/main.py" "${@:2}"
        ;;
    dashboard)
        echo "[*] Starting Dashboard Server..."
        "$PYTHON" "$BASE_DIR/dashboard-server/app.py" "${@:2}"
        ;;
    dispatcher)
        echo "[*] Starting Alert Dispatcher..."
        "$PYTHON" "$BASE_DIR/alert-dispatcher/main.py" "${@:2}"
        ;;
    exporter)
        echo "[*] Starting Data Exporter..."
        "$PYTHON" "$BASE_DIR/data-exporter/main.py" "${@:2}"
        ;;
    reporter)
        echo "[*] Starting Reporting Tool..."
        "$PYTHON" "$BASE_DIR/reporter/main.py" "${@:2}"
        ;;
    all)
        echo "[*] Starting all components..."
        "$PYTHON" "$BASE_DIR/kernel-panic-logger/main.py" &
        "$PYTHON" "$BASE_DIR/kernel-event-streamer/main.py" &
        "$PYTHON" "$BASE_DIR/anomaly-detector/main.py" &
        "$PYTHON" "$BASE_DIR/dashboard-server/app.py" &
        "$PYTHON" "$BASE_DIR/alert-dispatcher/main.py" &
        echo "[+] All components started. Check logs for details."
        ;;
    test)
        echo "[*] Running test suite..."
        "$PYTHON" "$BASE_DIR/test_suite.py"
        ;;
    *)
        echo "Usage: $0 <alkalmazas> [opciók]"
        echo ""
        echo "Alkalmazások:"
        echo "  logger      - Kernel Panic Logger"
        echo "  streamer    - Kernel Event Streamer"
        echo "  anomaly     - Anomaly Detector"
        echo "  trainer     - Model Trainer"
        echo "  dashboard   - Dashboard Server"
        echo "  dispatcher  - Alert Dispatcher"
        echo "  exporter    - Data Exporter"
        echo "  reporter    - Reporting Tool"
        echo "  test        - Test suite futtatása"
        echo "  all         - Összes alkalmazás indítása"
        echo ""
        echo "Példa: $0 logger --config config.yaml"
        exit 1
        ;;
esac
