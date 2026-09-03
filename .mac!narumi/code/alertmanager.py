#!/usr/bin/env python3
"""
Alert Manager
ClickHouse backend-rel.
"""

import requests
import smtplib
from email.mime.text import MIMEText
import os
import json
import time
from datetime import datetime

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_DATABASE = "kernel_events"

class AlertManager:
    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        self.email_host = os.getenv('EMAIL_HOST', '')
        self.email_port = int(os.getenv('EMAIL_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_pass = os.getenv('EMAIL_PASS', '')
    
    def send_slack(self, message: dict):
        """Slack riasztás küldése"""
        if not self.slack_webhook:
            return
        
        try:
            payload = {
                "text": f"🚨 *Kernel Anomaly Alert*",
                "attachments": [{
                    "color": "danger",
                    "fields": [
                        {"title": "Level", "value": message['alert_level']},
                        {"title": "Probability", "value": f"{message['panic_probability']:.2%}"},
                        {"title": "Time", "value": message['timestamp']},
                        {"title": "Events", "value": str(message['events'][:5])}
                    ]
                }]
            }
            
            requests.post(self.slack_webhook, json=payload, timeout=5)
        except Exception as e:
            print(f"[!] Slack error: {e}")
    
    def send_email(self, message: dict):
        """Email riasztás küldése"""
        if not self.email_host:
            return
        
        try:
            msg = MIMEText(f"Kernel anomaly detected!\n\n{json.dumps(message, indent=2)}")
            msg['Subject'] = f"🚨 Kernel Alert: {message['alert_level']}"
            msg['From'] = self.email_user
            msg['To'] = self.email_user
            
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
        except Exception as e:
            print(f"[!] Email error: {e}")
    
    def save_to_clickhouse(self, message: dict):
        """Riasztás mentése ClickHouse-ba"""
        try:
            query = f"""
            INSERT INTO kernel_alerts 
            (timestamp, alert_level, panic_probability, events_count, events) 
            VALUES 
            ('{message['timestamp']}', '{message['alert_level']}', {message['panic_probability']}, {len(message['events'])}, '{json.dumps(message['events'])}')
            """
            
            response = requests.post(
                f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/",
                params={"query": query},
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"[!] ClickHouse error: {response.text}")
        except Exception as e:
            print(f"[!] ClickHouse error: {e}")
    
    def process_alert(self, message: dict):
        """Riasztás feldolgozása"""
        print(f"[!] ALERT: {message['alert_level']} - {message['panic_probability']:.2%}")
        
        self.send_slack(message)
        self.send_email(message)
        self.save_to_clickhouse(message)
    
    def run(self):
        """Futtatási ciklus"""
        print("[*] Alert Manager started with ClickHouse...")
        
        while True:
            try:
                # Itt valós időben kellene lekérdezni a ClickHouse-t
                message = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "alert_level": "WARNING",
                    "panic_probability": 0.85,
                    "events": ["sys_enter_open", "sys_enter_read", "kmalloc"]
                }
                
                self.process_alert(message)
                time.sleep(60)
            except Exception as e:
                print(f"[!] Error: {e}")
                time.sleep(60)

def main():
    alert_manager = AlertManager()
    alert_manager.run()

if __name__ == "__main__":
    main()
