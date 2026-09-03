CC ?= clang
CFLAGS ?= -std=c99 -Wall -Wextra -O2 -Iinclude

all: bin/tui_dashboard bin/ipc_controller

bin/tui_dashboard: src/tui_dashboard.c include/zero_noise.h
	mkdir -p bin
	$(CC) $(CFLAGS) -o bin/tui_dashboard src/tui_dashboard.c

bin/ipc_controller: src/ipc_controller.c include/zero_noise.h
	mkdir -p bin
	$(CC) $(CFLAGS) -o bin/ipc_controller src/ipc_controller.c

clean:
	rm -rf bin

test: bin/tui_dashboard bin/ipc_controller
	./bin/tui_dashboard --snapshot
	./bin/ipc_controller TEST_SILENT_MODE
