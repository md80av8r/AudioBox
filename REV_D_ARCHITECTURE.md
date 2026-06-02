# MD-88 Crew Audio Breakout — Rev D Architecture

**Decision date:** 2026-05-26
**Status:** Design committed, hardware build pending rev C validation

## Headline change: ESP32-S3 + Dual USB-C with Smart Power Management

Rev D replaces the WROVER + CH340C + A2DP + AUX_IN paradigm with a modern
USB-C-native audio + power architecture matching consumer device expectations.

---

## 1. Chip swap

| | Rev C (current) | Rev D (new) |
|---|---|---|
| Module | ESP32-WROVER-E-N8R8 (C2973667) | **ESP32-S3-WROOM-1-N16R8 (C2913202)** |
| CPU | LX6 dual-core 240 MHz | LX7 dual-core 240 MHz + vector ops |
| Flash | 8 MB | **16 MB** |
| PSRAM | 8 MB | 8 MB |
| USB | None (needs CH340C) | **Native USB-OTG** |
| BT | Classic + BLE 4.2 (has A2DP) | BLE 5.0 only (no A2DP) |
| Module size | 31.4 × 18 mm | 25.5 × 18 mm (smaller) |
| Usable GPIO | ~32 | ~45 |

---

## 2. Audio sourcing — USB Audio Class instead of A2DP

Rev D drops Bluetooth Classic A2DP entirely. Phone audio enters via
**USB Audio Class** (UAC1 or UAC2) through the ESP32-S3's native USB.

**Why:**
- Higher quality (uncompressed PCM vs SBC-compressed BT)
- Lower latency (<10 ms vs 100+ ms)
- Same cable used for phone charging (see Section 3)
- S3's native USB means no CH340C needed for programming either

**Firmware:** TinyUSB Audio Class. ATC clips still play from PSRAM via I2S.

---

## 3. Dual USB-C ports with smart power management

### Port roles

| Port | Function | What's wired |
|---|---|---|
| **USB-C #1 — "Phone Port"** | Audio data + bidirectional power + programming | Full USB-C: D+/D− to ESP32-S3 GPIO19/20, CC1/CC2 to PD controller |
| **USB-C #2 — "Aircraft Power"** | Power input only (sink), no data | CC1/CC2 pulldowns to advertise as 5V/3A sink; VBUS to system 5V rail. No D+/D− wiring |

### Hardware additions

| Part | Purpose |
|---|---|
| USB PD controller (FUSB302 or similar) | Negotiates power direction on Port #1 |
| ESD protection array (USBLC6) | Protects ESP32 USB pins from spikes |
| Beefier +5V rail (buck-boost capable of sourcing 2A) | To charge phone via Port #1 when aircraft power available |
| TVS diodes on both VBUS lines | EMI/transient protection in aircraft environment |

### Power flow scenarios

```
Aircraft power IN ──► Port #2 ──► system + LiPo charging
                                       │
                                       └──► (optional) Port #1 VBUS out ──► Phone charging
                                                                                ▲
                                                                                │
Phone plugged IN ──► Port #1 ──► USB Audio data ──► ESP32-S3
                                       │
                                       └──► (when no aircraft power)
                                             Phone supplies VBUS ──► system
```

### Smart power state machine (firmware)

```
if (aircraft_5V_present):
    run from aircraft → charge LiPo → source 5V to phone
    UI: "Phone charging from aircraft"

elif (lipo_voltage > 3.5V):
    run from LiPo → optionally source to phone (user setting)
    UI: "Phone charging from LiPo (Xmin remaining)" or "Battery saver on"

else (lipo critical):
    stop sourcing to phone
    UI: "Low battery — connect power"
    graceful shutdown imminent
```

---

## 4. Parts removed from rev D

| Removed | Why |
|---|---|
| **CH340C (U14)** + auto-reset NPNs (Q2, Q3) + decap (C26) + base resistors (R22, R23) | S3 native USB handles programming |
| **AUX_IN 3.5mm jack (J5)** | USB-C is the audio input now |
| Single USB-C J1 | Replaced by two new USB-C connectors |

**Net BOM reduction:** ~10 components removed, board space freed for PD chip + second USB-C.

---

## 5. Parts added to rev D

| Added | Purpose |
|---|---|
| 2× USB-C receptacles | Phone port + aircraft power port |
| FUSB302 PD controller | Power direction negotiation |
| USBLC6 ESD array | USB pin protection |
| TVS diodes (×2) | Aircraft EMI protection |
| 5V buck-boost (replace MT3608 boost) | Source 2A capable for phone charging |
| **microSD card holder** (push-push, SMD, ~$0.50 LCSC) | Mass storage for audio clips, voice memos, flight audio log |
| 4× 10k pull-ups (SD CMD/DAT lines) | Standard SD bus requirement |

---

## 6. Carryover bug fixes from rev C

Already captured in the rev C schematic:

1. **BT1 power path** — VBAT_RAW merged into BAT+; no GND short
2. **J4 LEMO pinout** — relabeled to match Bose convention
3. **MIC_LO net** — defined (even if functionally GND for single-ended)
4. **Value typos** — all normalized (lowercase k/u, R41 = 10k not 1OK)

Plus:
5. **BT2 placement** — move CR2032 holder to a clear area (no component overlap)

---

## 7. Pin assignment changes (S3 vs WROVER)

S3 has different strapping pins, USB pins, and ADC mapping. New `pins.h` needed:

| Function | Rev C (WROVER) | Rev D (S3) |
|---|---|---|
| USB D+ / D− | (CH340C handles) | **GPIO19 / GPIO20** (hardware fixed) |
| I2S BCLK / WS / DOUT | 27 / 26 / 25 | TBD — S3 has flexible I2S pins |
| SPI MOSI/SCK/CS (display) | 23 / 18 / 5 | TBD — shared bus with SD card |
| **SD card CS** | (rev C had SD_CS = TBD) | **dedicated GPIO, shares MOSI/MISO/SCK with display** |
| I2C SDA / SCL | 21 / 22 | TBD |
| ADCs (mic, batt, airframe) | 36, 34, 39 | TBD — S3 ADC1 channels |

Will draft full pin map when rev D PCB pass begins.

### Shared SPI bus strategy

Display (TFT) and SD card both use SPI. Share MOSI/MISO/SCK between them;
give each its own chip-select line. Standard pattern, well-supported in Arduino
and ESP-IDF.

```
ESP32-S3 SPI ─┬── DISP_CS ──► TFT display
              └── SD_CS   ──► microSD card holder
```

---

## 8. Firmware-side changes

| Component | Change |
|---|---|
| Platform target | `esp32-wrover-kit` → `esp32-s3-devkitc-1` |
| USB stack | None → **TinyUSB + USB Audio Class** |
| BT code | A2DP sink → **BLE only** (ESP-NOW unchanged) |
| Audio source UI | "BT music" → **"USB phone audio"** |
| Master/slave role | New: DIP switch reads role at boot (Captain / FO / Slave) |
| Power management | New: smart PD state machine, battery indicator |
| **SD card support** | New: `SdFat` library — mount FAT32, browse/play WAV files, voice memo recording |
| **ATC clip library** | Migrate from PSRAM-resident to SD-file-backed |
| **Flight audio logger** | New feature: optional record-all-audio mode with rotating log files |

---

## 9. Timeline

**Do NOT order rev D until rev C boards are validated.** Working order:

1. Receive rev C boards (~1-2 weeks from JLC)
2. Patch rev C (LiPo direct wire + Lemo adapter cable)
3. Bring up firmware on rev C, validate all features work
4. Catalog any additional rev C bugs discovered during testing
5. Apply ALL fixes + this rev D architecture in one final design pass
6. Order rev D → expect to be the final hardware revision

---

## 10. Cost expectation for rev D

Rev C was ~$380 for 5 assembled boards.
Rev D should be similar (~$350-400):
- Saved: CH340C, AUX jack, single USB-C
- Added: 2× USB-C, PD controller, ESD/TVS protection
- Net: similar BOM count, slightly better part density
