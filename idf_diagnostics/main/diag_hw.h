// Hardware access for the companion-board diagnostics.
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "driver/i2c_master.h"

typedef struct {
    const char *name;
    uint8_t addr;
    bool present;
} diag_dev_t;

// Expander bit meanings (PCA9534 at 0x38, from the companion board nets)
#define EXP_BIT_ENC_A      0
#define EXP_BIT_ENC_B      1
#define EXP_BIT_PWR_BTN    2
#define EXP_BIT_ENC_IA     3
#define EXP_BIT_ENC_IB     4
#define EXP_BIT_ENC_PUSH   5
#define EXP_BIT_BYP_STATE  6
#define EXP_BIT_SPARE5     7

void diag_hw_init(i2c_master_bus_handle_t bus);
int diag_dev_count(void);
const diag_dev_t *diag_dev(int i);
void diag_scan(void);
void diag_set_anr(bool on);
void diag_set_bypass(bool on);
bool diag_expander_read(uint8_t *bits);   // latest polled value; false if the expander does not answer

// Dual concentric encoder, decoded from the expander by a 2 ms polling task.
// Counts are in detents (positive = clockwise). Push is active low.
void diag_enc_get(int32_t *outer, int32_t *inner, bool *pushed);
void diag_enc_reset(void);
bool diag_haptic_buzz(void);              // false on I2C error

// Drives the four I2S output pins (MCLK, BCLK, LRCK, DOUT) so they can be checked with a meter.
// mode 0 = all low, 1 = all high, 2 = released (inputs, no pulls).
void diag_pin_test(int mode);

// Generic I2C access for the web tools: val < 0 reads one register into *out, otherwise writes val.
bool diag_i2c_rw(uint8_t addr, uint8_t reg, int val, uint8_t *out);
