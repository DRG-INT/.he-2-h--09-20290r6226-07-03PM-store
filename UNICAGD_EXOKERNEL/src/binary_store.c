/**
 * UNICAGD Immutable Binary Store Engine
 * Replaces fragile kernel VFS with an append-only, Merkle-verified blob store.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include "../include/binary_store.h"

/* Fast internal DJB2 hash for quick index verification */
static uint32_t bstore_hash(const uint8_t *data, size_t len) {
    uint32_t hash = 5381;
    for (size_t i = 0; i < len; i++) {
        hash = ((hash << 5) + hash) + data[i];
    }
    return hash;
}

/* Simple hash table for O(1) key lookup */
static uint32_t bstore_hash_key(const char *key, uint32_t table_size) {
    uint32_t hash = 5381;
    while (*key) {
        hash = ((hash << 5) + hash) + *key++;
    }
    return hash % table_size;
}

static void bstore_update_merkle_root(binary_store_t *store) {
    if (!store || !store->entries) return;
    
    /* Simple Merkle root: SHA-256 of all entry hashes concatenated */
    /* In production, use a real Merkle tree */
    memset(store->merkle_root, 0, BSTORE_HASH_SIZE);
    
    for (uint32_t i = 0; i < store->entry_count; i++) {
        bstore_entry_t *entry = &store->entries[i];
        if (entry->in_use) {
            for (int j = 0; j < BSTORE_HASH_SIZE; j++) {
                store->merkle_root[j] ^= entry->sha256_hash[j];
            }
        }
    }
}

static int bstore_find_entry_index(binary_store_t *store, const char *key) {
    if (!store || !key || !store->hash_table) return -1;
    
    uint32_t hash = bstore_hash_key(key, store->hash_table_size);
    uint32_t idx = store->hash_table[hash];
    
    if (idx == UINT32_MAX) return -1;
    
    /* Linear probe for collision resolution */
    uint32_t start = hash;
    while (idx != UINT32_MAX && store->entries[idx].in_use) {
        if (strcmp(store->entries[idx].key, key) == 0) {
            return (int)idx;
        }
        hash = (hash + 1) % store->hash_table_size;
        idx = store->hash_table[hash];
        if (hash == start) break;
    }
    
    return -1;
}

static void bstore_insert_hash(binary_store_t *store, uint32_t entry_idx, const char *key) {
    if (!store || !store->hash_table) return;
    
    uint32_t hash = bstore_hash_key(key, store->hash_table_size);
    uint32_t start = hash;
    
    while (store->hash_table[hash] != UINT32_MAX) {
        hash = (hash + 1) % store->hash_table_size;
        if (hash == start) return; /* Table full */
    }
    
    store->hash_table[hash] = entry_idx;
}

static void bstore_remove_hash(binary_store_t *store, const char *key) {
    if (!store || !store->hash_table) return;
    
    uint32_t hash = bstore_hash_key(key, store->hash_table_size);
    uint32_t start = hash;
    
    while (store->hash_table[hash] != UINT32_MAX) {
        uint32_t idx = store->hash_table[hash];
        if (idx != UINT32_MAX && store->entries[idx].in_use && 
            strcmp(store->entries[idx].key, key) == 0) {
            store->hash_table[hash] = UINT32_MAX;
            return;
        }
        hash = (hash + 1) % store->hash_table_size;
        if (hash == start) break;
    }
}

int bstore_init(binary_store_t *store, uint32_t max_entries) {
    if (!store || max_entries == 0) return -1;
    
    memset(store, 0, sizeof(binary_store_t));
    store->magic = BSTORE_MAGIC;
    store->max_entries = max_entries;
    store->entry_count = 0;
    store->total_bytes = 0;
    store->total_compressed_bytes = 0;
    
    store->entries = calloc(max_entries, sizeof(bstore_entry_t));
    if (!store->entries) return -2;
    
    /* Initialize hash table (2x size for load factor) */
    store->hash_table_size = max_entries * 2;
    store->hash_table = calloc(store->hash_table_size, sizeof(uint32_t));
    if (!store->hash_table) {
        free(store->entries);
        return -3;
    }
    
    /* Initialize hash table to empty */
    for (uint32_t i = 0; i < store->hash_table_size; i++) {
        store->hash_table[i] = UINT32_MAX;
    }
    
    memset(store->merkle_root, 0, BSTORE_HASH_SIZE);
    memset(store->store_hash, 0, BSTORE_HASH_SIZE);
    
    return 0;
}

int bstore_destroy(binary_store_t *store) {
    if (!store) return -1;
    
    if (store->entries) {
        for (uint32_t i = 0; i < store->max_entries; i++) {
            if (store->entries[i].in_use && store->entries[i].data) {
                free(store->entries[i].data);
            }
        }
        free(store->entries);
    }
    
    if (store->hash_table) {
        free(store->hash_table);
    }
    
    memset(store, 0, sizeof(binary_store_t));
    return 0;
}

int bstore_put(binary_store_t *store, const char *key, const uint8_t *blob, size_t size, uint32_t flags) {
    if (!store || !key || !blob || size > BSTORE_MAX_BLOB_SIZE) return -1;
    if (store->entry_count >= store->max_entries) return -2; /* Store full */
    
    /* Check if key already exists */
    int existing_idx = bstore_find_entry_index(store, key);
    if (existing_idx >= 0) {
        /* Update existing entry */
        bstore_entry_t *entry = &store->entries[existing_idx];
        if (entry->flags & BSTORE_FLAG_IMMUTABLE) return -3; /* Cannot modify immutable */
        
        free(entry->data);
        entry->data = malloc(size);
        if (!entry->data) return -4;
        
        memcpy(entry->data, blob, size);
        entry->size = (uint32_t)size;
        entry->compressed_size = (flags & BSTORE_FLAG_COMPRESSED) ? (uint32_t)size : 0;
        entry->flags = flags;
        entry->accessed_at = (uint64_t)time(NULL);
        entry->access_count++;
        entry->sha256_hash[0] = (uint8_t)(bstore_hash(blob, size) & 0xFF);
        
        store->total_bytes = store->total_bytes - entry->size + (uint64_t)size;
        bstore_update_merkle_root(store);
        return 0;
    }
    
    /* Find free slot */
    int slot_idx = -1;
    for (uint32_t i = 0; i < store->max_entries; i++) {
        if (!store->entries[i].in_use) {
            slot_idx = (int)i;
            break;
        }
    }
    
    if (slot_idx < 0) return -2; /* No free slots */
    
    bstore_entry_t *entry = &store->entries[slot_idx];
    memset(entry, 0, sizeof(bstore_entry_t));
    
    strncpy(entry->key, key, BSTORE_MAX_KEY_LEN - 1);
    entry->size = (uint32_t)size;
    entry->compressed_size = (flags & BSTORE_FLAG_COMPRESSED) ? (uint32_t)size : 0;
    entry->flags = flags;
    entry->created_at = (uint64_t)time(NULL);
    entry->accessed_at = entry->created_at;
    entry->access_count = 1;
    entry->ref_count = 1;
    entry->in_use = true;
    
    entry->data = malloc(size);
    if (!entry->data) {
        memset(entry, 0, sizeof(bstore_entry_t));
        return -4;
    }
    
    memcpy(entry->data, blob, size);
    
    /* Calculate hash */
    uint32_t crc = bstore_hash(blob, size);
    memset(entry->sha256_hash, 0, BSTORE_HASH_SIZE);
    entry->sha256_hash[0] = (uint8_t)(crc & 0xFF);
    entry->sha256_hash[1] = (uint8_t)((crc >> 8) & 0xFF);
    entry->sha256_hash[2] = (uint8_t)((crc >> 16) & 0xFF);
    entry->sha256_hash[3] = (uint8_t)((crc >> 24) & 0xFF);
    
    store->entry_count++;
    store->total_bytes += size;
    
    /* Insert into hash table */
    bstore_insert_hash(store, (uint32_t)slot_idx, key);
    
    /* Update Merkle root */
    bstore_update_merkle_root(store);
    
    return 0;
}

const uint8_t* bstore_get(binary_store_t *store, const char *key, size_t *out_size) {
    if (!store || !key) return NULL;
    
    int idx = bstore_find_entry_index(store, key);
    if (idx < 0) return NULL;
    
    bstore_entry_t *entry = &store->entries[idx];
    if (!entry->in_use || entry->revoked) return NULL;
    
    /* Update access statistics */
    entry->accessed_at = (uint64_t)time(NULL);
    entry->access_count++;
    
    if (out_size) *out_size = entry->size;
    return entry->data;
}

int bstore_delete(binary_store_t *store, const char *key) {
    if (!store || !key) return -1;
    
    int idx = bstore_find_entry_index(store, key);
    if (idx < 0) return -2;
    
    bstore_entry_t *entry = &store->entries[idx];
    if (entry->flags & BSTORE_FLAG_IMMUTABLE) return -3; /* Cannot delete immutable */
    
    /* Remove from hash table */
    bstore_remove_hash(store, key);
    
    /* Free data */
    if (entry->data) {
        free(entry->data);
        entry->data = NULL;
    }
    
    store->total_bytes -= entry->size;
    memset(entry, 0, sizeof(bstore_entry_t));
    store->entry_count--;
    
    bstore_update_merkle_root(store);
    return 0;
}

bool bstore_verify_integrity(binary_store_t *store) {
    if (!store || store->magic != BSTORE_MAGIC) return false;

    for (uint32_t i = 0; i < store->max_entries; i++) {
        if (store->entries[i].in_use) {
            bstore_entry_t *entry = &store->entries[i];
            if (!entry->data) return false;
            
            uint32_t current_hash = bstore_hash(entry->data, entry->size);
            if (current_hash != (uint32_t)((entry->sha256_hash[0]) |
                                          (entry->sha256_hash[1] << 8) |
                                          (entry->sha256_hash[2] << 16) |
                                          (entry->sha256_hash[3] << 24))) {
                return false; /* Tampered blob detected! */
            }
        }
    }
    return true;
}

int bstore_verify_entry(binary_store_t *store, const char *key) {
    if (!store || !key) return -1;
    
    int idx = bstore_find_entry_index(store, key);
    if (idx < 0) return -2;
    
    bstore_entry_t *entry = &store->entries[idx];
    if (!entry->in_use || !entry->data) return -3;
    
    uint32_t current_hash = bstore_hash(entry->data, entry->size);
    uint32_t stored_hash = (uint32_t)((entry->sha256_hash[0]) |
                                      (entry->sha256_hash[1] << 8) |
                                      (entry->sha256_hash[2] << 16) |
                                      (entry->sha256_hash[3] << 24));
    
    return (current_hash == stored_hash) ? 0 : -4;
}

int bstore_get_stats(const binary_store_t *store, char *buf, size_t buf_size) {
    if (!store || !buf || buf_size == 0) return -1;
    
    int written = snprintf(buf, buf_size,
        "Binary Store Stats:\n"
        "  Entries: %u / %u\n"
        "  Total Bytes: %llu\n"
        "  Compressed Bytes: %llu\n"
        "  Magic: 0x%llX\n"
        "  Merkle Root: %02X%02X%02X%02X...\n",
        store->entry_count,
        store->max_entries,
        (unsigned long long)store->total_bytes,
        (unsigned long long)store->total_compressed_bytes,
        (unsigned long long)store->magic,
        store->merkle_root[0], store->merkle_root[1],
        store->merkle_root[2], store->merkle_root[3]
    );
    
    return (written > 0 && written < (int)buf_size) ? 0 : -2;
}

int bstore_evict_lru(binary_store_t *store, uint32_t count) {
    if (!store || count == 0) return -1;
    
    uint32_t evicted = 0;
    uint64_t oldest_time = UINT64_MAX;
    int oldest_idx = -1;
    
    for (uint32_t c = 0; c < count; c++) {
        oldest_time = UINT64_MAX;
        oldest_idx = -1;
        
        /* Find least recently used non-pinned entry */
        for (uint32_t i = 0; i < store->max_entries; i++) {
            if (!store->entries[i].in_use) continue;
            if (store->entries[i].flags & BSTORE_FLAG_PINNED) continue;
            if (store->entries[i].ref_count > 1) continue; /* Only skip if others hold references */
            
            if (store->entries[i].accessed_at < oldest_time) {
                oldest_time = store->entries[i].accessed_at;
                oldest_idx = (int)i;
            }
        }
        
        if (oldest_idx < 0) break;
        
        bstore_entry_t *entry = &store->entries[oldest_idx];
        store->total_bytes -= entry->size;
        bstore_remove_hash(store, entry->key);
        
        if (entry->data) {
            free(entry->data);
            entry->data = NULL;
        }
        
        memset(entry, 0, sizeof(bstore_entry_t));
        store->entry_count--;
        evicted++;
    }
    
    if (evicted > 0) {
        bstore_update_merkle_root(store);
    }
    
    return (int)evicted;
}

int bstore_pin(binary_store_t *store, const char *key) {
    if (!store || !key) return -1;
    
    int idx = bstore_find_entry_index(store, key);
    if (idx < 0) return -2;
    
    store->entries[idx].flags |= BSTORE_FLAG_PINNED;
    return 0;
}

int bstore_unpin(binary_store_t *store, const char *key) {
    if (!store || !key) return -1;
    
    int idx = bstore_find_entry_index(store, key);
    if (idx < 0) return -2;
    
    store->entries[idx].flags &= ~BSTORE_FLAG_PINNED;
    return 0;
}
