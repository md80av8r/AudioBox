#!/usr/bin/env python3
"""
place_panel.py — Apply rev C panel PCB layout.

Updates each footprint's position and rotation. Adds Edge.Cuts rectangle
and 4 M2 mounting holes.

Board: 95mm × 53mm (fits 97.8×55.4mm enclosure with clearance)
Coordinates: KiCad convention (origin top-left, +X right, +Y down)
Board outline: (13, 13) → (108, 66)

USAGE:
    1. Open panel project in KiCad
    2. Tools → Update PCB from Schematic (brings in components)
    3. Save and CLOSE the PCB editor
    4. python3 place_panel.py
    5. Reopen PCB in KiCad → check 3D viewer
"""

import re
import shutil
from datetime import datetime

PCB = "/Users/jeffreykadans/Developer/MicBreakoutBoxrev_C/md88_panel/md88_panel_revC.kicad_pcb"

# (ref, x, y, rotation, layer)
PLACEMENTS = [
    # === User-facing controls (right side) ===
    ("SW3",   100,  22,    0, "F.Cu"),   # Power button — upper right
    ("SW1",    96,  55,    0, "F.Cu"),   # EC11 encoder — bottom right

    # === FFC connectors ===
    ("CN2",    18,  30,  180, "F.Cu"),   # Display FFC — left side, opening LEFT
    ("FPC2",   55,  62,   90, "F.Cu"),   # Main board FFC — bottom, opening DOWN

    # === I²C pull-ups (near display FFC) ===
    ("R6",     28,  26,    0, "F.Cu"),   # SDA pull-up (4.7k)
    ("R7",     28,  30,    0, "F.Cu"),   # SCL pull-up (4.7k)

    # === Encoder support (near SW1) ===
    ("R2",     85,  48,    0, "F.Cu"),   # Encoder A pull-up
    ("R4",     85,  52,    0, "F.Cu"),   # Encoder B pull-up
    ("R5",     85,  56,    0, "F.Cu"),   # Encoder SW pull-up
    ("C1",     90,  48,    0, "F.Cu"),   # Encoder A debounce
    ("C3",     90,  52,    0, "F.Cu"),   # Encoder B debounce
]

# Board outline
BOARD = dict(x1=13, y1=13, x2=108, y2=66)

# Mounting holes (M2 non-plated)
MOUNTING_HOLES = [
    (18, 18),   # upper left
    (103, 18),  # upper right
    (18, 61),   # lower left
    (103, 61),  # lower right
]


def find_footprint_block(text, ref):
    for m in re.finditer(r'\n\t\(footprint "[^"]+"', text):
        start = m.start() + 1
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
        rm = re.search(r'property "Reference"\s+"([^"]+)"', blk)
        if rm and rm.group(1) == ref:
            return start, end
    return None, None


def update_footprint(text, ref, x, y, rot, layer):
    start, end = find_footprint_block(text, ref)
    if start is None:
        return text, False
    blk = text[start:end]
    new_at = f"(at {x} {y} {rot})"
    blk = re.sub(r'\(at\s+[-\d.]+\s+[-\d.]+(?:\s+[-\d.]+)?\)',
                 new_at, blk, count=1)
    new_layer = f'(layer "{layer}")'
    blk = re.sub(r'\(layer "(?:F\.Cu|B\.Cu)"\)',
                 new_layer, blk, count=1)
    return text[:start] + blk + text[end:], True


def add_edge_cuts(text):
    """Insert Edge.Cuts rectangle before the file's final ')'."""
    edges = []
    pts = [(BOARD['x1'], BOARD['y1']),
           (BOARD['x2'], BOARD['y1']),
           (BOARD['x2'], BOARD['y2']),
           (BOARD['x1'], BOARD['y2']),
           (BOARD['x1'], BOARD['y1'])]
    for i in range(4):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        edges.append(
            f'\t(gr_line (start {x1} {y1}) (end {x2} {y2}) '
            f'(stroke (width 0.1) (type default)) (layer "Edge.Cuts"))'
        )
    return "\n" + "\n".join(edges) + "\n"


def add_mounting_holes(text):
    """Add M2 non-plated through-hole mounting holes."""
    holes = []
    for i, (x, y) in enumerate(MOUNTING_HOLES, 1):
        holes.append(f"""\t(footprint "MountingHole:MountingHole_2.2mm_M2"
\t\t(layer "F.Cu")
\t\t(uuid "00000000-0000-0000-0000-mh{i:013d}")
\t\t(at {x} {y})
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(property "Reference" "H{i}"
\t\t\t(at 0 -3 0)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "00000000-0000-0000-0000-mhr{i:012d}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "MountingHole_M2"
\t\t\t(at 0 3 0)
\t\t\t(layer "F.Fab")
\t\t\t(uuid "00000000-0000-0000-0000-mhv{i:012d}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2)
\t\t\t(layers "*.Cu" "*.Mask")
\t\t\t(uuid "00000000-0000-0000-0000-mhp{i:012d}"))
\t)""")
    return "\n" + "\n".join(holes) + "\n"


def main():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f"{PCB}.bak_panel_{ts}"
    shutil.copy(PCB, backup)
    print(f"Backup: {backup}")

    with open(PCB) as f:
        text = f.read()

    placed, missing = [], []
    for ref, x, y, rot, layer in PLACEMENTS:
        text, ok = update_footprint(text, ref, x, y, rot, layer)
        if ok:
            placed.append(ref)
        else:
            missing.append(ref)

    print(f"\nPlaced {len(placed)} footprints:")
    for r in placed:
        print(f"  {r}")
    if missing:
        print(f"\nNot found ({len(missing)}):")
        for r in missing:
            print(f"  {r}")
        print("Did you run Update PCB from Schematic first?")

    # Insert Edge.Cuts + mounting holes before final )
    last = text.rstrip().rfind(')')
    if last > 0:
        text = text[:last] + add_edge_cuts(text) + add_mounting_holes(text) + text[last:]
        print(f"\nAdded Edge.Cuts rectangle ({BOARD['x1']},{BOARD['y1']}) → ({BOARD['x2']},{BOARD['y2']})")
        print(f"Added {len(MOUNTING_HOLES)} M2 mounting holes")

    with open(PCB, "w") as f:
        f.write(text)
    print(f"\nSaved.")


if __name__ == "__main__":
    main()
