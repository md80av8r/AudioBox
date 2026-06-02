# Rev D Pin Assignment — ESP32-S3-WROOM-1-N16R8

**Module:** ESP32-S3-WROOM-1-N16R8 (LCSC C2913202)
**Chip:** ESP32-S3R8 (Quad PSRAM, no internal Octal pins reserved)
**Status:** Draft — refine when rev D PCB layout begins

---

## ⚠️ ESP32-S3 pins you CANNOT use freely

These are off-limits or strapping/special-purpose. Avoid mapping signals here:

| GPIO | Restriction |
|---|---|
| 0 | Boot mode strap. Must be HIGH for normal boot. Use only with care |
| 19 | **USB D−** (hardware fixed, do not reassign) |
| 20 | **USB D+** (hardware fixed, do not reassign) |
| 26-32 | Internal SPI flash / PSRAM (module internal) — physically NC on WROOM-1 |
| 33-37 | Reserved for internal Octal flash (some variants) — safe on WROOM-1-N16R8 but treat as fragile |
| 45 | VDD_SPI strap. Must be LOW at boot |
| 46 | Boot ROM print strap. Should be LOW at boot to suppress ROM messages |
| 43 | UART0 TX (also strap-ish, OK to use after boot) |
| 44 | UART0 RX |
| 3 | JTAG MTDO (boot strap-ish, prefer not to use as I/O) |

**Usable pool:** GPIO1–18, 21, 33–42, 47, 48 = **~32 free pins** for application use. Plenty.

---

## Pin assignments — Rev D draft

### USB (hardware fixed)

| Function | GPIO | Notes |
|---|---|---|
| USB D− | **19** | To USB-C #1 D− (via USBLC6 ESD) |
| USB D+ | **20** | To USB-C #1 D+ (via USBLC6 ESD) |

### I2S audio (to MAX98357A amp + INMP441 mic)

| Function | GPIO | Notes |
|---|---|---|
| I2S BCLK | **5** | Bit clock |
| I2S WS (LRCLK) | **6** | Word select / left-right |
| I2S DOUT | **7** | Data out to amp |
| I2S DIN | **15** | Data in from mic |

### SPI bus — shared between display and SD card

| Function | GPIO | Notes |
|---|---|---|
| SPI MOSI | **11** | Shared |
| SPI MISO | **13** | Shared (display ignores, SD uses) |
| SPI SCK | **12** | Shared |
| **DISP_CS** | **10** | Chip select — TFT display |
| **SD_CS** | **9** | Chip select — microSD card |
| DISP_DC | **14** | Display data/command |
| DISP_RST | **8** | Display reset (or tie high if module has its own) |
| DISP_BL | **16** | Backlight PWM |

### I2C — touch panel + BME280 + DS3231 + PD controller (shared bus)

| Function | GPIO | Notes |
|---|---|---|
| I2C SDA | **17** | 400 kHz fast mode |
| I2C SCL | **18** | 400 kHz fast mode |
| TOUCH_INT | **21** | Touch interrupt (optional, can poll) |
| PD_INT | **2** | FUSB302 PD controller interrupt |
| RTC_INT | **4** | DS3231 alarm interrupt (optional) |

### Buttons + encoder + headset detect

| Function | GPIO | Notes |
|---|---|---|
| PWR_BTN | **35** | Momentary, pull-up, debounced |
| PWR_HOLD | **36** | Output to AO3401A latch — drive HIGH to stay on |
| PTT_BTN | **37** | Input-only friendly, pull-up |
| ATC_BTN | **38** | Pull-up |
| ENC_A | **39** | Encoder A |
| ENC_B | **40** | Encoder B |
| ENC_SW | **41** | Encoder press |
| J3_DETECT | **42** | Headset jack detect (low = inserted) |

### ADC inputs (ADC1 only — ADC2 conflicts with WiFi)

| Function | GPIO | ADC channel | Notes |
|---|---|---|---|
| MIC_ADC | **1** | ADC1_CH0 | Mic level monitoring |
| BATT_SENSE | **3** | ADC1_CH2 | LiPo voltage divider (÷2) |
| AIRFRAME_ADC | **4** | ADC1_CH3 | Airframe audio level monitor |

### Master/slave DIP + status LEDs

| Function | GPIO | Notes |
|---|---|---|
| ROLE_DIP_0 | **47** | DIP bit 0 (00 = Slave, 01 = FO/backup, 10 = Captain/Master) |
| ROLE_DIP_1 | **48** | DIP bit 1 |
| LED_STATUS | **33** | Status LED (boot/error indicator) |
| LED_PTT_ACTIVE | **34** | Lit when PTT is keyed |

---

## Free pins remaining

After all above assigned: GPIO 0, 19, 20 fixed-purpose; ~6 unassigned (3, 22, etc.).
Plenty of room to add features later (second mic input, more LEDs, additional sensors).

---

## Strapping pin verification

Boot state required (so device boots normally):
- GPIO0 = HIGH (default with internal pullup) ✅
- GPIO3 = either (don't use as input at boot)
- GPIO45 = LOW (default external pulldown required)
- GPIO46 = LOW (default external pulldown)

All assignments above respect this — no application signals on strapping pins
during the critical boot window.

---

## Cross-check against panel board FFC link

The 20-pin FFC from main board → panel board carries these signals (unchanged from rev C, just renumbered GPIOs):

| FFC pin | Net | Rev D GPIO | Direction |
|---|---|---|---|
| 1 | +3V3 | — | Power |
| 2 | GND | — | Power |
| 3 | DISP_MOSI | 11 | Out |
| 4 | DISP_SCK | 12 | Out |
| 5 | DISP_CS | 10 | Out |
| 6 | DISP_DC | 14 | Out |
| 7 | DISP_RST | 8 | Out |
| 8 | DISP_BL | 16 | Out (PWM) |
| 9 | DISP_MISO | 13 | In |
| 10 | TOUCH_SDA | 17 | Bi |
| 11 | TOUCH_SCL | 18 | Out |
| 12 | TOUCH_INT | 21 | In |
| 13 | TOUCH_RST | — | (tie to EN or unused) |
| 14 | SD_CS | 9 | Out (if SD on panel board) — TBD whether SD lives on main or panel |
| 15 | ENC_A | 39 | In |
| 16 | ENC_B | 40 | In |
| 17 | ENC_SW | 41 | In |
| 18 | PWR_BTN_SIG | 35 | In |
| 19 | +BAT | — | Power (so panel runs off main board's battery) |
| 20 | GND | — | Power |

Decision needed: does SD card live on main board (with the FPC1 connector area) or on panel board (next to display, easier user access)?

---

## Open decisions (resolve before rev D PCB pass)

1. **SD card location** — main board (compact) or panel board (user-accessible)?
2. **Display module** — confirm exact spec before locking DISPLAY_* params in SCAD
3. **PD controller variant** — FUSB302BMPX vs newer alternatives
4. **Second USB-C connector orientation** — vertical mount or right-angle?
5. **DIP switch type** — 2-position SMD slide vs panel-mount toggle
