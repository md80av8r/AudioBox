// MD-88 Breakout — Enclosure Base Plate
// Minimal base: flat plate sized to PCB + clearance, with a shallow
// pocket the PCB drops into. Side walls and lid are designed separately.
//
// Print: 0.2mm layers, 3+ walls, 20% infill. PETG or ABS preferred for
// cockpit thermal range; PLA only if cabin stays cool.

// === DIMENSIONS ===
PCB_W       = 113.467;   // PCB width  (X)
PCB_D       = 136.0;     // PCB depth  (Y)
PCB_T       = 1.6;       // PCB thickness

POCKET_GAP  = 0.4;       // clearance around PCB inside the pocket
POCKET_DEPTH= 1.2;       // how deep the PCB sits into the base (< PCB_T so it sticks up)

WALL        = 3.0;       // outer wall thickness around pocket
BASE_T      = 3.0;       // floor thickness below the pocket

CORNER_R    = 4.0;       // outer corner radius (cosmetic)

// Mounting screws for the side walls/lid you'll design — through the
// outer rim of the base. M3 clearance.
SCREW_HOLE_D = 3.2;
SCREW_INSET  = 6.0;      // distance from outer edge to screw center

// Optional cable relief slots in the floor for under-PCB wiring runs.
// Set FLOOR_VENTS = true to add them; false for a sealed floor.
FLOOR_VENTS  = true;

$fn = 64;

// === DERIVED ===
POCKET_W = PCB_W + 2*POCKET_GAP;
POCKET_D = PCB_D + 2*POCKET_GAP;
OUTER_W  = POCKET_W + 2*WALL;
OUTER_D  = POCKET_D + 2*WALL;
TOTAL_H  = BASE_T + POCKET_DEPTH;

// === BUILD ===
difference() {
    // Outer body
    rounded_box(OUTER_W, OUTER_D, TOTAL_H, CORNER_R);

    // PCB pocket (recess from the top)
    translate([WALL, WALL, BASE_T])
        cube([POCKET_W, POCKET_D, POCKET_DEPTH + 0.1]);

    // 4 corner M3 clearance holes for side walls / lid screws
    for (x = [SCREW_INSET, OUTER_W - SCREW_INSET])
        for (y = [SCREW_INSET, OUTER_D - SCREW_INSET])
            translate([x, y, -0.1])
                cylinder(d = SCREW_HOLE_D, h = TOTAL_H + 0.2);

    // Optional floor vent slots — 4 narrow slots inside the pocket
    if (FLOOR_VENTS) {
        for (i = [0:3]) {
            translate([WALL + 8 + i*((POCKET_W - 16) / 3) - 1.5,
                       WALL + POCKET_D/2 - 30,
                       -0.1])
                cube([3, 60, BASE_T + 0.2]);
        }
    }
}

// === MODULES ===
module rounded_box(w, d, h, r) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, d - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h);
    }
}
