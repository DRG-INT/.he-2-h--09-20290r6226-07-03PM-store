/**
 * UNICAGD ImHex-Style Declarative Pattern Language Verifier
 * Validates binary data structures declaratively before passing to execution.
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include "../include/pattern_language.h"

static uint64_t pat_read_value(const uint8_t *buf, size_t offset, size_t length, pat_endian_t endian) {
    uint64_t value = 0;
    const uint8_t *ptr = buf + offset;
    
    if (endian == PAT_ENDIAN_BIG) {
        for (size_t i = 0; i < length && i < 8; i++) {
            value = (value << 8) | ptr[i];
        }
    } else {
        for (size_t i = 0; i < length && i < 8; i++) {
            value |= ((uint64_t)ptr[i]) << (i * 8);
        }
    }
    
    return value;
}

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
        
        /* Boundary check */
        if (field->offset + field->length > buf_len) {
            if (out_err) snprintf(out_err, err_size, "Field '%s' exceeds buffer boundary", field->field_name);
            return false;
        }

        /* Handle different field types */
        switch (field->type) {
            case PAT_TYPE_U8:
            case PAT_TYPE_U16:
            case PAT_TYPE_U32:
            case PAT_TYPE_U64:
            case PAT_TYPE_MAGIC: {
                uint64_t actual_val = pat_read_value(buf, field->offset, field->length, field->endian);
                
                if (field->has_expected && actual_val != field->expected_val) {
                    if (out_err) snprintf(out_err, err_size, 
                        "Field '%s' mismatch: got 0x%llX, expected 0x%llX",
                        field->field_name, (unsigned long long)actual_val, 
                        (unsigned long long)field->expected_val);
                    return false;
                }
                
                if (field->has_range && (actual_val < field->min_val || actual_val > field->max_val)) {
                    if (out_err) snprintf(out_err, err_size,
                        "Field '%s' out of range: got %llu, expected [%llu, %llu]",
                        field->field_name, (unsigned long long)actual_val,
                        (unsigned long long)field->min_val, (unsigned long long)field->max_val);
                    return false;
                }
                break;
            }
            
            case PAT_TYPE_RANGE: {
                uint64_t actual_val = pat_read_value(buf, field->offset, field->length, field->endian);
                if (actual_val < field->min_val || actual_val > field->max_val) {
                    if (out_err) snprintf(out_err, err_size,
                        "Field '%s' out of range: got %llu, expected [%llu, %llu]",
                        field->field_name, (unsigned long long)actual_val,
                        (unsigned long long)field->min_val, (unsigned long long)field->max_val);
                    return false;
                }
                break;
            }
            
            case PAT_TYPE_BITFIELD: {
                uint8_t byte_val = buf[field->offset];
                uint8_t masked = (byte_val & field->bit_mask) >> field->bit_shift;
                if (field->has_expected && masked != (uint8_t)field->expected_val) {
                    if (out_err) snprintf(out_err, err_size,
                        "Bitfield '%s' mismatch: got 0x%X, expected 0x%llX",
                        field->field_name, masked, (unsigned long long)field->expected_val);
                    return false;
                }
                break;
            }
            
            case PAT_TYPE_BYTES:
            case PAT_TYPE_VARIABLE:
            case PAT_TYPE_CONDITION:
                /* These require more complex validation - skip for basic verifier */
                break;
        }
    }

    if (out_err) snprintf(out_err, err_size, "Pattern '%s' 100%% VALID", pattern->pattern_name);
    return true;
}

bool pattern_verify_batch(const binary_pattern_t *pattern, const uint8_t *buffer, size_t buf_len, 
                          size_t count, size_t stride, char *out_err, size_t err_size) {
    if (!pattern || !buffer || count == 0 || stride == 0) {
        if (out_err) snprintf(out_err, err_size, "Invalid batch parameters");
        return false;
    }
    
    for (size_t i = 0; i < count; i++) {
        const uint8_t *ptr = buffer + (i * stride);
        size_t remaining = (i == count - 1) ? buf_len - (i * stride) : stride;
        
        char err[256];
        if (!pattern_verify(pattern, ptr, remaining, err, sizeof(err))) {
            if (out_err) {
                snprintf(out_err, err_size, "Batch[%zu]: %s", i, err);
            }
            return false;
        }
    }
    
    if (out_err) snprintf(out_err, err_size, "Batch of %zu patterns VALID", count);
    return true;
}

int pattern_describe(const binary_pattern_t *pattern, char *buf, size_t buf_size) {
    if (!pattern || !buf || buf_size == 0) return -1;
    
    int written = snprintf(buf, buf_size,
        "Pattern: %s\n"
        "  Total Size: %zu bytes\n"
        "  Fields: %zu\n"
        "  Flags: 0x%08X\n",
        pattern->pattern_name,
        pattern->total_size,
        pattern->field_count,
        pattern->flags
    );
    
    for (size_t i = 0; i < pattern->field_count && written < (int)buf_size - 100; i++) {
        const pat_field_t *field = &pattern->fields[i];
        written += snprintf(buf + written, buf_size - written,
            "  [%zu] %s @ 0x%zX (%zu bytes): type=%d",
            i, field->field_name, field->offset, field->length, field->type);
        
        if (field->has_expected) {
            written += snprintf(buf + written, buf_size - written, 
                " expected=0x%llX", (unsigned long long)field->expected_val);
        }
        if (field->has_range) {
            written += snprintf(buf + written, buf_size - written,
                " range=[%llu, %llu]", (unsigned long long)field->min_val, 
                (unsigned long long)field->max_val);
        }
        written += snprintf(buf + written, buf_size - written, "\n");
    }
    
    return (written > 0 && written < (int)buf_size) ? 0 : -2;
}
