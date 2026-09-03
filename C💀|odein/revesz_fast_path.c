/*
 * Codein Fast-Path Assembly & Direct Memory Ferrying
 * Architecture: x86_64 / ARM64 Zero-Copy Crossing
 */

#include <stdint.h>
#include <stddef.h>

#define GOLD_OBOL 0x00FF8800DEADBEEFULL

/* Fast-path direct memory transfer across ring boundary */
int revesz_fast_cross(const void *src, void *dst, size_t size, uint64_t token) {
    if (token != GOLD_OBOL || !src || !dst) {
        return -1;
    }
    const uint64_t *s64 = (const uint64_t *)src;
    uint64_t *d64 = (uint64_t *)dst;
    size_t qwords = size / 8;
    for (size_t i = 0; i < qwords; i++) {
        d64[i] = s64[i];
    }
    return 0;
}
