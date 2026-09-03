#!/bin/bash
# Kernel-LSTM Agent telepítő script
# Használat: ./install_agent.sh

set -e

echo "[*] Kernel-LSTM Agent telepítése..."

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
pip3 install bcc torch pandas numpy scikit-learn influxdb-client

# Kernel fejlesztői csomagok
echo "[*] Kernel fejlesztői csomagok ellenőrzése..."
if ! dpkg -l | grep -q linux-headers-$(uname -r); then
    echo "[!] Kernel headers nincsenek telepítve!"
    echo "[!] Futtasd: sudo apt install linux-headers-$(uname -r)"
    exit 1
fi

# eBPF program fordítása
echo "[*] eBPF program fordítása..."
cd kernel_events.bpf.c
clang -target bpf -O2 -c kernel_events.bpf.c -o kernel_events.bpf.o
cd ..

# InfluxDB adatbázis létrehozása
echo "[*] InfluxDB adatbázis létrehozása..."
if ! curl -s http://localhost:8086/health | grep -q "pass"; then
    echo "[!] InfluxDB nem fut! Indítsd el: docker compose up -d influxdb"
    exit 1
fi

curl -X POST \
  http://localhost:8086/api/v2/buckets \
  -H "Authorization: Token my-super-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "orgID": "1",
    "name": "kernel_events",
    "retentionRules": [{
      "type": "expire",
      "everySeconds": 86400,
      "shardGroupDurationSeconds": 86400
    }]
  }'

echo "[+] Agent telepítve!"
echo "[*] Futtasd: sudo python3 agent.py"
