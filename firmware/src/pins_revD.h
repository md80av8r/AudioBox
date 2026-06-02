// pins_revD.h — MD-88 rev D GPIO assignments (ESP32-S3-WROOM-1-N16R8 / LCSC C2913202)
//
// Status: CORRECTED — earlier draft used GPIO 33-37 which are NOT available on this
// module variant (33-34 not broken out; 35-37 used by internal Octal flash for N16).
//
// Source of truth: /Users/jeffreykadans/Developer/MicBreakoutBoxrev_C/REV_D_PINMAP.md
//
// Debug serial: this design uses USB-CDC (over the native USB port) for `Serial.print()`.
// UART0 pins (GPIO 43/44) are repurposed for buttons because we don't need UART for
// debug — USB-CDC works whenever a USB host is connected.
//
#pragma once

// ──────────────────────────────────────────────────────────────
// USB (hardware-fixed — DO NOT REASSIGN)
// ──────────────────────────────────────────────────────────────
#define PIN_USB_DM            19   // USB D-
#define PIN_USB_DP            20   // USB D+

// ──────────────────────────────────────────────────────────────
// Power latch (must boot HIGH so soft-latch stays engaged)
// ──────────────────────────────────────────────────────────────
#define PIN_PWR_HOLD           0   // Output HIGH = stay on. Boot strap (pulled high by default) is compatible.

// ──────────────────────────────────────────────────────────────
// I2S audio bus
// ──────────────────────────────────────────────────────────────
#define PIN_I2S_BCLK           5
#define PIN_I2S_WS             6
#define PIN_I2S_DOUT           7
#define PIN_I2S_DIN           15

// ──────────────────────────────────────────────────────────────
// Shared SPI bus (display + SD card)
// ──────────────────────────────────────────────────────────────
#define PIN_SPI_MOSI          11
#define PIN_SPI_MISO          13
#define PIN_SPI_SCK           12

#define PIN_DISP_CS           10
#define PIN_DISP_DC           14
#define PIN_DISP_RST           8
#define PIN_DISP_BL           16

#define PIN_SD_CS              9

// ──────────────────────────────────────────────────────────────
// Shared I2C bus (touch + BME280 + DS3231 + FUSB302)
// ──────────────────────────────────────────────────────────────
#define PIN_I2C_SDA           17
#define PIN_I2C_SCL           18

// Note: no hardware interrupt pins. FUSB302, touch, and RTC are all polled via I2C.
// PD events check every 50ms, touch every 30ms.

// ──────────────────────────────────────────────────────────────
// LEDs
// ──────────────────────────────────────────────────────────────
#define PIN_LED_STATUS         2   // Boot / error / general status
#define PIN_LED_PTT_ACTIVE    21   // Lit when local PTT keyed

// ──────────────────────────────────────────────────────────────
// Buttons + encoder + headset detect
// ──────────────────────────────────────────────────────────────
#define PIN_PWR_BTN           43   // Was UART TX. Input pullup; HIGH at boot = normal boot
#define PIN_PTT_BTN           44   // Was UART RX. Input pullup
#define PIN_ATC_BTN           38
#define PIN_ENC_A             39
#define PIN_ENC_B             40
#define PIN_ENC_SW            41
#define PIN_J3_DETECT         42   // LOW = headset plugged in

// ──────────────────────────────────────────────────────────────
// ADC inputs (ADC1 only — ADC2 conflicts with WiFi)
// ──────────────────────────────────────────────────────────────
#define PIN_MIC_ADC            1   // ADC1_CH0
#define PIN_BATT_SENSE         3   // ADC1_CH2 — LiPo via ÷2 divider
#define PIN_AIRFRAME_ADC       4   // ADC1_CH3

// ──────────────────────────────────────────────────────────────
// Master/slave role DIP switch
// ──────────────────────────────────────────────────────────────
#define PIN_ROLE_DIP_0        47
#define PIN_ROLE_DIP_1        48
//   00 = SLAVE
//   01 = FO (backup master)
//   10 = CAPTAIN (master)
//   11 = reserved

// ──────────────────────────────────────────────────────────────
// NOT AVAILABLE on this module (do not try to use)
// ──────────────────────────────────────────────────────────────
// GPIO 22-25   — chip-level gap, don't exist
// GPIO 26-37   — internal SPI flash + PSRAM (N16R8 uses Octal flash → 33-37 occupied)
// GPIO 45      — VDD_SPI boot strap (must be LOW at boot)
// GPIO 46      — Boot ROM print strap (must be LOW at boot)
