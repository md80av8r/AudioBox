# MD-88 Audio Companion - master respin checklist (single source of truth)

**This file lives in the AudioBox repo (`audio_companion/`). Edit it here only.** Bench log: `../BRINGUP_TODO.md`.

## File map (what is what)
| File | Meaning |
|---|---|
| `audio_companion.kicad_pcb` | **AS ORDERED** (Y15, fab_v7). This is the board on the bench. Do not edit. |
| `audio_companion.kicad_sch` | Current schematic (newer than the v19 PCB: has J-BAT-2, J-USB-1, J-USB5V-1, CC resistors). |
| `audio_companion_v19_r3.kicad_pcb/.pro` | **Respin work board** (v19 layout, not yet ordered). Make v20 from this. |
| `fab_v7/` | Fab package that was ordered (BOM, CPL, gerbers). |
| `scripts/`, `mech_viewer.html`, `ref/` | Router/placement scripts, 3D stack viewer, datasheets. |
Older backups and the cancelled fab_v6 stay in the local `REV_D/audio_companion_work` folder (archive, not in git).

## v20 MUST-FIX list from bring-up (2026-11-12)
1. **Relay coil polarity reversed on BOTH relays.** G6K-2F-Y: coil pin 1 = +, pin 8 = -. Board has pin 1 -> K1_COIL_DRIVE, pin 8 -> +3V3. Swap on HEADPHONE_BYPASS-1 and MIC_BYPASS-1 (pin 1 -> +3V3, pin 8 -> K1_COIL_DRIVE). D1/D2 stay across the coil. (My v19 error; fix in schematic and PCB.)
2. **Mic bias:** replace 3V3 + 2.2 kohm with bias from +12 V via ~1 kohm (bench-proven: 0.98 kohm, 12.7 V rail, 6.2 V / ~6.6 mA at the mic), with RC filter (10-47 uF to AGND). Gate it OFF in the bypass/relay-rest state so the aircraft's own bias is not fought. Replace the BIAS solder jumper with a resistor footprint option. Check C23 stays >= 16 V (1 uF 25 V OK).
3. **BTN_IN** is on PCA9534 U3 pin 13 (INT output): move to pin 12 (SPARE5).
4. **IO19/IO20 are native USB pins:** move MCLK and BYPASS_EN; rename BYPASS_EN -> ACTIVE_EN.
5. **Battery path:** add reverse-polarity protection (P-MOS), fuse/PTC, and a battery on/off switch. VBAT tap from CrowPanel J3 (charger TP4059 is on the panel, PROG 2 kohm) or document the PH2.0 jumper cable J3 -> J-BAT-1.
6. **ANR rail off must be off:** MT3608 leaves the 12 V rail at ~3.3 V via inductor/diode; gate the ANR LED / add load switch.
7. Test points: mic bias node, codec LIN1/RIN1, +12 V.
8. MIC relay spare contacts (pins 5, 6, 7) are paralleled with the right headphone channel: confirm intent.
9. ES8388 ADC L/R slot order varies between monitor starts: add test point / layout check.
10. Mechanical: rotate the two zip-tie slots by 90 degrees next to the LEMO plug.
11. Known board facts: `MIC_IN` needs a 3-contact aviation jack; JST ENC/PANEL ear connectors; L2 needs <= 3.0 mm or a 12.5 mm gap.

# MD-88 audio companion: respin checklist (started 2026-10-17)

Starting point: `audio_companion_v18_final.*` (= `fab_v6`, the files that were NOT produced). The v6 order was held at the production-file confirmation step and is being cancelled.

## Why a respin
The v6 board was ordered without a mechanical fit check against the CrowPanel. Checking afterwards found:
- ENC1 (Alps EC10E1220503) is 11 mm tall, hollow-shaft, horizontal-mount only, has NO push switch, and sits directly under the CrowPanel BOOT/RESET buttons.
- The panel's tan JST connectors hang 8.9 mm (0.35 in) below its back; its black header sockets are 4.3 mm (0.17 in). Several of those connectors sit directly over tall JST sockets, the LEMO header and the aircraft JST on the daughterboard.
- The daughterboard's 4 mounting holes (92 x 45 mm) do not line up with the CrowPanel's 4 holes (111.5 x 65.2 mm).
- The "10 mm gap" used earlier was an assumption, not a measurement.

## Measured / confirmed facts (use these, not assumptions)
| Item | Value | Source |
|---|---|---|
| CrowPanel hole pattern | about 4.4 x 2.6 in (file: 111.5 x 65.2 mm) | user calipers + V1.3 file |
| Header column spacing | 0.618 in measured (file and board: 15.494 mm, 0.610 in) | user calipers |
| Header socket height | 0.17 in = 4.3 mm | user |
| Tan JST connectors on panel | 0.35 in = 8.9 mm tall | user |
| Panel silkscreen | V1.1 (reference files are V1.3; pin labels match) | user photo |
| Panel board outline | 117.5 x 71.2 mm (file) vs daughterboard 117.15 x 70.15 mm | V1.3 file |
| Panel header pinout | J9 = IO20, IO5, IO4, IO6, 3V3, GND, IOT_5V; J11 = IO19, IO16, IO15, NC, IO2, IO8, NC | V1.3 file + photo labels |
| Panel mapping onto daughterboard | x mirrored (panel faces down onto board); header match is exact in x, y uncertain by about 2 mm | overlay script |

## Still to measure (need the real parts)
- [ ] Gap you actually want, board top to panel back, and the pin length that gives it
- [ ] Heights of the daughterboard parts that will face the panel (JST sockets, relays, headers, inductor, tantalums)
- [ ] Panel V1.1 hole positions (vertical spacing) and edge-to-hole distances
- [ ] What you will plug into the panel connectors, and how the panel is powered (USB-C, battery, or external 5 V)

## Decisions needed before layout
1. **Through-hole parts on top or bottom?** Recommendation: bottom side, so only low SMD parts face the CrowPanel and the gap only has to clear its 8.9 mm connectors (about 12 mm). Tall parts then live in the rear-cover space.
2. **Encoder.** Options: (a) off-board panel-mount encoder on wires to the spare header; (b) on-board at a spot that clears the panel's buttons and connectors; (c) a different encoder (normal shaft, with push switch). Dual purpose (volume plus a second function) needs the push switch, so (a) or (c) is preferred.
3. **Mounting.** Add the CrowPanel hole pattern to the daughterboard so one M3 stack ties display, board and case together, or keep a separate floor pattern. Case rear-cover screws go in wall bosses outside the board outline either way.
4. **Assembly scope per part family:** SMT where possible; JLCPCB through-hole service (rules and cost not yet checked); or hand-solder. The long-pin headers are not on LCSC either way.
5. **Case concept:** CrowPanel on its own holes to the case top; daughterboard on standoffs from the rear cover; slots for panel edge connectors and USB-C (left side of the stack).

## Design tasks
- [ ] Move or replace ENC1 and add an off-board encoder connector (A, B, push, GND) if chosen
- [ ] Re-place tall through-hole parts (bottom side or clear of the panel's tall parts)
- [ ] Add mounting holes per decision 3
- [ ] Keep: 7 test pads (GND x2, 3V3, 3V3A, 12V, AGND, SDA), 7-pin spare IO header, TPA6111A2 fix, mic DC block, AO3400A on Q1
- [ ] Check LEMO pigtail pin order against the schematic (open item from before)
- [ ] Fix test-point footprints to the library version (clears 7 cosmetic DRC warnings)

## Pre-order gates (all must pass before any fab files are uploaded)
- [ ] DRC 0 errors, 0 unconnected; schematic ERC clean; PCB nets match schematic netlist
- [ ] No vias inside SMD pads (only the U1 thermal vias)
- [ ] Overlay of CrowPanel outline, holes, connectors and tall parts onto the board with real heights: no tall-over-tall overlap at the chosen gap
- [ ] Encoder/knob/thumbwheel access confirmed against the case concept
- [ ] User confirms THT vs JLCPCB-assembled per part family in writing
- [ ] JLCPCB placement preview rotations match (U1, U5, Q1 offsets already known)

## Reusable from v6
Scripts in `scripts/` (place, route, maze router with own-pad via keepout, fab export recipe), `fab_v6` BOM/CPL structure (SMT BOM and CPL carry over if SMT parts do not move), LCSC/DigiKey part lists, `overlay_crowpanel_vs_daughterboard.png`.

## 3D model (added 2026-10-17)
`mech_viewer.html` (open in any browser, needs internet for the 3D library) is generated by `scripts/mech_model.py` from the current PCB: daughterboard parts with real 3D-model heights, CrowPanel parts mapped from the V1.3 file, case walls, rear cover, top plate with display window, corner screw bosses outside the board outline, and markers for where each control sits on the top surface. Run it after every layout change and read the collision readout before exporting fab files. Measured so far (mm): sockets 4.3, tan edge connectors 8.9, UART0-IN 8.0, BAT 6.35, coin cell 5.1, RESET and BOOT 9.14. Still estimated: SPK connector, buzzer, USB-C, DIP switch.

## Proposed layout: controls strip (added 2026-10-17, shown in mech_viewer.html)
Nothing under the CrowPanel is reachable and the 13.7 mm hollow-shaft encoder cannot fit under its 9.14 mm RESET/BOOT buttons (needs a gap of 22.8 mm). Proposal:
- Extend the daughterboard about 24 mm past the CrowPanel's right edge (strip), holding the encoder and the power and bypass buttons outside the panel footprint; knob and button caps pass through the bezel. Case becomes about 162 x 91 x 31 mm at a 12 mm gap.
- Gap about 13 mm: with the encoder out of the way the worst remaining overlap needs 12.8 mm (UART0-IN connector over the button-input JST).
- Replace the EC10E with a standard 6 mm-shaft encoder with push switch (EC11 type) so ordinary knobs fit and the push switch gives the second function.
- Add a remote "front panel" SMT header (JLCPCB-assembled) carrying ENC A, ENC B, ENC push, power button, bypass button, GND and 3V3 in parallel with the strip footprints, so a separate remote encoder or panel board can be wired if the strip does not work out.
- RESET/BOOT stay behind the panel; USB-C auto-download should make them unnecessary for programming (verify on the real panel).
- Strip layout (viewer layout B, chosen tentatively 2026-10-17): encoder lower on the right strip, power and bypass buttons stacked above it; button cap diameter adjustable in the viewer. The four status LEDs (PWR, ACT, ANR, BYP) currently sit at the top edge UNDER the CrowPanel and would be invisible: move them to the strip beside the buttons.

## Bypass control: requirements (user decision 2026-10-17)
- The bypass control must be LATCHING, not momentary: one press drops the relays to the direct aircraft-to-headset path and it stays there; it re-engages processing only after a second press. Must work with hung firmware (hardware path, no dependence on the ESP32). Power loss and power-up default stay BYPASS (relays off).
- Current v18 wiring (momentary tactile shorting the Q1 gate to GND) fails this: it only forces bypass while held, firmware cannot see the press, and the red BYP LED follows BYPASS_EN, not the real relay state.
- Fixes to design: (1) latching action; (2) firmware sense input from a spare PCA9534 pin (read the real state, e.g. the Q1 gate node through a high-value resistor); (3) BYP LED driven from the actual relay state, not from BYPASS_EN; (4) firmware must never re-engage by itself after a pilot bypass.
- Options being weighed: A) mechanical push-on/push-off switch (panel-mount via the remote front-panel header, state visible, fail-safe by physics) plus sense line; B) electronic toggle latch on the strip (tactile + toggle flip-flop + AND with BYPASS_EN, power-up reset to bypass), adds ICs to the safety path.
- Layout: right-edge strip kept as shown (layout B) unless a bigger latching switch changes the hole size.

## Encoder: dual concentric with push (user direction 2026-10-17)
- Large rotary = dual concentric encoder with push ("Garmin style"): outer ring + inner shaft + push. Candidate: ELMA E37 (10-pin THT, 11.5 x 12.3 x 9.1 mm body, M7 x 0.75 bushing, 7 mm panel hole, about $60-90 each; see memory note project_revD_encoder_options). Hobby EC11 dual clones (about $5-15) for prototypes via the remote header. Verify body orientation/height on the datasheet before layout.
- Signals: outer A, outer B, inner A, inner B, push = 5 inputs + GND. Map onto PCA9534: outer A/B on the existing EXP_ENC_A/B, inner A/B and push on three of the five spare pins; one spare for the bypass-state sense; one left over.
- Debounce on the strip: 10k pull-up + 10k + 10 nF per line (5 lines), optional 74HC14 Schmitt; E37 needs external debounce.
- Mechanical: E37 body 9.1 mm + 6 mm bushing = 15.1 mm, but the bezel plate underside is about 18 mm above the strip board at a 12 mm gap, so add a printed 3 mm boss around the encoder hole (shown in the viewer).
- Keep the two small buttons (power, latching bypass) as already decided.

## DECISIONS LOCKED (2026-10-17)
- Bypass: Option A. Mechanical latching push-on/push-off switch, panel-mounted, wired through the remote front-panel header; one press = bypass (relays drop), second press = re-engage. Add a firmware sense input (spare PCA9534 pin) and drive the BYP LED from the real relay state. Firmware never re-engages by itself.
- Encoder: ELMA E37 dual concentric with push as the final part; hobby dual-encoder clone wired to the remote header for prototyping.
- Right-edge controls strip (about 24 mm), layout B, two small buttons kept (power, plus the bypass control above).
- Gap about 13 mm; case about 162 x 91 x 31 mm.
- Still open: through-hole parts on top or bottom (recommendation: bottom); mounting-hole pattern (CrowPanel pattern on the daughterboard vs keep floor pattern); JLCPCB through-hole assembly scope; remote header connector type; E37 datasheet dimensions; status LEDs move to the strip.

## E37 datasheet data (read from the ELMA PDF, saved in ref/ELMA_E37_datasheet.pdf, 2026-10-17)
Preferred type E37-VT6330-1 (vertical THT, threaded M7 bushing, 6 N push, 16 detent / 8 PPR both shafts, IP60); IP68 is E37-VT6332-1. Knobs sold separately (collets 10 mm / 14.5 mm for the 3 mm inner shaft version, or metal knobs 11 / 15 mm for 4 mm shafts).
- Vertical heights above the seating plane: body 9.75, M7 x 0.75 thread 5.35 (9.75 to 15.1), outer shaft dia 6 x 10 mm, inner shaft dia 4 x 13.8 mm, 38.9 mm total. Nut 2 mm (supplied), 10 mm across flats.
- Footprint (from component side): two rows of 5 pins, 2.54 pitch, drill 1.0 mm, rows 13.69 mm apart (6.84 + 6.85). Bottom row left to right: B S S C A = pins 1 to 5 (Bi, S, S, Ci, Ai). Top row left to right: A C NC NC B = pins 10, 9, 8, 7, 6 (Ao, Co, NC, NC, Bo). Two rectangular plated slots 1.6 x 2.6 mm at about x = +/-5.35 mm, y = 0 (check against the drawing before layout). Panel hole: 7 mm with a 6.2 mm flat when threaded.
- Datasheet PCB thickness is 1 to 1.5 mm; our 4-layer board is 1.6 mm. Decide: order the board at 1.2 mm, or confirm the clamp legs tolerate 1.6 mm.
- Panel clamping: the nut needs a plate between about 9.75 and 13.1 mm above the board, so the bezel over the strip steps down to a plate at about 10.2 to 12.7 mm. Knob stack then reaches about 38.9 mm, about 48 mm above the rear cover (the viewer shows this). Options to reduce: cut or order shorter shafts (ELMA lists shaft length as a customization), or use the horizontal version with a side-wall knob.
- Needs external debounce: 5 x 10k pull-up, 5 x 10k series, 5 x 10 nF, optional 74HC14 (circuit in the datasheet).

## More decisions (2026-10-17)
- Board thickness stays 1.6 mm (E37 datasheet says 1 to 1.5 mm; 0.1 mm over, judged acceptable; pins still protrude about 1.7 mm for soldering). Ask ELMA only if the clamp legs do not seat.
- E37 is hand-soldered (not on LCSC; datasheet limit: hand soldering below 300 C for 3 s). If the knob is not mounted on the board, wire the encoder to the remote header: 5 signals + GND + 3V3, debounce stays on the board, keep leads short (about 30 cm or less), E37 footprint left unpopulated.
- Vertical rotary only (no side-wall knob).
- Relays: change to the SMT version of the same family so JLCPCB assembles them: Omron G6K-2F-Y DC3 (LCSC C93168, SMD 10 x 6.5 mm, DPDT, 3 V coil). The JLCPCB assembly library listing found is G6K-2F-Y-TR DC3 (C2153097), flagged Extended (about $3 per distinct part type, both relays share one). VERIFY both numbers and stock in the JLCPCB parts library before the BOM is built. Check relay height (about 5.2 mm) against the panel parts above in the 3D viewer.
- Through-hole parts that move to the bottom side leave pin tails on the top (about 3.4 mm untrimmed); trim them after soldering and check against the panel connectors above.
- Strip alignment (user, 2026-10-17; viewer layout D): the knob's bottom edge is aligned with the bottom edge of the display window, and the top button starts at the display's top edge. Positions follow the real glass position, which is still an estimate (centered, 93.7 x 56.2 mm): MEASURE on the CrowPanel the distance from the board edges to the glass edges before layout. At the estimate: display window y = 28.6 to 84.8 mm, knob center y about 77.6 mm.
- Display module outline (user measured 2026-10-17): 4.15 x 2.65 in = 105.41 x 67.31 mm (module/glass outline). Still needed: where the lit (active) area sits inside it and how big the bezel window should be (active area for an 800x480 4.3 in panel is about 93.7 x 56.2 mm, not measured), plus the module's offset from the CrowPanel board edges. The knob/button alignment uses the bezel window edges.
- Display geometry (user calipers, 2026-10-17): module 4.15 x 2.65 in (105.41 x 67.31 mm); lit area 3.75 x 2.125 in (95.25 x 53.98 mm); left and right margins 0.2 in (5.08 mm); top margin 0.14 in (3.56 mm); bottom margin 0.385 in (9.78 mm; computed as 2.65 - 2.125 - 0.14, assuming the "3.65" in the message was a typo for 2.65). Bezel window = lit area. STILL UNMEASURED: where the module sits on the CrowPanel board (assumed centered), measured from the board edges.
- Strip width set to 28 mm (2026-10-17): the bezel step now sits at the CrowPanel's right edge (not 8 mm out as first drawn), and the knob edge clears the step wall by 3.3 mm. The 12-pin remote header also needs about 26 mm along the strip's bottom edge.

## Gap decision (2026-10-17)
- Gap 12 mm, CrowPanel left untouched (UART-IN stays). Keep tall daughterboard parts out from under the panel's tall connectors. At exactly 12 mm two daughterboard parts need attention: J-BTN-1 (JST, under UART0-IN, needs 12.8 mm) must move; L2 (3.2 mm) under UART0-OUT needs 12.1 mm, so either move L2 or use a slightly lower inductor, otherwise fall back to a 12.5 mm gap. Re-run the 3D collision check after placement.
- Haptic connector J-HAPTIC-1: candidate to change to the SMT side-entry JST (S2B-PH-SM4-TB family) so JLCPCB assembles it. Footprint JST_PH_S2B-PH-SM4-TB exists in the KiCad library; check the LCSC/JLCPCB part number, stock and height before use. Each new distinct SMT connector type is an Extended part (about $3 once per type).
- User does NOT like the stepped (offset) top cover over the strip (2026-10-17). Cause: the E37 nut must clamp a plate 9.75 to about 13.1 mm above the board, while the flat display bezel is 18+ mm up. Flat-cover options: (A) panel-mount the E37 to the flat cover by its own nut (body hangs below the cover, about 8.4 mm above the board) and wire it to the J-FRONT header, no E37 footprint on the PCB; (B) a separate front-panel board raised to about 8.5 mm under the cover, cabled to the header; (C) ask ELMA for a longer outer shaft and sink the encoder in a well under the flat cover. Recommendation: A. Decision pending.
- Haptic connector: yes, change J-HAPTIC-1 (low cable stress) to the SMT PH side-entry; keep through-hole PH for the audio jacks and aircraft connector.

## DECIDED 2026-10-17: flat cover, all controls on the cover (option A)
- E37 dual concentric encoder with push: clamped to the flat cover by its own nut, body hangs below the cover outside the CrowPanel footprint, hand-wired to the board header. The power button and the latching bypass switch are also panel-mounted on the cover and wired. No strip on the PCB: the board stays about 117 x 70 mm.
- Case gets an "ear" about 28 mm wide past the CrowPanel's right edge to hold the three controls and the hanging encoder body; case about 166 x 91 x 31 mm before knobs.
- Encoder stack above the cover top is about 26 mm with the shafts as supplied (outer shaft 10 mm + inner 13.8 mm + thread remainder). Trim the stainless inner shaft, or ask ELMA for shorter shafts, to bring it to a Garmin-like height (about 12 to 15 mm).
- Board header(s) must carry: 5 encoder signals + GND, power button + GND, bypass switch (Q1_GATE) + GND, and the four status LEDs if they go on the cover. Decide on LEDs (panel LEDs on the cover vs screen only). Likely two connectors: encoder (8-pin) and panel (10-pin).
- Remove the controls strip from the PCB plan and remove the E37 footprint from the board (J-FRONT header stays).
- Status indicators (proposal 2026-10-17, awaiting OK): drop the PWR, ACT and ANR LEDs (D4, D5, D6 and their resistors) and show those states as icons on the display. Keep ONE hardware BYP indicator, independent of firmware (wired panel LED on the cover, or an LED built into the latching bypass switch), driven from the real relay state (K1_COIL_DRIVE) so it stays truthful if the firmware hangs. Saves two Extended LED part types. Panel connector then carries: power button + GND, bypass switch (Q1_GATE) + GND, BYP LED anode + GND.
- Status LEDs revised (user point, 2026-10-17): LEDs also serve as diagnostics when the display is dead. Proposal: on the cover, two hardware-driven LEDs independent of the display: PWR (straight from the 3.3 V rail) and BYP (from the real relay state). ACT and ANR: keep as board-edge diagnostic LEDs visible through a small slot or light pipe in the case, or drop them and show them as icons. Prefer Basic-library LED colors (red, white) over green and yellow to avoid Extended-part fees. Decision pending.
- DECIDED (user, 2026-10-17): NO LEDs on the cover (extra mounting and wiring for little gain). All four status LEDs stay on the board (SMT, assembled by JLCPCB) at an accessible edge for bench use; the display shows status as icons. Bypass state is also visible from the latching switch position. Cover carries only the E37 encoder, the power button and the latching bypass switch. Board connectors (SMT PH side-entry): J-ENC-1 (8-pin: GND, ENC_OA, ENC_OB, ENC_IA, ENC_IB, ENC_PUSH, GND, +3V3) and J-PANEL-1 (6-pin: EXP_PWR_BTN, GND, Q1_GATE (bypass switch), GND, EXP_SPARE5, +3V3). SW-PWR-1 leaves the board. The E37 symbol/footprint leave the board.

## STATUS 2026-10-17 (v19 layout done, in main files)
- Main files audio_companion.kicad_{sch,pcb} = v19 (v18 kept as audio_companion_before_v19.* and v18_final). Board 131.6 x 72.5 mm (CrowPanel outline + 14 mm right ear for J-ENC-1 and J-PANEL-1), CrowPanel-pattern mounting holes at 3.0 mm from the panel edges (H1-H4, optional use), relays now SMT G6K-2F-Y, E37 / power button / bypass button off the board, SW-PWR-1, R2, R3, J-SPARE-1 removed, 16 new 0402 parts (debounce + sense), LEDs untouched (to be DNP).
- DRC: 0 errors, 0 unconnected; warnings only (silk overlaps on the relay labels, 10 harmless copper stubs, 2 dangling vias, lib footprint notices). PCB nets match the v19 netlist; vias in SMD pads only in U1's exposed pad.
- 3D check on the real v19 layout: smallest gap that clears everything is 12.1 mm (UART0-OUT connector over L2; next is 11.2 mm). At exactly 12 mm L2 (3.2 mm model height, datasheet 3.0 mm max) is the only touch.
- TODO before fab: fix relay silk labels; clean copper stubs; BOM (relays C93168 / JLC C2153097 verify, J-ENC-1 S8B-PH-SM4-TB and J-PANEL-1 S6B-PH-SM4-TB LCSC numbers and stock, DNP the four LEDs and their resistors, remove old parts), CPL; hand-solder list update; verify relay pin mapping (G6K-2P vs 2F) on the Omron datasheet; user to review layout in KiCad.

## STATUS 2026-10-17 late (post-v19 cleanup, main files changed after v19 delivery)
- Backups: audio_companion_before_netfix.kicad_pcb (v19 as delivered), audio_companion_before_cleanup.kicad_{pcb,pro}.
- NET FIX: v19 router had tied MIC_BYPASS-1 pads 5-7 (unused pole 2) to HP_R_AMP/OUT/RAW. Ripped up and rerouted those three nets; pads 5-7 now no-net, matching the schematic. Schematic netlist vs PCB: no electrical mismatches.
- Cleanup: removed 2 dangling vias (K1_COIL_DRIVE, I2C_SCL) and their stubs; moved HP RELAY silk, pin-1 "1" labels and J-BAT +/- labels; removed 2 L2 silk segments. DRC = 0 violations (not 0 errors + warnings: zero total).
- lib_footprint_mismatch and lib_footprint_issues set to IGNORE in audio_companion.kicad_pro. Reason: TP1-TP7 are deliberately BOTTOM-side pads (board is sandwiched under the CrowPanel, top inaccessible) with no silk/courtyard, H1-H4 and easyeda parts are customised. Do NOT "fix test points to the library version": it flips them to the top side. (Supersedes the old design task.)
- Schematic parity (127 items) is cosmetic only: footprint-name/description field diffs, NC pads, SH pins, mounting holes. ERC: K1/K2_COIL_DRIVE labels intentionally on one net (one drive, two relays).
- Still TODO before fab: BOM/CPL (fab_v7), DNP D4-D7 + resistors, verify relay pin map and LCSC numbers, L2 height, user layout review. No fab export or ordering without explicit user OK.
- 2026-10-17: H1-H4 changed to plated GND pads (3.2 mm drill, 4.4 mm pad, all layers, net GND). CrowPanel V1.3 holes J4/J6/J7/J8 are plated GND (5 mm pad) so metal standoffs only join GND to GND; V1.1 hole nets not metered. 4.4 mm (not 5.0) because a 5 mm pad at H2 touched the +BATT track at J-BAT-1. "OUT 2" silk moved 2.5 mm left. Backup: audio_companion_before_gndholes.kicad_pcb. DRC 0 violations.
- 2026-10-17: J-PANEL-1 footprint swapped to JLCPCB/EasyEDA S6B-PH-SM4-TB(LF)(SN), LCSC C265405 (tab pads 7.40 vs KiCad 7.35, same pins). J-ENC-1 KEPT on the KiCad S8B footprint (LCSC C265121): the EasyEDA S8B has its tab pads at +/-9.85 mm, inconsistent with its own S6B (offset 2.4 from pin span) and with the KiCad S8B/S6B (offset 2.35, i.e. +/-9.35). Both use JLCPCB's real 3D models in 3d/ (JST datasheet: S8B 19.9 x 6(+2.6) x 5.5 mm). Backup before swap: audio_companion_before_jlcfp.kicad_pcb. Connectors are assembled by JLCPCB (about $10 extra, user OK). Cable plugs: genuine JST PHR-8/PHR-6 + SPH-002T-P0.5S from DigiKey/Mouser. TODO: check JLC Basic/Extended for C265121/C265405 at BOM time; CPL rotation check in JLC preview.
- 2026-10-17: J-LEMO-1 is now six plated holes (1.7 mm pad, 1.0 mm drill) for hand-soldered pigtail wires (no header, no 3D model), plus two NPTH oval slots 3.2 x 1.6 mm at +/-4.0 mm either side of the column, y = 89.4 mm, for a zip-tie strain relief. Pigtail diameter/gauge not yet confirmed; check cable and tie clearance under the CrowPanel in the 3D viewer. Backup: audio_companion_before_lemo.kicad_pcb. OPEN: change J-BAT-1 from vertical B2B-PH-K to side-entry S2B-PH-K; USB-C power-in jack (option B) location and link to panel J10 (pin 3 +5V_IN, pin 4 GND) not yet decided; panel battery J3 powers everything, panel TP4059 charges it.
- 2026-10-17 ORDER NOTE: PCB solder mask colour = BLACK for this respin (the cancelled Y14 order was blue). Pick Black in the JLCPCB quote; check the colour surcharge and lead time. Silkscreen white.
- 2026-10-17 (pending install while KiCad was open): LEDs D4-D7 + R12-R15 moved to the right ear (LED x = 146.0 mm, y = 23/27/31/35, resistors x = 142.4, labels PWR/ACT/ANR/BYP at x = 137.5) for light pipes (4.0 mm pitch), stay POPULATED (not DNP). CrowPanel header silk labels added (L: IO19, IO16, IO15, NC, IO2, IO8, NC; R: IO20, IO5, IO4, IO6, 3V3, GND, 5V). U1 3D model = EasyEDA QFN-28 (C365736) in 3d/.
- 2026-10-17 USB-C POWER IN (option B) built in a scratch copy (installed on user OK): J-USB-1 = Korean Hroparts TYPE-C-31-M-12 (LCSC C165948, ~$0.17, 346k stock; Basic/Extended not confirmed), power-only: VBUS -> USB_5V, GND, CC1/CC2 each 5.1k (R-CC-1/2, LCSC C25905 to verify) to GND, D+/D-/SBU left NC. Jack on the LEFT edge, mid-height (origin 23.5, 66 mm, opening left). 2-pin PH 2.0 header J-USB5V-1 (S2B-PH-K, hand-soldered) at (38, 88) carries USB_5V + GND; cable goes to the CrowPanel J10 (XH 2.54 mm 4-pin: pin 3 +5V_IN, pin 4 GND; pins 1-2 are UART0 RX/TX). OPEN: D+/D- shorted option for BC1.2 dedicated-charger detect (aircraft USB-A ports may limit to 500 mA without it); USB 3D model via EasyEDA C165948 (offset y -1.57). Panel's own USB-C stays for programming. J-BAT-2 added in parallel with J-BAT-1 for the battery Y-connection.
- 2026-10-17: removed stale BATT/+/- silk beside H2 (left over from old J-BAT-1 position). D+/D- short for BC1.2 considered and REJECTED (the port, not the sink, shorts D+/D-). Panel charger: TP4059, PROG resistor R16 = 2k => about 500-600 mA charge current (TP4056-family formula, datasheet not read); fixed by hardware.
- 2026-10-17 FAB v7 PREPARED: fab_v7/ (gerber zip, BOM 37 lines/109 SMT parts, CPL, README_V7.md, PARTS_TO_BUY_v7.md). Uploaded to JLCPCB quote (own Chrome tab, NOT yet in cart/paid): 4 layers 131.5x72.41, black mask, white silk, ENIG, 0.2 mm via (forces FR4 TG155 + 4-wire Kelvin test), plugged vias, 5 PCB + 5 PCBA Standard top side, confirm production file + confirm parts placement = Yes with auto-confirm OFF, depanel Yes, edge rails by JLCPCB. Quote 2026-10-17: PCB $97.28 + PCBA $171.95 = $269.23 before shipping. JLCPCB placement viewer: relays, J-ENC-1, J-PANEL-1, J-USB-1, U1, U5, Q1 orientations look right. Extended parts: tantalum C1952817, green/yellow LEDs, ferrite C19330, relay C2153097, J-ENC C265121, J-PANEL C265405, USB-C C165948, L2, U1-U3, U5, U6, U8.
- PENDING: board file with the 3 final silk labels (5V, G, USB) is audio_companion_v7_labels.kicad_pcb (md5 in fab_v7/SOURCE_MD5.txt); copy over audio_companion.kicad_pcb once KiCad is closed (main file does not have them yet).
- 2026-10-17: v7 labels installed into audio_companion.kicad_pcb (backup audio_companion_before_v7labels.kicad_pcb). Re-exported gerbers/drill from the installed file: all 12 files identical to the zip uploaded to JLCPCB (cart item Y15-12510236A), so no re-upload needed. DRC 0.
- 2026-10-17: ORDER PLACED by user (JLCPCB Y15-12510236A, 5 PCB + 5 PCBA, black, ENIG). Placement preview confirmed good by user. Post-order changes to main files must be logged as such.
- 2026-10-18: J-USB5V-1 (38,88 mm, opening right) plug would collide with the PTT plug (PTT opens down at x 48-55, y 86-93; PH plug needs ~6-8 mm in front of the mouth, only 3.4 mm free to the PTT body). Decision: do NOT populate the header; solder the USB 5V/G wires into the 2 holes (5V = pin 1, lower; G = upper) and route left/down with strain relief. Boards are ordered as-is.

## CASE NOTES (2026-10-18) - boards are IN PRODUCTION (placement approved by user), do not edit the fab files
- Panel UART0-IN / J10 (GND, 5V_IN, IO43-TX0, IO44-RX0; about 2.5 mm pitch, likely XH 4-pin) is SIDE-ENTRY: it opens toward the panel edge (bottom edge in the daughterboard view, x about 28-45 mm). The plug slides in horizontally through the 12 mm gap. Case: keep about 8-10 mm clear beyond that edge plus wire-bend room, or put a slot in the wall there. The connector hangs 8.0 mm below the panel, leaving only about 4 mm above our board: nothing taller than about 3 mm may sit under it (the J-USB5V-1 header must stay unpopulated; wires only).
- J-USB5V-1 (38,88 mm): do NOT populate; solder 5V (lower hole, pin 1) and G (upper hole) wires flat and run them to the J10 plug.
- USB-C power jack J-USB-1 sits on the LEFT edge at y about 66 mm, flush with the board edge, fairly close to the panel's own USB-C jack. Intent was to have it set further inside the case; if the case needs it recessed, use a short USB-C extender, or desolder and relocate after the boards arrive.
- If any JST connector fouls the case or another plug, desolder it after the boards arrive (user will do this).
- 2026-10-18: REFERENCE_labelled/ created (labelled copy for the user's reference; knockout white-box/black-text labels). Production files unchanged.
- 2026-10-18 POST-ORDER CHANGE (silkscreen only): audio_companion.kicad_pcb now = the labelled reference board (knockout name boxes, USB text removed, ATC BTN label moved). Copper, footprints, nets and fab_v7 gerbers UNCHANGED. As-ordered board saved as audio_companion_AS_ORDERED.kicad_pcb (md5 31c5550f580b0899a5cd1f6b2df7c369). Main file therefore no longer matches the built silkscreen. DRC: 0 errors, 0 unconnected, 48 silk warnings (silk over copper / overlap, cosmetic).
- 2026-10-18: user measured the panel BAT connector (J3) at 2.5 mm pitch (schematic name said PH2.0). Treat as XH: jumper from J-BAT-2 to J3 = PHR-2 (our end) + XHP-2/SXH (panel end). Panel J10 UART0-IN also ~2.5 mm (XH), unverified. Our board headers stay PH 2.0.
