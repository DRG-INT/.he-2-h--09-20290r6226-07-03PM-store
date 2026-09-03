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
    bool     valid;
} exo_capability_t;

/* Exokernel Core State */
typedef struct {
    uint64_t magic;
    uint32_t active_processes;
    uint64_t uptime_ticks;
    uint64_t total_syscalls;
    uint64_t fault_count;
    uint64_t recovered_crashes;
    exo_capability_t capabilities[EXO_MAX_CAPABILITIES];
} exokernel_state_t;

/* Core Exokernel Functions */
int  exo_init(exokernel_state_t *kernel);
int  exo_yield(exokernel_state_t *kernel);
int  exo_map_page(exokernel_state_t *kernel, uint64_t cap_id, uint64_t phys_addr, uint32_t perms);
int  exo_route_irq(exokernel_state_t *kernel, uint32_t irq_num, void (*user_irq_handler)(int));
void exo_handle_user_fault(exokernel_state_t *kernel, uint32_t pid, const char *reason);

#ifdef __cplusplus
}
#endif

#endif /* UNICAGD_EXOKERNEL_H */
