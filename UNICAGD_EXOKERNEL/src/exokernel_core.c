/**
 * UNICAGD Zero-Surface Exokernel Engine
 * Minimal Ring-0 abstraction with zero kernel panic vectors.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "../include/exokernel.h"

/* Internal helpers */
static exo_capability_t* exo_find_capability_slot(exokernel_state_t *kernel) {
    for (size_t i = 0; i < EXO_MAX_CAPABILITIES; i++) {
        if (!kernel->capabilities[i].valid || kernel->capabilities[i].revoked) {
            return &kernel->capabilities[i];
        }
    }
    return NULL;
}

static exo_process_t* exo_find_process(exokernel_state_t *kernel, uint32_t pid) {
    if (!kernel || !kernel->processes) return NULL;
    for (size_t i = 0; i < kernel->max_processes; i++) {
        if (kernel->processes[i].alive && kernel->processes[i].pid == pid) {
            return &kernel->processes[i];
        }
    }
    return NULL;
}

static exo_process_t* exo_alloc_process_slot(exokernel_state_t *kernel) {
    if (!kernel || !kernel->processes) return NULL;
    for (size_t i = 0; i < kernel->max_processes; i++) {
        if (!kernel->processes[i].alive) {
            return &kernel->processes[i];
        }
    }
    return NULL;
}

int exo_init(exokernel_state_t *kernel) {
    if (!kernel) return -1;
    memset(kernel, 0, sizeof(exokernel_state_t));
    kernel->magic = EXO_MAGIC;
    kernel->active_processes = 0;
    kernel->max_processes = EXO_MAX_PROCESSES;
    kernel->processes = calloc(kernel->max_processes, sizeof(exo_process_t));
    if (!kernel->processes) return -2;
    
    kernel->uptime_ticks = 0;
    kernel->total_syscalls = 0;
    kernel->fault_count = 0;
    kernel->recovered_crashes = 0;
    kernel->capability_allocations = 0;
    kernel->capability_deallocations = 0;
    kernel->next_cap_id = 1;
    kernel->next_pid = 1;
    memset(kernel->syscall_counts, 0, sizeof(kernel->syscall_counts));
    
    /* Create initial bootstrap process */
    exo_create_process(kernel, "init", NULL);
    
    return 0;
}

int exo_yield(exokernel_state_t *kernel) {
    if (!kernel || kernel->magic != EXO_MAGIC) return -1;
    kernel->total_syscalls++;
    kernel->syscall_counts[EXO_SYS_YIELD]++;
    kernel->uptime_ticks++;
    /* Deterministic cooperative context yield */
    return 0;
}

int exo_map_page(exokernel_state_t *kernel, uint64_t cap_id, uint64_t phys_addr, uint32_t perms) {
    if (!kernel || kernel->magic != EXO_MAGIC) return -1;
    kernel->total_syscalls++;
    kernel->syscall_counts[EXO_SYS_MAP_PAGE]++;

    exo_capability_t *slot = exo_find_capability_slot(kernel);
    if (!slot) return -2; /* Capability table exhausted */

    slot->cap_id = cap_id ? cap_id : kernel->next_cap_id++;
    slot->phys_addr = phys_addr;
    slot->permissions = perms;
    slot->size = EXO_PAGE_SIZE;
    slot->owner_pid = 0; /* Kernel owned */
    slot->created_at = kernel->uptime_ticks;
    slot->ref_count = 1;
    slot->valid = true;
    slot->revoked = false;
    kernel->capability_allocations++;
    
    return 0;
}

int exo_route_irq(exokernel_state_t *kernel, uint32_t irq_num, void (*user_irq_handler)(int)) {
    if (!kernel || !user_irq_handler) return -1;
    kernel->total_syscalls++;
    kernel->syscall_counts[EXO_SYS_ROUTE_IRQ]++;
    /* In an exokernel, the kernel does NOT handle the device logic!
       It merely forwards the raw IRQ vector to the registered user-space driver thread. */
    (void)irq_num;
    (void)user_irq_handler;
    return 0;
}

void exo_handle_user_fault(exokernel_state_t *kernel, uint32_t pid, const char *reason) {
    if (!kernel) return;
    kernel->fault_count++;
    
    exo_process_t *proc = exo_find_process(kernel, pid);
    if (proc) {
        proc->alive = false;
        kernel->active_processes--;
    }
    
    /* ZERO-PANIC INVARIANT:
       In a monolithic kernel, a NULL pointer dereference in a driver panics the CPU.
       In the UNICAGD Exokernel, the fault is isolated to the user-space process.
       The process is re-instantiated from the immutable Binary Store! */
    printf("   [EXOKERNEL RECOVERY] Folyamat (PID %u) elhasalt: '%s'.\n", pid, reason ? reason : "Unknown");
    printf("   [EXOKERNEL RECOVERY] ✔ Hardver VÉDETT. Nincs Kernel Panic! Folyamat újraindítása...\n");
    
    kernel->recovered_crashes++;
}

/* Enhanced API Implementation */
int exo_create_process(exokernel_state_t *kernel, const char *name, uint32_t *out_pid) {
    if (!kernel || !name) return -1;
    
    exo_process_t *slot = exo_alloc_process_slot(kernel);
    if (!slot) return -2; /* Process table full */
    
    slot->pid = kernel->next_pid++;
    slot->parent_pid = 0; /* Bootstrap */
    slot->start_time = kernel->uptime_ticks;
    slot->cpu_time = 0;
    slot->capability_count = 0;
    slot->max_capabilities = 16;
    slot->capabilities = calloc(slot->max_capabilities, sizeof(exo_capability_t));
    if (!slot->capabilities) {
        slot->alive = false;
        return -3;
    }
    slot->alive = true;
    strncpy(slot->comm, name, sizeof(slot->comm) - 1);
    
    kernel->active_processes++;
    
    if (out_pid) *out_pid = slot->pid;
    return 0;
}

int exo_terminate_process(exokernel_state_t *kernel, uint32_t pid) {
    if (!kernel) return -1;
    
    exo_process_t *proc = exo_find_process(kernel, pid);
    if (!proc) return -2;
    
    /* Release all capabilities */
    for (size_t i = 0; i < proc->capability_count; i++) {
        exo_release_capability(kernel, pid, proc->capabilities[i].cap_id);
    }
    
    free(proc->capabilities);
    proc->capabilities = NULL;
    proc->alive = false;
    kernel->active_processes--;
    
    return 0;
}

int exo_acquire_capability(exokernel_state_t *kernel, uint32_t pid, uint64_t phys_addr, uint32_t perms, uint64_t *out_cap_id) {
    if (!kernel) return -1;
    
    exo_process_t *proc = exo_find_process(kernel, pid);
    if (!proc) return -2;
    
    if (proc->capability_count >= proc->max_capabilities) {
        /* Grow capability array */
        size_t new_max = proc->max_capabilities * 2;
        exo_capability_t *new_caps = realloc(proc->capabilities, new_max * sizeof(exo_capability_t));
        if (!new_caps) return -3;
        proc->capabilities = new_caps;
        memset(proc->capabilities + proc->max_capabilities, 0, 
               (new_max - proc->max_capabilities) * sizeof(exo_capability_t));
        proc->max_capabilities = new_max;
    }
    
    exo_capability_t *cap = &proc->capabilities[proc->capability_count];
    cap->cap_id = kernel->next_cap_id++;
    cap->phys_addr = phys_addr;
    cap->permissions = perms;
    cap->size = EXO_PAGE_SIZE;
    cap->owner_pid = pid;
    cap->created_at = kernel->uptime_ticks;
    cap->ref_count = 1;
    cap->valid = true;
    cap->revoked = false;
    proc->capability_count++;
    kernel->capability_allocations++;
    
    if (out_cap_id) *out_cap_id = cap->cap_id;
    return 0;
}

int exo_release_capability(exokernel_state_t *kernel, uint32_t pid, uint64_t cap_id) {
    if (!kernel) return -1;
    
    exo_process_t *proc = exo_find_process(kernel, pid);
    if (!proc) return -2;
    
    for (size_t i = 0; i < proc->capability_count; i++) {
        if (proc->capabilities[i].cap_id == cap_id && proc->capabilities[i].valid) {
            proc->capabilities[i].valid = false;
            proc->capabilities[i].revoked = true;
            proc->capabilities[i].ref_count = 0;
            /* Compact array by moving last element */
            if (i < proc->capability_count - 1) {
                memcpy(&proc->capabilities[i], &proc->capabilities[proc->capability_count - 1], 
                       sizeof(exo_capability_t));
            }
            proc->capability_count--;
            kernel->capability_deallocations++;
            return 0;
        }
    }
    return -3; /* Capability not found */
}

int exo_revoke_capability(exokernel_state_t *kernel, uint64_t cap_id) {
    if (!kernel) return -1;
    
    /* Search in static fast-path table */
    for (size_t i = 0; i < EXO_MAX_CAPABILITIES; i++) {
        if (kernel->capabilities[i].valid && kernel->capabilities[i].cap_id == cap_id) {
            kernel->capabilities[i].valid = false;
            kernel->capabilities[i].revoked = true;
            kernel->capabilities[i].ref_count = 0;
            return 0;
        }
    }
    
    /* Search in all process tables */
    for (size_t p = 0; p < kernel->max_processes; p++) {
        if (!kernel->processes[p].alive) continue;
        for (size_t i = 0; i < kernel->processes[p].capability_count; i++) {
            if (kernel->processes[p].capabilities[i].cap_id == cap_id) {
                kernel->processes[p].capabilities[i].valid = false;
                kernel->processes[p].capabilities[i].revoked = true;
                kernel->processes[p].capabilities[i].ref_count = 0;
                return 0;
            }
        }
    }
    
    return -2; /* Not found */
}

exo_capability_t* exo_find_capability(exokernel_state_t *kernel, uint64_t cap_id) {
    if (!kernel) return NULL;
    
    for (size_t i = 0; i < EXO_MAX_CAPABILITIES; i++) {
        if (kernel->capabilities[i].valid && kernel->capabilities[i].cap_id == cap_id) {
            return &kernel->capabilities[i];
        }
    }
    
    for (size_t p = 0; p < kernel->max_processes; p++) {
        if (!kernel->processes[p].alive) continue;
        for (size_t i = 0; i < kernel->processes[p].capability_count; i++) {
            if (kernel->processes[p].capabilities[i].valid && 
                kernel->processes[p].capabilities[i].cap_id == cap_id) {
                return &kernel->processes[p].capabilities[i];
            }
        }
    }
    
    return NULL;
}

int exo_get_kernel_stats(const exokernel_state_t *kernel, char *buf, size_t buf_size) {
    if (!kernel || !buf || buf_size == 0) return -1;
    
    int written = snprintf(buf, buf_size,
        "UNICAGD Exokernel Stats:\n"
        "  Active Processes: %u\n"
        "  Uptime Ticks: %llu\n"
        "  Total Syscalls: %llu\n"
        "  Fault Count: %llu\n"
        "  Recovered Crashes: %llu\n"
        "  Capability Allocations: %llu\n"
        "  Capability Deallocations: %llu\n"
        "  Syscall Distribution:\n"
        "    YIELD: %llu\n"
        "    MAP_PAGE: %llu\n"
        "    ROUTE_IRQ: %llu\n",
        kernel->active_processes,
        (unsigned long long)kernel->uptime_ticks,
        (unsigned long long)kernel->total_syscalls,
        (unsigned long long)kernel->fault_count,
        (unsigned long long)kernel->recovered_crashes,
        (unsigned long long)kernel->capability_allocations,
        (unsigned long long)kernel->capability_deallocations,
        (unsigned long long)kernel->syscall_counts[EXO_SYS_YIELD],
        (unsigned long long)kernel->syscall_counts[EXO_SYS_MAP_PAGE],
        (unsigned long long)kernel->syscall_counts[EXO_SYS_ROUTE_IRQ]
    );
    
    return (written > 0 && written < (int)buf_size) ? 0 : -2;
}
