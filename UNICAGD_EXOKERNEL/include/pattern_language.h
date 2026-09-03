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
    PAT_TYPE_BYTES
} pat_type_t;

typedef struct {
    const char *field_name;
    pat_type_t  type;
    size_t      offset;
    size_t      length;
    uint64_t    expected_val; /* For MAGIC or constants */
    bool        has_expected;
} pat_field_t;

typedef struct {
    const char  *pattern_name;
    size_t       total_size;
    size_t       field_count;
    pat_field_t  fields[16];
} binary_pattern_t;

/* Pattern Verifier API */
bool pattern_verify(const binary_pattern_t *pattern, const uint8_t *buffer, size_t buf_len, char *out_err, size_t err_size);

#ifdef __cplusplus
}
#endif

#endif /* PATTERN_LANGUAGE_H */
