// pins.h — MD-88 rev C GPIO assignments
// Locked from the schematic. Do not rebind without updating hardware.
#pragma once

// ─── Display (SPI, panel daughter board via FFC) ─────────────
#define PIN_DISP_MOSI   23
#define PIN_DISP_SCK    18
#define PIN_DISP_CS      5
#define PIN_DISP_DC      2
#define PIN_DISP_RST    -1   // tied to EN, no pin
#define PIN_DISP_BL     19   // backlight PWM
#define PIN_DISP_MISO   -1   // not connected (write-only display)

// ─── Touch (I2C, panel) ──────────────────────────────────────
#define PIN_TOUCH_SDA   21
#define PIN_TOUCH_SCL   22
#define PIN_TOUCH_INT   -1   // not connected — polled
#define PIN_TOUCH_RST   -1   // tied to EN

// ─── I2S audio out (to MAX98357A amp) ────────────────────────
#define PIN_I2S_BCLK    27
#define PIN_I2S_WS      26
#define PIN_I2S_DOUT    25

// ─── Encoder (EC11 on panel) ─────────────────────────────────
#define PIN_ENC_A       13
#define PIN_ENC_B       14
#define PIN_ENC_SW       4

// ─── Buttons ─────────────────────────────────────────────────
#define PIN_PWR_BTN     12   // momentary, debounced
#define PIN_PWR_HOLD    32   // drives Q5 — keeps soft-latch on
#define PIN_PTT_BTN     35   // input-only pin
#define PIN_ATC_BTN     33

// ─── Audio level monitoring (ADC) ────────────────────────────
#define PIN_MIC_ADC     36   // input-only — INMP441 level sense
#define PIN_AIRFRAME_ADC 39  // input-only — airframe audio level

// ─── Battery sense ───────────────────────────────────────────
#define PIN_BATT_SENSE  34   // input-only — LiPo voltage divider

// ─── Misc ────────────────────────────────────────────────────
#define PIN_J3_DETECT   15   // headset jack-detect

// ─── UART (USB-C via CH340C, auto-reset) ─────────────────────
// Pins 1 (TX) and 3 (RX) — used by Serial, no need to define
