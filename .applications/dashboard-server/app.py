"""
Dashboard Server
Grafana dashboard és API szerver a kernel metrikákhoz.
"""

from datetime import datetime, timedelta

import requests
from flask import Flask, jsonify, render_template

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DATABASE = "kernel_events"

app = Flask(__name__)

@app.route('/')
def index():
    """Dashboard főoldal"""
    return render_template('dashboard.html')

@app.route('/api/metrics/events-per-second')
def events_per_second():
    """Események száma másodpercenként"""
    try:
        query = """
        SELECT
            toStartOfSecond(timestamp) as time,
            count() as count
        FROM kernel_events.kernel_events
        WHERE timestamp > now() - INTERVAL 1 HOUR
        GROUP BY time
        ORDER BY time ASC
        """

        response = requests.post(
            f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
            params={"query": query},
            timeout=10
        )

        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            data = []
            for line in lines[1:]:
                parts = line.split('\t')
                if len(parts) >= 2:
                    data.append({
                        'time': parts[0],
                        'count': int(parts[1])
                    })
            return jsonify(data)
    except Exception:
        print(" [!] Error: {e}")

    return jsonify([])

@app.route('/api/metrics/anomalies')
def anomalies():
    """Anomáliák száma időegység alatt"""
    try:
        query = """
        SELECT
            toStartOfMinute(timestamp) as time,
            count() as count
        FROM kernel_alerts.kernel_alerts
        WHERE timestamp > now() - INTERVAL 1 HOUR
        GROUP BY time
        ORDER BY time ASC
        """

        response = requests.post(
            f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
            params={"query": query},
            timeout=10
        )

        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            data = []
            for line in lines[1:]:
                parts = line.split('\t')
                if len(parts) >= 2:
                    data.append({
                        'time': parts[0],
                        'count': int(parts[1])
                    })
            return jsonify(data)
    except Exception:
        print(" [!] Error: {e}")

    return jsonify([])

@app.route('/api/metrics/cpu')
def cpu_usage():
    """CPU használat"""
    try:
        # Itt valós CPU metrikák kellenének
        # Most placeholder adat
        return jsonify([
            {'time': datetime.now().isoformat(), 'usage': 45.2},
            {'time': (datetime.now() - timedelta(minutes=1)).isoformat(), 'usage': 42.1},
            {'time': (datetime.now() - timedelta(minutes=2)).isoformat(), 'usage': 48.5}
        ])
    except Exception:
        print(" [!] Error: {e}")

    return jsonify([])

@app.route('/api/metrics/memory')
def memory_usage():
    """Memória használat"""
    try:
        # Itt valós memória metrikák kellenének
        # Most placeholder adat
        return jsonify([
            {'time': datetime.now().isoformat(), 'usage': 62.3},
            {'time': (datetime.now() - timedelta(minutes=1)).isoformat(), 'usage': 61.8},
            {'time': (datetime.now() - timedelta(minutes=2)).isoformat(), 'usage': 63.1}
        ])
    except Exception:
        print(" [!] Error: {e}")

    return jsonify([])

@app.route('/api/alerts/recent')
def recent_alerts():
    """Legújabb riasztások"""
    try:
        query = """
        SELECT timestamp, alert_level, panic_probability, events
        FROM kernel_alerts.kernel_alerts
        ORDER BY timestamp DESC
        LIMIT 20
        """

        response = requests.post(
            f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
            params={"query": query},
            timeout=10
        )

        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            alerts = []
            for line in lines[1:]:
                parts = line.split('\t')
                if len(parts) >= 4:
                    alerts.append({
                        'timestamp': parts[0],
                        'level': parts[1],
                        'probability': float(parts[2]),
                        'events': parts[3]
                    })
            return jsonify(alerts)
    except Exception:
        print(" [!] Error: {e}")

    return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
