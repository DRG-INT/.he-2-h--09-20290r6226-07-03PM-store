"""
Kernel Event Streamer
Kernel események streamelése ClickHouse adatbázisba.
"""

import os
import threading
import time
from datetime import datetime
from queue import Empty, Queue

import requests

CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
CLICKHOUSE_PORT = int(os.getenv('CLICKHOUSE_PORT', 8123))
CLICKHOUSE_DATABASE = 'kernel_events'

class KernelEventStreamer:
    """Kernel események streamelése ClickHouse-ba"""

    def __init__(self, batch_size: int = 1000, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.event_queue = Queue()
        self.running = False
        self.stats = {
            'events_received': 0,
            'events_flushed': 0,
            'errors': 0
        }

    def start(self):
        """Streamer indítása"""
        self.running = True

        # Flush thread indítása
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()

        print("[*] Kernel Event Streamer started")
        print(f"[*] Batch size: {self.batch_size}")
        print(f"[*] Flush interval: {self.flush_interval}s")

    def stop(self):
        """Streamer leállítása"""
        self.running = False
        if hasattr(self, 'flush_thread'):
            self.flush_thread.join(timeout=5)
        print("[+] Kernel Event Streamer stopped")

    def ingest_event(self, event: dict):
        """Egyedi esemény befogadása"""
        try:
            self.event_queue.put(event, block=False)
            self.stats['events_received'] += 1
        except Exception as e:
            print(f"[!] Error ingesting event: {e}")
            self.stats['errors'] += 1

    def ingest_events(self, events: list[dict]):
        """Több esemény befogadása"""
        for event in events:
            self.ingest_event(event)

    def _flush_loop(self):
        """Automatikus flush ciklus"""
        last_flush = time.time()

        while self.running:
            try:
                current_time = time.time()

                # Ellenőrzés: van-e elég esemény vagy eltelt idő
                if (self.event_queue.qsize() >= self.batch_size or
                    current_time - last_flush >= self.flush_interval):

                    self._flush()
                    last_flush = current_time

                time.sleep(0.1)
            except Exception as e:
                print(f"[!] Error in flush loop: {e}")
                time.sleep(1)

    def _flush(self):
        """Események küldése ClickHouse-ba"""
        events = []

        # Események kiolvasása a sorából
        while len(events) < self.batch_size:
            try:
                event = self.event_queue.get(block=False)
                events.append(event)
            except Empty:
                break

        if not events:
            return

        # Adatok formázása
        rows = []
        for event in events:
            row = self._format_event(event)
            rows.append(row)

        # ClickHouse-be küldés
        try:
            self._insert_events(rows)
            self.stats['events_flushed'] += len(rows)
            print(f"[+] Flushed {len(rows)} events to ClickHouse")
        except Exception as e:
            print(f"[!] Error flushing events: {e}")
            self.stats['errors'] += 1

    def _format_event(self, event: dict) -> str:
        """Esemény formázása ClickHouse sorba"""
        timestamp = event.get('timestamp', datetime.now().isoformat())
        pid = event.get('pid', 0)
        tid = event.get('tid', 0)
        cpu = event.get('cpu', 0)
        event_type = event.get('event_type', 'unknown')
        duration_ns = event.get('duration_ns', 0)
        retval = event.get('retval', 0)
        comm = event.get('comm', 'unknown')

        # Tab-separated format for ClickHouse
        return f"{timestamp}\t{pid}\t{tid}\t{cpu}\t{event_type}\t{duration_ns}\t{retval}\t{comm}"

    def _insert_events(self, rows: list[str]):
        """Események beszúrása ClickHouse-ba"""
        query = f"INSERT INTO {CLICKHOUSE_DATABASE}.kernel_events \
            (timestamp, pid, tid, cpu, event_type, duration_ns, retval, comm) VALUES"

        data = []
        for row in rows:
            parts = row.split('\t')
            if len(parts) >= 8:
                data.append(parts)

        if not data:
            return

        # HTTP API-n keresztül beszúrás
        url = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/"

        # Formázott adat
        values_str = ""
        for parts in data:
            values_str += f"('{parts[0]}', {parts[1]}, {parts[2]}, {parts[3]}, '{parts[4]}', {parts[5]}, {parts[6]}, '{parts[7]}'),\n"
        values_str = values_str.rstrip(',\n')

        full_query = f"{query}\n{values_str}"

        response = requests.post(
            url,
            params={"query": full_query},
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"ClickHouse insert failed: {response.text}")

    def get_stats(self) -> dict:
        """Statisztikák lekérdezése"""
        return self.stats.copy()

    def run(self):
        """Futtatás ciklus"""
        self.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[+] Shutting down...")
            self.stop()

def main():
    """Példa futtatás"""
    streamer = KernelEventStreamer(
        batch_size=1000,
        flush_interval=5.0
    )

    # Teszt események generálása
    import random

    event_types = [
        'sys_enter_open', 'sys_enter_read', 'sys_enter_write', 'sys_enter_close',
        'do_fork', 'do_exit', 'kmalloc', 'kfree', 'handle_mm_fault'
    ]

    print("[*] Generating test events...")
    for i in range(100):
        event = {
            'timestamp': datetime.now().isoformat(),
            'pid': random.randint(1, 1000),
            'tid': random.randint(1, 10000),
            'cpu': random.randint(0, 7),
            'event_type': random.choice(event_types),
            'duration_ns': random.randint(100, 100000),
            'retval': random.choice([0, -1, -2, -12]),
            'comm': random.choice(['python', 'chrome', 'firefox', 'kernel', 'systemd'])
        }
        streamer.ingest_event(event)

    print("[*] Starting streamer...")
    streamer.run()

if __name__ == "__main__":
    main()
