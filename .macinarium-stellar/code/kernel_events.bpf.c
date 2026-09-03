#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/dcache.h>
#include <linux/fs.h>

#ifndef CPU_MAX
#define CPU_MAX 128
#endif

#ifndef PID_MAX
#define PID_MAX 4194304
#endif

/* Esemény típusok */
enum event_type {
    EVENT_SYSCALL = 0,
    EVENT_PROCESS_FORK,
    EVENT_PROCESS_EXIT,
    EVENT_KMALLOC,
    EVENT_KFREE,
    EVENT_PAGE_FAULT,
    EVENT_IRQ,
    EVENT_NETWORK,
    EVENT_COUNT
};

/* Esemény struktúra */
struct event_t {
    u64 ts;                  /* időbélyeg (ns) */
    u32 pid;                 /* processz azonosító */
    u32 tid;                 /* szál azonosító */
    u32 cpu;                 /* CPU azonosító */
    u32 event_type;          /* esemény típus */
    u64 duration_ns;         /* esemény időtartam (ns) */
    s64 retval;              /* visszatérési érték */
    char comm[16];           /* processz név */
    char filename[256];      /* fájl név */
    u32 size;                /* méret */
    u32 gfp_flags;           /* GFP flags */
};

/* Perf buffer események kiküldésére */
BPF_PERF_OUTPUT(events);

/* Hash map a syscall kezdeti időpontjainak tárolására */
BPF_HASH(start, u64, u64);

/* Hash map a processz információk tárolására */
BPF_HASH(proc_info, u32, struct proc_info_t);

struct proc_info_t {
    u32 pid;
    u32 ppid;
    char comm[16];
    u64 start_time;
};

/* Syscall belépés kezelő */
int trace_sys_enter(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    u64 ts = bpf_ktime_get_ns();
    
    /* Kezdeti időpont tárolása */
    start.update(&pid, &ts);
    
    return 0;
}

/* Syscall kilépés kezelő */
int trace_sys_exit(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    u64 *tsp = start.lookup(&pid);
    if (!tsp) return 0;
    
    u64 duration = bpf_ktime_get_ns() - *tsp;
    start.delete(&pid);
    
    /* Esemény összeállítása */
    struct event_t evt = {};
    evt.pid = pid >> 32;
    evt.tid = pid & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.duration_ns = duration;
    evt.retval = PT_REGS_RC(ctx);
    evt.event_type = EVENT_SYSCALL;
    
    /* Processz név lekérdezése */
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    /* Syscall szám lekérdezése */
    u32 syscall_nr = PT_REGS_SYSCALL_NR(ctx);
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}

/* Processz fork kezelő */
int trace_process_fork(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = bpf_get_current_pid_tgid() >> 32;
    evt.tid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_PROCESS_FORK;
    
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}

/* Processz exit kezelő */
int trace_process_exit(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = bpf_get_current_pid_tgid() >> 32;
    evt.tid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_PROCESS_EXIT;
    
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}

/* kmalloc kezelő */
int trace_kmalloc(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = bpf_get_current_pid_tgid() >> 32;
    evt.tid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_KMALLOC;
    evt.size = PT_REGS_PARM1(ctx);
    evt.gfp_flags = PT_REGS_PARM2(ctx);
    
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}

/* kfree kezelő */
int trace_kfree(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = bpf_get_current_pid_tgid() >> 32;
    evt.tid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_KFREE;
    
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}

/* Page fault kezelő */
int trace_page_fault(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = bpf_get_current_pid_tgid() >> 32;
    evt.tid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_PAGE_FAULT;
    
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}

/* IRQ kezelő */
int trace_irq_handler(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = 0;
    evt.tid = 0;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_IRQ;
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}

/* Network socket kezelő */
int trace_socket(struct pt_regs *ctx) {
    struct event_t evt = {};
    evt.pid = bpf_get_current_pid_tgid() >> 32;
    evt.tid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;
    evt.cpu = bpf_get_smp_processor_id();
    evt.ts = bpf_ktime_get_ns();
    evt.event_type = EVENT_NETWORK;
    
    bpf_get_current_comm(&evt.comm, sizeof(evt.comm));
    
    events.perf_submit(ctx, &evt, sizeof(evt));
    return 0;
}
