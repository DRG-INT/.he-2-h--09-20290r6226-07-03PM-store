#ifndef LSTM_KERNEL_ENGINE_H
#define LSTM_KERNEL_ENGINE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define LSTM_MAX_INPUT_DIM   16
#define LSTM_MAX_HIDDEN_DIM  32

/* Fixed-memory LSTM Weight Matrix Container */
typedef struct {
    size_t input_dim;
    size_t hidden_dim;
    
    /* Input to Gate Weights: [hidden_dim x input_dim] */
    float W_f[LSTM_MAX_HIDDEN_DIM * LSTM_MAX_INPUT_DIM];
    float W_i[LSTM_MAX_HIDDEN_DIM * LSTM_MAX_INPUT_DIM];
    float W_c[LSTM_MAX_HIDDEN_DIM * LSTM_MAX_INPUT_DIM];
    float W_o[LSTM_MAX_HIDDEN_DIM * LSTM_MAX_INPUT_DIM];
    
    /* Recurrent Hidden Weights: [hidden_dim x hidden_dim] */
    float U_f[LSTM_MAX_HIDDEN_DIM * LSTM_MAX_HIDDEN_DIM];
    float U_i[LSTM_MAX_HIDDEN_DIM * LSTM_MAX_HIDDEN_DIM];
    float U_c[LSTM_MAX_HIDDEN_DIM * LSTM_MAX_HIDDEN_DIM];
    float U_o[LSTM_MAX_HIDDEN_DIM * LSTM_MAX_HIDDEN_DIM];
    
    /* Biases: [hidden_dim] */
    float b_f[LSTM_MAX_HIDDEN_DIM];
    float b_i[LSTM_MAX_HIDDEN_DIM];
    float b_c[LSTM_MAX_HIDDEN_DIM];
    float b_o[LSTM_MAX_HIDDEN_DIM];
} lstm_weights_t;

/* State Container: Preserves Long-Term Memory (C) and Visible State (h) */
typedef struct {
    float C[LSTM_MAX_HIDDEN_DIM]; /* Cell State (Long-term invariants) */
    float h[LSTM_MAX_HIDDEN_DIM]; /* Hidden State (Engineer's View) */
    size_t hidden_dim;
    uint64_t step_count;
    float last_anomaly_score;
} lstm_state_t;

/* Public API for Kernel and Driver Inference */
void  lstm_engine_init_weights(lstm_weights_t *weights, size_t in_dim, size_t hid_dim);
void  lstm_state_reset(lstm_state_t *state, size_t hid_dim);
int   lstm_forward_step(const lstm_weights_t *w, lstm_state_t *state, const float *x_t);
float lstm_compute_anomaly_score(const lstm_state_t *state, const float *expected);

#ifdef __cplusplus
}
#endif

#endif /* LSTM_KERNEL_ENGINE_H */
