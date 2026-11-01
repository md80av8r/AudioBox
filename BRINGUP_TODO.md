# Audio companion bring-up — to-do

## To buy (Amazon)
- [x] Ordered: dual-shaft encoder (SimFlight, EC11-based) + 8-pin JST PH 2.0 pigtail for J-ENC-1
- [x] Ordered: haptic motor (3V ERM coin, bare leads) + 2-pin JST PH 2.0 pigtail
- [ ] (original note) Haptic motor for the DRV2605L (connector J-HAPTIC-1). Decide ERM vs LRA; the
      diagnostics firmware defaults to ERM (`HAPTIC_IS_LRA` in `idf_diagnostics/main/diag_hw.c`).
      Check the connector pitch on the board before ordering.
- [ ] LiPo battery: single cell 3.7 V, 2000 mAh, built-in protection circuit,
      2-pin JST PH 2.0 plug. Check polarity against the board before plugging in
      (J-BAT-1 / J-BAT-2: pin 1 = +BATT, pin 2 = GND).

## Verified on hardware
- I2C: ES8388 (0x10), PCA9534 (0x38), DRV2605L (0x5A) all answer.
- Bypass: IO20 drives the relay and the expander reads the state back.
- Display and touch (CrowPanel Advance 4.3") via `idf_diagnostics`.
- Over-the-air update via the Wi-Fi hotspot (upload `diagnostics.bin` at http://192.168.4.1), board restarts into the new firmware.

## Still to test
- [ ] ANR_POWER_EN (IO8) -> +12V boost (needs the battery)
- [ ] Haptic motor
- [ ] Encoder (firmware ready, polled via expander; confirm outer/inner assignment and
      `ENC_STEPS_PER_DETENT` in `diag_hw.c` once the encoder arrives), power button
- [ ] ES8388 audio: tone out ("Play tone" button, written, not yet tested on hardware), mic in
- [ ] Headphone amp and mic preamp paths

## Possible board bug
- BTN_IN lands on PCA9534 U3 pin 13 (INT, an output), so that button can't be read.
  Confirm in the KiCad schematic. Fix: jumper to pin 12 (SPARE5) or re-route next rev.

## Notes
- IO19/IO20 are the ESP32-S3 native USB pins; flash over the CH340 (COM port) instead.

## Over-the-air updates
- Wi-Fi hotspot update: tap "Firmware update" on the diagnostics screen, join `AudioBox-Update`
  (password `audiobox1`), open http://192.168.4.1 and upload `build/diagnostics.bin`.
- First time only: the partition table changed (two 4 MB app slots), so flash once over USB
  after deleting `sdkconfig` and `build`.
