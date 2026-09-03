#ifndef REVESZ_CORE_H
#define REVESZ_CORE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Magic Identification: 'R', 'E', 'V', 'E', 'S', 'Z', 0x00, 0x03 */
#define REVESZ_MAGIC            0x52455645535A0003ULL

/* A Révész Aranya: Ferryman's Gold Obol (Cryptographic Verification Token) */
#define REVESZ_GOLD_TOKEN       0x00FF8800DEADBEEFULL

/* Crossing Ring Buffer Configuration */
#define REVESZ_RING_CAPACITY    1024
#define REVESZ_MAX_PAYLOAD_SIZE 4096

/* State Machine Across the Boundary */
typedef enum {
    REVESZ_STATE_IDLE            = 0x00,
    REVESZ_STATE_PASSAGE_REQUEST = 0x01,
    REVESZ_STATE_FERRYING        = 0x02,
    REVESZ_STATE_SAFE_SHORE      = 0x03,
    REVESZ_STATE_PANIC_DIVERTED  = 0x04,
    REVESZ_STATE_PASSAGE_DENIED  = 0xFF
} revesz_state_t;

/* Single Crossing Packet Definition */
typedef struct {
    uint64_t magic;              /* REVESZ_MAGIC */
    uint64_t gold_token;         /* Ferryman Token (Proof of Clearance) */
    uint32_t sequence_id;        /* Monotonically increasing counter */
    uint16_t source_ring;        /* Privilege Ring (0: Kernel, 3: Userspace) */
    uint16_t target_ring;        /* Target Privilege Ring */
    uint32_t payload_len;        /* Data length */
    uint8_t  payload[REVESZ_MAX_PAYLOAD_SIZE];
    uint32_t checksum_crc32;     /* Data integrity checksum */
} __attribute__((packed)) revesz_packet_t;

/* Lockless Single-Producer Single-Consumer (SPSC) Ferryman Ring */
typedef struct {
    volatile uint32_t head;      /* Producer pointer (Write) */
    volatile uint32_t tail;      /* Consumer pointer (Read) */
    uint32_t capacity;           /* Must be power of 2 */
    revesz_state_t state;        /* Active crossing state */
    uint64_t total_ferried;      /* Statistics: total packets passed */
    uint64_t panics_diverted;    /* Statistics: fatal panics avoided */
    revesz_packet_t slots[REVESZ_RING_CAPACITY];
} revesz_ring_t;

/* Public Engine API */
int  revesz_ring_init(revesz_ring_t *ring);
bool revesz_verify_gold_token(uint64_t token);
int  revesz_ferry_enqueue(revesz_ring_t *ring, const uint8_t *data, uint32_t len, uint16_t src, uint16_t dst);
int  revesz_ferry_dequeue(revesz_ring_t *ring, revesz_packet_t *out_pkt);
void revesz_emergency_divert(revesz_ring_t *ring, const char *panic_reason);

#ifdef __cplusplus
}
#endif

#endif /* REVESZ_CORE_H */
