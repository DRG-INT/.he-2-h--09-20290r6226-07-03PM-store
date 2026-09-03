#ifndef BINARY_STORE_H
#define BINARY_STORE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BSTORE_MAGIC         0x4253544F52453031ULL /* "BSTORE01" */
#define BSTORE_MAX_ENTRIES   4096  /* Increased from 256 */
#define BSTORE_MAX_KEY_LEN   128   /* Increased from 64 */
#define BSTORE_MAX_BLOB_SIZE (4 * 1024 * 1024) /* 4MB, increased from 64KB */
#define BSTORE_HASH_SIZE     32    /* SHA-256 size */

/* Entry flags */
#define BSTORE_FLAG_IMMUTABLE 0x01
#define BSTORE_FLAG_COMPRESSED 0x02
#define BSTORE_FLAG_ENCRYPTED 0x04
#define BSTORE_FLAG_PINNED    0x08  /* Never evict */

typedef struct {
    char     key[BSTORE_MAX_KEY_LEN];
    uint32_t size;
    uint32_t compressed_size;
    uint32_t flags;
    uint32_t ref_count;
    uint64_t created_at;
    uint64_t accessed_at;
    uint32_t access_count;
    uint8_t  sha256_hash[BSTORE_HASH_SIZE];
    uint8_t  *data;  /* Dynamic allocation for large blobs */
    bool     in_use;
    bool     revoked;      /* Entry has been revoked */
} bstore_entry_t;

typedef struct {
    uint64_t magic;
    uint32_t entry_count;
    uint32_t max_entries;
    uint64_t total_bytes;
    uint64_t total_compressed_bytes;
    uint8_t  merkle_root[BSTORE_HASH_SIZE];
    uint8_t  store_hash[BSTORE_HASH_SIZE];
    bstore_entry_t *entries; /* Dynamic array */
    uint32_t hash_table_size;
    uint32_t *hash_table;    /* O(1) lookup hash table */
} binary_store_t;

/* Binary Store API */
int  bstore_init(binary_store_t *store, uint32_t max_entries);
int  bstore_destroy(binary_store_t *store);
int  bstore_put(binary_store_t *store, const char *key, const uint8_t *blob, size_t size, uint32_t flags);
const uint8_t* bstore_get(binary_store_t *store, const char *key, size_t *out_size);
int  bstore_delete(binary_store_t *store, const char *key);
bool bstore_verify_integrity(binary_store_t *store);
int  bstore_verify_entry(binary_store_t *store, const char *key);
int  bstore_get_stats(const binary_store_t *store, char *buf, size_t buf_size);
int  bstore_evict_lru(binary_store_t *store, uint32_t count);
int  bstore_pin(binary_store_t *store, const char *key);
int  bstore_unpin(binary_store_t *store, const char *key);

/* Hash function type */
typedef uint32_t (*bstore_hash_func_t)(const uint8_t *data, size_t len);

#ifdef __cplusplus
}
#endif

#endif /* BINARY_STORE_H */
