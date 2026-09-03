"""
Kernel Panic Logger
Kernel események gyűjtése és naplózása.
"""

import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime

import requests

CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
CLICKHOUSE_PORT = int(os.getenv('CLICKHOUSE_PORT', 8123))
CLICKHOUSE_DATABASE = 'kernel_events'

@dataclass
class KernelEvent:
    """Kernel esemény struktúra"""
    timestamp: str
    pid: int
    tid: int
    cpu: int
    event_type: str
    duration_ns: int
    retval: int
    comm: str

class KernelPanicLogger:
    """Kernel események naplózása"""

    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self.event_buffer: list[dict] = []
        self.running = False
        self.stats = {
            'events_logged': 0,
            'events_flushed': 0,
            'errors': 0
        }

    def log_event(self, event: KernelEvent):
        """Egyedi esemény naplózása"""
        try:
            self.event_buffer.append(asdict(event))
            self.stats['events_logged'] += 1

            # Automatikus flush, ha a buffer megtelt
            if len(self.event_buffer) >= self.buffer_size:
                self.flush()
        except Exception as e:
            print(f"[!] Error logging event: {e}")
            self.stats['errors'] += 1

    def log_events(self, events: list[KernelEvent]):
        """Több esemény naplózása"""
        for event in events:
            self.log_event(event)

    def flush(self):
        """Események küldése ClickHouse-ba"""
        if not self.event_buffer:
            return

        try:
            self._insert_events(self.event_buffer)
            self.stats['events_flushed'] += len(self.event_buffer)
            print(f"[+] Flushed {len(self.event_buffer)} events")
            self.event_buffer.clear()
        except Exception as e:
            print(f"[!] Error flushing events: {e}")
            self.stats['errors'] += 1

    def _insert_events(self, events: list[dict]):
        """Események beszúrása ClickHouse-ba"""
        url = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/"

        for event in events:
            query = f"""
            INSERT INTO {CLICKHOUSE_DATABASE}.kernel_events
            (timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm)
            VALUES
            ('{event['timestamp']}', {event['pid']}, {event['tid']}, {event['cpu']},
             '{event['event_type']}', {event['duration_ns']}, {event['retval']}, '{event['comm']}')
            """

            response = requests.post(
                url,
                params={"query": query},
                timeout=10
            )

            if response.status_code != 200:
                raise Exception(f"Insert failed: {response.text}")

    def get_stats(self) -> dict:
        """Statisztikák lekérdezése"""
        return self.stats.copy()

    def get_buffer_size(self) -> int:
        """Buffer méret lekérdezése"""
        return len(self.event_buffer)

    def run(self):
        """Futtatási ciklus"""
        self.running = True
        print("[*] Kernel Panic Logger started")
        print(f"[*] Buffer size: {self.buffer_size}")

        try:
            while self.running:
                time.sleep(1)

                # Rendszeres flush
                if len(self.event_buffer) > 0:
                    self.flush()
        except KeyboardInterrupt:
            print("\n[+] Shutting down...")
            self.flush()

def generate_test_events(count: int = 100) -> list[KernelEvent]:
    """Teszt események generálása"""
    import random

    event_types = [
        'sys_enter_open', 'sys_enter_read', 'sys_enter_write', 'sys_enter_close',
        'do_fork', 'do_exit', 'kmalloc', 'kfree', 'handle_mm_fault'
    ]

    events = []
    for i in range(count):
        event = KernelEvent(
            timestamp=datetime.now().isoformat(),
            pid=random.randint(1, 1000),
            tid=random.randint(1, 10000),
            cpu=random.randint(0, 7),
            event_type=random.choice(event_types),
            duration_ns=random.randint(100, 100000),
            retval=random.choice([0, -1, -2, -12]),
            comm=random.choice(['python', 'chrome', 'firefox', 'kernel', 'systemd'])
        )
        events.append(event)

    return events

def main():
    """Példa futtatás"""
    logger = KernelPanicLogger(buffer_size=1000)

    # Teszt események generálása és naplózása
    print("[*] Generating test events...")
    events = generate_test_events(count=500)
    logger.log_events(events)

    print(f"[*] Logged {len(events)} events")
    print(f"[*] Buffer size: {logger.get_buffer_size()}")

    # Futtatás
    logger.run()

if __name__ == "__main__":
    main()
