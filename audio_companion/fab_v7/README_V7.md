# fab_v7 - audio companion respin (supersedes fab_v6, which was never produced)

Board: 131.6 x 72.5 mm, 4 layers, 1.6 mm. Sandwiched behind the CrowPanel at a 12 mm gap; the top side is not reachable once assembled.

## Order settings (same as the cancelled Y14 order except the colour)
- Solder mask colour: **BLACK** (white silkscreen). Black may add a surcharge / lead time: check on the quote.
- 4 layers, 1.6 mm, 5 PCBs, 5 PCBA, Standard assembly, assembly side = Top only, confirm placement = Yes.
- Via 0.2 mm min, finish ENIG recommended (HASL leaded was chosen before).
- Files: `audio_companion_gerbers_JLCPCB_v7.zip`, `JLCPCB_BOM.csv` (header "JLCPCB Part #"), `JLCPCB_CPL.csv`. Tick "Select all" on the BOM or lines get dropped.
- Origin of gerbers, drill and CPL = board lower-left corner (JLCPCB rejected a non-corner origin once).

## Contents
- 109 SMT parts on 37 BOM lines (JLCPCB assembles). New or changed vs v6: SMT relays G6K-2F-Y-TR (C2153097), JST S8B-PH-SM4-TB (C265121) and S6B-PH-SM4-TB (C265405) cable connectors, USB-C jack TYPE-C-31-M-12 (C165948), 5.1k CC resistors (C25905), 10nF encoder debounce (C15195), 16 small debounce/sense parts. LEDs D4-D7 and their resistors ARE populated (they sit on the right ear for light pipes).
- Expect several Extended-part fees (about $3 per distinct Extended type); the quote screen will show the real number. Basic/Extended status of the new parts could not be confirmed from LCSC.
- NOT assembled by JLCPCB (hand-solder): through-hole PH headers, the two 1x7 long-pin headers, LEMO pigtail wires (plated holes), test pads (bare copper, bottom). See `PARTS_TO_BUY_v7.md`.

## CPL rotation / position corrections already applied
Found by comparing our footprints with the JLCPCB (EasyEDA) footprints of each LCSC part: U1 +270, U5 +270, Q1 +180 (matches the v6 corrections that were checked in the JLCPCB viewer), relays +270 (new), J-ENC-1 and J-PANEL-1 +0, J-USB-1 +0 with the placement point moved 1.57 mm toward the rear pad row (EasyEDA origin differs from KiCad's).
**CHECK THESE IN THE JLCPCB PLACEMENT PREVIEW before paying:** MIC_BYPASS-1 and HEADPHONE_BYPASS-1 (pin 1 / marker), J-ENC-1, J-PANEL-1, J-USB-1 (opening must face the left board edge), U1, U5, Q1. If one is wrong, change its Rotation in the CPL by +90 / +180 / +270 and re-upload (or use Edit Order).

## Design state
- DRC: 0 violations, 0 unconnected. PCB pads match the schematic netlist (388 pads, 0 mismatches). Schematic parity shows only cosmetic footprint-name / field items.
- Plated GND mounting holes H1-H4 (3.2 mm drill, 4.4 mm pad) at the CrowPanel hole pattern (CrowPanel holes are plated GND).
- Power: battery plugs into J-BAT-1 or J-BAT-2 (parallel, JST PH 2.0, pin 1 = +); the other goes to the panel J3 by cable. USB-C jack J-USB-1 (left edge) feeds J-USB5V-1 (PH 2-pin) -> cable to the panel J10 (XH 2.54 mm 4-pin: pin 3 +5V, pin 4 GND). Panel charger TP4059 with R16 = 2k, about 0.5-0.6 A.
- 12 V for the headset (Bose A20 / ProFlight 2, about 0.25-0.5 W) is on LEMO pin 6; boost enable = ANR_POWER_EN (panel IO8).
- Source of truth: `audio_companion.kicad_pcb` md5 recorded in `SOURCE_MD5.txt`.

## Open items (do not block the order)
- Latching bypass switch and power button not chosen yet (cover-mounted, wired to J-PANEL-1).
- LEMO pigtail pin order must be checked against the pigtail; wire gauge/diameter unknown (zip-tie slots 8 mm apart).
- Panel pin check on the V1.1 board (labels are from V1.3 files); polarity of any LiPo you buy must match panel J3 (pin 1 = VBAT).
- Long-pin header length for the 12 mm gap (about 21 mm overall, to be confirmed).
