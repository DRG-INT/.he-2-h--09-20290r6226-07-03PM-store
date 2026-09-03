CC ?= clang
CFLAGS ?= -std=c99 -Wall -Wextra -O2 -Iinclude

all: bin/revesz_cli

bin/revesz_cli: src/revesz_core.c include/revesz.h
	mkdir -p bin
	$(CC) $(CFLAGS) -DREVESZ_STANDALONE -o bin/revesz_cli src/revesz_core.c

clean:
	rm -rf bin

test: bin/revesz_cli
	./bin/revesz_cli
