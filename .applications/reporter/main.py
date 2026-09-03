"""
Reporting Tool
Automatikus jelentések generálása a kernel eseményekről és anomáliákról.
"""

import os
from datetime import datetime, timedelta

import pandas as pd
import requests

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
REPORT_DIR = "/tmp/kernel_reports"

class ReportGenerator:
    """Jelentések generálása"""

    def __init__(self):
        self.report_dir = REPORT_DIR
        os.makedirs(self.report_dir, exist_ok=True)

    def fetch_events(self,
                     start_time: datetime | None = None,
                     end_time: datetime | None = None,
                     limit: int = 100000) -> pd.DataFrame:
        """Események lekérdezése"""
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

    def generate_summary_report(self, days: int = 1) -> str:
        """Összefoglaló jelentés generálása"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        events_df = self.fetch_events(start_time, end_time)
        alerts_df = self.fetch_alerts(start_time, end_time)

        report = []
        report.append("=" * 70)
        report.append("KERNEL PANIC ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"Period: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Event Summary
        report.append("-" * 70)
        report.append("EVENT SUMMARY")
        report.append("-" * 70)
        report.append(f"Total Events: {len(events_df):,}")

        if not events_df.empty:
            report.append(f"Unique Processes: {events_df['pid'].nunique():,}")
            report.append(f"Unique Event Types: {events_df['event_type'].nunique():,}")
            report.append(f"Average Duration: {events_df['duration_ns'].mean():.2f} ns")
            report.append(f"Max Duration: {events_df['duration_ns'].max():.2f} ns")
            report.append(f"Min Duration: {events_df['duration_ns'].min():.2f} ns")
            report.append("")

            # Top processes
            report.append("Top 10 Processes by Event Count:")
            top_processes = events_df['pid'].value_counts().head(10)
            for pid, count in top_processes.items():
                report.append(f"  PID {pid}: {count:,} events")
            report.append("")

            # Event type distribution
            report.append("Event Type Distribution (Top 10):")
            event_types = events_df['event_type'].value_counts().head(10)
            for event_type, count in event_types.items():
                report.append(f"  {event_type}: {count:,}")
            report.append("")

        # Alert Summary
        report.append("-" * 70)
        report.append("ALERT SUMMARY")
        report.append("-" * 70)
        report.append(f"Total Alerts: {len(alerts_df):,}")

        if not alerts_df.empty:
            report.append(f"Average Panic Probability: {alerts_df['panic_probability'].mean():.2%}")
            report.append(f"Max Panic Probability: {alerts_df['panic_probability'].max():.2%}")
            report.append("")

            # Alert level distribution
            report.append("Alert Level Distribution:")
            alert_levels = alerts_df['alert_level'].value_counts()
            for level, count in alert_levels.items():
                report.append(f"  {level}: {count:,}")
            report.append("")

            # Recent critical alerts
            critical_alerts = alerts_df[alerts_df['alert_level'] == 'CRITICAL'].head(10)
            if not critical_alerts.empty:
                report.append("Recent Critical Alerts:")
                for _, alert in critical_alerts.iterrows():
                    report.append(f"  [{alert['timestamp']}] Probability: {alert['panic_probability']:.2%} - {alert['events']}")
            report.append("")

        # Recommendations
        report.append("-" * 70)
        report.append("RECOMMENDATIONS")
        report.append("-" * 70)

        if not alerts_df.empty and len(alerts_df) > 0:
            critical_count = len(alerts_df[alerts_df['alert_level'] == 'CRITICAL'])
            if critical_count > 0:
                report.append(f"[!] {critical_count} CRITICAL alerts detected. Immediate investigation recommended.")

            high_count = len(alerts_df[alerts_df['alert_level'] == 'HIGH'])
            if high_count > 0:
                report.append(f"[!] {high_count} HIGH severity alerts detected. Review recommended within 24 hours.")

        if not events_df.empty:
            suspicious_procs = events_df[events_df['duration_ns'] > events_df['duration_ns'].quantile(0.99)]
            if len(suspicious_procs) > 0:
                report.append(f"[i] {len(suspicious_procs)} events with unusually high duration detected.")

        report.append("")
        report.append("=" * 70)
        report.append("END OF REPORT")
        report.append("=" * 70)

        return "\n".join(report)

    def save_report(self, report_text: str, filename: str | None = None) -> str:
        """Jelentés mentése fájlba"""
        if not filename:
            filename = f"kernel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        filepath = os.path.join(self.report_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"[+] Report saved to: {filepath}")
        return filepath

    def generate_and_save(self, days: int = 1) -> str:
        """Jelentés generálása és mentése"""
        print(f"[*] Generating report for last {days} day(s)...")
        report = self.generate_summary_report(days)
        filepath = self.save_report(report)
        return filepath

    def print_report(self, days: int = 1):
        """Jelentés megjelenítése konzolon"""
        report = self.generate_summary_report(days)
        print(report)

def main():
    reporter = ReportGenerator()
    reporter.print_report(days=1)

if __name__ == "__main__":
    main()
