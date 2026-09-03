CC ?= clang
CFLAGS ?= -std=c99 -Wall -Wextra -O2 -Iinclude

SRCS = src/exokernel_core.c src/binary_store.c src/pattern_language.c src/main.c
OBJS = $(SRCS:.c=.o)
TARGET = bin/exokernel_demo

all: $(TARGET)

$(TARGET): $(SRCS)
	mkdir -p bin
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS)

test: $(TARGET)
	./$(TARGET)

clean:
	rm -rf bin $(OBJS)
