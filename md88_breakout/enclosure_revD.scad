// MD-88 Audio Breakout — Rev D enclosure (3-piece, faceplate + body + back)
//
// Architecture:
//   Faceplate (front)  ── window for 4" TFT, encoder+power button cutouts
//      ↓ M2 screws into brass heat-set inserts in body
//   Body (mid-shell)   ── panel PCB on near standoffs, main PCB on far standoffs,
//                         LiPo pouch pocket, side cutouts for connectors
//      ↓ M2 screws into brass heat-set inserts in back cover
//   Back cover         ── removable for LiPo service, vent slots, label area
//
// Coordinate convention inside the body cavity:
//   X = width (left ↔ right when looking at faceplate)
//   Y = height (bottom ↔ top of faceplate)
//   Z = depth into box (faceplate at z=0, back cover at z=TOTAL_DEPTH)
//
// Both PCBs sit FACE-UP (components toward faceplate). Main PCB X/Y axes are
// aligned with box X/Y. Panel PCB X/Y axes are aligned with box X/Y. The
// SHIFT_* parameters position each PCB origin inside the box cavity.

$fn = 72;

/* =====================================================================
   1. DISPLAY — swap these 6 numbers to switch display models
   ===================================================================== */

// --- 4" target (default) — placeholder, refine when exact module chosen
DISPLAY_ACTIVE_W   = 85.0;   // visible touch area width
DISPLAY_ACTIVE_H   = 53.0;   // visible touch area height
DISPLAY_MODULE_W   = 98.0;   // outer module PCB width (drives faceplate min size)
DISPLAY_MODULE_H   = 60.0;   // outer module PCB height
DISPLAY_GLASS_T    = 2.5;    // glass + PCB stack thickness behind faceplate
DISPLAY_FLEX_SIDE  = "bottom"; // "top"/"bottom"/"left"/"right" — where the FFC exits

// --- 3.5" Hosyond fallback (uncomment to use, comment block above)
// DISPLAY_ACTIVE_W   = 73.0;
// DISPLAY_ACTIVE_H   = 49.0;
// DISPLAY_MODULE_W   = 96.0;
// DISPLAY_MODULE_H   = 74.0;
// DISPLAY_GLASS_T    = 2.0;
// DISPLAY_FLEX_SIDE  = "bottom";

DISPLAY_RECESS     = DISPLAY_GLASS_T + 0.3;   // pocket depth in faceplate
DISPLAY_BEZEL      = 4.0;    // faceplate material around the active window

/* =====================================================================
   2. BOARDS — sourced from rev D KiCad PCBs (do not edit unless layout changes)
   ===================================================================== */

// Main board (md88_breakout_main_revD.kicad_pcb)
MAIN_W            = 74.6;
MAIN_H            = 68.7;
MAIN_T            = 1.6;
MAIN_TALLEST_TOP  = 8.5;     // ESP32 module + coin cell holder dominate this
MAIN_TALLEST_BOT  = 2.0;     // SMD passives back side
// 4 mounting holes in main-board local coords (X then Y), from KiCad
MAIN_HOLES = [
    [31.50 - 28.85, 35.95 - 20.15],  // = [ 2.65, 15.80]
    [64.80 - 28.85, 22.95 - 20.15],  // = [35.95,  2.80]
    [31.25 - 28.85, 86.05 - 20.15],  // = [ 2.40, 65.90]
    [100.55 - 28.85, 85.95 - 20.15], // = [71.70, 65.80]
];
MAIN_ANTENNA_NOTCH = true;   // top-left corner has antenna keepout — leave RF air

// Panel board (md88_panel_revC.kicad_pcb — unchanged in rev D)
PANEL_W           = 95.0;
PANEL_H           = 53.0;
PANEL_T           = 1.6;
PANEL_TALLEST_TOP = 13.5;    // EC11 encoder body + shaft + cap
PANEL_TALLEST_BOT = 1.5;     // bottom-side passives only
// Mounting holes (panel-local coords, KiCad origin offset removed)
PANEL_HOLES = [
    [18.00 - 13.00, 18.00 - 13.00], // [ 5,  5]
    [18.00 - 13.00, 61.00 - 13.00], // [ 5, 48]
    [103.00 - 13.00, 18.00 - 13.00],// [90,  5]
    [103.00 - 13.00, 61.00 - 13.00],// [90, 48]
];
// User-facing controls (panel-local coords)
PANEL_SW3_PWR     = [93.10 - 13.00, 20.26 - 13.00]; // [80.10, 7.26]
PANEL_SW1_ENC     = [93.54 - 13.00, 48.75 - 13.00]; // [80.54, 35.75]
PANEL_CN2_DISP_FFC = [37.00 - 13.00, 36.95 - 13.00]; // [24.00, 23.95]
                  // 14-pin KH-FG0.5 — display flex folds down to this
PANEL_BTN_HOLE_D  = 4.5;     // tactile cap clearance for SW3
PANEL_ENC_SHAFT_D = 7.5;     // EC11 D-shaft + knob clearance
PANEL_ENC_BOSS_D  = 9.0;     // boss for knob to spin without rubbing

// Layout strategy:
//   - Panel PCB sits against the RIGHT interior wall so its SW1/SW3 button
//     column lands near the right edge of the faceplate.
//   - Display module sits to the LEFT of the button column, mounted to the
//     faceplate from behind. It freely overhangs the panel PCB to the left.
//   - The display's 14-pin FFC pigtail folds back and routes to CN2 on the
//     panel PCB (panel-local 24,24).
BUTTON_COL_CLEAR = 7.0;  // clearance from display right edge to button center column
BUTTON_BEZEL_R   = 8.0;  // half-width of button column on the right of the faceplate

/* =====================================================================
   3. BATTERY — LiPo pouch
   ===================================================================== */
LIPO_W = 50.0;   // along enclosure X
LIPO_H = 34.0;   // along enclosure Y
LIPO_T = 8.0;    // depth (Z)
LIPO_PAD = 1.5;  // foam allowance around cell

/* =====================================================================
   3b. PANEL JACKS (bottom face of body) — bulkhead-mount, wired to main board
   ===================================================================== */
// Through-hole diameters for each jack body (mounting nut clearance)
JACK_PHONES_D   = 9.6;   // 1/4" Switchcraft 11 PJ-055B (mounting thread ~0.375")
JACK_MIC_D      = 8.0;   // 0.206" Switchcraft 12A PJ-068
JACK_AUX_D      = 7.0;   // 3.5mm TRS panel jack
JACK_LEMO_D     = 12.5;  // LEMO FGG.1B.306 panel nut clearance
JACK_INSTALL    = true;  // false = bare bottom face for prototype

// X positions along the bottom edge (in box-X). Order: AUX, MIC, PHONES, LEMO
// Spaced for headset cable fingering clearance.
JACK_X_AUX      = 25;
JACK_X_MIC      = 50;
JACK_X_PHONES   = 78;
JACK_X_LEMO     = 108;

USBC_CUTOUT_W   = 9.5;   // panel-side opening for USB-C receptacle
USBC_CUTOUT_H   = 4.0;
USBC_RIGHT_INSET= 14;    // box-Y from bottom edge to USB-C center

GROMMET_D       = 8.0;   // back-face strain-relief grommet for airframe pigtail

/* =====================================================================
   4. ENCLOSURE SHELL
   ===================================================================== */

WALL          = 2.4;     // side wall thickness
FACEPLATE_T   = 3.0;
BACK_T        = 2.8;
CORNER_R      = 4.0;
INTERIOR_GAP  = 1.0;     // clearance between PCBs and inner wall

// Standoff stack along Z (faceplate at z=0):
FACEPLATE_TO_PANEL = DISPLAY_RECESS + 4.0;            // gap behind display for FFC fold
PANEL_TO_MAIN      = max(PANEL_TALLEST_TOP + MAIN_TALLEST_TOP + 1.0, 14.0);
MAIN_TO_BACK       = max(LIPO_T + LIPO_PAD + 1.0, MAIN_TALLEST_BOT + 3.0);

// Total interior depth (face inside → back inside)
INTERIOR_D = FACEPLATE_TO_PANEL + PANEL_T
           + PANEL_TO_MAIN + MAIN_T
           + MAIN_TO_BACK;
TOTAL_D    = FACEPLATE_T + INTERIOR_D + BACK_T;

// Width strategy:
//   panel PCB hugs right wall → SW3/SW1 land at box-x = INNER_W - (PANEL_W - SW3.x) - INTERIOR_GAP
//   display right edge = button_x - BUTTON_COL_CLEAR
//   display left edge must clear left interior wall by INTERIOR_GAP
// Solving: INNER_W ≥ DISPLAY_MODULE_W + BUTTON_COL_CLEAR + (PANEL_W - SW3.x) + 2*INTERIOR_GAP
PANEL_SW3_FROM_RIGHT = PANEL_W - PANEL_SW3_PWR[0];   // 95 - 80.1 = 14.9
INNER_W = max(
    DISPLAY_MODULE_W + BUTTON_COL_CLEAR + PANEL_SW3_FROM_RIGHT + 2*INTERIOR_GAP,
    PANEL_W + 2*INTERIOR_GAP,
    MAIN_W  + 2*INTERIOR_GAP
);
INNER_H = max(PANEL_H, MAIN_H, DISPLAY_MODULE_H) + 2*INTERIOR_GAP;
OUTER_W = INNER_W + 2*WALL;
OUTER_H = INNER_H + 2*WALL;

// Panel PCB shifted RIGHT (against right interior wall, with INTERIOR_GAP).
// Main PCB stays vertically centered, but horizontally also right-shifted so
// its connector edges align consistently with the panel side.
PANEL_SHIFT = [INNER_W - PANEL_W - INTERIOR_GAP, (INNER_H - PANEL_H)/2];
MAIN_SHIFT  = [INNER_W - MAIN_W  - INTERIOR_GAP, (INNER_H - MAIN_H)/2];

// Display position: right edge sits BUTTON_COL_CLEAR to the left of SW3 button center.
SW3_BOX_X       = PANEL_SHIFT[0] + PANEL_SW3_PWR[0];
DISPLAY_RIGHT_X = SW3_BOX_X - BUTTON_COL_CLEAR;
DISPLAY_LEFT_X  = DISPLAY_RIGHT_X - DISPLAY_MODULE_W;
DISPLAY_ACTIVE_LEFT_X = DISPLAY_LEFT_X + (DISPLAY_MODULE_W - DISPLAY_ACTIVE_W)/2;
DISPLAY_BOTTOM_Y      = (INNER_H - DISPLAY_MODULE_H)/2;
DISPLAY_ACTIVE_BOT_Y  = (INNER_H - DISPLAY_ACTIVE_H)/2;

// Faceplate→body and body→back screw posts: 4 corners, inset
SHELL_SCREW_INSET = 4.5;
SHELL_SCREW_HOLE  = 2.2;   // M2 clearance for screw shank
SHELL_INSERT_D    = 3.5;   // brass heat-set insert OD for M2 (verify against your stock)
SHELL_BOSS_D      = 6.5;   // boss OD around inserts

echo(str("OUTER ", OUTER_W, " x ", OUTER_H, " x ", TOTAL_D, " mm"));
echo(str("INTERIOR depth ", INTERIOR_D, " mm"));

/* =====================================================================
   5. MODULES
   ===================================================================== */

module rounded_box(w, h, t, r) {
    hull() for (x=[r, w-r]) for (y=[r, h-r])
        translate([x, y, 0]) cylinder(r=r, h=t);
}

module shell_screw_xy_list() {
    for (x=[SHELL_SCREW_INSET, OUTER_W-SHELL_SCREW_INSET])
        for (y=[SHELL_SCREW_INSET, OUTER_H-SHELL_SCREW_INSET])
            translate([x,y,0]) children();
}

// Cosmetic dimensions
BUTTON_BEZEL_OD     = 11.0;  // outer dia of round bezel pocket around power button
BUTTON_BEZEL_DEPTH  = 1.0;   // recess depth for inset chiclet look
DISPLAY_FRAME_LIP   = 2.0;   // raised lip width around display active window
DISPLAY_FRAME_H     = 1.0;   // raised lip height above faceplate surface

module faceplate() {
    union() {
        difference() {
            rounded_box(OUTER_W, OUTER_H, FACEPLATE_T, CORNER_R);

            // Display active window (through hole)
            translate([WALL + DISPLAY_ACTIVE_LEFT_X,
                       WALL + DISPLAY_ACTIVE_BOT_Y,
                       -0.1])
                cube([DISPLAY_ACTIVE_W, DISPLAY_ACTIVE_H, FACEPLATE_T + 0.2]);

            // Display module recess (pocket behind window for glass + carrier PCB)
            translate([WALL + DISPLAY_LEFT_X,
                       WALL + DISPLAY_BOTTOM_Y,
                       FACEPLATE_T - DISPLAY_RECESS])
                cube([DISPLAY_MODULE_W, DISPLAY_MODULE_H, DISPLAY_RECESS + 0.1]);

            // Power button: through-hole + outer bezel pocket
            translate([WALL + PANEL_SHIFT[0] + PANEL_SW3_PWR[0],
                       WALL + PANEL_SHIFT[1] + PANEL_SW3_PWR[1], 0]) {
                translate([0,0,-0.1])
                    cylinder(d=PANEL_BTN_HOLE_D, h=FACEPLATE_T+0.2);
                translate([0,0,-0.05])
                    cylinder(d=BUTTON_BEZEL_OD, h=BUTTON_BEZEL_DEPTH+0.05);
            }

            // Encoder shaft through-hole
            translate([WALL + PANEL_SHIFT[0] + PANEL_SW1_ENC[0],
                       WALL + PANEL_SHIFT[1] + PANEL_SW1_ENC[1], -0.1])
                cylinder(d=PANEL_ENC_SHAFT_D, h=FACEPLATE_T+0.2);

            // M2 clearance for faceplate→body screws
            shell_screw_xy_list() translate([0,0,-0.1])
                cylinder(d=SHELL_SCREW_HOLE, h=FACEPLATE_T+0.2);
        }

        // Raised display frame (cosmetic lip around the active window)
        difference() {
            translate([WALL + DISPLAY_ACTIVE_LEFT_X - DISPLAY_FRAME_LIP,
                       WALL + DISPLAY_ACTIVE_BOT_Y - DISPLAY_FRAME_LIP,
                       FACEPLATE_T])
                cube([DISPLAY_ACTIVE_W + 2*DISPLAY_FRAME_LIP,
                      DISPLAY_ACTIVE_H + 2*DISPLAY_FRAME_LIP,
                      DISPLAY_FRAME_H]);
            translate([WALL + DISPLAY_ACTIVE_LEFT_X,
                       WALL + DISPLAY_ACTIVE_BOT_Y,
                       FACEPLATE_T - 0.1])
                cube([DISPLAY_ACTIVE_W, DISPLAY_ACTIVE_H, DISPLAY_FRAME_H + 0.2]);
        }
    }
}

module body() {
    difference() {
        rounded_box(OUTER_W, OUTER_H, INTERIOR_D, CORNER_R);

        // Interior cavity
        translate([WALL, WALL, -0.1])
            cube([INNER_W, INNER_H, INTERIOR_D + 0.2]);

        // Corner shell-screw clearance (top opens to faceplate, bottom to back)
        shell_screw_xy_list() translate([0,0,-0.1])
            cylinder(d=SHELL_SCREW_HOLE, h=INTERIOR_D+0.2);

        // Panel jacks on the BOTTOM face (Y=0 wall) — bulkhead-mount
        // through-holes. Pigtails inside wire to main-board JSTs.
        if (JACK_INSTALL) {
            jack_z = INTERIOR_D / 2;  // vertically centered on bottom-face strip
            for (cfg = [
                [JACK_X_AUX,    JACK_AUX_D],
                [JACK_X_MIC,    JACK_MIC_D],
                [JACK_X_PHONES, JACK_PHONES_D],
                [JACK_X_LEMO,   JACK_LEMO_D],
            ]) {
                translate([cfg[0], -0.1, jack_z])
                    rotate([-90, 0, 0])
                        cylinder(d=cfg[1], h=WALL + 0.2);
            }
        }

        // USB-C cutout on the RIGHT side wall (X = OUTER_W)
        translate([OUTER_W - WALL - 0.1,
                   USBC_RIGHT_INSET,
                   INTERIOR_D - FACEPLATE_TO_PANEL - PANEL_T - PANEL_TO_MAIN/2])
            cube([WALL + 0.2, USBC_CUTOUT_W, USBC_CUTOUT_H], center=false);

        // Airframe pigtail strain-relief grommet on BACK face center
        translate([OUTER_W/2, OUTER_H - WALL - 0.1, INTERIOR_D/2])
            rotate([-90, 0, 0])
                cylinder(d=GROMMET_D, h=WALL + 0.2);
    }

    // Bosses for heat-set inserts (faceplate side, project UP from base)
    translate([0,0,INTERIOR_D - 6])
        shell_screw_xy_list() difference() {
            cylinder(d=SHELL_BOSS_D, h=6);
            translate([0,0,-0.1]) cylinder(d=SHELL_INSERT_D, h=6.1);
        }

    // Panel-PCB standoffs (M2)
    for (h = PANEL_HOLES)
        translate([WALL + PANEL_SHIFT[0] + h[0],
                   WALL + PANEL_SHIFT[1] + h[1],
                   INTERIOR_D - FACEPLATE_TO_PANEL - PANEL_T])
            difference() {
                cylinder(d=5.5, h=FACEPLATE_TO_PANEL + PANEL_T);
                translate([0,0,-0.1]) cylinder(d=SHELL_INSERT_D, h=4);
            }

    // Main-PCB standoffs (M2)
    main_z = INTERIOR_D - FACEPLATE_TO_PANEL - PANEL_T - PANEL_TO_MAIN - MAIN_T;
    for (h = MAIN_HOLES)
        translate([WALL + MAIN_SHIFT[0] + h[0],
                   WALL + MAIN_SHIFT[1] + h[1],
                   main_z])
            difference() {
                cylinder(d=5.5, h=PANEL_TO_MAIN + MAIN_T);
                translate([0,0,-0.1]) cylinder(d=SHELL_INSERT_D, h=4);
            }

    // LiPo pocket walls (a soft rectangular cage in the back-cover region)
    translate([(OUTER_W - LIPO_W)/2 - LIPO_PAD,
               (OUTER_H - LIPO_H)/2 - LIPO_PAD,
               0])
        difference() {
            cube([LIPO_W + 2*LIPO_PAD, LIPO_H + 2*LIPO_PAD, LIPO_T + LIPO_PAD]);
            translate([LIPO_PAD, LIPO_PAD, -0.1])
                cube([LIPO_W, LIPO_H, LIPO_T + LIPO_PAD + 0.2]);
        }
}

module back_cover() {
    difference() {
        rounded_box(OUTER_W, OUTER_H, BACK_T, CORNER_R);

        // Vent grid for heat (TP4056, MT3608s, LiPo gas escape)
        for (x=[10:6:OUTER_W-10]) for (y=[10:6:OUTER_H-10])
            translate([x,y,-0.1]) cylinder(d=2.5, h=BACK_T+0.2);

        // Shell screw clearance into bosses from below
        shell_screw_xy_list() translate([0,0,-0.1])
            cylinder(d=SHELL_SCREW_HOLE, h=BACK_T+0.2);
    }
}

/* =====================================================================
   6. ASSEMBLY VIEW — set RENDER below to "faceplate", "body", "back",
      or "exploded" to inspect / export each part
   ===================================================================== */
RENDER = "exploded";

if (RENDER == "faceplate") faceplate();
else if (RENDER == "body") body();
else if (RENDER == "back") back_cover();
else if (RENDER == "exploded") {
    translate([0,0, TOTAL_D + 15]) faceplate();
    translate([0,0, BACK_T])       body();
    back_cover();
}
