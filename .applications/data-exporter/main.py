"""
Data Exporter
Kernel események exportálása különböző formátumokba (JSON, CSV, Parquet, STIX).
"""

import json
import os
from datetime import datetime, timedelta

import pandas as pd
import requests

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
EXPORT_DIR = "/tmp/kernel_exports"

class DataExporter:
    """Adatok exportálása különböző formátumokba"""

    def __init__(self, config=None):
        self.config = config or {}
        self.export_dir = self.config.get('export_dir', EXPORT_DIR)
        os.makedirs(self.export_dir, exist_ok=True)

    def fetch_events(self,
                     start_time: datetime | None = None,
                     end_time: datetime | None = None,
                     limit: int = 100000) -> pd.DataFrame:
        """Események lekérdezése ClickHouse-ból"""
        if not start_time:
            start_time = datetime.now() - timedelta(days=1)
        if not end_time:
            end_time = datetime.now()

        try:
            query = f"""
            SELECT timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm
            FROM kernel_events.kernel_events
            WHERE timestamp >= '{start_time.isoformat()}'
              AND timestamp <= '{end_time.isoformat()}'
            ORDER BY timestamp ASC
            LIMIT {limit}
            """

            response = requests.post(
                f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
                params={"query": query},
                timeout=60
            )

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                data = []
                for line in lines[1:]:
                    parts = line.split('\t')
                    if len(parts) >= 8:
                        data.append(parts)

                columns = ['timestamp', 'pid', 'tid', 'cpu', 'event_type',
                          'duration_ns', 'retval', 'comm']
                df = pd.DataFrame(data, columns=columns)
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns', errors='coerce')
                df['duration_ns'] = pd.to_numeric(df['duration_ns'], errors='coerce')
                df['pid'] = pd.to_numeric(df['pid'], errors='coerce')
                df['tid'] = pd.to_numeric(df['tid'], errors='coerce')
                df['cpu'] = pd.to_numeric(df['cpu'], errors='coerce')
                df['retval'] = pd.to_numeric(df['retval'], errors='coerce')
                df = df.dropna()
                return df
        except Exception as e:
            print(f"[!] Error fetching events: {e}")

        return pd.DataFrame()

    def fetch_alerts(self,
                     start_time: datetime | None = None,
                     end_time: datetime | None = None,
                     limit: int = 10000) -> pd.DataFrame:
        """Riasztások lekérdezése"""
        if not start_time:
            start_time = datetime.now() - timedelta(days=1)
        if not end_time:
            end_time = datetime.now()

        try:
            query = f"""
            SELECT timestamp, alert_level, panic_probability, events
            FROM kernel_alerts.kernel_alerts
            WHERE timestamp >= '{start_time.isoformat()}'
              AND timestamp <= '{end_time.isoformat()}'
            ORDER BY timestamp DESC
            LIMIT {limit}
            """

            response = requests.post(
                f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
                params={"query": query},
                timeout=60
            )

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                data = []
                for line in lines[1:]:
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        data.append(parts)

                columns = ['timestamp', 'alert_level', 'panic_probability', 'events']
                df = pd.DataFrame(data, columns=columns)
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns', errors='coerce')
                df['panic_probability'] = pd.to_numeric(df['panic_probability'], errors='coerce')
                df = df.dropna()
                return df
        except Exception as e:
            print(f"[!] Error fetching alerts: {e}")

        return pd.DataFrame()

    def export_to_json(self, df: pd.DataFrame, filename: str):
        """Exportálás JSON formátumba"""
        filepath = os.path.join(self.export_dir, f"{filename}.json")
        try:
            df['timestamp'] = df['timestamp'].astype(str)
            records = df.to_dict('records')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            print(f"[+] JSON exported: {filepath}")
        except Exception as e:
            print(f"[!] Error exporting JSON: {e}")

    def export_to_csv(self, df: pd.DataFrame, filename: str):
        """Exportálás CSV formátumba"""
        filepath = os.path.join(self.export_dir, f"{filename}.csv")
        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"[+] CSV exported: {filepath}")
        except Exception as e:
            print(f"[!] Error exporting CSV: {e}")

    def export_to_parquet(self, df: pd.DataFrame, filename: str):
        """Exportálás Parquet formátumba (hatékony tárolás)"""
        filepath = os.path.join(self.export_dir, f"{filename}.parquet")
        try:
            df.to_parquet(filepath, index=False, engine='pyarrow')
            print(f"[+] Parquet exported: {filepath}")
        except Exception as e:
            print(f"[!] Error exporting Parquet: {e}")

    def export_to_stix(self, df: pd.DataFrame, filename: str):
        """Exportálás STIX 2.1 formátumba (fenyegetésfelderítés)"""
        filepath = os.path.join(self.export_dir, f"{filename}_stix.json")
        try:
            stix_bundle = {
                "type": "bundle",
                "id": f"bundle--{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "objects": []
            }

            for _, row in df.iterrows():
                indicator = {
                    "type": "indicator",
                    "id": f"indicator--{hash(str(row)) % 10**16:016x}",
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat(),
                    "pattern": f"[kernel:event_type = '{row.get('event_type', 'unknown')}' AND pid = '{row.get('pid', '0')}']",
                    "pattern_type": "stix",
                    "valid_from": str(row.get('timestamp', datetime.now().isoformat())),
                    "labels": ["kernel-panic-indicator"],
                    "custom_properties": {
                        "kernel_event": {
                            "pid": str(row.get('pid', '')),
                            "tid": str(row.get('tid', '')),
                            "cpu": str(row.get('cpu', '')),
                            "duration_ns": str(row.get('duration_ns', '')),
                            "retval": str(row.get('retval', '')),
                            "comm": str(row.get('comm', ''))
                        }
                    }
                }
                stix_bundle["objects"].append(indicator)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(stix_bundle, f, ensure_ascii=False, indent=2)

            print(f"[+] STIX exported: {filepath}")
        except Exception as e:
            print(f"[!] Error exporting STIX: {e}")

    def export_all(self, days: int = 1):
        """Összes adat exportálása minden formátumba"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        print(f"[*] Exporting data from {start_time} to {end_time}...")

        # Események exportálása
        events_df = self.fetch_events(start_time, end_time)
        if not events_df.empty:
            print(f"[*] Found {len(events_df)} events")
            self.export_to_json(events_df, f"kernel_events_{timestamp}")
            self.export_to_csv(events_df, f"kernel_events_{timestamp}")
            self.export_to_parquet(events_df, f"kernel_events_{timestamp}")

        # Riasztások exportálása
        alerts_df = self.fetch_alerts(start_time, end_time)
        if not alerts_df.empty:
            print(f"[*] Found {len(alerts_df)} alerts")
            self.export_to_json(alerts_df, f"kernel_alerts_{timestamp}")
            self.export_to_csv(alerts_df, f"kernel_alerts_{timestamp}")
            self.export_to_parquet(alerts_df, f"kernel_alerts_{timestamp}")
            self.export_to_stix(alerts_df, f"kernel_alerts_{timestamp}")

        print(f"\n[+] Export completed. Files saved to: {self.export_dir}")

def main():
    exporter = DataExporter()
    exporter.export_all(days=1)

if __name__ == "__main__":
    main()
