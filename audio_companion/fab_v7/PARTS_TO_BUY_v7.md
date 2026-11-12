# Parts to buy for 5 boards (updated 2026-10-17 after the order was placed)
JLCPCB places only the SMT parts. Everything below is hand-soldered or bought separately.

## A. Board-side through-hole headers: TAN/IVORY versions (no "-S" suffix) to match the CrowPanel (LCSC; stock checked 2026-10-17)
JST naming: "-S" = natural WHITE, no suffix = IVORY (tan). LCSC's own descriptions call all of them "white", so confirm against the product photo; JST's datasheet is the reference.
| Part | LCSC | Buy | Stock now |
|---|---|---|---|
| JST S2B-PH-K(LF)(SN) 2-pin | C265016 | 35 (6 per board x5 + 5 spare) | 2,790 |
| JST S3B-PH-K(LF)(SN) 3-pin | C545716 | 25 | 13,340 |
| JST S4B-PH-K(LF)(SN) 4-pin | C265452 | 8 | 3,480 |
| JST S5B-PH-K(LF)(SN) 5-pin | not found on LCSC; search DigiKey/Farnell for S5B-PH-K(LF)(SN), or use white S5B-PH-K-S C157923 (60,750) for this one | 8 | - |
Per board: 2-pin x6 (J-BAT-1, J-BAT-2, J-BTN-1, J-HAPTIC-1, J-MIC-IN-1, PTT jack). J-USB5V-1 is NOT populated: its plug would collide with the PTT plug, so solder the 5V/G wires straight into its two holes (5V = lower hole, G = upper) and route the cable left/down with strain relief, 3-pin x4 (J-35-1/2/3, J-635-IN-1), 4-pin x1 (J-BTN-IN-1), 5-pin x1 (J-AIRCRAFT-1). Same footprints as the "-S" parts, so nothing on the board changes.
(White "-S" versions, for reference only: C173752 2-pin, C157929 3-pin, C157926 4-pin, C157923 5-pin.)

## B. Stack headers
- 1x7 male header, long pins, about 21 mm overall (v6 used 19 mm for a 10 mm gap). 2 per board = 10 + 2 spare. Not on LCSC: DigiKey/Mouser/Amazon "stackable/long pin header 1x7 2.54".

## C. Cable side (genuine JST from DigiKey / Mouser / Farnell), per board assuming one plug per header
- PHR-2 x6 (J-BAT-1/2 jumper cable end on our board, J-BTN-1, J-HAPTIC-1, J-MIC-IN-1, PTT, spare; none for J-USB5V-1), PHR-3 x4, PHR-4 x1, PHR-5 x1, PHR-6 x1 (J-PANEL-1), PHR-8 x1 (J-ENC-1).
- SPH-002T-P0.5S crimp contacts: about 70 per board (count your pins + 20%); buy a few hundred. EJ-PH extraction tool optional.
- Panel J10 power cable: XH 2.54 mm 4-pin plug (XHP-4 + SXH-001T-P0.6 crimps); wire pins 3 (+5V) and 4 (GND). 24-26 AWG wire.
- Battery: single-cell 3.7 V LiPo with protection circuit and a JST PH 2.0 2-pin plug (plugs into our J-BAT-1/2). Meter polarity first.
- Panel J3 battery jumper (user measured the panel BAT connector at 2.5 mm pitch = XH, not PH): cable from J-BAT-2 = PHR-2 on our end, XHP-2 housing + SXH-001T-P0.6 crimps on the panel end. J3 pin 1 = VBAT (+).

## D. Cover controls
- ELMA E37-VT6330-1 dual concentric encoder with push + knobs (wired to J-ENC-1: GND, outer A, outer B, inner A, inner B, push, GND, 3V3).
- Power button and latching push-on/push-off bypass switch: not chosen yet (wire to J-PANEL-1).
- 4 light pipes (4.0 mm pitch, about 15-18 mm long) over the ear LEDs PWR / ACT / ANR / BYP.

## E. Mechanical / misc
- M3 standoffs + screws (plated GND holes at the CrowPanel pattern), zip ties (2.5 mm) for the LEMO slots, 6 wires for the LEMO pigtail, USB-A to USB-C cable or power bank (needs 1 A).

## F. DigiKey order (5 boards; quantities include spares). Numbers found on DigiKey 2026-10-18; check stock/lead time (pages quote 16-25 weeks factory lead time)
| Part | DigiKey # | Qty |
|---|---|---|
| PHR-2 housing | 455-1165-ND | 40 |
| PHR-3 housing | 455-1126-ND | 25 |
| PHR-4 housing | 455-1164-ND | 8 |
| PHR-5 housing | 455-1163-ND | 8 |
| PHR-6 housing | 455-1162-ND | 8 |
| PHR-8 housing | 455-1189-ND | 8 |
| SPH-002T-P0.5S crimp contact (24-30 AWG) | 455-1127-1-ND (cut tape) | 300 |
| SXH-001T-P0.6 crimp contact (XH) | 455-1135-1-ND (cut tape) | 50 |
| XHP-2 housing (panel J3 battery jumper) | not found: search "XHP-2" | 8 |
| XHP-4 housing (panel J10 power) | not found: search "XHP-4" | 8 |
| S2B-PH-K-S 2-pin header (WHITE) | 455-1719-ND | 35 |
| S3B-PH-K-S 3-pin header (WHITE) | 455-1720-ND | 25 |
| S4B-PH-K-S 4-pin header (WHITE) | 455-1721-ND | 8 |
| S5B-PH-K-S 5-pin header (WHITE) | 455-1722-ND | 8 |
The tan (ivory, no "-S") headers: DigiKey numbers not found; LCSC numbers are in section A. Long-pin 1x7 headers: not searched.
