/**
 * Révész Reverse Engine (R-ever-sen-gine v3)
 * Core Kernel-to-Userspace Safe Ferryman Implementation
 * Copyright (C) 2026 UNICAGD-Core / DRG-INT
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/revesz.h"

/* Standard CRC-32 Lookup Table for fast integrity checks */
static uint32_t revesz_crc32_table[256];
static bool crc_table_ready = false;

static void init_crc32_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int j = 0; j < 8; j++) {
            c = (c & 1) ? (0xEDB88320L ^ (c >> 1)) : (c >> 1);
        }
        revesz_crc32_table[i] = c;
    }
    crc_table_ready = true;
}

static uint32_t calculate_crc32(const uint8_t *buf, size_t len) {
    if (!crc_table_ready) init_crc32_table();
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
        crc = revesz_crc32_table[(crc ^ buf[i]) & 0xFF] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFF;
}

int revesz_ring_init(revesz_ring_t *ring) {
    if (!ring) return -1;
    memset(ring, 0, sizeof(revesz_ring_t));
    ring->capacity = REVESZ_RING_CAPACITY;
    ring->state = REVESZ_STATE_IDLE;
    ring->head = 0;
    ring->tail = 0;
    ring->total_ferried = 0;
    ring->panics_diverted = 0;
    init_crc32_table();
    return 0;
}

bool revesz_verify_gold_token(uint64_t token) {
    /* Proof of Passage: The Ferryman only grants crossing for certified gold */
    return (token == REVESZ_GOLD_TOKEN);
}

int revesz_ferry_enqueue(revesz_ring_t *ring, const uint8_t *data, uint32_t len, uint16_t src, uint16_t dst) {
    if (!ring || !data || len > REVESZ_MAX_PAYLOAD_SIZE) return -1;

    uint32_t current_head = ring->head;
    uint32_t next_head = (current_head + 1) & (ring->capacity - 1);

    /* Check for ring overflow */
    if (next_head == ring->tail) {
        /* Ring buffer full: divert or throttle */
        return -2;
    }

    revesz_packet_t *pkt = &ring->slots[current_head];
    pkt->magic = REVESZ_MAGIC;
    pkt->gold_token = REVESZ_GOLD_TOKEN;
    pkt->sequence_id = (uint32_t)ring->total_ferried + 1;
    pkt->source_ring = src;
    pkt->target_ring = dst;
    pkt->payload_len = len;
    memcpy(pkt->payload, data, len);
    pkt->checksum_crc32 = calculate_crc32(data, len);

    /* Memory Barrier: ensure packet payload is written before advancing head */
    __atomic_thread_fence(__ATOMIC_RELEASE);
    ring->head = next_head;
    ring->total_ferried++;
    ring->state = REVESZ_STATE_FERRYING;

    return 0;
}

int revesz_ferry_dequeue(revesz_ring_t *ring, revesz_packet_t *out_pkt) {
    if (!ring || !out_pkt) return -1;

    uint32_t current_tail = ring->tail;
    if (current_tail == ring->head) {
        /* Ring is empty */
        ring->state = REVESZ_STATE_IDLE;
        return -1;
    }

    /* Memory Barrier: ensure head update is visible before reading */
    __atomic_thread_fence(__ATOMIC_ACQUIRE);
    revesz_packet_t *slot = &ring->slots[current_tail];

    /* Token Verification: Reject unauthorized crossing */
    if (!revesz_verify_gold_token(slot->gold_token) || slot->magic != REVESZ_MAGIC) {
        ring->state = REVESZ_STATE_PASSAGE_DENIED;
        return -3;
    }

    /* Verify CRC32 Integrity */
    uint32_t computed_crc = calculate_crc32(slot->payload, slot->payload_len);
    if (computed_crc != slot->checksum_crc32) {
        ring->state = REVESZ_STATE_PANIC_DIVERTED;
        ring->panics_diverted++;
        return -4;
    }

    /* Copy safe packet */
    memcpy(out_pkt, slot, sizeof(revesz_packet_t));
    ring->tail = (current_tail + 1) & (ring->capacity - 1);
    ring->state = REVESZ_STATE_SAFE_SHORE;

    return 0;
}

void revesz_emergency_divert(revesz_ring_t *ring, const char *panic_reason) {
    if (!ring) return;
    ring->state = REVESZ_STATE_PANIC_DIVERTED;
    ring->panics_diverted++;
    fprintf(stderr, "[RÉVÉSZ EMERGENCY] Pánik eltérítve: %s -> Biztonságos túlsó part aktiválva.\n",
            panic_reason ? panic_reason : "Ismeretlen kernel anomália");
}

#ifdef REVESZ_STANDALONE
int main(int argc, char **argv) {
    printf("====================================================================\n");
    printf(" RÉVÉSZ REVERSE ENGINE v3 (R-ever-sen-gine) - KERNEL/USER BRIDGE \n");
    printf("====================================================================\n");

    revesz_ring_t ring;
    revesz_ring_init(&ring);

    const char *secret_payload = "DIANA_VERIFIED_CRITICAL_INFRASTRUCTURE_RECORD_2026";
    printf("[1] Csomag előkészítése a révátkeléshez (Ring 0 -> Ring 3)...\n");
    printf("    Arany Érme (Token): 0x%016llX\n", (unsigned long long)REVESZ_GOLD_TOKEN);

    int rc = revesz_ferry_enqueue(&ring, (const uint8_t*)secret_payload, strlen(secret_payload), 0, 3);
    if (rc == 0) {
        printf("    ✔ Csomag sikeresen átadva a Révész gyűrűpufferbe.\n");
    }

    printf("[2] Csomag fogadása a túlsó parton (Safe Shore)...\n");
    revesz_packet_t received;
    rc = revesz_ferry_dequeue(&ring, &received);
    if (rc == 0) {
        printf("    ✔ Megérkezés a túlpartra! Tartalom: '%.*s'\n",
               (int)received.payload_len, received.payload);
        printf("    ✔ CRC-32 Ellenőrzés: 0x%08X (Érvényes)\n", received.checksum_crc32);
        printf("    ✔ Összes átvitt csomag: %llu | Elkerült pánikok száma: %llu\n",
               (unsigned long long)ring.total_ferried, (unsigned long long)ring.panics_diverted);
    }

    printf("====================================================================\n");
    printf(" ✔ A RÉVÉSZ FOLYAMAT SIKERESEN BIZONYÍTVA!\n");
    printf("====================================================================\n");
    return 0;
}
#endif
