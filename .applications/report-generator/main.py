"""
Report Generator
Automatikus jelentések készítése a kernel eseményekről és anomáliákról.
"""

from datetime import datetime, timedelta

import requests
from jinja2 import Template

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DATABASE = "kernel_events"

class ReportGenerator:
    """Jelentések készítése"""

    def __init__(self):
        self.reports_dir = "reports"
        import os
        os.makedirs(self.reports_dir, exist_ok=True)

    def fetch_daily_stats(self, date=None):
        """Napi statisztikák lekérdezése"""
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        try:
            # Események száma
            query = f"""
            SELECT
                toDate(timestamp) as date,
                count() as total_events,
                countDistinct(pid) as unique_processes,
                avg(duration_ns) as avg_duration,
                max(duration_ns) as max_duration
            FROM kernel_events.kernel_events
            WHERE date = '{date_str}'
            GROUP BY date
            """

            response = requests.post(
                f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
                params={"query": query},
                timeout=30
            )

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split('\t')
                    return {
                        'date': date_str,
                        'total_events': int(parts[1]) if len(parts) > 1 else 0,
                        'unique_processes': int(parts[2]) if len(parts) > 2 else 0,
                        'avg_duration': float(parts[3]) if len(parts) > 3 else 0,
                        'max_duration': float(parts[4]) if len(parts) > 4 else 0
                    }
        except Exception as e:
            print(f"[!] Error fetching daily stats: {e}")

        return {
            'date': date_str,
            'total_events': 0,
            'unique_processes': 0,
            'avg_duration': 0,
            'max_duration': 0
        }

    def fetch_anomalies(self, date=None, limit=100):
        """Anomáliák lekérdezése"""
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        try:
            query = f"""
            SELECT timestamp, alert_level, panic_probability, events_count, events
            FROM kernel_alerts.kernel_alerts
            WHERE date = '{date_str}'
            ORDER BY timestamp DESC
            LIMIT {limit}
            """

            response = requests.post(
                f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
                params={"query": query},
                timeout=30
            )

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                anomalies = []
                for line in lines[1:]:
                    parts = line.split('\t')
                    if len(parts) >= 5:
                        anomalies.append({
                            'timestamp': parts[0],
                            'alert_level': parts[1],
                            'panic_probability': float(parts[2]),
                            'events_count': int(parts[3]),
                            'events': parts[4]
                        })
                return anomalies
        except Exception as e:
            print(f"[!] Error fetching anomalies: {e}")

        return []

    def fetch_event_distribution(self, date=None):
        """Esemény típusok eloszlása"""
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        try:
            query = f"""
            SELECT event_type, count() as count
            FROM kernel_events.kernel_events
            WHERE date = '{date_str}'
            GROUP BY event_type
            ORDER BY count DESC
            """

            response = requests.post(
                f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
                params={"query": query},
                timeout=30
            )

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                distribution = []
                for line in lines[1:]:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        distribution.append({
                            'event_type': parts[0],
                            'count': int(parts[1])
                        })
                return distribution
        except Exception as e:
            print(f"[!] Error fetching event distribution: {e}")

        return []

    def generate_daily_report(self, date=None):
        """Napi jelentés generálása"""
        if date is None:
            date = datetime.now()

        # Adatok lekérdezése
        stats = self.fetch_daily_stats(date)
        anomalies = self.fetch_anomalies(date)
        distribution = self.fetch_event_distribution(date)

        # HTML sablon
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Kernel-LSTM Daily Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .stat-box {
            display: inline-block;
            padding: 20px;
            margin: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }
        .stat-number { font-size: 24px; font-weight: bold; color: #0066cc; }
        .stat-label { color: #666; }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th { background: #f2f2f2; }
        .alert-critical { color: #cc0000; font-weight: bold; }
        .alert-warning { color: #cc9900; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Kernel-LSTM Daily Report</h1>
    <p>Report date: {{ date }}</p>

    <h2>Statistics</h2>
    <div class="stat-box">
        <div class="stat-number">{{ total_events }}</div>
        <div class="stat-label">Total Events</div>
    </div>
    <div class="stat-box">
        <div class="stat-number">{{ unique_processes }}</div>
        <div class="stat-label">Unique Processes</div>
    </div>
    <div class="stat-box">
        <div class="stat-number">{{ avg_duration|round(2) }}</div>
        <div class="stat-label">Avg Duration (ns)</div>
    </div>
    <div class="stat-box">
        <div class="stat-number">{{ max_duration|round(2) }}</div>
        <div class="stat-label">Max Duration (ns)</div>
    </div>

    <h2>Event Distribution</h2>
    <table>
        <tr>
            <th>Event Type</th>
            <th>Count</th>
        </tr>
        {% for event in distribution %}
        <tr>
            <td>{{ event.event_type }}</td>
            <td>{{ event.count }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>Anomalies</h2>
    {% if anomalies %}
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Level</th>
            <th>Probability</th>
            <th>Events</th>
        </tr>
        {% for anomaly in anomalies %}
        <tr>
            <td>{{ anomaly.timestamp }}</td>
            <td class="alert-{{ anomaly.alert_level|lower }}">
                {{ anomaly.alert_level }}
            </td>
            <td>{{ "%.2f"|format(anomaly.panic_probability * 100) }}%</td>
            <td>{{ anomaly.events[:50] }}...</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
    <p>No anomalies detected.</p>
    {% endif %}

    <hr>
    <p><small>Generated by Kernel-LSTM Report Generator</small></p>
</body>
</html>
        """

        # HTML generálása
        template = Template(html_template)
        html_content = template.render(
            date=stats['date'],
            total_events=stats['total_events'],
            unique_processes=stats['unique_processes'],
            avg_duration=stats['avg_duration'],
            max_duration=stats['max_duration'],
            distribution=distribution,
            anomalies=anomalies
        )

        # Fájl mentése
        filename = f"{self.reports_dir}/daily_report_{date.strftime('%Y%m%d')}.html"
        with open(filename, 'w') as f:
            f.write(html_content)

        print(f"[+] Daily report generated: {filename}")
        return filename

    def generate_weekly_report(self):
        """Heti jelentés generálása"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Adatok lekérdezése
        all_stats = []
        all_anomalies = []
        all_distribution = []

        for i in range(7):
            date = start_date + timedelta(days=i)
            stats = self.fetch_daily_stats(date)
            anomalies = self.fetch_anomalies(date)
            distribution = self.fetch_event_distribution(date)

            all_stats.append(stats)
            all_anomalies.extend(anomalies)
            all_distribution.append(distribution)

        # Összesítés
        total_events = sum(s['total_events'] for s in all_stats)
        total_anomalies = len(all_anomalies)

        # HTML generálása
        rows_html = ""
        for stat in all_stats:
            rows_html += f"""
        <tr>
            <td>{stat['date']}</td>
            <td>{stat['total_events']:,}</td>
            <td>{stat['unique_processes']:,}</td>
        </tr>"""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Kernel-LSTM Weekly Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .stat-box {{
            display: inline-block;
            padding: 20px;
            margin: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        .stat-label {{ color: #666; }}
    </style>
</head>
<body>
    <h1>Kernel-LSTM Weekly Report</h1>
    <p>Period: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}</p>

    <div class="stat-box">
        <div class="stat-number">{total_events:,}</div>
        <div class="stat-label">Total Events (7 days)</div>
    </div>
    <div class="stat-box">
        <div class="stat-number">{total_anomalies}</div>
        <div class="stat-label">Total Anomalies</div>
    </div>

    <h2>Daily Breakdown</h2>
    <table>
        <tr>
            <th>Date</th>
            <th>Events</th>
            <th>Processes</th>
        </tr>
        {rows_html}
    </table>

    <hr>
    <p><small>Generated by Kernel-LSTM Report Generator</small></p>
</body>
</html>
        """

        filename = f"{self.reports_dir}/weekly_report_{end_date.strftime('%Y%m%d')}.html"
        with open(filename, 'w') as f:
            f.write(html)

        print(f"[+] Weekly report generated: {filename}")
        return filename

def main():
    """Példa használat"""
    generator = ReportGenerator()

    # Napi jelentés
    generator.generate_daily_report()

    # Heti jelentés
    generator.generate_weekly_report()

if __name__ == "__main__":
    main()
