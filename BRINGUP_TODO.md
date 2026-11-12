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

## Bench tools (diagnostics firmware, hotspot on)
- `Self-test` button on the screen runs every check; full text at http://192.168.4.1/report
- Poke I2C: `/i2c?dev=0x10&reg=0x08` (read), add `&val=0x00` to write
- Pins: `/gpio?pin=5&mode=out&level=0` (mode: in, out, release; pins 4, 5, 6, 19)
- Tone: `/tone?on=1` / `/tone?on=0`

## Note
- The Haptic buzz button was replaced by Loopback test while debugging audio; add it back when the haptic motor arrives
  (`diag_haptic_buzz()` is still in diag_hw.c).

## Confirmed design bug: relay coil polarity reversed (both relays, all boards)
- Omron G6K-2F-Y datasheet (terminal arrangement, top view): coil pin 1 = +, pin 8 = -.
  Contacts at rest: 2-3 and 7-6 closed (NC); energized: 3-4 and 6-5 closed (NO).
- Board (production Y15 and KiCad v19_r3): pin 1 -> K1_COIL_DRIVE (Q1 drain), pin 8 -> +3V3.
  The coil is driven backwards, so the polarized relay never operates.
- Effect: PHONES / Lemo always get the AIRCRAFT (RAW) path, never the amp. This was the "no audio" fault.
- Fix for the next revision: swap the two coil nets on HEADPHONE_BYPASS-1 and MIC_BYPASS-1
  (pin 1 -> +3V3, pin 8 -> K1_COIL_DRIVE). D1/D2 stay across the coil as they are.
- Bench workaround on a built board: solder-bridge HEADPHONE_BYPASS-1 pins 3-4 and 5-6
  (amp permanently on PHONES; removes the fail-safe, bench use only).
- Also still open: BTN_IN on PCA9534 INT pin (U3.13); ACT LED / IO20 not going high.

## Verified after the relay bridge (board A)
- HP relay pins 3-4 and 5-6 solder-bridged: 1 kHz tone heard in both earcups on PHONES.
- Bypass switch now swaps the BYP/ACT LEDs (IO20 works with the USB pad fix firmware).
- Keep the board off conductive surfaces: the underside shorted on the table during testing.
- Next: mic monitor / mic level (check the BIAS solder jumper if the mic is dead).

## Mic path findings
- ES8388 ADC digital volume (reg 0x10/0x11) powers up at 0xC0 = -96 dB; firmware now sets 0 dB.
- Mic monitor is now a digital sidetone (ADC -> ESP32 -> DAC, both ears); `/micscan` picks the codec input.
- MIC IN needs a 3-contact aviation mic jack (mic on the ring); the BIAS solder jumper must be closed on the bench.
- Do NOT bridge the mic relay.
- One display (Elecrow) board does not drive IO20; keep it out of tests.

## Mic bring-up result (diagnostics firmware, `/mic` page)
- Sidetone path verified: with the aviation handheld supplying bias (PTT pressed) the voice is heard in both ears, with constant static.
- Without handheld bias the left ADC channel shows constant noise (rms ~1200-2000, no change when talking): the mic is not powered, hardware bias issue, not firmware.
- Right channel is dead (mono mic on left); use `src=1`.
- `/mic?input=1&gain=3&src=1&sw=4&inv=0&dc=1&mute=0&beep=0&ms=6000` for level/DC/regs. `beep=1` proves the output path.
- Open: codec regs read back as all `09` once while the handheld was connected (possible glitch); re-check.
- Open: measure DC at the MIC IN ring with no handheld; fix bias (12 V rail) next rev or via rework.

## Next revision notes (collected during bring-up)
- Relay coils: swap coil nets on HEADPHONE_BYPASS-1 and MIC_BYPASS-1 (pin 1 -> +3V3, pin 8 -> K1_COIL_DRIVE); mark +/- on the symbol.
- Mic bias: replace 3V3 via 2.2 kohm (measured 2.69 V on M with headset in MIC IN, 3.3 V open) with a filtered bias from the 12 V rail and ~470 ohm - 1 kohm series. Wi-Fi ripple on 3V3 shows up as static/pulsing. Add RC filtering and keep the bias off the digital supply.
- MIC IN jack and LEMO: with the headset in the LEMO and the mic relay never operating, the board MIC IN jack sees no load; verify the intended mic signal path after the relay fix.
- BTN_IN: move from PCA9534 U3 pin 13 (INT output) to a real input (pin 12).
- IO19/IO20 are the native USB pins: move MCLK and BYPASS_EN so USB debugging stays available. Rename BYPASS_EN to ACTIVE_EN.
- MIC relay spare contacts (pins 5, 6, 7) are paralleled with the right headphone channel in v19_r3: confirm intent.
- ES8388 ADC L/R data slot order was seen to vary between monitor starts (loud channel moved L<->R): add test point/layout check; firmware uses Auto channel select as a workaround.
- Add test points: MIC bias node, codec LIN1/RIN1, +12 V rail, so bias and noise can be probed without rework.
- Consider a series jumper or footprint for BIAS (resistor option) instead of a solder bridge.
- Mechanical: the two zip-tie slots next to the LEMO plug need to be rotated 90 degrees.
