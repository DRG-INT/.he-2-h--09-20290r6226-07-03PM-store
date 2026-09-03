#ifndef ZERO_NOISE_H
#define ZERO_NOISE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define ZERO_NOISE_SOCKET_PATH "/tmp/zero_noise.sock"
#define ZERO_NOISE_VERSION     "1.0.0-silent"

/* ANSI Escape Sequences for Zero-Dependency Terminal Graphics */
#define ANSI_CLEAR        "\033[2J\033[H"
#define ANSI_RESET        "\033[0m"
#define ANSI_BOLD         "\033[1m"
#define ANSI_DIM          "\033[2m"
#define ANSI_GREEN        "\033[32m"
#define ANSI_RED          "\033[31m"
#define ANSI_CYAN         "\033[36m"
#define ANSI_YELLOW       "\033[33m"
#define ANSI_WHITE_BG     "\033[47m\033[30m"

/* Local Zero-Noise IPC Message */
typedef struct {
    uint32_t magic;           /* 0x5A4E4F53 ("ZNOS") */
    uint32_t command_id;      /* 1: STATUS, 2: PURGE_LOGS, 3: SHUTDOWN */
    uint32_t payload_len;
    char     payload[256];
} __attribute__((packed)) zero_noise_ipc_msg_t;

/* System Health Metric State */
typedef struct {
    float    cpu_usage_pct;
    uint64_t ram_used_mb;
    uint64_t ram_total_mb;
    bool     network_offline;
    uint64_t uptime_seconds;
    char     last_event[128];
} zero_noise_status_t;

#ifdef __cplusplus
}
#endif

#endif /* ZERO_NOISE_H */
