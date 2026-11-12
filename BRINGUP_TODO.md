# Audio companion bring-up — to-do

## Status (2026-11-12)
- Working: LiPo battery + 12 V boost (ANR power, 12.7 V), mic bias from 12 V rail (bench rework), display/touch, I2C devices, OTA update, tone on PHONES/LEMO, mic + sidetone with external bias, on-screen Audio Mixer (diagnostics firmware, branch claude/laughing-franklin-d2ruqb).
- Mixer defaults: preamp 0 dB, sidetone 0 dB, output -13 dB, mic channel Auto.
- Open hardware: relay coil polarity, mic bias, BTN_IN on INT pin, battery path untested.
- Board files: uploaded audio_companion.kicad_sch is newer than audio_companion_v19.kicad_pcb (adds J-BAT-2, J-USB-1, J-USB5V-1, CC resistors). The PCB open in KiCad (Rev D 2026) also has them; commit the current files.
- Power: BATT1/BATT2 are parallel on +BATT (pin 1 = +) feeding only the MT3608 12 V boost. No charger, fuse or reverse protection. USB-C 5 V goes only to the USB 5V OUT JST.

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
- [x] ES8388 audio: tone out works on PHONES and LEMO (with HP relay bridge)
- [x] Mic in and sidetone: works with proper bias (bench 9 V + ~550 ohm); on-board bias too weak
- [x] Headphone amp and mic preamp paths
- [x] Rework mic bias on this board from the 12 V rail (done 2026-11-12, see 'Bench rework' below)
- [ ] Relay coil rework on one board (remove HP bridge, confirm click and bypass switching)
- [ ] LiPo battery: confirm polarity of the CrowPanel battery connector vs J-BAT pin 1 (+) BEFORE plugging in (no reverse protection, no charger on companion board)
- [ ] Re-check ES8388 register read-back (once read all 09 with handheld connected)

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

## Next revision notes
Moved: the master v20 change list is `audio_companion/RESPIN_CHECKLIST.md` (single source of truth). Add new findings there.

## Mic bias bench test: PASSED
- BIAS bridge removed; 9 V battery + ~550 ohm series (two-resistor combo) onto MIC IN M, battery - to G, headset mic in the MIC IN jack, no radio.
- Result: voice through the mixer sidetone is about 1000% cleaner and clear. Confirms the on-board 3.3 V / 2.2 kohm bias is the cause of the weak, noisy mic.
- Rev fix: bias from the 12 V rail (or ~9 V) through ~470-560 ohm, with RC filtering. Use this value as the starting point.
- Firmware mixer defaults (15 dB preamp, +24 dB sidetone) were set for the weak bias; with proper bias drop them back (try 0-6 dB preamp, 0-12 dB sidetone).

## Bench rework: mic bias from the 12 V rail (2026-11-12) - WORKING
- Battery: LiPo on J-BAT-2, polarity verified with a meter; PH2.0 jumper from CrowPanel J3 to J-BAT-1 ties VBAT so the CrowPanel TP4059 charger (PROG 2 kohm, estimated ~0.5 A) charges the same cell.
- ANR power (IO8) switch on the diagnostics screen: off = rail dim at ~3.3 V (MT3608 has no load disconnect, expected), on = 12.7 V at LEMO pin 6.
- Rework: BIAS solder jumper (JP-MIC-BIAS-1) left OPEN; 0.98 kohm resistor soldered between J-LEMO-1 pin 6 (+12V) and pin 4 (MIC_RAW), sleeved where it passes pin 5 (AGND).
- Measured: M to G = 12.7 V unloaded, 6.2 V with headset in MIC IN (~6.6 mA). Sidetone heard, works.
- Caution: bench only. In relay rest state MIC_RAW goes to the aircraft mic jack, so do not connect to an aircraft with this resistor fitted. No filter cap on the bias yet (add 10-47 uF to AGND if boost noise shows up).
- Next-rev fixes for this: see `audio_companion/RESPIN_CHECKLIST.md`.

## UI work (2026-11-12)
- Home screen added (idf_diagnostics/main/ui_home.c): status tiles MODE (tap toggles IO20, high = ACTIVE), ANR (tap toggles IO8), MIC (tap = mic monitor, with level bar), LINK (placeholder, "NO LINK"). Gear button opens Settings: Audio Mixer, Diagnostics, Firmware update. Old diagnostics screen is kept as-is behind Settings.
- Plan: (1) feel/polish the UI, (2) ESP-NOW link between two boxes (heartbeat + status, link tile with RSSI), (3) crew voice audio over the link (mic -> u-law -> ESP-NOW -> jitter buffer -> mix into headphones). Wi-Fi OTA hotspot and ESP-NOW must share one channel.
- MODE tile polarity (IO20 high = ACTIVE) follows the planned ACTIVE_EN rename; the real relay state is not sensed yet. Confirm on the board.
- Crew link step 1 done in code (untested on hardware): `link.c` = ESP-NOW broadcast heartbeat every 500 ms on channel 6 (same channel as the update hotspot, which now runs in AP+STA mode so the link stays up). LINK tile shows LINKED + RSSI and the peer's MODE. Needs two boards on the same firmware.
