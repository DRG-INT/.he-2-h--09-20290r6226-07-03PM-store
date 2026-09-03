CC ?= clang
CFLAGS ?= -std=c99 -Wall -Wextra -O2 -Iinclude

all: bin/macos9_terminal

bin/macos9_terminal: src/macos9_sioux_terminal.c include/macos9_toolbox.h
	mkdir -p bin
	$(CC) $(CFLAGS) -o bin/macos9_terminal src/macos9_sioux_terminal.c

clean:
	rm -rf bin

test: bin/macos9_terminal
	./bin/macos9_terminal 5
