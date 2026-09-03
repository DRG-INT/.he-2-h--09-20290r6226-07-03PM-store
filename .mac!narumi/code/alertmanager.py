#!/usr/bin/env python3
"""
Alert Manager
Riasztásokat kezeli és továbbítja.
"""

import requests
import smtplib
from email.mime.text import MIMEText
from influxdb import InfluxDBClient
from datetime import datetime
import os
import json

class AlertManager:
    def __init__(self):
        self.influx_client = InfluxDBClient(
            host=os.getenv('INFLUXDB_HOST', 'localhost'),
            port=int(os.getenv('INFLUXDB_PORT', 8086))
        )
        self.influx_client.switch_database('kernel_events')
        
        # Konfiguráció
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
    
    def save_to_influxdb(self, message: dict):
        """Riasztás mentése InfluxDB-be"""
        try:
            point = {
                "measurement": "kernel_alerts",
                "tags": {
                    "alert_level": message['alert_level']
                },
                "fields": {
                    "panic_probability": message['panic_probability'],
                    "events_count": len(message['events'])
                },
                "time": message['timestamp']
            }
            self.influx_client.write_points([point])
        except Exception as e:
            print(f"[!] InfluxDB error: {e}")
    
    def process_alert(self, message: dict):
        """Riasztás feldolgozása"""
        print(f"[!] ALERT: {message['alert_level']} - {message['panic_probability']:.2%}")
        
        # Továbbítás
        self.send_slack(message)
        self.send_email(message)
        self.save_to_influxdb(message)
    
    def run(self):
        """Futtatási ciklus - egyszerű példa"""
        print("[*] Alert Manager started...")
        
        while True:
            try:
                # Itt valós időben kellene lekérdezni az InfluxDB-t
                # Most csak példa üzenet
                message = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "alert_level": "WARNING",
                    "panic_probability": 0.85,
                    "events": ["sys_enter_open", "sys_enter_read", "kmalloc"]
                }
                
                self.process_alert(message)
                time.sleep(60)  # 1 perc várakozás
            except Exception as e:
                print(f"[!] Error: {e}")
                time.sleep(60)

def main():
    alert_manager = AlertManager()
    alert_manager.run()

if __name__ == "__main__":
    main()
