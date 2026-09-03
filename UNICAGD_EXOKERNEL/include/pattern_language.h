#ifndef PATTERN_LANGUAGE_H
#define PATTERN_LANGUAGE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PAT_TYPE_U8,
    PAT_TYPE_U16,
    PAT_TYPE_U32,
    PAT_TYPE_U64,
    PAT_TYPE_MAGIC,
    PAT_TYPE_BYTES,
    PAT_TYPE_VARIABLE,  /* Variable-length field */
    PAT_TYPE_RANGE,     /* Numeric range check */
    PAT_TYPE_BITFIELD,  /* Bit field within byte */
    PAT_TYPE_CONDITION  /* Conditional validation */
} pat_type_t;

typedef enum {
    PAT_ENDIAN_LITTLE = 0,
    PAT_ENDIAN_BIG = 1,
    PAT_ENDIAN_NATIVE = 2
} pat_endian_t;

typedef struct {
    const char *field_name;
    pat_type_t  type;
    size_t      offset;
    size_t      length;
    uint64_t    expected_val;
    uint64_t    min_val;
    uint64_t    max_val;
    bool        has_expected;
    bool        has_range;
    uint8_t     bit_mask;
    uint8_t     bit_shift;
    pat_endian_t endian;
} pat_field_t;

typedef struct {
    const char  *pattern_name;
    size_t       total_size;
    size_t       field_count;
    uint32_t     flags;
    pat_field_t  fields[32]; /* Increased from 16 */
} binary_pattern_t;

/* Pattern Verifier API */
bool pattern_verify(const binary_pattern_t *pattern, const uint8_t *buffer, size_t buf_len, char *out_err, size_t err_size);
bool pattern_verify_batch(const binary_pattern_t *pattern, const uint8_t *buffer, size_t buf_len, size_t count, size_t stride, char *out_err, size_t err_size);
int  pattern_describe(const binary_pattern_t *pattern, char *buf, size_t buf_size);

/* Helper macros for pattern definition */
#define PATTERN_FIELD_U8(name, offset, expected) {name, PAT_TYPE_U8, offset, 1, expected, 0, 0, true, false, 0, 0, PAT_ENDIAN_NATIVE}
#define PATTERN_FIELD_U16(name, offset, expected) {name, PAT_TYPE_U16, offset, 2, expected, 0, 0, true, false, 0, 0, PAT_ENDIAN_NATIVE}
#define PATTERN_FIELD_U32(name, offset, expected) {name, PAT_TYPE_U32, offset, 4, expected, 0, 0, true, false, 0, 0, PAT_ENDIAN_NATIVE}
#define PATTERN_FIELD_U64(name, offset, expected) {name, PAT_TYPE_U64, offset, 8, expected, 0, 0, true, false, 0, 0, PAT_ENDIAN_NATIVE}
#define PATTERN_FIELD_MAGIC(name, offset, magic) {name, PAT_TYPE_MAGIC, offset, 8, magic, 0, 0, true, false, 0, 0, PAT_ENDIAN_NATIVE}
#define PATTERN_FIELD_RANGE(name, offset, length, min, max) {name, PAT_TYPE_RANGE, offset, length, 0, min, max, false, true, 0, 0, PAT_ENDIAN_NATIVE}
#define PATTERN_FIELD_VAR(name, offset, max_len) {name, PAT_TYPE_VARIABLE, offset, max_len, 0, 0, 0, false, false, 0, 0, PAT_ENDIAN_NATIVE}

#ifdef __cplusplus
}
#endif

#endif /* PATTERN_LANGUAGE_H */
