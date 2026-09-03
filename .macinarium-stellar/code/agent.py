#!/usr/bin/env python3
"""
Kernel-LSTM eBPF Collector Agent
Gyűjti a kernel eseményeket eBPF segítségével és továbbítja az InfluxDB-be.
"""

import time
import json
import signal
import sys
from bcc import BPF
from influxdb import InfluxDBClient
from datetime import datetime

# Konfiguráció
INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = "kernel_events"
BUFFER_SIZE = 1048576
POLL_INTERVAL_MS = 10

# eBPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct event_t {
    u64 ts;
    u32 pid;
    u32 tid;
    u32 cpu;
    u32 event_type;
    u64 duration_ns;
    s64 retval;
    char comm[16];
};

BPF_PERF_OUTPUT(events);
BPF_HASH(start, u64, u64);

int trace_sys_enter(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    u64 ts = bpf_ktime_get_ns();
    start.update(&pid, &ts);
    return 0;
}

int trace_sys_exit(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    u64 *tsp = start.lookup(&pid);
    if (!tsp) return 0;
    u64 duration = bpf_ktime_get_ns() - *tsp;
    start.delete(&pid);
    
    struct event_t evt = {};
    evt.pid = pid >> 32;
    evt.tid = pid & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.duration_ns = duration;
    evt.retval = PT_REGS_RC(ctx);
    evt.event_type = 0;
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}
"""

class KernelLSTMAgent:
    def __init__(self):
        self.b = BPF(text=bpf_text)
        self.client = InfluxDBClient(
            host=INFLUXDB_HOST,
            port=INFLUXDB_PORT
        )
        self.client.switch_database(INFLUXDB_DATABASE)
        self.running = True
        
        # Signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"[!] Signal {signum} received, shutting down...")
        self.running = False
        sys.exit(0)
    
    def handle_event(self, cpu, data, size):
        try:
            event = self.b["events"].event(data)
            
            point = {
                "measurement": "kernel_events",
                "tags": {
                    "pid": str(event.pid),
                    "tid": str(event.tid),
                    "cpu": str(event.cpu),
                    "comm": event.comm.decode('utf-8', 'replace')
                },
                "fields": {
                    "ts": event.ts,
                    "duration_ns": event.duration_ns,
                    "retval": event.retval,
                    "event_type": event.event_type
                }
            }
            
            self.client.write_points([point])
        except Exception as e:
            print(f"[!] Error handling event: {e}")
    
    def attach_probes(self):
        """eBPF probe-ok hozzáfűzése"""
        try:
            self.b.attach_kprobe(event="sys_enter", fn_name="trace_sys_enter")
            self.b.attach_kprobe(event="sys_exit", fn_name="trace_sys_exit")
            print("[+] eBPF probes attached successfully")
        except Exception as e:
            print(f"[!] Failed to attach probes: {e}")
            sys.exit(1)
    
    def run(self):
        """Futtatási ciklus"""
        print(f"[*] Starting Kernel-LSTM Agent...")
        print(f"[*] InfluxDB: {INFLUXDB_HOST}:{INFLUXDB_PORT}")
        print(f"[*] Database: {INFLUXDB_DATABASE}")
        
        self.attach_probes()
        
        # Perf buffer nyitása
        self.b["events"].open_perf_buffer(self.handle_event)
        
        print("[*] Agent running, collecting events...")
        
        while self.running:
            try:
                self.b.perf_buffer_poll(timeout=POLL_INTERVAL_MS)
            except KeyboardInterrupt:
                print("\n[!] Interrupted by user")
                break
            except Exception as e:
                print(f"[!] Error: {e}")
                time.sleep(1)
        
        print("[*] Agent stopped")

def main():
    agent = KernelLSTMAgent()
    agent.run()

if __name__ == "__main__":
    main()
