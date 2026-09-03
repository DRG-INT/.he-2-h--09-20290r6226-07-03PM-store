CC ?= clang
CFLAGS ?= -std=c99 -Wall -Wextra -O2 -Iinclude

all: bin/macos9_terminal bin/pkg

bin/macos9_terminal: src/macos9_sioux_terminal.c include/macos9_toolbox.h
	mkdir -p bin
	$(CC) $(CFLAGS) -o bin/macos9_terminal src/macos9_sioux_terminal.c

bin/pkg: src/macos9_pkg.c include/macos9_pkg.h
	mkdir -p bin
	$(CC) $(CFLAGS) -o bin/pkg src/macos9_pkg.c

clean:
	rm -rf bin

test: bin/macos9_terminal bin/pkg
	./bin/pkg ports
	./bin/pkg update
	./bin/pkg search Sprocket
	./bin/pkg install DrawSprocket
	./bin/pkg benchmark
