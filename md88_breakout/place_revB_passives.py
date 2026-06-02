#!/usr/bin/env python3
"""Place the remaining 24 unplaced passives based on their net connections."""

import re, shutil
from datetime import datetime

PCB = "/Users/jeffreykadans/Developer/MicBreakoutBoxrev_B/md88_breakout/md88_breakout_revB.kicad_pcb"

# Placement based on net analysis from schematic
# (ref, x, y, rotation, layer)
PLACEMENTS = [
    # LED current limit (for D4/D5 charge LEDs at 42,45-48)
    ("R6",   38, 47, 0, "F.Cu"),   # 470Ω LED limit

    # Auto-reset cluster (near Q2, Q3 at 58,22 / 61,22 and CH340C U14 at 65,22)
    ("R30",  58, 25, 0, "F.Cu"),   # 10k base resistor for Q2 (DTR→EN)
    ("R31",  61, 25, 0, "F.Cu"),   # 10k base resistor for Q3 (RTS→IO0)
    ("R28",  52, 25, 0, "F.Cu"),   # 10k IO0 pull-up
    ("C21",  68, 26, 0, "F.Cu"),   # 100nF USB decoupling
    ("C20",  56, 25, 0, "F.Cu"),   # 100nF near auto-reset

    # Power rail bulk caps (power section: power cluster 20-36, y=42-58)
    ("C12",  24, 38, 0, "F.Cu"),   # 10µF USB_VBUS bulk
    ("C13",  24, 41, 0, "F.Cu"),   # 10µF VBAT_RAW bulk
    ("C18",  36, 48, 0, "F.Cu"),   # 10µF +5V/+3V3 bulk
    ("C24",  36, 55, 0, "F.Cu"),   # 22µF +5V bulk
    ("C19",  38, 58, 0, "F.Cu"),   # 22µF +3V3 (AMS1117 output)
    ("C11",  30, 50, 0, "F.Cu"),   # 22µF +5V MT3608 output
    ("C10",  30, 56, 0, "F.Cu"),   # 22µF +12V MT3608 output

    # USB VBUS indicator current limits (near J1)
    ("R22",  70, 28, 0, "F.Cu"),   # 1k VBUS indicator
    ("R23",  70, 30, 0, "F.Cu"),   # 1k VBUS indicator

    # Mic/ADC analog chain (audio section, y=55-60)
    ("R32",  47, 58, 0, "F.Cu"),   # 10k MIC_ADC series
    ("R34",  54, 60, 0, "F.Cu"),   # 100k bias top
    ("R35",  54, 62, 0, "F.Cu"),   # 100k bias bottom
    ("R36",  42, 41, 0, "F.Cu"),   # 100k pull-up near U15

    # Audio output cap near MAX98357A
    ("C25",  44, 42, 0, "F.Cu"),   # 100nF MAX98357 decoupling

    # Encoder pull-ups and debounce (SW8 at 48,32)
    ("R39",  44, 29, 0, "F.Cu"),   # 10k ENC_A pull-up
    ("R38",  44, 35, 0, "F.Cu"),   # 10k ENC_B pull-up
    ("C26",  44, 31, 0, "F.Cu"),   # 100nF ENC_A debounce
    ("C27",  44, 33, 0, "F.Cu"),   # 100nF ENC_B debounce

    # The MT3608 inductors (when they show up after next Update PCB)
    ("L1",   26, 52, 0, "F.Cu"),   # 4.7uH +5V boost
    ("L2",   26, 58, 0, "F.Cu"),   # 4.7uH +12V boost
]


def find_footprint_block(text, ref):
    for m in re.finditer(r'\n\t\(footprint "[^"]+"', text):
        start = m.start() + 1
        depth = 0; i = start
        while i < len(text):
            c = text[i]
            if c == '(': depth += 1
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
    at_m = re.search(r'\(at\s+[-\d.]+\s+[-\d.]+(?:\s+[-\d.]+)?\)', blk)
    if not at_m:
        return text, False
    blk = blk[:at_m.start()] + new_at + blk[at_m.end():]
    new_layer = f'(layer "{layer}")'
    layer_m = re.search(r'\(layer "(?:F\.Cu|B\.Cu)"\)', blk)
    if layer_m:
        blk = blk[:layer_m.start()] + new_layer + blk[layer_m.end():]
    return text[:start] + blk + text[end:], True


def main():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy(PCB, f"{PCB}.bak_passives_{ts}")
    with open(PCB) as f: text = f.read()
    placed, missing = [], []
    for ref, x, y, rot, layer in PLACEMENTS:
        text, ok = update_footprint(text, ref, x, y, rot, layer)
        (placed if ok else missing).append(ref)
    print(f"Placed {len(placed)}: {', '.join(placed)}")
    if missing:
        print(f"Not found {len(missing)}: {', '.join(missing)}")
        print("  (run Update PCB from Schematic, then re-run this script)")
    with open(PCB, "w") as f: f.write(text)
    print(f"Saved.")


if __name__ == "__main__":
    main()
