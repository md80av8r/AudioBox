# Session Snapshot — MD-88 Audio Breakout Box

**Date:** 2026-05-26
**Status:** Pausing here to switch to rev A firmware work

---

## 🎯 Active Todo List

1. **Check pins and correct labelling** — final sanity-pass on the rev D pin map
   - Current map: `REV_D_PINMAP.md` + `firmware/src/pins_revD.h` (corrected — no longer uses GPIO 33/34/35-37 which aren't broken out on the WROOM-1-N16R8 module)
   - Reassigned: PWR_BTN→43, PTT_BTN→44, LED_STATUS→2, LED_PTT_ACTIVE→21, PWR_HOLD→0
   - Uses USB-CDC for debug instead of UART (frees GPIO 43/44 for buttons)

2. **Choose a reset button** (PCB mount or enclosure mount?)
   - EN pin needs 10kΩ pull-up to 3V3 + 100nF cap to GND
   - Optional reset button to GND for manual reset
   - PCB-mount (under enclosure) = clean, requires opening box to reset
   - Enclosure-mount = always accessible, recessed style preferred (no accidental hits)
   - Decision pending

3. **Choose connectors — 2.0mm SMD vs through-hole trade-off**
   - Current rev C: all 2.0mm JST PH SMD (B2B-PH-SM4-TB family)
   - Concerns: smaller pitch is more fragile, especially battery connector
   - Options considered:
     - **Battery (BT1):** swap to JST XH 2.5mm **through-hole** (C158012) — committed
     - **Other pigtails:** keep PH SMD or upgrade to JST EH/PA locking variants
     - Trade-off: through-hole adds board space and JLC THT fee (~$0.30/part)
   - Decision pending on signal connectors

4. **Much more to do!** — open items for rev D:
   - Display module selection (4" TFT placeholder, exact part TBD)
   - PD controller variant (FUSB302 default, alternatives possible)
   - Master/slave DIP switch type (SMD slide vs panel-mount)
   - SD card placement (main board vs panel board)
   - Second USB-C connector orientation (vertical vs right-angle)
   - Update enclosure SCAD for new component layout

5. **Switching context: working on rev A firmware now**
   - Rev A hardware in hand, want to build firmware there while rev C boards ship
   - Rev D plan captured in this folder, will resume when rev C boards arrive

---

## 📂 Where Everything Lives

### Rev C (in production, ~$380 for 5 boards, ~1-2 weeks to arrive)
```
/Users/jeffreykadans/Developer/MicBreakoutBoxrev_C/
├── md88_breakout/              KiCad project (main board + ESP32-WROVER)
│   ├── md88_breakout_main_revC.kicad_sch   ✅ Fixed BT1 power short + J4 Bose pinout
│   └── md88_breakout_main_revC.kicad_pcb   Boards in production with patches needed
├── md88_panel/                 KiCad project (panel daughter board)
├── REV.C.MAIN.BOARD.COMPLETE/  Gerbers + BOM + CPL submitted to JLC
├── REV.C.PANEL.BOARD.COMPLETE/ Gerbers + BOM + CPL submitted to JLC
├── enclosure_revD.scad         OpenSCAD enclosure (sized for rev C — name is misleading)
└── firmware/                   PlatformIO project + Wokwi setup (rev C target)
```

### Rev D Planning Docs (captured today, not yet built)
```
├── REV_D_ARCHITECTURE.md   ESP32-S3 + dual USB-C + SD + smart power
├── REV_D_PINMAP.md         Full pin assignment table
├── firmware/src/pins_revD.h  Compilable C header with all pin #defines
└── SESSION_SNAPSHOT.md     ← this file
```

---

## ✅ What's Been Decided & Locked In

### Rev C bug fixes (in schematic — for rev D fab order)
1. **BT1 power path** — VBAT_RAW merged into BAT+ net, misplaced GND symbol removed at (481.33, 351.79)
2. **J4 LEMO Bose pinout** — relabeled to standard Bose convention
3. **MIC_LO net** — defined (single-ended → functionally GND, but named correctly)
4. **Value typos** — all uppercase normalized, R41 fixed from "1OK" to "10k"

### Rev C patches needed when boards arrive
1. **Don't solder BT1** — hand-wire LiPo+ to Q4 pad 2 (60.8, 52.6 mm), LiPo− to U12 pad 6 (46.6, 62.8 mm)
2. **Build Lemo→JST-PH-6 adapter cable** with wires swapped per Bose pinout mapping

### Rev D architecture (locked)
- **Chip:** ESP32-S3-WROOM-1-N16R8 (LCSC C2913202)
- **USB:** Two USB-C ports — Port 1 = phone audio + bidirectional power, Port 2 = aircraft power sink only
- **PD controller:** FUSB302 for power-direction negotiation
- **Storage:** microSD card slot (push-push SMD)
- **Audio source:** USB Audio Class (TinyUSB) replaces A2DP — phone connects via USB-C, sees box as DAC
- **Master/slave:** DIP switch reads role at boot (Captain / FO / Slave)
- **Smart power:** Aircraft → box → phone when available; LiPo backup ~3-4 hours standalone
- **Removed:** CH340C, AUX_IN 3.5mm jack, original single USB-C
- **Battery connector:** JST XH 2.5mm through-hole (C158012) — upgrade from JST PH 2.0mm SMD

### Rev D firmware (planned)
- Platform target: `esp32-s3-devkitc-1`
- USB-CDC for debug serial (over native USB)
- TinyUSB Audio Class for phone audio in
- ESP-NOW for crew comms (broadcast mode, supports unlimited peers)
- SD card for ATC clip library + voice memos + flight audio log
- Smart power state machine with battery indicator
- Pin map: `pins_revD.h`

---

## ⏸️ Open Decisions (for next session)

| # | Decision | Notes |
|---|---|---|
| 1 | Reset button location & type | PCB-mount vs enclosure-mount |
| 2 | Signal connector upgrade | Keep PH SMD vs upgrade to locking |
| 3 | Display module exact part | 4" placeholder, need real spec |
| 4 | SD card location | Main board or panel board |
| 5 | DIP switch type | SMD slide vs panel-mount |
| 6 | Second USB-C orientation | Vertical or right-angle |

---

## 🚦 Order of Operations Going Forward

1. **Now:** User switches to rev A firmware work (separate chat/context)
2. **~1-2 weeks:** Rev C boards arrive from JLC
3. **Rev C bring-up session:**
   - Hand-patch BT1 (LiPo direct wire to Q4)
   - Build Lemo adapter cable
   - Bench test: power-on with current-limited supply first, then LiPo
   - Validate firmware against actual hardware (port from Wokwi)
4. **Rev D design session:**
   - Apply all rev C bug fixes + rev D architecture
   - Copy `md88_breakout/` → `md88_breakout_revD/`
   - Schematic surgery: WROVER → S3, add 2nd USB-C + PD chip + SD slot
   - Resolve the 6 open decisions above
   - PCB layout pass
   - Export Gerbers + order
5. **Future:** Rev D boards arrive — should be final hardware revision

---

## 💡 Reminders for Next Session

- **Don't order rev D until rev C is validated.** Testing rev C will reveal additional bugs that should be rolled into rev D.
- **The 6 open decisions can wait** — none block firmware progress on rev A or Wokwi development.
- **Pin map for rev D is solid** — use `pins_revD.h` directly when porting firmware.
- **Schematic fixes are already saved** in the rev C files but only flow to fabrication via a re-export, which we won't do for rev C.

---

**Session ends here. Good progress today.** 🛬
