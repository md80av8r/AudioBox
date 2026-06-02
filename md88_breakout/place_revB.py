#!/usr/bin/env python3
"""
place_revB.py — Apply rev B placement plan to the PCB.

Updates each footprint's (at X Y ROT) and (layer F.Cu/B.Cu) based on the
PLACEMENTS table below. Adds Edge.Cuts rectangle and antenna keepout.

Coordinates: KiCad convention (origin top-left of page, +X right, +Y down).
Board outline (13,13) → (78,63), 65×50mm working area inside 13mm page border.

USAGE:
    1. In KiCad: Tools → Update PCB from Schematic → check "Delete footprints
       with no symbols". This brings the new JST footprints in.
    2. Close KiCad PCB editor (don't leave it open while we edit the file).
    3. python3 place_revB.py
    4. Reopen the PCB in KiCad. Verify in 3D viewer.

The script makes a timestamped backup before editing.
"""

import re
import shutil
import sys
from datetime import datetime

PCB = "/Users/jeffreykadans/Developer/MicBreakoutBoxrev_B/md88_breakout/md88_breakout_revB.kicad_pcb"

# (ref, x, y, rotation, layer)  layer = "F.Cu" (top) or "B.Cu" (bottom)
PLACEMENTS = [
    # === ESP32-WROVER (upper-left, antenna up) ===
    ("U1",   27,  26,   0, "F.Cu"),  # WROVER body, antenna overhangs top edge

    # === USB programming cluster (upper-right) ===
    ("J1",   76,  22,  90, "F.Cu"),  # USB-C, opening right
    ("U14",  65,  22,   0, "F.Cu"),  # CH340C
    ("Q2",   58,  22,   0, "F.Cu"),  # auto-reset NPN (DTR → EN)
    ("Q3",   61,  22,   0, "F.Cu"),  # auto-reset NPN (RTS → IO0)
    ("R25",  73,  28,  90, "F.Cu"),  # 5.1k CC1 pulldown
    ("R26",  73,  31,  90, "F.Cu"),  # 5.1k CC2 pulldown
    ("C28",  65,  26,   0, "F.Cu"),  # CH340C decoupling 100nF

    # === User interface (mid-right strip) ===
    ("U4",   48,  20,   0, "F.Cu"),  # OLED JST 4-pin
    ("R_SDA_PU1", 52, 18, 0, "F.Cu"),  # I²C SDA pull-up
    ("R_SCL_PU1", 52, 22, 0, "F.Cu"),  # I²C SCL pull-up
    ("SW8",  48,  32,   0, "F.Cu"),  # EC11 encoder
    ("SW1",  62,  36,   0, "F.Cu"),  # DIP-4 config
    ("SW3",  40,  20,   0, "F.Cu"),  # Power slide switch
    ("SW6",  54,  40,   0, "F.Cu"),  # BOOT button
    ("SW7",  58,  40,   0, "F.Cu"),  # User button (GPIO13)

    # LEDs
    ("D4",   42,  45,   0, "F.Cu"),  # LED_CHRG_RED
    ("D5",   42,  48,   0, "F.Cu"),  # LED_CHRG_GREEN

    # === Power section (lower-left) ===
    ("U11",  20,  45,   0, "F.Cu"),  # TP4056
    ("U12",  26,  45,   0, "F.Cu"),  # DW01A
    ("Q1",   32,  45,   0, "F.Cu"),  # FS8205A protection FET
    ("U9",   20,  52,   0, "F.Cu"),  # MT3608 +5V
    ("L1",   26,  52,   0, "F.Cu"),  # +5V inductor 4.7uH
    ("D1",   30,  52,   0, "F.Cu"),  # +5V Schottky SS24
    ("U10",  20,  58,   0, "F.Cu"),  # MT3608 +12V
    ("L2",   26,  58,   0, "F.Cu"),  # +12V inductor 4.7uH
    ("D3",   30,  58,   0, "F.Cu"),  # +12V Schottky SS24
    ("U13",  36,  52,   0, "F.Cu"),  # AMS1117-3.3
    ("C_BYPASS1", 36, 58, 0, "F.Cu"),  # AMS1117 input bulk

    # === Audio section (lower-mid/right) ===
    ("U15",  42,  45,   0, "F.Cu"),  # MAX98357A
    ("L3",   46,  45,   0, "F.Cu"),  # LC filter inductor
    ("C_HP_FILTER1", 49, 45, 0, "F.Cu"),  # LC filter cap 1nF
    ("U16",  53,  45,   0, "F.Cu"),  # TPA6111A2
    ("C_OUT_L1", 58, 43, 0, "F.Cu"),  # 100µF DC-block (L)
    ("C_OUT_R1", 58, 48, 0, "F.Cu"),  # 100µF DC-block (R)
    ("C_HP_VCC_BULK1", 53, 49, 0, "F.Cu"),
    ("C_HP_VCC_DECAP1", 53, 41, 0, "F.Cu"),
    ("R_SHUTDOWN1", 49, 49, 0, "F.Cu"),

    # Airframe input chain
    ("R_AF1", 42, 55, 0, "F.Cu"),
    ("R_AF2", 42, 58, 0, "F.Cu"),
    ("C_AC_COUPLE1", 46, 55, 0, "F.Cu"),
    ("R_AF_BIAS1", 50, 55, 0, "F.Cu"),
    ("R_AF_BIAS2", 50, 58, 0, "F.Cu"),
    ("C_AF_BIAS1", 54, 55, 0, "F.Cu"),
    ("C_AF1", 54, 58, 0, "F.Cu"),

    # === Right-edge cable headers ===
    ("J4",   74,  38,  90, "F.Cu"),  # LEMO (B6B 6-pin)
    ("J5",   74,  45,  90, "F.Cu"),  # AUX (B3B 3-pin)
    ("J3",   74,  51,  90, "F.Cu"),  # Mic jack (B3B 3-pin)
    ("J2",   74,  57,  90, "F.Cu"),  # HP jack (B3B 3-pin)

    # === Left-edge cable headers ===
    ("BT1",  16,  18, 270, "F.Cu"),  # LiPo 2-pin JST
    ("CABLE1", 16, 50, 270, "F.Cu"),  # Mic airframe
    ("CABLE2", 16, 56, 270, "F.Cu"),  # Audio airframe

    # === Existing extra JST headers (CN1-CN5) — tuck on bottom edge ===
    ("CN1",  35, 60,    0, "F.Cu"),
    ("CN2",  43, 60,    0, "F.Cu"),
    ("CN3",  50, 60,    0, "F.Cu"),
    ("CN4",  57, 60,    0, "F.Cu"),
    ("CN5",  64, 60,    0, "F.Cu"),

    # === WROVER decoupling — close to module ===
    ("C22",  22, 38,    0, "F.Cu"),  # 10µF
    ("C29",  24, 38,    0, "F.Cu"),  # 100nF
]

# Board outline: 65×50 working area
BOARD = dict(x1=13, y1=13, x2=78, y2=63)

# Antenna keepout: 24mm wide × 9mm tall extending above top edge
KEEPOUT = dict(x1=15, y1=5, x2=39, y2=14)


def find_footprint_block(text, ref):
    """Return (start, end) indices of the footprint block whose Reference == ref."""
    for m in re.finditer(r'\n\t\(footprint "[^"]+"', text):
        start = m.start() + 1  # skip leading newline
        # find matching close paren
        depth = 0
        i = start
        while i < len(text):
            c = text[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
            i += 1
        else:
            continue
        blk = text[start:end]
        ref_m = re.search(r'property "Reference"\s+"([^"]+)"', blk)
        if ref_m and ref_m.group(1) == ref:
            return start, end
    return None, None


def update_footprint(text, ref, x, y, rot, layer):
    """Replace the footprint-level (at X Y ROT) and (layer "...") for ref."""
    start, end = find_footprint_block(text, ref)
    if start is None:
        return text, False
    blk = text[start:end]

    # The footprint-level (at ...) is the first (at after (footprint "..." and
    # before any (property, (pad, (fp_text, (gr_text. It may have 2 or 3 fields.
    new_at = f"(at {x} {y} {rot})"
    # Find the FIRST (at ...) line in the block, after the (footprint header line
    at_m = re.search(r'\(at\s+[-\d.]+\s+[-\d.]+(?:\s+[-\d.]+)?\)', blk)
    if not at_m:
        return text, False
    blk = blk[:at_m.start()] + new_at + blk[at_m.end():]

    # The footprint-level (layer "...") is also near the top — the first occurrence
    new_layer = f'(layer "{layer}")'
    layer_m = re.search(r'\(layer "(?:F\.Cu|B\.Cu)"\)', blk)
    if layer_m:
        blk = blk[:layer_m.start()] + new_layer + blk[layer_m.end():]

    return text[:start] + blk + text[end:], True


def add_edge_cuts_and_keepout(text):
    """Insert Edge.Cuts rectangle and a keepout zone before the final ')'."""
    # Edge.Cuts rectangle
    edges = []
    pts = [(BOARD['x1'], BOARD['y1']),
           (BOARD['x2'], BOARD['y1']),
           (BOARD['x2'], BOARD['y2']),
           (BOARD['x1'], BOARD['y2']),
           (BOARD['x1'], BOARD['y1'])]
    for i in range(4):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        edges.append(
            f'\t(gr_line (start {x1} {y1}) (end {x2} {y2}) '
            f'(stroke (width 0.1) (type default)) (layer "Edge.Cuts"))'
        )
    edge_block = "\n" + "\n".join(edges) + "\n"

    # Keepout zone (no tracks, vias, pads, copper on all copper layers)
    kp = KEEPOUT
    keepout_block = f"""
\t(zone
\t\t(net 0) (net_name "")
\t\t(layers "F.Cu" "B.Cu")
\t\t(name "antenna_keepout")
\t\t(hatch edge 0.5)
\t\t(connect_pads (clearance 0))
\t\t(min_thickness 0.25)
\t\t(filled_areas_thickness no)
\t\t(keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed) (copperpour not_allowed) (footprints not_allowed))
\t\t(fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
\t\t(polygon
\t\t\t(pts
\t\t\t\t(xy {kp['x1']} {kp['y1']})
\t\t\t\t(xy {kp['x2']} {kp['y1']})
\t\t\t\t(xy {kp['x2']} {kp['y2']})
\t\t\t\t(xy {kp['x1']} {kp['y2']})
\t\t\t)
\t\t)
\t)
"""

    # Insert before the file's final closing paren
    # Strategy: find last ')' character and insert before it
    last = text.rstrip().rfind(')')
    if last < 0:
        return text
    return text[:last] + edge_block + keepout_block + text[last:]


def main():
    # Backup
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f"{PCB}.bak_place_{ts}"
    shutil.copy(PCB, backup)
    print(f"Backup: {backup}")

    with open(PCB) as f:
        text = f.read()
    orig_len = len(text)

    # Apply placements
    placed, missing = [], []
    for ref, x, y, rot, layer in PLACEMENTS:
        text, ok = update_footprint(text, ref, x, y, rot, layer)
        if ok:
            placed.append(ref)
        else:
            missing.append(ref)

    print(f"\nPlaced {len(placed)} footprints:")
    print("  " + ", ".join(placed))
    if missing:
        print(f"\nNOT FOUND ({len(missing)} — run 'Update PCB from Schematic' first):")
        print("  " + ", ".join(missing))

    # Add Edge.Cuts and keepout
    text = add_edge_cuts_and_keepout(text)
    print(f"\nAdded Edge.Cuts rectangle ({BOARD['x1']},{BOARD['y1']}) → "
          f"({BOARD['x2']},{BOARD['y2']})")
    print(f"Added antenna keepout ({KEEPOUT['x1']},{KEEPOUT['y1']}) → "
          f"({KEEPOUT['x2']},{KEEPOUT['y2']})")

    with open(PCB, "w") as f:
        f.write(text)
    print(f"\nWrote {PCB} (was {orig_len} chars, now {len(text)} chars)")
    print("\nOpen the PCB in KiCad and verify:")
    print("  - 3D viewer (Alt+3) — board outline + components in zones")
    print("  - Ratsnest — short airwires within each cluster")
    print("  - DRC will complain about old un-placed footprints; ignore for now")


if __name__ == "__main__":
    main()
