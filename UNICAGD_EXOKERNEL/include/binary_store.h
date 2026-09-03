#ifndef BINARY_STORE_H
#define BINARY_STORE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BSTORE_MAGIC         0x4253544F52453031ULL /* "BSTORE01" */
#define BSTORE_MAX_ENTRIES   256
#define BSTORE_MAX_KEY_LEN   64
#define BSTORE_MAX_BLOB_SIZE 65536

typedef struct {
    char     key[BSTORE_MAX_KEY_LEN];
    uint32_t size;
    uint32_t crc32;
    uint8_t  sha256_hash[32];
    uint8_t  data[BSTORE_MAX_BLOB_SIZE];
    bool     immutable;
    bool     in_use;
} bstore_entry_t;

typedef struct {
    uint64_t magic;
    uint32_t entry_count;
    uint8_t  merkle_root[32];
    bstore_entry_t entries[BSTORE_MAX_ENTRIES];
} binary_store_t;

/* Binary Store API */
int  bstore_init(binary_store_t *store);
int  bstore_put(binary_store_t *store, const char *key, const uint8_t *blob, size_t size);
const uint8_t* bstore_get(const binary_store_t *store, const char *key, size_t *out_size);
bool bstore_verify_integrity(binary_store_t *store);

#ifdef __cplusplus
}
#endif

#endif /* BINARY_STORE_H */
