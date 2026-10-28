// pins_companion.h — Audio Companion board GPIO assignments
// (Elecrow ESP32-S3 Advanced "Wireless module" header -> companion HDR-CP-L-1 / HDR-CP-R-1)
//
// Source: traced from production gerbers (audio_companion v7 Y15) and the
// Elecrow header silkscreen. Header columns read top to bottom.
//
// NOTE: GPIO19/20 are the ESP32-S3 native USB D-/D+ pins. Using them here
// disables USB-Serial/JTAG; flash over the Elecrow UART port instead.
//
#pragma once

// ──────────────────────────────────────────────────────────────
// I2S audio bus (ES8388 codec, U1)
// ──────────────────────────────────────────────────────────────
#define PIN_I2S_MCLK          19   // HDR-CP-L-1 pin 1
#define PIN_I2S_BCLK           5   // HDR-CP-R-1 pin 2
#define PIN_I2S_LRCK           6   // HDR-CP-R-1 pin 4
#define PIN_I2S_DOUT           4   // ESP out -> codec DAC in  (HDR-CP-R-1 pin 3)
#define PIN_I2S_DIN            2   // codec ADC out -> ESP in  (HDR-CP-L-1 pin 5)

// ──────────────────────────────────────────────────────────────
// I2C bus (ES8388, PCA9534 expander, DRV2605L haptic)
// ──────────────────────────────────────────────────────────────
#define PIN_I2C_SCL           16   // HDR-CP-L-1 pin 2
#define PIN_I2C_SDA           15   // HDR-CP-L-1 pin 3

// ──────────────────────────────────────────────────────────────
// Control outputs
// ──────────────────────────────────────────────────────────────
#define PIN_ANR_POWER_EN       8   // Enables MT3608 +12V boost (HDR-CP-L-1 pin 6)
#define PIN_BYPASS_EN         20   // Bypass enable, drives D5 LED (HDR-CP-R-1 pin 1)
