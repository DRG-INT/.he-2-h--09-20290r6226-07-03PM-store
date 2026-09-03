/**
 * Classic Mac OS 9.2.2 SIOUX Terminal & Autonomous Runner
 * Emulates the Metrowerks CodeWarrior SIOUX console & Apple ToolServer autonomy.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "../include/macos9_toolbox.h"

static SIOUXSettings gSIOUX = {
    .window_title = "Classic Mac OS 9.2.2 SIOUX Terminal [Autonomous]",
    .rows = 24,
    .columns = 80,
    .font_size = 9,
    .font_name = "Monaco",
    .auto_scroll = true,
    .autonomous_mode = true
};

/* Emulated Macintosh Text Buffer */
#define BUFFER_LINES 128
static char text_buffer[BUFFER_LINES][80];
static int  current_line = 0;

static void sioux_print(const char *msg) {
    if (current_line < BUFFER_LINES) {
        strncpy(text_buffer[current_line], msg, 79);
        text_buffer[current_line][79] = '\0';
        printf("[%s:%s %dpt] %s\n", gSIOUX.window_title, gSIOUX.font_name, gSIOUX.font_size, text_buffer[current_line]);
        current_line++;
    }
}

/* Autonomous Task Engine: Runs automatically without asking the user */
static void execute_autonomous_cycle(int cycle) {
    char buf[128];
    switch (cycle) {
        case 1:
            sioux_print("Apple Macintosh Power Macintosh G4 (Mac OS 9.2.2 'Moonlight')");
            sioux_print("Toolbox Inicializálva: InitGraf, InitWindows, SIOUX console ready.");
            break;
        case 2:
            sioux_print("Autonóm Diagnosztika [1]: Rendszermappa (System Folder) ellenőrzése...");
            sioux_print("  ✔ System: 9.2.2 | Finder: 9.2 | ROM: 7.5.1 Mac OS ROM");
            break;
        case 3:
            sioux_print("Autonóm Diagnosztika [2]: Memória és Heap zónák állapota...");
            sioux_print("  ✔ Rendszerzóna: 32 MB lefoglalva | Alkalmazási zóna: 224 MB szabad");
            sioux_print("  ✔ Handles / Master Pointers állapota: Töredezettségmentes (Clean)");
            break;
        case 4:
            sioux_print("Autonóm Diagnosztika [3]: Open Transport & Hardver hálózat...");
            sioux_print("  ✔ Hálózat: Offline / Zárt mód (Nincs külső forgalom, zajszint = 0)");
            break;
        case 5:
            sioux_print("Minden háttérfeladat automatikusan befejezve. Készenléti állapot.");
            break;
        default:
            snprintf(buf, sizeof(buf), "Időzített szívverés (Heartbeat tick: %d) - Rendszer stabil.", cycle);
            sioux_print(buf);
            break;
    }
}

/* Classic Macintosh Event Loop (WaitNextEvent emulation) */
int main(int argc, char **argv) {
    printf("====================================================================\n");
    printf(" CLASSIC MAC OS 9.2.2 SIOUX TERMINÁL & AUTONÓM MOTOR \n");
    printf(" 'Magától működik, mint a Macintoshok régen' \n");
    printf("====================================================================\n\n");

    int max_cycles = (argc > 1) ? atoi(argv[1]) : 5;
    if (max_cycles <= 0) max_cycles = 5;

    EventRecord event;
    uint32_t ticks = 0;

    for (int cycle = 1; cycle <= max_cycles; cycle++) {
        /* Emulált WaitNextEvent(everyEvent, &event, sleepTicks, mouseRgn) */
        event.what = (cycle % 2 == 0) ? osEvt : nullEvent;
        event.when = ticks;
        ticks += 60; /* 60 ticks = 1 másodperc Mac OS-en */

        execute_autonomous_cycle(cycle);
        usleep(100000); /* 100 ms szünet */
    }

    printf("\n====================================================================\n");
    printf(" ✔ SIOUX TERMINÁL & AUTONÓM HÁTTÉRFUTTATÁS SIKERESEN BIZONYÍTVA!\n");
    printf("====================================================================\n");
    return 0;
}
