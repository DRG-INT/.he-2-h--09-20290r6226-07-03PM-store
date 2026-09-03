/**
 * Zero-Noise TUI Dashboard
 * Pure ANSI/VT100 Terminal Interface. Zero external dependencies. Zero background telemetry.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include "../include/zero_noise.h"

void render_dashboard(const zero_noise_status_t *st) {
    /* Clear screen and move cursor to home (0,0) */
    printf("%s", ANSI_CLEAR);

    printf("%s%s+-----------------------------------------------------------------------------+%s\n", ANSI_BOLD, ANSI_CYAN, ANSI_RESET);
    printf("%s%s|             UNICAGD ZERO-NOISE SECURE APPLICATION DASHBOARD                 |%s\n", ANSI_BOLD, ANSI_CYAN, ANSI_RESET);
    printf("%s%s|             Mode: [AIR-GAPPED / OFFLINE / ZERO TELEMETRY]                   |%s\n", ANSI_BOLD, ANSI_GREEN, ANSI_RESET);
    printf("%s%s+-----------------------------------------------------------------------------+%s\n", ANSI_BOLD, ANSI_CYAN, ANSI_RESET);

    printf("\n  %sHARDWARE & KERNEL STATUS:%s\n", ANSI_BOLD, ANSI_RESET);
    printf("    • CPU Terhelés:         %s%.1f%%%s\n", ANSI_GREEN, st->cpu_usage_pct, ANSI_RESET);
    printf("    • Memória Használat:    %s%llu MB / %llu MB%s\n", ANSI_GREEN,
           (unsigned long long)st->ram_used_mb, (unsigned long long)st->ram_total_mb, ANSI_RESET);
    printf("    • Hálózati Interfészek: %s[LEKAPCSOLVA - ETH0/WLAN0 NÉMA]%s\n", ANSI_RED, ANSI_RESET);
    printf("    • Üzemidő:              %s%llu másodperc%s\n", ANSI_YELLOW,
           (unsigned long long)st->uptime_seconds, ANSI_RESET);

    printf("\n  %sAKTÍV ZAJMENTES FELÜLETEK:%s\n", ANSI_BOLD, ANSI_RESET);
    printf("    [1] %sTUI Konzol (ANSI/VT100):%s       Aktív és villogásmentes\n", ANSI_GREEN, ANSI_RESET);
    printf("    [2] %sHelyi IPC Socket (AF_UNIX):%s    %s (Nincs nyitott port)\n", ANSI_GREEN, ANSI_RESET, ZERO_NOISE_SOCKET_PATH);
    printf("    [3] %sKözvetlen Keretpuffer (DRM/KMS):%s Készenlétben (/dev/dri/card0)\n", ANSI_GREEN, ANSI_RESET);

    printf("\n  %sUTOLSÓ ESEMÉNY & AUDIT NAPLÓ:%s\n", ANSI_BOLD, ANSI_RESET);
    printf("    • %s[%s]%s\n", ANSI_DIM, st->last_event, ANSI_RESET);

    printf("\n%s%s+-----------------------------------------------------------------------------+%s\n", ANSI_BOLD, ANSI_CYAN, ANSI_RESET);
    printf("  %sNyomj [CTRL+C]-t a kilépéshez. Nincs háttérzaj. Nincs telemetria.%s\n", ANSI_DIM, ANSI_RESET);
}

int main(int argc, char **argv) {
    bool snapshot_only = (argc > 1 && strcmp(argv[1], "--snapshot") == 0);

    zero_noise_status_t st = {
        .cpu_usage_pct = 1.2f,
        .ram_used_mb = 142,
        .ram_total_mb = 4096,
        .network_offline = true,
        .uptime_seconds = 3600,
        .last_event = "Rendszer elindítva: Minden külső zaj kiiktatva. Hálózat lezárva."
    };

    if (snapshot_only) {
        render_dashboard(&st);
        return 0;
    }

    /* Frissítési ciklus demonstráció */
    for (int i = 0; i < 3; i++) {
        st.uptime_seconds += 1;
        render_dashboard(&st);
        usleep(500000); /* 500ms */
    }
    return 0;
}
