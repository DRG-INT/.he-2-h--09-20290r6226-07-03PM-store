#ifndef UNICAGD_EXOKERNEL_H
#define UNICAGD_EXOKERNEL_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EXO_MAGIC             0x554E494341474401ULL /* "UNICAGD\1" */
#define EXO_MAX_PAGES         4096
#define EXO_PAGE_SIZE         4096
#define EXO_MAX_DRIVERS       16
#define EXO_MAX_CAPABILITIES  64
#define EXO_MAX_PROCESSES     1024
#define EXO_MAX_SYSCALLS      3

/* Exokernel Syscall Primitives: STRICTLY 3 SYSCALLS ONLY */
typedef enum {
    EXO_SYS_YIELD    = 1,  /* Voluntarily surrender CPU timeslice */
    EXO_SYS_MAP_PAGE = 2,  /* Grant physical hardware page to capability holder */
    EXO_SYS_ROUTE_IRQ= 3   /* Route hardware interrupt directly to user-space thread */
} exo_syscall_t;

/* Capability Token for Hardware Access */
typedef struct {
    uint64_t cap_id;
    uint32_t permissions; /* 1: Read, 2: Write, 4: Execute, 8: MMIO */
    uint64_t phys_addr;
    uint32_t size;
    uint32_t ref_count;    /* Reference counting for safe deallocation */
    uint32_t owner_pid;    /* Owning process */
    uint64_t created_at;   /* Tick when capability was created */
    bool     valid;
    bool     revoked;      /* Capability has been revoked */
} exo_capability_t;

/* Process Control Block */
typedef struct {
    uint32_t pid;
    uint32_t parent_pid;
    uint64_t start_time;
    uint64_t cpu_time;
    uint32_t capability_count;
    uint32_t max_capabilities;
    exo_capability_t *capabilities; /* Dynamic capability array */
    bool     alive;
    char     comm[64];
} exo_process_t;

/* Exokernel Core State */
typedef struct {
    uint64_t magic;
    uint32_t active_processes;
    uint32_t max_processes;
    exo_process_t *processes; /* Dynamic process table */
    uint64_t uptime_ticks;
    uint64_t total_syscalls;
    uint64_t fault_count;
    uint64_t recovered_crashes;
    uint64_t capability_allocations;
    uint64_t capability_deallocations;
    exo_capability_t capabilities[EXO_MAX_CAPABILITIES]; /* Static fast-path table */
    uint32_t next_cap_id;
    uint32_t next_pid;
    uint32_t syscall_counts[EXO_MAX_SYSCALLS + 1];
} exokernel_state_t;

/* Core Exokernel Functions */
int  exo_init(exokernel_state_t *kernel);
int  exo_yield(exokernel_state_t *kernel);
int  exo_map_page(exokernel_state_t *kernel, uint64_t cap_id, uint64_t phys_addr, uint32_t perms);
int  exo_route_irq(exokernel_state_t *kernel, uint32_t irq_num, void (*user_irq_handler)(int));
void exo_handle_user_fault(exokernel_state_t *kernel, uint32_t pid, const char *reason);

/* Enhanced API */
int  exo_create_process(exokernel_state_t *kernel, const char *name, uint32_t *out_pid);
int  exo_terminate_process(exokernel_state_t *kernel, uint32_t pid);
int  exo_acquire_capability(exokernel_state_t *kernel, uint32_t pid, uint64_t phys_addr, uint32_t perms, uint64_t *out_cap_id);
int  exo_release_capability(exokernel_state_t *kernel, uint32_t pid, uint64_t cap_id);
int  exo_revoke_capability(exokernel_state_t *kernel, uint64_t cap_id);
exo_capability_t* exo_find_capability(exokernel_state_t *kernel, uint64_t cap_id);
int  exo_get_kernel_stats(const exokernel_state_t *kernel, char *buf, size_t buf_size);

#ifdef __cplusplus
}
#endif

#endif /* UNICAGD_EXOKERNEL_H */
