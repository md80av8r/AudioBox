# MD-88 Breakout — Parts Order List (prototype qty 2–3)

Status legend: ✅ in hand / ordered  ·  ☐ to order

## Already covered

- ✅ **PCBs** — submitted to JLCPCB with SMT assembly of 16 passives
- ✅ **U1 ESP32 DevKitC WROOM-32D, 38-pin** — qty 4 on hand (AITRIP)
- ✅ **LEMO 6-pin panel socket** — ordered (Bose A20 / Lightspeed Zulu compatible, generic)

---

## Order 1: Amazon (modules — fastest, buy ≥1 spare each)

| ☐ | Ref | Part | Qty | Notes |
|---|---|---|---|---|
| ☐ | U2 | INMP441 I²S MEMS mic breakout | 4 | Generic 6-pin module, all clones identical |
| ☐ | U3 | MAX98357A I²S amp breakout | 4 | Adafruit #3006 preferred, generic OK |
| ☐ | U4 | SH1106 1.3" 128×64 OLED, I²C, 4-pin | 4 | **Verify SH1106 not SSD1306** — different controller |
| ☐ | U5 | TP4056 charger module **with DW01 protection IC** | 4 | The "USB-C TP4056 + protection" version |
| ☐ | U6, U8 | MT3608 boost module | 6 | U6 set to 5V output, U8 set to 12V (set with onboard pot before install) |
| ☐ | BT1 cell | Protected 18650, ~3400mAh (Panasonic NCR18650B or Samsung 30Q) | 4 | **Buy from a reputable seller — Amazon has many fakes** |

**Verify before clicking buy:**
- DevKitC modules already include CP2102 USB-UART, so if buying spares pick "WROOM-32D, 38-pin, USB-C, CP2102"
- OLED: search "1.3 inch SH1106 OLED I2C 4 pin" and check the seller's photos for `SH1106` printed on the controller chip

---

## Order 2: Digikey or Mouser (one cart — small parts, amortizes shipping)

### Through-hole passives + power
| ☐ | Ref | Value | Package | Qty |
|---|---|---|---|---|
| ☐ | C1 | 10µF / 25V radial alum elec | D5.0mm P2.00mm | 5 |
| ☐ | C2 | 100µF / 16V radial | D6.3mm P2.50mm | 5 |
| ☐ | C4 | 10µF radial | D5.0mm P2.00mm | 5 |
| ☐ | C5 | 22µF radial | D6.3mm P2.50mm | 5 |
| ☐ | C7 | 47µF / 25V radial | D6.3mm P2.50mm | 5 |
| ☐ | D1 | 3mm green LED, T-1 leaded | through-hole | 5 |
| ☐ | D2 | 1N5819 Schottky diode | DO-41 axial | 5 |
| ☐ | R7 | 1.2kΩ axial resistor, 1/4W | DIN 0207 | 5 |

### Connectors
| ☐ | Ref | Part | Qty |
|---|---|---|---|
| ☐ | J1 | USB-C receptacle, GCT USB4105-GF-A (matches your KiCad footprint exactly) | 5 |
| ☐ | J2 | 1×3 pin header, 2.54mm, vertical | 5 |
| ☐ | J3 | 1×3 pin header, 2.54mm, vertical | 5 |
| ☐ | J4 | 1×6 pin header, 2.54mm, vertical | 5 |
| ☐ | J5 | 1×3 pin header, 2.54mm, vertical | 5 |
| ☐ | (modules) | 1×4 pin headers (for U4 OLED + U6/U8 MT3608) | 10 |
| ☐ | (modules) | 1×6 pin headers (for U2 INMP441 + U3 MAX98357A + U5 TP4056) | 12 |
| ☐ | (DevKitC) | 2×19 dual-row female socket, 2.54mm (or 2× 1×19 female sockets) | 8 |

### Switches
| ☐ | Ref | Part | Qty |
|---|---|---|---|
| ☐ | SW1 | DIP slide 4-pos SPST, 9.78×12.34mm body, 2.54mm pitch — CTS or C&K | 4 |
| ☐ | SW2 | SP3T slide switch, PCM13 footprint — Nidec/Copal CL-SB series or equivalent | 4 |
| ☐ | SW3 | DIP slide 1-pos SPST, low profile 6.7×4.1mm | 4 |
| ☐ | SW4, SW5 | Panel-mount momentary pushbutton (PTT + ATC playback) | 6 |

### Pots
| ☐ | Ref | Part | Qty |
|---|---|---|---|
| ☐ | VR1, VR2 | Alps RK09K, 10kΩ audio taper, panel-mount, vertical | 6 |

### Battery holder
| ☐ | Ref | Part | Qty |
|---|---|---|---|
| ☐ | BT1 | Keystone 1042 — 18650 holder, PCB through-hole | 4 |

### Panel jacks
| ☐ | Function | Part | Qty |
|---|---|---|---|
| ☐ | 1/4" stereo TRS audio out | Switchcraft 12B (open frame) or Neutrik NRJ6HF (sealed) | 4 |
| ☐ | 3.5mm aux in (GDL-52) | CUI SJ-3523 or similar panel-mount | 4 |

---

## Order 3: Aircraft Spruce (specialty aviation jack)

| ☐ | Function | Part | Qty | Notes |
|---|---|---|---|---|
| ☐ | 0.206" GA mic jack, panel-mount | Switchcraft TM5M or PJRAS-202M | 4 | aircraftspruce.com, ~$15–20 each |

---

## Order 4: Connector kits + supplies

| ☐ | Item | Qty | Notes |
|---|---|---|---|
| ☐ | Mixed JST PH 2.0mm + Dupont 2.54mm pre-crimped kit — Amazon | 1 kit | Brands: Hilitchi, Glarks. ~$25. Skip kits that include only crimp tool + bare terminals. |
| ☐ | Heat-shrink tubing assortment | 1 | $10 Amazon |

**Wire:** ✅ user has aviation-grade shielded wire on hand (22 AWG for power, 24 AWG for pigtails and audio). No purchase needed.

---

## Recommended order sequence

1. **Today:** ✅ LEMO socket (done — longest lead)
2. **This week:** Amazon modules — get them in hand, breadboard-test the I²S mic chain before PCBs arrive
3. **This week:** Digikey/Mouser one-cart order — bundle everything in section 2
4. **This week:** Aircraft Spruce GA mic jack
5. **Whenever:** JST crimp kit (only needed at final assembly)

Aim to have everything except the PCBs in hand the day boards ship from JLCPCB. Then full assembly is one weekend.

## Open items before assembly

- Confirm panel jack layout on enclosure top/front faces
- Measure actual LEMO panel hole diameter when it arrives (need this for top cover SCAD)
- Verify OLED module model when it arrives (need exact mounting hole spacing for top cover)
- Confirm pot bushing thread (M7×0.75 typical for Alps RK09K)
- Decide knob style for VR1/VR2
