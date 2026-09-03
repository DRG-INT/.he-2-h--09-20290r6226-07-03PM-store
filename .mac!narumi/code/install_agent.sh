#!/bin/bash
# Kernel-LSTM Agent telepítő script ClickHouse-al
# Használat: ./install_agent.sh

set -e

echo "[*] Kernel-LSTM Agent telepítése ClickHouse-al..."

# Függőségek ellenőrzése
echo "[*] Függőségek ellenőrzése..."

if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 nincs telepítve!"
    exit 1
fi

if ! command -v gcc &> /dev/null; then
    echo "[!] GCC nincs telepítve!"
    exit 1
fi

# Python csomagok telepítése
echo "[*] Python csomagok telepítése..."
pip3 install --upgrade pip
pip3 install bcc torch pandas numpy scikit-learn requests joblib

# Kernel fejlesztői csomagok
echo "[*] Kernel fejlesztői csomagok ellenőrzése..."
if ! dpkg -l | grep -q linux-headers-$(uname -r); then
    echo "[!] Kernel headers nincsenek telepítve!"
    echo "[!] Futtasd: sudo apt install linux-headers-$(uname -r)"
    exit 1
fi

# ClickHouse ellenőrzése
echo "[*] ClickHouse ellenőrzése..."
if ! curl -s http://localhost:8123/ping | grep -q "Ok"; then
    echo "[!] ClickHouse nem fut! Indítsd el: docker compose up -d clickhouse"
    exit 1
fi

# Adatbázis és tábla létrehozása
echo "[*] ClickHouse adatbázis és tábla létrehozása..."

# Adatbázis létrehozása
curl -X POST "http://localhost:8123/" --data "CREATE DATABASE IF NOT EXISTS kernel_events"

# Tábla létrehozása
curl -X POST "http://localhost:8123/" --data "
CREATE TABLE IF NOT EXISTS kernel_events.kernel_events (
    timestamp DateTime64(9),
    pid UInt32,
    tid UInt32,
    cpu UInt32,
    event_type String,
    duration_ns UInt64,
    retval Int64,
    comm String
) ENGINE = MergeTree()
ORDER BY timestamp
PARTITION BY toYYYYMMDD(timestamp)
TTL toDateTime(timestamp) + INTERVAL 7 DAY
"

# Riasztási tábla
curl -X POST "http://localhost:8123/" --data "
CREATE TABLE IF NOT EXISTS kernel_events.kernel_alerts (
    timestamp DateTime64(9),
    alert_level String,
    panic_probability Float64,
    events_count UInt32,
    events String
) ENGINE = MergeTree()
ORDER BY timestamp
PARTITION BY toYYYYMMDD(timestamp)
TTL toDateTime(timestamp) + INTERVAL 30 DAY
"

echo "[+] Adatbázis és táblák létrehozva!"

# eBPF program fordítása
echo "[*] eBPF program fordítása..."
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BPF_SOURCE="${BPF_SOURCE:-$SCRIPT_DIR/kernel_events.bpf.c}"
if [ ! -f "$BPF_SOURCE" ]; then
    echo "[!] BPF source not found: $BPF_SOURCE"
    echo "[!] Set BPF_SOURCE or place kernel_events.bpf.c next to this script."
    exit 1
fi

clang -target bpf -O2 -c "$BPF_SOURCE" -o "${BPF_SOURCE%.c}.o"

echo "[+] Agent telepítve ClickHouse-al!"
echo "[*] Futtasd: sudo python3 agent.py"
