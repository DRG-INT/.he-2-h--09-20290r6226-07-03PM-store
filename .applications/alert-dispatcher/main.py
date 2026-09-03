"""
Alert Dispatcher
Riasztások kiküldése különböző csatornákon (email, Slack, webhook).
"""

import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import requests

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123

class AlertDispatcher:
    """Riasztások kiküldése"""

    def __init__(self, config):
        self.config = config
        self.enabled_channels = config.get('channels', [])

    def check_new_alerts(self) -> list[dict]:
        """Új riasztások lekérdezése ClickHouse-ból"""
        try:
            query = """
            SELECT timestamp, alert_level, panic_probability, events
            FROM kernel_alerts.kernel_alerts
            WHERE timestamp > now() - INTERVAL 5 MINUTE
            ORDER BY timestamp DESC
            LIMIT 100
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
                return alerts
        except Exception as e:
            print(f"[!] Error checking alerts: {e}")

        return []

    def send_email(self, alert: dict):
        """Email küldése"""
        if 'email' not in self.enabled_channels:
            return

        try:
            email_config = self.config['email']

            msg = MIMEText(f"""
            KERNEL PANIC FIGYELMEZETÉS

            Szint: {alert['level']}
            Idő: {alert['timestamp']}
            Valószínűség: {alert['probability']:.2%}

            Események: {alert['events']}

            Ez egy automatikus üzenet a kernel panic figyelő rendszerből.
            """, 'plain', 'utf-8')

            msg['Subject'] = f"[KERNEL ALERT] {alert['level']} - {alert['probability']:.1%}"
            msg['From'] = email_config['from_address']
            msg['To'] = email_config['to_address']

            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)

            print(f"[+] Email alert sent: {alert['level']}")
        except Exception as e:
            print(f"[!] Error sending email: {e}")

    def send_slack(self, alert: dict):
        """Slack üzenet küldése"""
        if 'slack' not in self.enabled_channels:
            return

        try:
            slack_config = self.config['slack']
            webhook_url = slack_config['webhook_url']

            color_map = {
                'CRITICAL': '#FF0000',
                'HIGH': '#FF6600',
                'MEDIUM': '#FFCC00',
                'LOW': '#00FF00'
            }

            payload = {
                "attachments": [{
                    "color": color_map.get(alert['level'], '#CCCCCC'),
                    "title": f"Kernel Panic Alert: {alert['level']}",
                    "text": f"Probability: {alert['probability']:.2%}\nEvents: {alert['events']}",
                    "ts": datetime.now().timestamp()
                }]
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"[+] Slack alert sent: {alert['level']}")
        except Exception:
            print(" [!] Error sending Slack: {e}")

    def send_webhook(self, alert: dict):
        """Webhook hívás"""
        if 'webhook' not in self.enabled_channels:
            return

        try:
            webhook_config = self.config['webhook']
            url = webhook_config['url']

            payload = {
                'alert': alert,
                'timestamp': datetime.now().isoformat(),
                'source': 'kernel_panic_monitor'
            }

            response = requests.post(
                url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code in [200, 201]:
                print(f"[+] Webhook alert sent: {alert['level']}")
        except Exception:
            print(" [!] Error sending webhook: {e}")

    def dispatch(self, alert: dict):
        """Riasztás kiküldése az összes engedélyezett csatornára"""
        self.send_email(alert)
        self.send_slack(alert)
        self.send_webhook(alert)

    def run(self):
        """Folyamatos figyelő ciklus"""
        print("[*] Alert Dispatcher started...")
        print(f"[*] Enabled channels: {', '.join(self.enabled_channels)}")

        import time
        while True:
            try:
                alerts = self.check_new_alerts()

                for alert in alerts:
                    print(f"[!] Dispatching alert: {alert['level']} - {alert['probability']:.1%}")
                    self.dispatch(alert)

                time.sleep(30)  # 30 másodperc várakozás
            except KeyboardInterrupt:
                print("\n[+] Alert Dispatcher stopped")
                break
            except Exception:
                print(" [!] Error in dispatcher loop: {e}")
                time.sleep(30)

def main():
    """Példa konfiguráció"""
    config = {
        'channels': ['email', 'slack', 'webhook'],
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password',
            'from_address': 'kernel-monitor@example.com',
            'to_address': 'admin@example.com'
        },
        'slack': {
            'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        },
        'webhook': {
            'url': 'https://your-webhook-endpoint.com/alerts'
        }
    }

    dispatcher = AlertDispatcher(config)
    dispatcher.run()

if __name__ == "__main__":
    main()
