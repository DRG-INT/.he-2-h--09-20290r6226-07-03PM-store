/**
 * UNICAGD ImHex-Style Declarative Pattern Language Verifier
 * Validates binary data structures declaratively before passing to execution.
 */

#include <stdio.h>
#include <string.h>
#include "../include/pattern_language.h"

bool pattern_verify(const binary_pattern_t *pattern, const uint8_t *buf, size_t buf_len, char *out_err, size_t err_size) {
    if (!pattern || !buf) {
        if (out_err) snprintf(out_err, err_size, "Null pointer parameter");
        return false;
    }

    if (buf_len < pattern->total_size) {
        if (out_err) snprintf(out_err, err_size, "Buffer size (%zu) smaller than expected pattern (%zu)",
                              buf_len, pattern->total_size);
        return false;
    }

    for (size_t i = 0; i < pattern->field_count; i++) {
        const pat_field_t *field = &pattern->fields[i];
        if (field->offset + field->length > buf_len) {
            if (out_err) snprintf(out_err, err_size, "Field '%s' exceeds buffer boundary", field->field_name);
            return false;
        }

        if (field->has_expected) {
            uint64_t actual_val = 0;
            switch (field->type) {
                case PAT_TYPE_U8:
                    actual_val = buf[field->offset];
                    break;
                case PAT_TYPE_U16:
                    actual_val = *(const uint16_t *)(buf + field->offset);
                    break;
                case PAT_TYPE_U32:
                    actual_val = *(const uint32_t *)(buf + field->offset);
                    break;
                case PAT_TYPE_U64:
                case PAT_TYPE_MAGIC:
                    actual_val = *(const uint64_t *)(buf + field->offset);
                    break;
                default:
                    break;
            }

            if (actual_val != field->expected_val) {
                if (out_err) snprintf(out_err, err_size, "Field '%s' mismatch: got 0x%llX, expected 0x%llX",
                                      field->field_name, (unsigned long long)actual_val, (unsigned long long)field->expected_val);
                return false;
            }
        }
    }

    if (out_err) snprintf(out_err, err_size, "Pattern '%s' 100%% VALID", pattern->pattern_name);
    return true;
}
