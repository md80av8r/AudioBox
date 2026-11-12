set -e
W=/Users/jeffreykadans/Developer/MicBreakoutBox/REV_D/audio_companion_work; cd $W
S=/private/tmp/claude-501/-Users-jeffreykadans-Developer-MicBreakoutBoxrev-B/f0565222-a613-4c2b-97d7-b1cd99af7037/scratchpad
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3; F='assert|Fontconfig|swig|Debug'
FPD=/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints; A=scripts/pcb_v19_add.py
$PY scripts/pcb_v19a.py 2>&1 | grep -v -E "$F"
$PY $A audio_companion_v19_s1.kicad_pcb $S/s2a.kicad_pcb $FPD/Relay_SMD.pretty Relay_DPDT_Omron_G6K-2F-Y $S/spec_relay.json 2>&1 | grep -v -E "$F"
$PY $A $S/s2a.kicad_pcb $S/s2b.kicad_pcb $FPD/Resistor_SMD.pretty R_0402_1005Metric $S/spec_r.json 2>&1 | grep -v -E "$F"
$PY $A $S/s2b.kicad_pcb $S/s2c.kicad_pcb $FPD/Capacitor_SMD.pretty C_0402_1005Metric $S/spec_c.json 2>&1 | grep -v -E "$F"
$PY $A $S/s2c.kicad_pcb $S/s2d.kicad_pcb $FPD/Connector_JST.pretty JST_PH_S8B-PH-SM4-TB_1x08-1MP_P2.00mm_Horizontal $S/spec_jenc.json 2>&1 | grep -v -E "$F"
$PY $A $S/s2d.kicad_pcb audio_companion_v19_s2.kicad_pcb $FPD/Connector_JST.pretty JST_PH_S6B-PH-SM4-TB_1x06-1MP_P2.00mm_Horizontal $S/spec_jpan.json 2>&1 | grep -v -E "$F"
$PY scripts/pcb_v19_place.py audio_companion_v19_s2.kicad_pcb audio_companion_v19_s3.kicad_pcb 2>&1 | grep -v -E "$F"
