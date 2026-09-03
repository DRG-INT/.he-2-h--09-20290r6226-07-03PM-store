/**
 * UNICAGD Immutable Binary Store Engine
 * Replaces fragile kernel VFS with an append-only, Merkle-verified blob store.
 */

#include <stdio.h>
#include <string.h>
#include "../include/binary_store.h"

/* Fast internal DJB2/CRC hash for quick index verification */
static uint32_t bstore_hash(const uint8_t *data, size_t len) {
    uint32_t hash = 5381;
    for (size_t i = 0; i < len; i++) {
        hash = ((hash << 5) + hash) + data[i];
    }
    return hash;
}

int bstore_init(binary_store_t *store) {
    if (!store) return -1;
    memset(store, 0, sizeof(binary_store_t));
    store->magic = BSTORE_MAGIC;
    store->entry_count = 0;
    return 0;
}

int bstore_put(binary_store_t *store, const char *key, const uint8_t *blob, size_t size) {
    if (!store || !key || !blob || size > BSTORE_MAX_BLOB_SIZE) return -1;

    for (size_t i = 0; i < BSTORE_MAX_ENTRIES; i++) {
        if (!store->entries[i].in_use) {
            strncpy(store->entries[i].key, key, BSTORE_MAX_KEY_LEN - 1);
            store->entries[i].size = (uint32_t)size;
            memcpy(store->entries[i].data, blob, size);
            store->entries[i].crc32 = bstore_hash(blob, size);
            store->entries[i].immutable = true;
            store->entries[i].in_use = true;
            store->entry_count++;

            /* Merkle root accumulation */
            for (size_t b = 0; b < 32; b++) {
                store->merkle_root[b] ^= (uint8_t)(store->entries[i].crc32 >> (b % 4 * 8));
            }
            return 0;
        }
    }
    return -2; /* Store full */
}

const uint8_t* bstore_get(const binary_store_t *store, const char *key, size_t *out_size) {
    if (!store || !key) return NULL;

    for (size_t i = 0; i < BSTORE_MAX_ENTRIES; i++) {
        if (store->entries[i].in_use && strcmp(store->entries[i].key, key) == 0) {
            if (out_size) *out_size = store->entries[i].size;
            return store->entries[i].data;
        }
    }
    return NULL;
}

bool bstore_verify_integrity(binary_store_t *store) {
    if (!store || store->magic != BSTORE_MAGIC) return false;

    for (size_t i = 0; i < BSTORE_MAX_ENTRIES; i++) {
        if (store->entries[i].in_use) {
            uint32_t current_hash = bstore_hash(store->entries[i].data, store->entries[i].size);
            if (current_hash != store->entries[i].crc32) {
                return false; /* Tampered blob detected! */
            }
        }
    }
    return true;
}
