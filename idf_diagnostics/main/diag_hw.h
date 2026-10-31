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
bool diag_expander_read(uint8_t *bits);   // false if the expander does not answer
bool diag_haptic_buzz(void);              // false on I2C error
